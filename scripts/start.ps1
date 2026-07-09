Param(
    [switch]$Install = $true,
    [int]$Port = 8000
)

$project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $project

if ($Install -and -not (Test-Path venv)) {
    python -m venv venv
}

$python = Join-Path $project "venv\Scripts\python.exe"
if ($Install) {
    & $python -m pip install --upgrade pip
    & $python -m pip install -r requirements.txt
}

Write-Host "Starting API on port $Port..."
& $python -m uvicorn api:app --reload --port $Port
