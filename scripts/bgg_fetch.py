from __future__ import annotations

import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover - handled at runtime
    Image = None  # type: ignore[assignment]
    UnidentifiedImageError = Exception  # type: ignore[assignment]

GAMES_DIR = Path("docs/games")
ASSETS_DIR = Path("docs/assets")
OUTPUT_JSON = ASSETS_DIR / "bgg-meta.json"
COVERS_DIR = ASSETS_DIR / "game-covers"

API_URL = "https://boardgamegeek.com/xmlapi2/thing"
REQUEST_TYPES = "boardgame"
CHUNK_SIZE = 20
REQUEST_SLEEP_SECONDS = 5
RETRY_MAX = 4
RETRY_BACKOFF_SECONDS = 5
IMAGE_TIMEOUT_SECONDS = 30
COVER_MAX_WIDTH = 480
COVER_MAX_HEIGHT = 640
COVER_WEBP_QUALITY = 85

FRONTMATTER_START = re.compile(r"^---\s*$")
FRONTMATTER_KV = re.compile(r"^bgg_id\s*:\s*['\"]?(\d+)['\"]?\s*$")
_PILLOW_MISSING_WARNED = False


@dataclass
class GameMeta:
    name: str | None
    players_min: int | None
    players_max: int | None
    time_min: int | None
    time_max: int | None
    year_published: int | None
    min_age: int | None
    designers: list[str]
    image_url: str | None
    thumbnail_url: str | None

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "players": {"min": self.players_min, "max": self.players_max},
            "playing_time": {"min": self.time_min, "max": self.time_max},
            "year_published": self.year_published,
            "min_age": self.min_age,
            "designers": self.designers,
        }


def read_frontmatter_bgg_id(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"Failed to read {path}: {exc}")
        return None

    if not lines or not FRONTMATTER_START.match(lines[0]):
        return None

    for line in lines[1:]:
        if FRONTMATTER_START.match(line):
            return None
        match = FRONTMATTER_KV.match(line.strip())
        if match:
            return match.group(1)
    return None


def collect_bgg_ids(games_dir: Path) -> list[str]:
    ids: list[str] = []
    for md_path in sorted(games_dir.glob("*.md")):
        if md_path.stem == "index":
            continue
        bgg_id = read_frontmatter_bgg_id(md_path)
        if bgg_id:
            ids.append(bgg_id)
    return sorted(set(ids))


def chunked(items: Iterable[str], size: int) -> list[list[str]]:
    chunk: list[str] = []
    chunks: list[list[str]] = []
    for item in items:
        chunk.append(item)
        if len(chunk) >= size:
            chunks.append(chunk)
            chunk = []
    if chunk:
        chunks.append(chunk)
    return chunks


def build_request(ids: list[str]) -> urllib.request.Request:
    params = {
        "id": ",".join(ids),
        "stats": "1",
        "type": REQUEST_TYPES,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    headers = {"Accept": "application/xml"}
    token = os.getenv("BGG_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def fetch_xml(ids: list[str]) -> str:
    if not os.getenv("BGG_TOKEN"):
        raise RuntimeError("BGG_TOKEN is not set.")

    request = build_request(ids)
    last_error: Exception | None = None
    for attempt in range(1, RETRY_MAX + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = getattr(response, "status", 200)
                data = response.read().decode("utf-8")
            if status in {500, 503}:
                raise RuntimeError(f"HTTP {status}")
            if "<message>" in data:
                raise RuntimeError("BGG returned a message response (likely queued).")
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as exc:
            last_error = exc
            if attempt < RETRY_MAX:
                sleep_for = RETRY_BACKOFF_SECONDS * attempt
                time.sleep(sleep_for)
            else:
                break
    raise RuntimeError(f"Failed to fetch ids {ids}: {last_error}")


def _int_attr(node: ET.Element | None, key: str = "value") -> int | None:
    if node is None:
        return None
    value = node.get(key)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _normalize_url(text: str | None) -> str | None:
    if not isinstance(text, str):
        return None
    value = text.strip()
    if not value:
        return None
    return value


def _load_image_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "image/*",
            "User-Agent": "18xx-summary-site/1.0 (+https://boardgamegeek.com)",
        },
    )
    with urllib.request.urlopen(request, timeout=IMAGE_TIMEOUT_SECONDS) as response:
        return response.read()


def _extract_previous_cover(previous_entry: object, bgg_id: str) -> dict | None:
    if not isinstance(previous_entry, dict):
        return None
    cover = previous_entry.get("cover")
    if not isinstance(cover, dict):
        return None

    path = cover.get("path")
    width = cover.get("width")
    height = cover.get("height")
    source = cover.get("source")
    if (
        isinstance(path, str)
        and isinstance(width, int)
        and isinstance(height, int)
        and isinstance(source, str)
        and width > 0
        and height > 0
    ):
        expected = f"assets/game-covers/{bgg_id}.webp"
        if path == expected and (COVERS_DIR / f"{bgg_id}.webp").exists():
            return {
                "path": path,
                "width": width,
                "height": height,
                "source": source,
            }
    return None


def _generate_cover(bgg_id: str, image_url: str | None, thumbnail_url: str | None) -> dict | None:
    global _PILLOW_MISSING_WARNED
    if Image is None:
        if not _PILLOW_MISSING_WARNED:
            print("Cover generation skipped: Pillow is not installed.")
            _PILLOW_MISSING_WARNED = True
        return None

    candidates = [
        ("image", image_url),
        ("thumbnail", thumbnail_url),
    ]

    resample = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    for source, url in candidates:
        if not url:
            continue
        try:
            raw = _load_image_bytes(url)
            with Image.open(io.BytesIO(raw)) as loaded:
                rgb = loaded.convert("RGB")
                rgb.thumbnail((COVER_MAX_WIDTH, COVER_MAX_HEIGHT), resample=resample)

                if rgb.width <= 0 or rgb.height <= 0:
                    continue

                COVERS_DIR.mkdir(parents=True, exist_ok=True)
                output_path = COVERS_DIR / f"{bgg_id}.webp"
                rgb.save(output_path, format="WEBP", quality=COVER_WEBP_QUALITY, method=6)
        except (
            OSError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            UnidentifiedImageError,
        ) as exc:
            print(f"Cover fetch failed for {bgg_id} ({source}): {exc}")
            continue

        return {
            "path": f"assets/game-covers/{bgg_id}.webp",
            "width": rgb.width,
            "height": rgb.height,
            "source": source,
        }

    return None


def parse_xml(xml_text: str) -> dict[str, GameMeta]:
    root = ET.fromstring(xml_text)
    result: dict[str, GameMeta] = {}
    for item in root.findall("item"):
        item_id = item.get("id")
        if not item_id:
            continue

        name = None
        for name_node in item.findall("name"):
            if name_node.get("type") == "primary":
                name = name_node.get("value")
                break
        if name is None:
            name_node = item.find("name")
            if name_node is not None:
                name = name_node.get("value")

        min_players = _int_attr(item.find("minplayers"))
        max_players = _int_attr(item.find("maxplayers"))

        min_play_time = _int_attr(item.find("minplaytime"))
        max_play_time = _int_attr(item.find("maxplaytime"))
        if min_play_time is None or max_play_time is None:
            playing_time = _int_attr(item.find("playingtime"))
            if min_play_time is None:
                min_play_time = playing_time
            if max_play_time is None:
                max_play_time = playing_time

        year_published = _int_attr(item.find("yearpublished"))
        min_age = _int_attr(item.find("minage"))

        designers = [
            link.get("value")
            for link in item.findall("link")
            if link.get("type") == "boardgamedesigner" and link.get("value")
        ]

        image_url = _normalize_url(item.findtext("image"))
        thumbnail_url = _normalize_url(item.findtext("thumbnail"))

        result[item_id] = GameMeta(
            name=name,
            players_min=min_players,
            players_max=max_players,
            time_min=min_play_time,
            time_max=max_play_time,
            year_published=year_published,
            min_age=min_age,
            designers=designers,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
        )
    return result


def load_previous_json(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Failed to load {path}: {exc}")
        return {}


def write_json(path: Path, payload: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    ids = collect_bgg_ids(GAMES_DIR)
    if not ids:
        print("No bgg_id found. Skipping.")
        return

    previous = load_previous_json(OUTPUT_JSON)
    result: dict[str, dict] = {}

    chunks = chunked(ids, CHUNK_SIZE)
    for index, chunk in enumerate(chunks, start=1):
        print(f"Fetching {index}/{len(chunks)}: {', '.join(chunk)}")
        try:
            xml_text = fetch_xml(chunk)
            parsed = parse_xml(xml_text)
            for bgg_id in chunk:
                meta = parsed.get(bgg_id)
                if meta:
                    current = meta.to_json()
                    cover = _generate_cover(bgg_id, meta.image_url, meta.thumbnail_url)
                    if cover:
                        current["cover"] = cover
                    else:
                        preserved_cover = _extract_previous_cover(previous.get(bgg_id), bgg_id)
                        if preserved_cover:
                            current["cover"] = preserved_cover
                    result[bgg_id] = current
                elif bgg_id in previous:
                    result[bgg_id] = previous[bgg_id]
        except RuntimeError as exc:
            print(f"Fetch failed for chunk {chunk}: {exc}")
            for bgg_id in chunk:
                if bgg_id in previous:
                    result[bgg_id] = previous[bgg_id]
        if index < len(chunks):
            time.sleep(REQUEST_SLEEP_SECONDS)

    write_json(OUTPUT_JSON, result)
    print(f"Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
