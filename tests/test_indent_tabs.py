import unittest

from scripts.indent_tabs import indent_tabs_in_content


class IndentTabsTests(unittest.TestCase):
    def test_indents_between_tab_headers(self) -> None:
        content = (
            '=== "SR"\n'
            "Line 1\n"
            "  Line 2\n"
            '=== "OR"\n'
            "Next\n"
        )
        expected = (
            '=== "SR"\n'
            "    Line 1\n"
            "      Line 2\n"
            '=== "OR"\n'
            "    Next\n"
        )
        self.assertEqual(indent_tabs_in_content(content), expected)

    def test_ignores_tab_markers_inside_code_fences(self) -> None:
        content = (
            "```markdown\n"
            '=== "Not a tab"\n'
            "```\n"
            "Outside\n"
            '=== "Real tab"\n'
            "Text\n"
        )
        expected = (
            "```markdown\n"
            '=== "Not a tab"\n'
            "```\n"
            "Outside\n"
            '=== "Real tab"\n'
            "    Text\n"
        )
        self.assertEqual(indent_tabs_in_content(content), expected)


if __name__ == "__main__":
    unittest.main()
