# 18xx サマリーサイト（MkDocs）

- `docs/` 配下に Markdown を置くとサイトになります
- `scripts/preview_site.ps1` でローカルプレビュー
- GitHub Actions で GitHub Pages に自動デプロイ（任意）

## 初回セットアップ

PowerShell で次を実行します。既存の `.venv` がある場合は作り直す必要はありません。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## ローカル確認

- プレビュー: `.\scripts\preview_site.ps1`（ポート変更: `-Port 8123`）
- 公開前チェック: `.\scripts\check_site.ps1`

チェックでは、テキスト版の再生成、ソースマニフェスト、構造、内部リンク、資産、Pythonテスト、`mkdocs build --strict` をまとめて実行します。

## サマリーを追加・更新する二つの流れ

### 1. 完成済みMarkdownを掲載する

1. `docs/games/<game>.md` を追加
2. `docs/games/index.md` にリンクを追加
3. `docs/games/.pages` の `nav` にファイルを追加
4. `.\scripts\check_site.ps1` で確認
5. push すると公開が更新される（GitHub Pagesの場合）

### 2. 公式ルールリソースからWebサマリーを作る

完成PDFを再要約するのではなく、別プロジェクトで整備したソース台帳・ルール台帳・主体表・未解決事項を正本としてWeb向けMarkdownを作成します。

1. `.codex/skills/publish-18xx-summary-to-site/SKILL.md` の手順を使う
2. `source-manifests/<game>.json` に対象版と上流リソースを登録する
3. 上流リソースの実在を含めて検証する
4. 既存ページとの出典付き差分を確認し、初回差し替えを承認する
5. Markdownとマニフェストを同時に更新する
6. テキスト版生成と全サイト検証を実行する

```powershell
.\scripts\check_site.ps1 -SummarySourceRoot "D:\My Document\1_Project\04_game\18xxサマリー作成"
```

通常のCIや上流フォルダがない環境では、引数なしでマニフェストの構造だけを検証します。

### テキスト版の生成

各ゲームページの「テキストDL」リンクで配布する `docs/assets/<game>.txt` は、`docs/games/` 配下の Markdown から生成します。

- `python scripts/export_text.py` で全ゲーム分のテキストを再生成
- ゲームを追加・更新したときは必ず実行し、既存のテキストもまとめて更新してください

### タブ内インデントの自動調整

Obsidian などでタブ内の記述をインデントなしで編集したい場合は、アップロード前にインデントを自動付与できます。

- 単一ファイルに適用: `python scripts/indent_tabs.py docs/games/18Chesapeake.md`
- すべてのゲームファイルに適用: `python scripts/indent_tabs.py`

### 構造チェック

ゲームページの必須構造（タイトル / actions / タブ構成）と、`docs/games/.pages` および `docs/games/index.md` の整合は次のコマンドで検証できます。

- `python scripts/validate_structure.py`
- `python scripts/check_links.py`
- `python scripts/check_assets.py`

個別に確認する場合は、次のコマンドも利用できます。

- `python -m unittest discover -s tests`
- `python -m mkdocs build --strict --site-dir $env:TEMP\18xx-summary-check`

## 編集を受け付ける運用

- GitHub の Pull Request で受け付ける
- ルールの誤記修正や、見出し分割の改善がしやすい構成です
