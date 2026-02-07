import tempfile
import unittest
from pathlib import Path

from scripts.validate_structure import run_validation, validate_game_file


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


class ValidateStructureTests(unittest.TestCase):
    def test_validate_game_file_passes_with_required_structure(self) -> None:
        content = """# 18Test サマリー

<div class="actions">
  {{ print_button() }}
  {{ download_link("18Test.txt") }}
</div>

=== "SR"
    text
=== "OR"
    text
=== "セットアップ / 早見"
    text
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "18Test.md"
            _write(path, content)
            result = validate_game_file(path)
            self.assertEqual(result.errors, [])
            self.assertEqual(result.warnings, [])

    def test_validate_game_file_detects_missing_required_elements(self) -> None:
        content = """# 18Bad

=== "SR"
    text
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "18Bad.md"
            _write(path, content)
            result = validate_game_file(path)
            messages = "\n".join(issue.message for issue in result.errors)
            self.assertIn("タイトル", messages)
            self.assertIn("actions", messages)
            self.assertIn('`=== "OR"`', messages)

    def test_validate_game_file_warns_legacy_setup_tab_by_default(self) -> None:
        content = """# 18Legacy サマリー

<div class="actions">
  {{ print_button() }}
  {{ download_link("18Legacy.txt") }}
</div>

=== "SR"
    text
=== "OR"
    text
=== "その他"
    text
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "18Legacy.md"
            _write(path, content)
            result = validate_game_file(path)
            self.assertEqual(result.errors, [])
            self.assertEqual(len(result.warnings), 1)
            self.assertIn("標準形式ではありません", result.warnings[0].message)

    def test_validate_game_file_allows_1862_legacy_setup_tab(self) -> None:
        content = """# 1862 サマリー

<div class="actions">
  {{ print_button() }}
  {{ download_link("1862.txt") }}
</div>

=== "SR"
    text
=== "OR"
    text
=== "その他"
    text
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "1862.md"
            _write(path, content)
            result = validate_game_file(path)
            self.assertEqual(result.errors, [])
            self.assertEqual(result.warnings, [])

    def test_run_validation_checks_pages_and_index_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            games = root / "docs" / "games"
            _write(
                games / "A.md",
                """# A サマリー

<div class="actions">
  {{ print_button() }}
  {{ download_link("A.txt") }}
</div>

=== "SR"
=== "OR"
=== "セットアップ / 早見"
""",
            )
            _write(
                games / ".pages",
                """title: ゲーム一覧
nav:
  - index.md
  - A.md
""",
            )
            _write(
                games / "index.md",
                """# ゲーム一覧
{{ game_actions("1", "A/") }}
""",
            )

            result = run_validation(
                games_dir=games,
                pages_path=games / ".pages",
                index_path=games / "index.md",
            )
            self.assertEqual(result.errors, [])

    def test_run_validation_detects_alignment_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            games = root / "docs" / "games"
            _write(
                games / "A.md",
                """# A サマリー

<div class="actions">
  {{ print_button() }}
  {{ download_link("A.txt") }}
</div>

=== "SR"
=== "OR"
=== "セットアップ / 早見"
""",
            )
            _write(
                games / ".pages",
                """title: ゲーム一覧
nav:
  - index.md
""",
            )
            _write(games / "index.md", "# ゲーム一覧\n")

            result = run_validation(
                games_dir=games,
                pages_path=games / ".pages",
                index_path=games / "index.md",
            )
            self.assertGreaterEqual(len(result.errors), 2)
            messages = "\n".join(issue.message for issue in result.errors)
            self.assertIn(".pages に不足しているゲーム", messages)
            self.assertIn("ゲーム一覧(index.md)に不足しているゲーム", messages)


if __name__ == "__main__":
    unittest.main()
