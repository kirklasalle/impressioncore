
# Download and install Ollama for Windows
$ErrorActionPreference = "Stop"

Write-Host "Downloading Ollama for Windows..." -ForegroundColor Green
$url = "https://ollama.ai/download/OllamaSetup.exe"
# NEVER use C: temp; use repo-local backups/tmp
$destDir = Join-Path "." "backups/tmp"
if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
$output = Join-Path $destDir "OllamaSetup.exe"

try {
    Invoke-WebRequest -Uri $url -OutFile $output
    Write-Host "Download complete. Running installer..." -ForegroundColor Green
    Start-Process -FilePath $output -Wait
    Write-Host "Ollama installation complete!" -ForegroundColor Green
} catch {
    Write-Host "Error downloading Ollama: $_" -ForegroundColor Red
    exit 1
}
