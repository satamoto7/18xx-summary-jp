# 18xx サマリーサイト（MkDocs）

- `docs/` 配下に Markdown を置くとサイトになります
- `mkdocs serve` でローカルプレビュー
- GitHub Actions で GitHub Pages に自動デプロイ（任意）

## 追加の流れ（例）

1. `docs/games/<game>.md` を追加
2. `mkdocs.yml` の nav に追加
3. push すると公開が更新される（GitHub Pagesの場合）

## 編集を受け付ける運用

- GitHub の Pull Request で受け付ける
- ルールの誤記修正や、見出し分割の改善がしやすい構成です
