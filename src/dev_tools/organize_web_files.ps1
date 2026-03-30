# Create directory structure
$webRoot = "src/web"
$dirs = @(
    "$webRoot/static/js",
    "$webRoot/static/css",
    "$webRoot/static/img",
    "$webRoot/templates",
    "$webRoot/templates/errors",
    "$webRoot/templates/tokenizer"
)

foreach ($dir in $dirs) {
    New-Item -Path $dir -ItemType Directory -Force
}

# Move files to correct locations
$fileMapping = @{
    # Static files
    "$webRoot/static/js/walkthrough.js"                 = $true
    "$webRoot/static/css/custom.css"                    = $true
    "$webRoot/static/js/script.js"                      = $true
    "$webRoot/static/css/styles.css"                    = $true

    # Template files
    "$webRoot/templates/layout.html"                    = $true
    "$webRoot/templates/intro.html"                     = $true
    "$webRoot/templates/setup.html"                     = $true
    "$webRoot/templates/define_model.html"              = $true
    "$webRoot/templates/data_prep.html"                 = $true
    "$webRoot/templates/pretrain.html"                  = $true
    "$webRoot/templates/training.html"                  = $true
    "$webRoot/templates/embedding.html"                 = $true
    "$webRoot/templates/evaluation.html"                = $true
    "$webRoot/templates/inference.html"                 = $true
    "$webRoot/templates/checkpoint.html"                = $true

    # Error templates
    "$webRoot/templates/errors/404.html"                = $true
    "$webRoot/templates/errors/500.html"                = $true

    # Tokenizer templates
    "$webRoot/templates/tokenizer/text_tokenizer.html"  = $true
    "$webRoot/templates/tokenizer/image_tokenizer.html" = $true
    "$webRoot/templates/tokenizer/tokenizer_info.html"  = $true

    # Server files
    "$webRoot/server.py"                                = $true
    "$webRoot/route_config.py"                          = $true
}

# Verify files
Write-Host "Verifying web application files..."
foreach ($file in $fileMapping.Keys) {
    if (Test-Path $file) {
        Write-Host "✓ Found: $file"
    }
    else {
        Write-Host "✗ Missing: $file"
    }
}

Write-Host "`nDirectory structure:"
Get-ChildItem -Path $webRoot -Recurse -Directory | Format-Table FullName
