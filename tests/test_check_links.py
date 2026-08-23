import tempfile
import unittest
from pathlib import Path

from scripts.check_links import check_links


class CheckLinksTests(unittest.TestCase):
    def test_detects_missing_local_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "docs"
            root.mkdir()
            (root / "index.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            issues = check_links(root)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].line, 1)

    def test_ignores_external_links_and_code_fences(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "docs"
            root.mkdir()
            (root / "index.md").write_text(
                "[external](https://example.com/missing)\n"
                "```markdown\n"
                "[fenced](missing.md)\n"
                "```\n",
                encoding="utf-8",
            )
            self.assertEqual(check_links(root), [])


if __name__ == "__main__":
    unittest.main()
