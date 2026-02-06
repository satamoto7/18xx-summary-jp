from __future__ import annotations

import html
import json
from pathlib import Path

BGG_META_PATH = Path("docs/assets/bgg-meta.json")


def _load_bgg_meta() -> dict[str, dict]:
    try:
        with BGG_META_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _format_range(min_value: object, max_value: object, suffix: str = "") -> str | None:
    if not isinstance(min_value, int) or not isinstance(max_value, int):
        return None
    if min_value == max_value:
        return f"{min_value}{suffix}"
    return f"{min_value}-{max_value}{suffix}"


def _attr_int(value: object) -> str:
    if isinstance(value, int):
        return str(value)
    return ""


def define_env(env) -> None:
    bgg_meta = _load_bgg_meta()

    def _extract_meta_fields(bgg_id: str) -> dict | None:
        meta = bgg_meta.get(str(bgg_id))
        if not isinstance(meta, dict):
            return None

        players = meta.get("players")
        playing_time = meta.get("playing_time")
        year = meta.get("year_published")
        designers = meta.get("designers")
        min_age = meta.get("min_age")

        players_min: object = None
        players_max: object = None
        players_text: str | None = None
        if isinstance(players, dict):
            players_min = players.get("min")
            players_max = players.get("max")
            players_text = _format_range(players_min, players_max, "人")

        time_min: object = None
        time_max: object = None
        time_text: str | None = None
        if isinstance(playing_time, dict):
            time_min = playing_time.get("min")
            time_max = playing_time.get("max")
            time_text = _format_range(time_min, time_max, "分")

        safe_designers: list[str] = []
        if isinstance(designers, list):
            safe_designers = [
                html.escape(name)
                for name in designers
                if isinstance(name, str) and name.strip()
            ]

        return {
            "bgg_id": str(bgg_id),
            "players_min": players_min,
            "players_max": players_max,
            "players_text": players_text,
            "time_min": time_min,
            "time_max": time_max,
            "time_text": time_text,
            "year": year,
            "min_age": min_age,
            "safe_designers": safe_designers,
        }

    @env.macro
    def print_button() -> str:
        return '<button onclick="window.print()">印刷</button>'

    @env.macro
    def download_link(filename: str) -> str:
        if not filename:
            return ""
        safe_name = html.escape(filename, quote=True)
        href = f"../../assets/{safe_name}"
        return f'<a class="action-link" href="{href}" download>テキストDL</a>'

    @env.macro
    def game_title(title: str, bgg_id: str) -> str:
        safe_title = html.escape(title) if title else ""
        year_badge = ""
        fields = _extract_meta_fields(bgg_id)
        if isinstance(fields, dict) and isinstance(fields.get("year"), int):
            year_badge = f'<span class="game-card__year-badge">{fields["year"]}</span>'
        return (
            f'<span class="game-card__title-text">{safe_title}</span>'
            f"{year_badge}"
        )

    @env.macro
    def game_chips(bgg_id: str) -> str:
        if not bgg_id:
            return ""

        fields = _extract_meta_fields(bgg_id)
        if not isinstance(fields, dict):
            return ""

        chips: list[str] = []
        if fields["players_text"]:
            chips.append(
                f'<span class="game-card__chip">'
                f'<span class="game-card__chip-label">人数</span>{fields["players_text"]}'
                "</span>"
            )
        if fields["time_text"]:
            chips.append(
                f'<span class="game-card__chip">'
                f'<span class="game-card__chip-label">時間</span>{fields["time_text"]}'
                "</span>"
            )

        if not chips:
            return ""

        data_attrs = (
            f'data-bgg-id="{html.escape(fields["bgg_id"], quote=True)}" '
            f'data-players-min="{_attr_int(fields["players_min"])}" '
            f'data-players-max="{_attr_int(fields["players_max"])}" '
            f'data-time-min="{_attr_int(fields["time_min"])}" '
            f'data-time-max="{_attr_int(fields["time_max"])}" '
            f'data-year="{_attr_int(fields["year"])}" '
            f'data-min-age="{_attr_int(fields["min_age"])}"'
        )
        return f'<li class="game-card__meta-primary" {data_attrs}>{"".join(chips)}</li>'

    @env.macro
    def game_details(bgg_id: str) -> str:
        if not bgg_id:
            return ""

        fields = _extract_meta_fields(bgg_id)
        if not isinstance(fields, dict):
            return ""

        detail_items: list[str] = []
        if isinstance(fields["year"], int):
            detail_items.append(
                '<li class="game-card__meta-inline">'
                '<span class="game-card__meta-label">発売年</span>'
                f'<span>{fields["year"]}</span>'
                "</li>"
            )

        if isinstance(fields["min_age"], int) and fields["min_age"] > 0:
            detail_items.append(
                '<li class="game-card__meta-inline">'
                '<span class="game-card__meta-label">対象年齢</span>'
                f'<span>{fields["min_age"]}+</span>'
                "</li>"
            )

        if fields["safe_designers"]:
            detail_items.append(
                '<li class="game-card__meta-inline">'
                '<span class="game-card__meta-label">デザイナー</span>'
                f'<span>{", ".join(fields["safe_designers"])}</span>'
                "</li>"
            )

        if not detail_items:
            return ""

        return (
            '<li class="game-card__meta-details">'
            '<ul class="game-card__meta-extra">'
            f"{''.join(detail_items)}"
            "</ul>"
            "</li>"
        )
