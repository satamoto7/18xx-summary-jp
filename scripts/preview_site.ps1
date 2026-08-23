param(
    [int]$Port = 8000
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

& $python -m mkdocs serve -a "127.0.0.1:$Port"
