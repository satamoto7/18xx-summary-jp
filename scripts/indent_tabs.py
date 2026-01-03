from __future__ import annotations

import argparse
import re
from pathlib import Path

GAMES_DIR = Path("docs/games")
TAB_HEADER = re.compile(r"^\s*===\s+\"")
CODE_FENCE = re.compile(r"^\s*(```|~~~)")
BASE_INDENT = " " * 4


def indent_tab_block(lines: list[str]) -> list[str]:
    non_blank_indents = [len(re.match(r"^ *", line).group(0)) for line in lines if line.strip()]
    min_indent = min(non_blank_indents) if non_blank_indents else 0
    indented: list[str] = []
    for line in lines:
        if line.strip():
            trimmed = line[min_indent:]
            indented.append(f"{BASE_INDENT}{trimmed}")
        else:
            indented.append(BASE_INDENT)
    return indented


def indent_tabs_in_content(content: str) -> str:
    lines = content.splitlines()
    output: list[str] = []
    in_code_block = False
    i = 0
    total = len(lines)
    while i < total:
        line = lines[i]
        output.append(line)

        if CODE_FENCE.match(line):
            in_code_block = not in_code_block
            i += 1
            continue

        i += 1
        if not in_code_block and TAB_HEADER.match(line):
            block_start = i
            while i < total and not TAB_HEADER.match(lines[i]):
                i += 1
            block = lines[block_start:i]
            output.extend(indent_tab_block(block))
    return "\n".join(output) + ("\n" if content.endswith("\n") else "")


def indent_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = indent_tabs_in_content(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"Indented tab content in {path}")
        return True
    print(f"No changes needed for {path}")
    return False


def gather_paths(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    return sorted(p for p in GAMES_DIR.glob("*.md") if p.name != "index.md")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indent Material for MkDocs tab content blocks by 4 spaces.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Specific Markdown files to reindent. Defaults to all games under docs/games.",
    )
    args = parser.parse_args()

    any_changed = False
    for path in gather_paths(args.paths):
        any_changed |= indent_file(path)

    if not any_changed:
        print("All files already have correct indentation.")


if __name__ == "__main__":
    main()
