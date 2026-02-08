# Search for Context7 library IDs
param(
    [Parameter(Mandatory=$true)]
    [string]$LibraryName,

    [Parameter(Mandatory=$false)]
    [string]$Query
)

if (-not $Query) {
    $Query = $LibraryName
}

# Load API key from .env file
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path (Split-Path (Split-Path $ScriptDir)) ".env"
$ApiKey = ""
if (Test-Path $EnvFile) {
    $EnvContent = Get-Content $EnvFile
    foreach ($line in $EnvContent) {
        if ($line -match '^CONTEXT7_API_KEY=(.+)$') {
            $ApiKey = $matches[1].Trim('"').Trim("'")
            break
        }
    }
}
# Fallback to environment variable
if (-not $ApiKey) {
    $ApiKey = $env:CONTEXT7_API_KEY
}

# Build URL with encoded parameters
$EncodedLib = [System.Web.HttpUtility]::UrlEncode($LibraryName)
$EncodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
$Url = "https://context7.com/api/v2/libs/search?libraryName=$EncodedLib&query=$EncodedQuery"

# Make request
$Headers = @{}
if ($ApiKey) {
    $Headers["Authorization"] = "Bearer $ApiKey"
}

try {
    $Response = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get

    Write-Host "Available Libraries:`n"
    foreach ($lib in $Response.results) {
        Write-Host "- **$($lib.title)**"
        Write-Host "  ID: ``$($lib.id)``"
        Write-Host "  Description: $($lib.description)"
        Write-Host "  Snippets: $($lib.totalSnippets)"
        Write-Host ""
    }
} catch {
    Write-Error "Error: $_"
    exit 1
}
