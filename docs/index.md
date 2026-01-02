# 18xx サマリーサイト（ひな形）

このリポジトリは、18xx の「サマリーシート（印刷物）」を **Web で読めて／編集しやすく／印刷もできる** 形にするための最小構成です。

- スマホで読みやすい（見出し＋タブ）
- SR / OR / セットアップ等を分離
- いつでもブラウザの印刷機能で紙に出せる（各ページの「印刷」ボタン）

## 使い方（ローカルで確認）

```bash
python -m venv .venv
source .venv/bin/activate  # Windows は .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve
```

ブラウザで `http://127.0.0.1:8000/` を開くとプレビューできます。

## 公開（例：GitHub Pages）

- GitHub Pages か、Netlify / Cloudflare Pages などの静的ホスティングで公開できます。
- 「他の人が編集できる」運用にしたい場合は、GitHub 上で Pull Request を受け付けるのが手堅いです。
