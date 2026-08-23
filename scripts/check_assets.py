"""Verify generated text files and metadata-referenced cover assets."""
from __future__ import annotations

import json
import sys
from pathlib import Path


DOCS_DIR = Path("docs")
GAMES_DIR = DOCS_DIR / "games"
ASSETS_DIR = DOCS_DIR / "assets"
META_PATH = ASSETS_DIR / "bgg-meta.json"


def find_missing_assets(
    games_dir: Path = GAMES_DIR,
    assets_dir: Path = ASSETS_DIR,
    meta_path: Path = META_PATH,
) -> list[str]:
    missing: list[str] = []
    game_files = sorted(path for path in games_dir.glob("*.md") if path.stem != "index")
    for game_path in game_files:
        text_path = assets_dir / f"{game_path.stem}.txt"
        if not text_path.is_file():
            missing.append(text_path.as_posix())

    if meta_path.is_file():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        for entry in metadata.values():
            cover = entry.get("cover") if isinstance(entry, dict) else None
            cover_path = cover.get("path") if isinstance(cover, dict) else None
            if not cover_path:
                continue
            resolved = assets_dir.parent / Path(cover_path)
            if not resolved.is_file():
                missing.append(resolved.as_posix())
    return sorted(set(missing))


def main() -> int:
    missing = find_missing_assets()
    if missing:
        for path in missing:
            print(f"[ERROR] 生成物が見つかりません: {path}")
        print(f"\n資産監査に失敗しました: {len(missing)}件")
        return 1
    print("Asset check passed: 0 missing asset(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
