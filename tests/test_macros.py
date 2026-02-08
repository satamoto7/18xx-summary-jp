"""Tests for main.py macro HTML output — verifies .btn classes are present."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_env():
    """Import define_env and wire up a minimal env stub."""
    import importlib
    import main as main_module

    importlib.reload(main_module)

    class _Env:
        def __init__(self):
            self.macros: dict = {}

        def macro(self, fn):
            self.macros[fn.__name__] = fn
            return fn

    env = _Env()
    main_module.define_env(env)
    return env.macros


class PrintButtonTests(unittest.TestCase):
    def setUp(self):
        self.macros = _load_env()

    def test_print_button_has_btn_classes(self):
        result = self.macros["print_button"]()
        self.assertIn("btn", result)
        self.assertIn("btn--outline", result)
        self.assertIn("btn--sm", result)

    def test_print_button_is_button_element(self):
        result = self.macros["print_button"]()
        self.assertTrue(result.startswith("<button"))


class DownloadLinkTests(unittest.TestCase):
    def setUp(self):
        self.macros = _load_env()

    def test_download_link_has_btn_classes(self):
        result = self.macros["download_link"]("18Test.txt")
        self.assertIn("btn", result)
        self.assertIn("btn--outline", result)
        self.assertIn("btn--sm", result)

    def test_download_link_has_download_attribute(self):
        result = self.macros["download_link"]("18Test.txt")
        self.assertIn("download", result)

    def test_download_link_empty_filename(self):
        result = self.macros["download_link"]("")
        self.assertEqual(result, "")


class GameActionsCTATests(unittest.TestCase):
    def setUp(self):
        meta = {
            "999": {
                "players": {"min": 3, "max": 5},
                "playing_time": {"min": 120, "max": 180},
                "year_published": 2020,
                "min_age": 14,
                "designers": ["Test Designer"],
                "cover": None,
            }
        }
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(meta, self.tmp)
        self.tmp.close()
        self._patcher = patch("main.BGG_META_PATH", Path(self.tmp.name))
        self._patcher.start()
        self.macros = _load_env()

    def tearDown(self):
        self._patcher.stop()
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_cta_has_btn_primary_class(self):
        result = self.macros["game_actions"]("999", "18Test/")
        self.assertIn("btn", result)
        self.assertIn("btn--primary", result)
        self.assertIn("game-card__cta", result)

    def test_cta_does_not_have_md_button_class(self):
        result = self.macros["game_actions"]("999", "18Test/")
        self.assertNotIn("md-button", result)


if __name__ == "__main__":
    unittest.main()
