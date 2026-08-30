"""Tests for main.py macro HTML output — verifies .btn classes are present."""
from __future__ import annotations

import html
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
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


class SummaryActionsTests(unittest.TestCase):
    def setUp(self):
        self.macros = _load_env()

    def test_summary_actions_omits_pdf_when_filename_is_empty(self):
        result = self.macros["summary_actions"]("1862")
        self.assertNotIn("卓上用PDF", result)
        self.assertIn("summary-actions__buttons--single", result)
        self.assertIn("Xでプレイ報告", result)

    def test_summary_actions_adds_approved_pdf_download(self):
        result = self.macros["summary_actions"]("1862", "1862-player-aid.pdf")
        self.assertIn("btn--primary", result)
        self.assertIn("../../downloads/1862-player-aid.pdf", result)
        self.assertIn("download", result)

    def test_summary_actions_rejects_nested_or_non_pdf_path(self):
        nested = self.macros["summary_actions"]("1862", "../1862-player-aid.pdf")
        text_file = self.macros["summary_actions"]("1862", "1862.txt")
        self.assertNotIn("卓上用PDF", nested)
        self.assertNotIn("卓上用PDF", text_file)

    def test_summary_actions_prefills_x_report(self):
        result = html.unescape(self.macros["summary_actions"]("1862"))
        href = result.split('href="', 1)[1].split('"', 1)[0]
        parsed = urlparse(href)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.netloc, "x.com")
        self.assertEqual(parsed.path, "/intent/tweet")
        self.assertIn("1862を遊びました", query["text"][0])
        self.assertIn("@hirombs", query["text"][0])
        self.assertEqual(query["hashtags"], ["18xxサマリー"])

    def test_summary_actions_includes_author_back_link_and_support(self):
        result = self.macros["summary_actions"]("1862")
        self.assertIn("作成：さたもと", result)
        self.assertIn("https://x.com/hirombs", result)
        self.assertIn('href="../"', result)
        self.assertIn("https://note.com/satamoto", result)


class GameQuickIndexTests(unittest.TestCase):
    def test_quick_index_uses_pages_order_and_strips_summary_suffix(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            games_dir = Path(tmp_dir)
            pages_path = games_dir / ".pages"
            pages_path.write_text(
                "nav:\n  - index.md\n  - 18Test.md\n  - 18Long Name.md\n",
                encoding="utf-8",
            )
            (games_dir / "18Test.md").write_text("# 18Test サマリー\n", encoding="utf-8")
            (games_dir / "18Long Name.md").write_text(
                "# 18Long Name サマリー\n", encoding="utf-8"
            )

            macros = _load_env()
            with patch("main.GAME_PAGES_PATH", pages_path):
                result = macros["game_quick_index"]()

        self.assertIn("GAME INDEX", result)
        self.assertIn("02 TITLES", result)
        self.assertIn('href="games/18Test/"', result)
        self.assertIn('href="games/18Long%20Name/"', result)
        self.assertNotIn("18Test サマリー", result)


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
