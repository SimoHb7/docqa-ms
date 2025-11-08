# Script to convert @/ path aliases to relative imports

$srcPath = "c:\docqa-ms\InterfaceClinique\src"

# Define import mappings for each directory level
$importMappings = @{
    # From src/pages/
    "pages" = @{
        "@/store" = "../store"
        "@/services/api" = "../services/api"
        "@/utils" = "../utils"
        "@/types" = "../types"
        "@/components/ui/LoadingSpinner" = "../components/ui/LoadingSpinner"
        "@/components/ui/Button" = "../components/ui/Button"
        "@/components/ui/Card" = "../components/ui/Card"
    }
    # From src/components/layout/
    "components/layout" = @{
        "@/store" = "../../store"
        "@/services/api" = "../../services/api"
        "@/utils" = "../../utils"
        "@/types" = "../../types"
    }
    # From src/store/
    "store" = @{
        "@/types" = "../types"
    }
    # From src/services/
    "services" = @{
        "@/types" = "../types"
    }
}

# Process each directory
foreach ($dir in $importMappings.Keys) {
    $fullPath = Join-Path $srcPath $dir
    if (Test-Path $fullPath) {
        Write-Host "Processing directory: $dir"
        
        $files = Get-ChildItem -Path $fullPath -Filter "*.tsx" -Recurse
        foreach ($file in $files) {
            Write-Host "  Processing file: $($file.Name)"
            $content = Get-Content $file.FullName -Raw
            $originalContent = $content
            
            foreach ($alias in $importMappings[$dir].Keys) {
                $relative = $importMappings[$dir][$alias]
                $content = $content -replace [regex]::Escape("from '$alias'"), "from '$relative'"
                $content = $content -replace [regex]::Escape("from `"$alias`""), "from `"$relative`""
            }
            
            if ($content -ne $originalContent) {
                Set-Content -Path $file.FullName -Value $content -NoNewline
                Write-Host "    Updated: $($file.Name)" -ForegroundColor Green
            }
        }
    }
}

Write-Host "`nImport conversion complete!" -ForegroundColor Cyan
