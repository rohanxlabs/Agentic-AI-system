$project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $project
$python = Join-Path $project "venv\Scripts\python.exe"
& $python main.py
