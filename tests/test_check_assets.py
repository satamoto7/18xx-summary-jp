import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_assets import find_missing_assets


class CheckAssetsTests(unittest.TestCase):
    def test_detects_missing_text_and_cover_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            games = root / "games"
            assets = root / "assets"
            games.mkdir()
            assets.mkdir()
            (games / "18Test.md").write_text("# test\n", encoding="utf-8")
            meta = assets / "bgg-meta.json"
            meta.write_text(
                json.dumps({"1": {"cover": {"path": "assets/covers/1.webp"}}}),
                encoding="utf-8",
            )
            missing = find_missing_assets(games, assets, meta)
            self.assertEqual(
                missing,
                [(assets / "18Test.txt").as_posix(), (assets / "covers/1.webp").as_posix()],
            )

    def test_accepts_existing_generated_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            games = root / "games"
            assets = root / "assets"
            games.mkdir()
            assets.mkdir()
            (games / "18Test.md").write_text("# test\n", encoding="utf-8")
            (assets / "18Test.txt").write_text("test\n", encoding="utf-8")
            meta = assets / "bgg-meta.json"
            meta.write_text("{}", encoding="utf-8")
            self.assertEqual(find_missing_assets(games, assets, meta), [])


if __name__ == "__main__":
    unittest.main()
