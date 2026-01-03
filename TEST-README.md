# テスト環境の使い方

新しいゲームのmdファイルをテスト表示する方法

## 1. テスト用ファイルを配置
```powershell
# 新しいmdファイルをtest-docs/gamesに配置
copy 新しいファイル.md test-docs\games\
```

## 2. mkdocs-test.ymlを編集
nav:セクションに新しいファイルを追加

## 3. テストサーバー起動
```powershell
.venv\Scripts\Activate.ps1
mkdocs serve -f mkdocs-test.yml
```

## 4. 確認後
- test-docs/gamesから不要なファイルを削除
- または本番に移動: copy test-docs\games\ファイル.md docs\games\
