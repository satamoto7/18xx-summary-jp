"""Regression checks against the real repository content."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.check_links import check_links
from scripts.validate_structure import run_validation


ROOT = Path(__file__).resolve().parent.parent


class RealSiteStructureTests(unittest.TestCase):
    def test_all_game_files_pass_structure_validation(self) -> None:
        result = run_validation(
            games_dir=ROOT / "docs" / "games",
            pages_path=ROOT / "docs" / "games" / ".pages",
            index_path=ROOT / "docs" / "games" / "index.md",
        )
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_all_local_links_resolve(self) -> None:
        self.assertEqual(check_links(ROOT / "docs"), [])


if __name__ == "__main__":
    unittest.main()
