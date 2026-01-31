$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent $root
$py = Join-Path $repo ".venv\\Scripts\\python.exe"

if (-not (Test-Path $py)) {
  Write-Error "Missing .venv. Create it with: py -3.11 -m venv .venv"
  exit 1
}

Set-Location $repo

Write-Host "Running py_compile..."
$files = $null
if (Get-Command rg -ErrorAction SilentlyContinue) {
  try {
    $files = rg --files -g "*.py" -g "!vendors/**" -g "!.venv/**"
  } catch {
    $files = $null
  }
}
if (-not $files) {
  $files = Get-ChildItem -Path $repo -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\vendors\\|\\.venv\\' } | ForEach-Object { $_.FullName }
}
& $py -m py_compile @files

Write-Host "Running smoke tests..."
& $py .\tests\smoke.py
