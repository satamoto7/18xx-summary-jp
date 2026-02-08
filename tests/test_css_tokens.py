"""Tests that theme-tokens.css defines all required design tokens."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

TOKENS_PATH = Path(__file__).resolve().parent.parent / "docs" / "stylesheets" / "theme-tokens.css"


def _read_tokens() -> str:
    return TOKENS_PATH.read_text(encoding="utf-8")


def _token_defined(css: str, name: str) -> bool:
    """Check that --<name> is defined (appears as a property, not just referenced)."""
    pattern = rf"^\s*{re.escape(name)}\s*:"
    return bool(re.search(pattern, css, re.MULTILINE))


class SpacingTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_spacing_tokens_exist(self):
        for n in (1, 2, 3, 4, 5, 6, 8):
            with self.subTest(token=f"--space-{n}"):
                self.assertTrue(
                    _token_defined(self.css, f"--space-{n}"),
                    f"--space-{n} not found",
                )


class RadiusTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_radius_tokens_exist(self):
        for suffix in ("sm", "md", "lg", "xl", "pill"):
            with self.subTest(token=f"--radius-{suffix}"):
                self.assertTrue(
                    _token_defined(self.css, f"--radius-{suffix}"),
                    f"--radius-{suffix} not found",
                )


class TypographyTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_text_size_tokens_exist(self):
        for suffix in ("xs", "sm", "base", "lg", "xl"):
            with self.subTest(token=f"--text-{suffix}"):
                self.assertTrue(
                    _token_defined(self.css, f"--text-{suffix}"),
                    f"--text-{suffix} not found",
                )

    def test_font_weight_tokens_exist(self):
        for name in ("--font-bold", "--font-extrabold"):
            with self.subTest(token=name):
                self.assertTrue(_token_defined(self.css, name), f"{name} not found")

    def test_leading_tokens_exist(self):
        for suffix in ("tight", "snug", "normal", "relaxed"):
            with self.subTest(token=f"--leading-{suffix}"):
                self.assertTrue(
                    _token_defined(self.css, f"--leading-{suffix}"),
                    f"--leading-{suffix} not found",
                )


class TransitionTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_transition_tokens_exist(self):
        for suffix in ("fast", "base"):
            with self.subTest(token=f"--transition-{suffix}"):
                self.assertTrue(
                    _token_defined(self.css, f"--transition-{suffix}"),
                    f"--transition-{suffix} not found",
                )


class ButtonTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_button_tokens_exist(self):
        for name in (
            "--btn-padding-y",
            "--btn-padding-x",
            "--btn-font-size",
            "--btn-font-weight",
            "--btn-radius",
            "--btn-min-height",
        ):
            with self.subTest(token=name):
                self.assertTrue(_token_defined(self.css, name), f"{name} not found")


class TabTokenTests(unittest.TestCase):
    def setUp(self):
        self.css = _read_tokens()

    def test_tab_tokens_exist(self):
        for name in (
            "--tab-border-color",
            "--tab-active-color",
            "--tab-active-bg",
            "--tab-hover-bg",
            "--tab-label-weight",
        ):
            with self.subTest(token=name):
                self.assertTrue(_token_defined(self.css, name), f"{name} not found")


if __name__ == "__main__":
    unittest.main()
