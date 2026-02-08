from __future__ import annotations

import html
import json
import markdown
from pathlib import Path
from material.extensions.emoji import to_svg, twemoji

BGG_META_PATH = Path("docs/assets/bgg-meta.json")
_icon_md = markdown.Markdown(
    extensions=["pymdownx.emoji"],
    extension_configs={
        "pymdownx.emoji": {
            "emoji_index": twemoji,
            "emoji_generator": to_svg,
        }
    },
)


def _material_icon(shortname: str, css_class: str | None = None) -> str:
    try:
        rendered = _icon_md.convert(f":{shortname}:")
        _icon_md.reset()
    except Exception:
        return ""

    rendered = rendered.strip()
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        rendered = rendered[3:-4]
    if not css_class:
        return rendered
    return f'<span class="{css_class}" aria-hidden="true">{rendered}</span>'


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


def _build_chip_html(fields: dict) -> str:
    chips: list[str] = []
    if fields["players_text"]:
        chips.append(
            '<span class="game-card__chip">'
            f'{_material_icon("material-account-group", "game-card__chip-icon")}'
            '<span class="game-card__chip-label">人数</span>'
            f'{fields["players_text"]}'
            "</span>"
        )
    if fields["time_text"]:
        chips.append(
            '<span class="game-card__chip">'
            f'{_material_icon("material-timer-outline", "game-card__chip-icon")}'
            '<span class="game-card__chip-label">時間</span>'
            f'{fields["time_text"]}'
            "</span>"
        )
    return "".join(chips)


def _build_detail_rows_html(fields: dict) -> str:
    rows: list[str] = []

    if isinstance(fields["year"], int):
        rows.append(
            '<li class="game-card__detail-row">'
            f'{_material_icon("material-calendar", "game-card__detail-icon")}'
            '<span class="game-card__detail-label">発売年</span>'
            f'<span>{fields["year"]}</span>'
            "</li>"
        )

    if isinstance(fields["min_age"], int) and fields["min_age"] > 0:
        rows.append(
            '<li class="game-card__detail-row">'
            f'{_material_icon("material-badge-account", "game-card__detail-icon")}'
            '<span class="game-card__detail-label">対象年齢</span>'
            f'<span>{fields["min_age"]}+</span>'
            "</li>"
        )

    if fields["safe_designers"]:
        rows.append(
            '<li class="game-card__detail-row">'
            f'{_material_icon("material-draw", "game-card__detail-icon")}'
            '<span class="game-card__detail-label">デザイナー</span>'
            f'<span>{", ".join(fields["safe_designers"])}</span>'
            "</li>"
        )

    return "".join(rows)


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
        cover = meta.get("cover")

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

        cover_path: str | None = None
        cover_width: int | None = None
        cover_height: int | None = None
        if isinstance(cover, dict):
            path = cover.get("path")
            width = cover.get("width")
            height = cover.get("height")
            if (
                isinstance(path, str)
                and path.startswith("assets/game-covers/")
                and isinstance(width, int)
                and isinstance(height, int)
                and width > 0
                and height > 0
                and (Path("docs") / path).exists()
            ):
                cover_path = path
                cover_width = width
                cover_height = height

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
            "cover_path": cover_path,
            "cover_width": cover_width,
            "cover_height": cover_height,
        }

    @env.macro
    def print_button() -> str:
        return '<button class="btn btn--outline btn--sm" onclick="window.print()">印刷</button>'

    @env.macro
    def icon(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            return ""
        return _material_icon(name.strip())

    @env.macro
    def download_link(filename: str) -> str:
        if not filename:
            return ""
        safe_name = html.escape(filename, quote=True)
        href = f"../../assets/{safe_name}"
        return f'<a class="btn btn--outline btn--sm" href="{href}" download>テキストDL</a>'

    @env.macro
    def game_title(title: str, bgg_id: str) -> str:
        safe_title = html.escape(title) if title else ""
        year_badge = ""
        fields = _extract_meta_fields(bgg_id)
        if isinstance(fields, dict) and isinstance(fields.get("year"), int):
            year_badge = (
                '<span class="game-card__year-badge">'
                f'{_material_icon("material-calendar", "game-card__year-icon")}'
                f'{fields["year"]}'
                "</span>"
            )
        return (
            f'<span class="game-card__title-text">{safe_title}</span>'
            f"{year_badge}"
        )

    @env.macro
    def game_cover(bgg_id: str, title: str, href: str = "") -> str:
        safe_bgg_id = str(bgg_id).strip()
        safe_title = html.escape(title) if title else "Game"
        fields = _extract_meta_fields(safe_bgg_id)

        if not safe_bgg_id:
            return (
                '<figure class="game-card__media game-card__media--placeholder">'
                '<span class="game-card__media-placeholder-text">NO IMAGE</span>'
                "</figure>"
            )

        if not isinstance(fields, dict):
            return (
                '<figure class="game-card__media game-card__media--placeholder">'
                '<span class="game-card__media-placeholder-text">NO IMAGE</span>'
                "</figure>"
            )

        cover_path = fields.get("cover_path")
        cover_width = fields.get("cover_width")
        cover_height = fields.get("cover_height")
        if (
            not isinstance(cover_path, str)
            or not isinstance(cover_width, int)
            or not isinstance(cover_height, int)
        ):
            return (
                '<figure class="game-card__media game-card__media--placeholder">'
                '<span class="game-card__media-placeholder-text">NO IMAGE</span>'
                "</figure>"
            )

        image_src = f"../{html.escape(cover_path, quote=True)}"
        image_html = (
            f'<img src="{image_src}" '
            f'alt="{safe_title} パッケージ画像" '
            f'width="{cover_width}" '
            f'height="{cover_height}" '
            'loading="lazy" '
            'decoding="async">'
        )

        if href:
            safe_href = html.escape(href, quote=True)
            aria_label = html.escape(f"{title} サマリーを見る", quote=True) if title else "サマリーを見る"
            image_html = (
                f'<a class="game-card__media-link" href="{safe_href}" '
                f'aria-label="{aria_label}">{image_html}</a>'
            )

        return f'<figure class="game-card__media">{image_html}</figure>'

    @env.macro
    def game_actions(bgg_id: str, summary_href: str) -> str:
        fields = _extract_meta_fields(bgg_id)
        safe_href = html.escape(summary_href, quote=True) if summary_href else ""

        chips_block = ""
        details_block = ""
        if isinstance(fields, dict):
            chips_html = _build_chip_html(fields)
            if chips_html:
                chips_attrs = (
                    f'data-bgg-id="{html.escape(fields["bgg_id"], quote=True)}" '
                    f'data-players-min="{_attr_int(fields["players_min"])}" '
                    f'data-players-max="{_attr_int(fields["players_max"])}" '
                    f'data-time-min="{_attr_int(fields["time_min"])}" '
                    f'data-time-max="{_attr_int(fields["time_max"])}" '
                    f'data-year="{_attr_int(fields["year"])}" '
                    f'data-min-age="{_attr_int(fields["min_age"])}"'
                )
                chips_block = f'<div class="game-card__chips" {chips_attrs}>{chips_html}</div>'

            detail_rows = _build_detail_rows_html(fields)
            if detail_rows:
                details_block = (
                    '<details class="game-card__details">'
                    '<summary class="game-card__details-summary">'
                    '<span class="game-card__details-summary-label">詳細情報</span>'
                    "</summary>"
                    f'<ul class="game-card__details-body">{detail_rows}</ul>'
                    "</details>"
                )

        cta_block = ""
        if safe_href:
            cta_block = (
                f'<a class="btn btn--primary game-card__cta" href="{safe_href}">'
                f'{_material_icon("material-file-document-outline", "game-card__cta-icon")}'
                '<span class="game-card__cta-label">サマリーを見る</span>'
                "</a>"
            )

        top_parts = "".join(part for part in (chips_block, cta_block) if part)
        top_block = ""
        if top_parts:
            top_block = f'<div class="game-card__actions-top">{top_parts}</div>'

        if not top_block and not details_block:
            return ""

        return f'<div class="game-card__actions">{top_block}{details_block}</div>'

    @env.macro
    def game_card(
        bgg_id: str,
        title: str,
        description: str,
        bgg_href: str,
        summary_href: str,
    ) -> str:
        safe_description = html.escape(description) if description else ""
        safe_bgg_href = html.escape(bgg_href, quote=True) if bgg_href else ""
        fields = _extract_meta_fields(bgg_id)

        data_attrs = ' data-year="" data-players-min="" data-players-max=""'
        if isinstance(fields, dict):
            data_attrs = (
                f' data-year="{_attr_int(fields["year"])}"'
                f' data-players-min="{_attr_int(fields["players_min"])}"'
                f' data-players-max="{_attr_int(fields["players_max"])}"'
            )

        bgg_link = ""
        if safe_bgg_href:
            bgg_link = f' (<a href="{safe_bgg_href}">BGG</a>)'

        return (
            f'<article class="game-card"{data_attrs}>'
            f'{game_cover(bgg_id, title, summary_href)}'
            '<div class="game-card__body">'
            '<h2 class="game-card__heading">'
            f'<span class="game-card__title-icon" aria-hidden="true">{icon("material-train")}</span>'
            f"{game_title(title, bgg_id)}"
            "</h2>"
            f'<p class="game-card__description">{safe_description}{bgg_link}</p>'
            f"{game_actions(bgg_id, summary_href)}"
            "</div>"
            "</article>"
        )
