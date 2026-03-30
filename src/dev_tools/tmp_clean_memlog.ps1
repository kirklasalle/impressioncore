$memlog = Resolve-Path .\src\memlog -ErrorAction SilentlyContinue
if (-not $memlog) { Write-Output 'src/memlog does not exist'; exit 0 }
$samplesDir = Resolve-Path .\src\deployment\samples -ErrorAction SilentlyContinue
if (-not $samplesDir) { New-Item -ItemType Directory -Path .\src\deployment\samples | Out-Null; $samplesDir = Resolve-Path .\src\deployment\samples }
Get-ChildItem -Path .\src\memlog -Recurse -File -Include *.npy,*.npz,*.ndjson | ForEach-Object {
    $dest = Join-Path $samplesDir $_.Name
    if (Test-Path $dest) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        $ext = $_.Extension
        $dest = Join-Path $samplesDir ("${name}_$(Get-Date -Format yyyyMMdd_HHmmss)${ext}")
    }
    Move-Item -Path $_.FullName -Destination $dest -Force
    Write-Output ("moved: {0} -> {1}" -f $_.FullName, $dest)
}
Write-Output '--- remaining files in src/memlog ---'
Get-ChildItem -Path .\src\memlog -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { Write-Output $_.FullName }
