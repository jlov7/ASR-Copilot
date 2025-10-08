Param(
    [switch]$InstallDependencies
)

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Resolve-Path (Join-Path $root "..")
Set-Location $root

$venvPath = Join-Path $repoRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts/Activate.ps1"

if ($InstallDependencies.IsPresent) {
    if (-not (Test-Path $venvPath -PathType Container)) {
        python -m venv $venvPath
    }
    & $activateScript
    pip install -r (Join-Path $repoRoot "requirements.txt")
    Set-Location (Join-Path $root "frontend")
    npm install
    Set-Location $root
}

if (-not (Test-Path $venvPath -PathType Container)) {
    Write-Error "Python virtual environment not found. Run with -InstallDependencies or create ..\.venv manually."
    exit 1
}

. $activateScript
$env:PYTHONPATH = "$repoRoot;$env:PYTHONPATH"

Write-Host "Seeding sample data..."
python -m app.scripts.seed_data | Out-Null

Write-Host "Launching ASR Copilot backend..."
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.backend.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $repoRoot -WindowStyle Hidden
Start-Sleep -Seconds 2

Write-Host "Launching ASR Copilot frontend..."
Set-Location (Join-Path $root "frontend")
if (-not (Test-Path "node_modules" -PathType Container)) {
    npm install
}
Start-Process -FilePath "npm" -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173" -WorkingDirectory (Get-Location)
Start-Sleep -Seconds 2

Write-Host "Opening dashboard..."
Start-Process "http://127.0.0.1:5173"

Write-Host "Status Pack exports will appear in $($repoRoot)\out\"
Write-Host "Press Ctrl+C in each terminal to stop the services."
