# BGGメタ情報 自動取得 実装設計版（案）

更新日: 2026-01-31

このドキュメントは、18xx-summary-site における BGG XML API2 からの
メタ情報自動取得の「実装設計版（最小）」です。スコープは必須項目のみ。

## 対象メタデータ（必須）
- min/max players
- playing time
- year published
- min age
- designer

## 前提
- 取得はビルド時のみ（GitHub Actions）。
- APIアクセスには BGG Application の Authorization token が必要。
- 生成物はリポジトリに同梱して静的配信（クライアント直叩きしない）。
- クレジット表示 + Powered by BGG ロゴをサイトに表示。
- 取得失敗時は前回JSONを維持してサイトを壊さない。

## 1) frontmatter 方針
各ゲームの Markdown 冒頭に `bgg_id` を1件だけ持たせる。

例:
```yaml
---
bgg_id: 192
---
```

## 2) 生成物（JSON）仕様
出力ファイル: `docs/assets/bgg-meta.json`

基本方針:
- キーは bgg_id（文字列）
- 値は取得した最小情報のみ
- 表示上の整形は MkDocs 側で行う（可能なら）

### JSONスキーマ（参考）
```json
{
  "192": {
    "name": "18India",
    "players": { "min": 2, "max": 6 },
    "playing_time": { "min": 120, "max": 240 },
    "year_published": 2007,
    "min_age": 12,
    "designers": ["Vivek", "X"]
  }
}
```

注意:
- `playing_time` は `minplayers/maxplayers` と同様に range で持つ。
- `designers` は複数あり得るので配列にする。
- `name` は BGG 由来。表示側で原案名と違う場合があるため注意。

## 3) API取得（最小仕様）
- エンドポイント: `/xmlapi2/thing`
- パラメータ: `id=...&stats=1&type=boardgame`
- `id` は最大20件までカンマ区切り
- リクエスト間は 5秒待機
- 500/503 は指数バックオフで最大リトライ
- URLは `https://boardgamegeek.com/xmlapi2/thing` を使用

## 4) GitHub Actions（疑似コード）

用途: 既存ゲームの Markdown から `bgg_id` を収集して JSON を生成。

```yaml
name: bgg-meta
on:
  workflow_dispatch:
  push:
    paths:
      - "docs/games/**.md"
      - "scripts/**"
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: generate bgg meta
        env:
          BGG_TOKEN: ${{ secrets.BGG_TOKEN }}
        run: python scripts/bgg_fetch.py
      - name: build mkdocs
        run: mkdocs build
```

## 5) `scripts/bgg_fetch.py` 役割（仕様）
最小の責務:
1. `docs/games/*.md` の先頭 frontmatter から `bgg_id` を収集
2. IDを20件ずつに分割
3. API呼び出し（5秒スリープ + リトライ）
4. XMLをパースして JSON 生成
5. 失敗IDは前回 `docs/assets/bgg-meta.json` から引き継ぐ

### 擬似コード（超簡略）
```python
ids = collect_bgg_ids("docs/games")
chunks = chunk(ids, 20)
result = load_previous_json("docs/assets/bgg-meta.json")
for chunk in chunks:
    xml = fetch_xml(chunk, token, retry=True, sleep=5)
    data = parse_xml(xml)
    result.update(data)
write_json("docs/assets/bgg-meta.json", result)
```

## 6) MkDocs側の表示
- `bgg-meta.json` を読み込み、該当 `bgg_id` があるゲームに表示
- 一覧ページにも同じ情報を表示可能
- フッター（または共通領域）に「Powered by BGG」ロゴ＋リンクを配置

## 7) 受け入れ条件（再掲）
- `bgg_id` を追加するだけで、一覧・ページのメタ情報が表示される
- API障害時も前回JSONでサイト表示が継続
- クレジット/ロゴが常に表示される

## 8) メモ（運用）
- BGGの規約変更に備え、取得処理は 1ファイルに集約
- 結果JSONは「必要最小限」の抽出に留める

