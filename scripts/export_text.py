from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import markdown

GAMES_DIR = Path("docs/games")
ASSETS_DIR = Path("docs/assets")

ACTIONS_BLOCK = re.compile(r'<div class="actions">.*?</div>', re.DOTALL)


class PlainTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.in_row = False
        self.cell_index = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        if tag == "table":
            self._ensure_newline()
            return
        if tag == "tr":
            self._ensure_newline()
            self.in_row = True
            self.cell_index = 0
            return
        if tag in {"td", "th"}:
            if self.in_row and self.cell_index > 0:
                self.parts.append(" | ")
            self.cell_index += 1
            return
        if tag in {
            "p",
            "div",
            "section",
            "article",
            "header",
            "footer",
            "li",
            "ul",
            "ol",
            "blockquote",
            "pre",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }:
            self._ensure_newline()
            if tag == "li":
                self.parts.append("・")
        if tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr":
            self._ensure_newline()
            self.in_row = False
            return
        if tag == "table":
            self._ensure_newline()
            return
        if tag in {
            "p",
            "div",
            "section",
            "article",
            "header",
            "footer",
            "li",
            "ul",
            "ol",
            "blockquote",
            "pre",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }:
            self._ensure_newline()

    def handle_data(self, data: str) -> None:
        if self.in_row:
            data = data.replace("\n", " ")
        if data.strip():
            self.parts.append(data)

    def _ensure_newline(self) -> None:
        if self.parts and not self.parts[-1].endswith("\n"):
            self.parts.append("\n")

    def get_text(self) -> str:
        text = "".join(self.parts)
        lines = [line.rstrip() for line in text.splitlines()]
        deduped: list[str] = []
        previous_blank = False
        for line in lines:
            if not line.strip():
                if not previous_blank:
                    deduped.append("")
                previous_blank = True
                continue
            deduped.append(line)
            previous_blank = False
        return "\n".join(deduped).strip() + "\n"


def markdown_to_text(content: str) -> str:
    cleaned = ACTIONS_BLOCK.sub("", content)
    html = markdown.markdown(
        cleaned,
        extensions=[
            "tables",
            "fenced_code",
            "pymdownx.tabbed",
            "pymdownx.superfences",
        ],
        output_format="html5",
    )
    parser = PlainTextExtractor()
    parser.feed(html)
    return parser.get_text()


def export_texts() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    games = sorted(path for path in GAMES_DIR.glob("*.md") if path.stem != "index")
    for md_path in games:
        text = markdown_to_text(md_path.read_text(encoding="utf-8"))
        asset_path = ASSETS_DIR / f"{md_path.stem}.txt"
        asset_path.write_text(text, encoding="utf-8")
        print(f"Wrote {asset_path}")


def main() -> None:
    export_texts()


if __name__ == "__main__":
    main()
