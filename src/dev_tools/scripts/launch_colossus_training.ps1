$env:PYTHONPATH="."
.venv310\Scripts\activate

# Ensure output directory exists
$OutputDir = "F:\models\management\training_sessions\colossus"
if (!(Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "Created output directory: $OutputDir"
}

# Teacher data files
$TeacherData = @(
    "src/training/distillation/kd_inputs/generated/ollama_plain_remediation_teacher_20251027.json",
    "src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251026_regulator_remediation_blend.json"
)

# Construct command arguments
$Args = @(
    "src/training/colossus_distillation.py",
    "--dataset-size", "4096",
    "--batch-size", "16",
    "--gradient-accumulation", "4",
    "--epochs", "5",
    "--learning-rate", "5e-4",
    "--output-dir", $OutputDir
)

foreach ($file in $TeacherData) {
    if (Test-Path $file) {
        $Args += "--teacher-data"
        $Args += $file
    } else {
        Write-Warning "Teacher data file not found: $file"
    }
}

Write-Host "Starting Colossus Distillation Training..."
python @Args
