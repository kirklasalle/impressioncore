Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "ImpressionCore Knowledge Distillation with Ollama" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "`nStep 1: Checking if Ollama is running..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Ollama is running! (version: $($response.version))" -ForegroundColor Green
    
    Write-Host "`nAvailable models:" -ForegroundColor Yellow
    $modelResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
    if ($modelResponse.models.Count -gt 0) {
        $models = $modelResponse.models | ForEach-Object { $_.name }
        Write-Host "Found $($models.Count) models: $($models -join ', ')" -ForegroundColor Green
    }
    else {
        Write-Host "No models found. Please pull a model using: ollama pull llama2" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Ollama is not running! Please start Ollama first." -ForegroundColor Red
    Write-Host "Run 'ollama serve' in a separate terminal." -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "`nStep 2: Checking Python environment..." -ForegroundColor Yellow
if (-Not (Test-Path "env")) {
    Write-Host "Python environment not found. Setting up..." -ForegroundColor Yellow
    & .\setup_environment.bat
}
else {
    Write-Host "✅ Python environment exists." -ForegroundColor Green
}

Write-Host "`nStep 3: Create directory structure if needed..." -ForegroundColor Yellow
if (-Not (Test-Path "training\web")) {
    Write-Host "Creating necessary directories..." -ForegroundColor Yellow
    & .\create_structure.bat
}
else {
    Write-Host "✅ Directory structure exists." -ForegroundColor Green
}

Write-Host "`nStep 4: Installing Flask-CORS if needed..." -ForegroundColor Yellow
if (-Not (Test-Path "env\Lib\site-packages\flask_cors")) {
    Write-Host "Installing Flask-CORS..." -ForegroundColor Yellow
    & env\Scripts\pip install flask-cors
}
else {
    Write-Host "✅ Flask-CORS already installed." -ForegroundColor Green
}

Write-Host "`nStep 5: Starting the training server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "run_training_server.py"

Write-Host "`nStep 6: Opening dashboard in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:5000"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "ImpressionCore Knowledge Distillation is now running!" -ForegroundColor Green
Write-Host "`nInstructions:"
Write-Host "1. In the web dashboard, select your Ollama model as the teacher"
Write-Host "2. Configure student model and training parameters"
Write-Host "3. Click 'Start Training' to begin knowledge distillation"
Write-Host "4. Monitor progress in the dashboard"
Write-Host "`nTo stop the server, close the Python command window that opened" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
