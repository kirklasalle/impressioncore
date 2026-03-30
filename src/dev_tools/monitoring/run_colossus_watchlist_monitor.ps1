param(
    [string]$Baseline = "F:/models/management/training_sessions/colossus/20251027_154628_colossus_distilled.pt",
    [string[]]$Checkpoints = @("F:/models/management/training_sessions/colossus/20251107_144544_colossus_regulator_blend.pt"),
    [string[]]$TeacherData = @(
        "src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251026_regulator_remediation_blend.json",
        "src/training/distillation/kd_inputs/generated/ollama_plain_remediation_teacher_20251027.json"
    ),
    [int[]]$Watchlist = @(27, 59, 70, 83, 118, 141, 191),
    [double]$WatchlistThreshold = 0.035,
    [string]$LogPath = "src/dev_tools/monitoring/logs/colossus_watchlist_monitor.log"
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..\..")).Path
Set-Location $repoRoot

$pythonExe = Join-Path $repoRoot ".venv310\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe"
}

$absoluteLogPath = Join-Path $repoRoot $LogPath
$logDirectory = Split-Path $absoluteLogPath -Parent
if (-not (Test-Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
}

$arguments = New-Object System.Collections.Generic.List[string]
$arguments.Add("src/dev_tools/monitoring/colossus_watchlist_monitor.py")
$arguments.Add("--baseline")
$arguments.Add($Baseline)
if ($Checkpoints.Count -gt 0) {
    $arguments.Add("--checkpoints")
    foreach ($checkpoint in $Checkpoints) {
        $arguments.Add($checkpoint)
    }
}

foreach ($dataset in $TeacherData) {
    $arguments.Add("--teacher-data")
    $arguments.Add($dataset)
}

if ($Watchlist.Count -gt 0) {
    $arguments.Add("--watchlist")
    foreach ($dimension in $Watchlist) {
        $arguments.Add($dimension.ToString())
    }
}
$arguments.Add("--watchlist-threshold")
$arguments.Add([string]::Format([System.Globalization.CultureInfo]::InvariantCulture, "{0:F3}", $WatchlistThreshold))

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logHeader = "[$timestamp] Running Colossus watchlist monitor"
Add-Content -Path $absoluteLogPath -Value $logHeader

$processOutput = & $pythonExe @arguments 2>&1
$exitCode = $LASTEXITCODE

if ($processOutput) {
    $processOutput | ForEach-Object {
        $line = $_.ToString()
        Add-Content -Path $absoluteLogPath -Value $line
        Write-Output $line
    }
}
Add-Content -Path $absoluteLogPath -Value "Completed with exit code $exitCode"
Write-Output "Completed with exit code $exitCode"

if ($exitCode -ne 0) {
    throw "Colossus watchlist monitor exited with code $exitCode"
}