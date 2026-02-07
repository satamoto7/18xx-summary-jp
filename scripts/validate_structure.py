from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

GAMES_DIR = Path("docs/games")
GAMES_INDEX_PATH = GAMES_DIR / "index.md"
GAMES_PAGES_PATH = GAMES_DIR / ".pages"

TAB_PATTERN = re.compile(r'^===\s+"([^"]+)"\s*$', re.MULTILINE)
TITLE_PATTERN = re.compile(r"^#\s+.+\s+サマリー\s*$", re.MULTILINE)
ACTION_BLOCK_PATTERN = re.compile(r'<div class="actions">(?P<body>.*?)</div>', re.DOTALL)
DOWNLOAD_MACRO_PATTERN = re.compile(r'{{\s*download_link\("(?P<filename>[^"]+)"\)\s*}}')
DOWNLOAD_HREF_PATTERN = re.compile(r'href\s*=\s*"(?P<href>[^"]+)"')
GAMES_INDEX_ACTION_PATTERN = re.compile(
    r'{{\s*game_actions\([^,]+,\s*"(?P<href>[^"]+)"\)\s*}}'
)
GAMES_INDEX_CARD_PATTERN = re.compile(
    r'{{\s*game_card\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"(?P<href>[^"]+)"\s*\)\s*}}'
)

ALLOWED_TAB_NAMES = {
    "SR",
    "OR",
    "セットアップ / 早見",
    "会社の種類 / 準備",
    "早見表",
    "その他",
    "プライベート一覧",
    "合併R",
    "ゲームの終了",
}

# 1862 は運用上 `その他` タブをセットアップ枠として許容する。
LEGACY_SETUP_ALLOWED_STEMS = {"1862"}


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    level: str
    message: str

    def format(self) -> str:
        return f"[{self.level}] {self.path.as_posix()}: {self.message}"


@dataclass
class ValidationSummary:
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]

    def has_errors(self) -> bool:
        return bool(self.errors)


def _collect_game_files(games_dir: Path) -> list[Path]:
    return sorted(path for path in games_dir.glob("*.md") if path.stem != "index")


def _extract_tabs(content: str) -> list[str]:
    return [match.group(1) for match in TAB_PATTERN.finditer(content)]


def _normalize_href_to_stem(href: str) -> str:
    decoded = unquote(href).strip()
    if decoded.endswith("/"):
        decoded = decoded[:-1]
    return Path(decoded).name


def _extract_pages_nav_entries(content: str) -> list[str]:
    entries: list[str] = []
    in_nav = False
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("nav:"):
            in_nav = True
            continue
        if not in_nav:
            continue
        if not raw_line.startswith("  - "):
            break
        item = stripped[2:].strip()
        if item.endswith(".md"):
            entries.append(item)
    return entries


def validate_game_file(path: Path) -> ValidationSummary:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    content = path.read_text(encoding="utf-8")
    if not TITLE_PATTERN.search(content):
        errors.append(
            ValidationIssue(
                path=path,
                level="ERROR",
                message='タイトル `# <ゲーム名> サマリー` が見つかりません。',
            )
        )

    action_match = ACTION_BLOCK_PATTERN.search(content)
    if not action_match:
        errors.append(
            ValidationIssue(
                path=path,
                level="ERROR",
                message='`<div class="actions">...</div>` ブロックが見つかりません。',
            )
        )
    else:
        action_body = action_match.group("body")
        if "{{ print_button() }}" not in action_body:
            errors.append(
                ValidationIssue(
                    path=path,
                    level="ERROR",
                    message="actionsブロック内に `print_button()` がありません。",
                )
            )

        expected_filename = f"{path.stem}.txt"
        macro_match = DOWNLOAD_MACRO_PATTERN.search(action_body)
        if macro_match:
            actual_filename = macro_match.group("filename")
            if actual_filename != expected_filename:
                errors.append(
                    ValidationIssue(
                        path=path,
                        level="ERROR",
                        message=(
                            f"download_linkのファイル名が不一致です。"
                            f" expected=`{expected_filename}`, actual=`{actual_filename}`"
                        ),
                    )
                )
        else:
            href_match = DOWNLOAD_HREF_PATTERN.search(action_body)
            expected_href = f"../../assets/{expected_filename}"
            if not href_match:
                errors.append(
                    ValidationIssue(
                        path=path,
                        level="ERROR",
                        message="actionsブロック内に download_link またはダウンロードhrefがありません。",
                    )
                )
            else:
                actual_href = href_match.group("href")
                if actual_href != expected_href:
                    errors.append(
                        ValidationIssue(
                            path=path,
                            level="ERROR",
                            message=(
                                f"テキストDLリンクが不一致です。"
                                f" expected=`{expected_href}`, actual=`{actual_href}`"
                            ),
                        )
                    )

    tabs = _extract_tabs(content)
    tab_set = set(tabs)
    if "SR" not in tab_set:
        errors.append(
            ValidationIssue(path=path, level="ERROR", message='`=== "SR"` タブがありません。')
        )
    if "OR" not in tab_set:
        errors.append(
            ValidationIssue(path=path, level="ERROR", message='`=== "OR"` タブがありません。')
        )

    has_standard_setup = "セットアップ / 早見" in tab_set
    has_split_setup = "会社の種類 / 準備" in tab_set and "早見表" in tab_set
    has_legacy_setup = "その他" in tab_set
    if not (has_standard_setup or has_split_setup):
        if has_legacy_setup and path.stem in LEGACY_SETUP_ALLOWED_STEMS:
            pass
        elif has_legacy_setup:
            warnings.append(
                ValidationIssue(
                    path=path,
                    level="WARN",
                    message=(
                        "セットアップ枠が標準形式ではありません。"
                        '`"セットアップ / 早見"` または `"会社の種類 / 準備"+"早見表"` の利用を推奨します。'
                    ),
                )
            )
        else:
            errors.append(
                ValidationIssue(
                    path=path,
                    level="ERROR",
                    message=(
                        "セットアップ枠タブがありません。"
                        ' `"セットアップ / 早見"` または `"会社の種類 / 準備"+"早見表"` が必要です。'
                    ),
                )
            )

    for tab_name in tabs:
        if tab_name not in ALLOWED_TAB_NAMES:
            warnings.append(
                ValidationIssue(
                    path=path,
                    level="WARN",
                    message=f"未登録のタブ名です: `{tab_name}`",
                )
            )

    return ValidationSummary(errors=errors, warnings=warnings)


def validate_pages_alignment(
    game_files: Iterable[Path], pages_path: Path, index_path: Path
) -> ValidationSummary:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    stems = {f"{path.stem}.md" for path in game_files}

    pages_content = pages_path.read_text(encoding="utf-8")
    nav_entries = _extract_pages_nav_entries(pages_content)
    nav_game_entries = [entry for entry in nav_entries if entry != "index.md"]
    nav_set = set(nav_game_entries)

    missing_in_pages = sorted(stems - nav_set)
    extra_in_pages = sorted(nav_set - stems)
    if missing_in_pages:
        errors.append(
            ValidationIssue(
                path=pages_path,
                level="ERROR",
                message=f".pages に不足しているゲームがあります: {', '.join(missing_in_pages)}",
            )
        )
    if extra_in_pages:
        errors.append(
            ValidationIssue(
                path=pages_path,
                level="ERROR",
                message=f".pages に存在しないゲームが含まれています: {', '.join(extra_in_pages)}",
            )
        )

    index_content = index_path.read_text(encoding="utf-8")
    index_entries = [
        _normalize_href_to_stem(match.group("href"))
        for match in GAMES_INDEX_ACTION_PATTERN.finditer(index_content)
    ]
    index_entries.extend(
        _normalize_href_to_stem(match.group("href"))
        for match in GAMES_INDEX_CARD_PATTERN.finditer(index_content)
    )
    index_set = {f"{name}.md" for name in index_entries if name}

    missing_in_index = sorted(stems - index_set)
    extra_in_index = sorted(index_set - stems)
    if missing_in_index:
        errors.append(
            ValidationIssue(
                path=index_path,
                level="ERROR",
                message=f"ゲーム一覧(index.md)に不足しているゲームがあります: {', '.join(missing_in_index)}",
            )
        )
    if extra_in_index:
        errors.append(
            ValidationIssue(
                path=index_path,
                level="ERROR",
                message=f"ゲーム一覧(index.md)に存在しないゲームが含まれています: {', '.join(extra_in_index)}",
            )
        )

    duplicate_entries = sorted(
        {entry for entry in index_entries if index_entries.count(entry) > 1}
    )
    if duplicate_entries:
        warnings.append(
            ValidationIssue(
                path=index_path,
                level="WARN",
                message=f"ゲーム一覧(index.md)に重複エントリがあります: {', '.join(duplicate_entries)}",
            )
        )

    return ValidationSummary(errors=errors, warnings=warnings)


def run_validation(
    games_dir: Path = GAMES_DIR,
    pages_path: Path = GAMES_PAGES_PATH,
    index_path: Path = GAMES_INDEX_PATH,
) -> ValidationSummary:
    game_files = _collect_game_files(games_dir)
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    for game_path in game_files:
        result = validate_game_file(game_path)
        errors.extend(result.errors)
        warnings.extend(result.warnings)

    alignment = validate_pages_alignment(game_files, pages_path, index_path)
    errors.extend(alignment.errors)
    warnings.extend(alignment.warnings)
    return ValidationSummary(errors=errors, warnings=warnings)


def main() -> int:
    summary = run_validation()
    for issue in summary.errors:
        print(issue.format())
    for issue in summary.warnings:
        print(issue.format())

    if summary.has_errors():
        print(f"\nValidation failed: {len(summary.errors)} error(s), {len(summary.warnings)} warning(s).")
        return 1

    print(f"Validation passed: 0 error(s), {len(summary.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
