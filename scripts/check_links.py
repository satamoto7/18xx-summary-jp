"""Check local Markdown/HTML links and referenced assets without network access."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


DOCS_DIR = Path("docs")
MARKDOWN_LINK = re.compile(r"(?<!!)(?:\[[^\]]*\])\(([^)]+)\)")
HTML_HREF = re.compile(r"\bhref\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
HTML_SRC = re.compile(r"\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


@dataclass(frozen=True)
class LinkIssue:
    source: Path
    line: int
    target: str

    def format(self) -> str:
        return f"[ERROR] {self.source.as_posix()}:{self.line}: リンク先が見つかりません: {self.target}"


def _is_external(target: str) -> bool:
    parsed = urlsplit(target)
    return bool(parsed.scheme or parsed.netloc) or target.startswith(("#", "//", "data:"))


def _target_path(raw_target: str) -> str:
    target = raw_target.strip().strip("<>")
    if target.startswith("{") or target.startswith("{{"):
        return ""
    return urlsplit(target).path


def _resolve_target(source: Path, raw_target: str) -> Path | None:
    target = _target_path(raw_target)
    if not target or _is_external(raw_target):
        return None
    decoded = Path(unquote(target))
    resolved = (source.parent / decoded).resolve()
    if target.endswith("/") or resolved.is_dir():
        resolved = resolved / "index.md"
    return resolved


def _iter_targets(path: Path) -> list[tuple[int, str]]:
    targets: list[tuple[int, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence = False
    for line_number, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        targets.extend((line_number, value) for value in MARKDOWN_LINK.findall(line))
        targets.extend((line_number, value) for value in HTML_HREF.findall(line))
        targets.extend((line_number, value) for value in HTML_SRC.findall(line))
    return targets


def check_links(docs_dir: Path = DOCS_DIR) -> list[LinkIssue]:
    issues: list[LinkIssue] = []
    docs_root = docs_dir.resolve()
    for source in sorted(docs_dir.rglob("*.md")):
        for line_number, raw_target in _iter_targets(source):
            resolved = _resolve_target(source, raw_target)
            if resolved is None or not resolved.is_relative_to(docs_root):
                continue
            if not resolved.exists():
                issues.append(LinkIssue(source, line_number, raw_target.strip()))
    return issues


def main() -> int:
    issues = check_links()
    for issue in issues:
        print(issue.format())
    if issues:
        print(f"\nリンク監査に失敗しました: {len(issues)}件")
        return 1
    print("Link check passed: 0 error(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
