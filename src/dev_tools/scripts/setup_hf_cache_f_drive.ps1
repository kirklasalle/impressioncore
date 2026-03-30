# HuggingFace Cache Configuration for F: Drive
# Run this before running any HuggingFace downloads

$env:HF_HOME="F:\huggingface_cache"
$env:HUGGINGFACE_HUB_CACHE="F:\huggingface_cache\hub"
$env:HF_DATASETS_CACHE="F:\huggingface_cache\datasets"

Write-Host "HuggingFace cache configured to use F: drive" -ForegroundColor Green
Write-Host "   HF_HOME: $env:HF_HOME"
Write-Host "   HUGGINGFACE_HUB_CACHE: $env:HUGGINGFACE_HUB_CACHE"
Write-Host "   HF_DATASETS_CACHE: $env:HF_DATASETS_CACHE"
