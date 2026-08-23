param(
    [string]$SiteDir = (Join-Path $env:TEMP "18xx-summary-check"),
    [string]$SummarySourceRoot
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python が見つかりません。.venv を作成するか、Python を PATH に追加してください。"
    }
    $python = $pythonCommand.Source
}

Write-Host "[1/7] テキスト版を再生成"
& $python scripts\export_text.py

Write-Host "[2/7] ソースマニフェスト監査"
$manifestArgs = @("scripts\validate_source_manifests.py")
if ($SummarySourceRoot) {
    $manifestArgs += @("--source-root", $SummarySourceRoot)
}
& $python @manifestArgs

Write-Host "[3/7] 構造チェック"
& $python scripts\validate_structure.py

Write-Host "[4/7] 内部リンク監査"
& $python scripts\check_links.py

Write-Host "[5/7] 資産監査"
& $python scripts\check_assets.py

Write-Host "[6/7] Python テスト"
& $python -m unittest discover -s tests

Write-Host "[7/7] MkDocs strict ビルド"
& $python -m mkdocs build --strict --site-dir $SiteDir

Write-Host "サイト検証が完了しました。出力先: $SiteDir"
