"""Tests for game filter data attributes emitted by game_card()."""
from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path


def _load_macros_with_meta(meta_payload: dict) -> tuple[dict, Path]:
    import main as main_module

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(meta_payload, tmp)
    tmp.close()

    importlib.reload(main_module)
    main_module.BGG_META_PATH = Path(tmp.name)

    class _Env:
        def __init__(self):
            self.macros: dict = {}

        def macro(self, fn):
            self.macros[fn.__name__] = fn
            return fn

    env = _Env()
    main_module.define_env(env)
    return env.macros, Path(tmp.name)


class GameCardDataAttributesTests(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, "_tmp_path"):
            Path(self._tmp_path).unlink(missing_ok=True)

    def test_game_card_has_data_attributes_when_meta_exists(self):
        meta = {
            "999": {
                "players": {"min": 2, "max": 5},
                "year_published": 2020,
            }
        }
        macros, tmp_path = _load_macros_with_meta(meta)
        self._tmp_path = tmp_path

        html = macros["game_card"](
            "999", "Test Title", "Test Description", "https://example.com", "Test/"
        )

        self.assertIn('data-year="2020"', html)
        self.assertIn('data-players-min="2"', html)
        self.assertIn('data-players-max="5"', html)

    def test_game_card_has_empty_data_attributes_when_meta_missing(self):
        macros, tmp_path = _load_macros_with_meta({})
        self._tmp_path = tmp_path

        html = macros["game_card"](
            "999", "Test Title", "Test Description", "https://example.com", "Test/"
        )

        self.assertIn('data-year=""', html)
        self.assertIn('data-players-min=""', html)
        self.assertIn('data-players-max=""', html)

    def test_game_card_uses_empty_year_when_value_is_not_int(self):
        meta = {
            "999": {
                "players": {"min": 3, "max": 4},
                "year_published": "2020",
            }
        }
        macros, tmp_path = _load_macros_with_meta(meta)
        self._tmp_path = tmp_path

        html = macros["game_card"](
            "999", "Test Title", "Test Description", "https://example.com", "Test/"
        )

        self.assertIn('data-year=""', html)
        self.assertIn('data-players-min="3"', html)
        self.assertIn('data-players-max="4"', html)


if __name__ == "__main__":
    unittest.main()
