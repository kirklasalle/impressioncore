param(
    [string]$TaskName = "ColossusWatchlistNightly",
    [ValidatePattern('^[0-2][0-9]:[0-5][0-9]$')]
    [string]$ScheduleTime = "02:00",
    [ValidateSet("Daily", "Hourly")]
    [string]$Frequency = "Daily",
    [string]$Baseline = "F:/models/management/training_sessions/colossus/20251027_154628_colossus_distilled.pt",
    [string[]]$Checkpoints = @("F:/models/management/training_sessions/colossus/20251107_144544_colossus_regulator_blend.pt"),
    [string[]]$TeacherData = @(
        "src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251026_regulator_remediation_blend.json",
        "src/training/distillation/kd_inputs/generated/ollama_plain_remediation_teacher_20251027.json"
    ),
    [string]$WatchlistThreshold = "0.035",
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..\..")).Path
$monitorScript = Join-Path $repoRoot "src/dev_tools/monitoring/run_colossus_watchlist_monitor.ps1"
if (-not (Test-Path $monitorScript)) {
    throw "Monitor script not found at $monitorScript"
}

$psExe = (Get-Command powershell.exe -ErrorAction Stop).Source

function Convert-ToQuoted([string]$value) {
    return '"' + $value.Replace('"', '\"') + '"'
}

$argumentBuilder = New-Object System.Text.StringBuilder
$null = $argumentBuilder.Append("-NoProfile -ExecutionPolicy Bypass -File ")
$null = $argumentBuilder.Append((Convert-ToQuoted $monitorScript))

if ($Baseline) {
    $null = $argumentBuilder.Append(" -Baseline ")
    $null = $argumentBuilder.Append((Convert-ToQuoted $Baseline))
}
if ($Checkpoints) {
    $null = $argumentBuilder.Append(" -Checkpoints")
    foreach ($checkpoint in $Checkpoints) {
        $null = $argumentBuilder.Append(" ")
        $null = $argumentBuilder.Append((Convert-ToQuoted $checkpoint))
    }
}
if ($TeacherData) {
    foreach ($dataset in $TeacherData) {
        $null = $argumentBuilder.Append(" -TeacherData ")
        $null = $argumentBuilder.Append((Convert-ToQuoted $dataset))
    }
}
if ($WatchlistThreshold) {
    $null = $argumentBuilder.Append(" -WatchlistThreshold ")
    $null = $argumentBuilder.Append((Convert-ToQuoted $WatchlistThreshold))
}

$actionArgs = $argumentBuilder.ToString()
$action = New-ScheduledTaskAction -Execute $psExe -Argument $actionArgs -WorkingDirectory $repoRoot

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$runTime = [DateTime]::ParseExact($ScheduleTime, "HH:mm", $culture)
$runDateTime = (Get-Date).Date.Add($runTime.TimeOfDay)

switch ($Frequency) {
    "Daily" {
        $trigger = New-ScheduledTaskTrigger -Daily -At $runDateTime
    }
    "Hourly" {
        $trigger = New-ScheduledTaskTrigger -Once -At $runDateTime
        $trigger.Repetition.Interval = (New-TimeSpan -Hours 1)
        $trigger.Repetition.Duration = [TimeSpan]::MaxValue
    }
}

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -DontStopIfGoingOnBatteries
$description = "Runs the Colossus watchlist monitor PowerShell wrapper from the ImpressionCore repo."

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask -and -not $Force) {
    throw "Scheduled task '$TaskName' already exists. Re-run with -Force to overwrite."
}

if ($existingTask -and $Force) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$currentUser = "{0}\\{1}" -f $env:USERDOMAIN, $env:USERNAME
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -RunLevel Limited

$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $description
Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force:$Force.IsPresent | Out-Null

Write-Output "Scheduled task '$TaskName' registered to run $Frequency at $ScheduleTime using working directory $repoRoot."