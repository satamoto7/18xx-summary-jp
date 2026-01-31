from __future__ import annotations

import html


def define_env(env) -> None:
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
