# 18xx サマリーサイト（MkDocs）

- `docs/` 配下に Markdown を置くとサイトになります
- `mkdocs serve` でローカルプレビュー
- GitHub Actions で GitHub Pages に自動デプロイ（任意）

## 追加の流れ（例）

1. `docs/games/<game>.md` を追加
2. `mkdocs.yml` の nav に追加
3. push すると公開が更新される（GitHub Pagesの場合）

### テキスト版の生成

各ゲームページの「テキストDL」リンクで配布する `docs/assets/<game>.txt` は、`docs/games/` 配下の Markdown から生成します。

- `python scripts/export_text.py` で全ゲーム分のテキストを再生成
- ゲームを追加・更新したときは必ず実行し、既存のテキストもまとめて更新してください

### タブ内インデントの自動調整

Obsidian などでタブ内の記述をインデントなしで編集したい場合は、アップロード前にインデントを自動付与できます。

- 単一ファイルに適用: `python scripts/indent_tabs.py docs/games/18Chesapeake.md`
- すべてのゲームファイルに適用: `python scripts/indent_tabs.py`

## 編集を受け付ける運用

- GitHub の Pull Request で受け付ける
- ルールの誤記修正や、見出し分割の改善がしやすい構成です
