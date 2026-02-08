# Fetch documentation from Context7
param(
    [Parameter(Mandatory=$true)]
    [string]$LibraryId,

    [Parameter(Mandatory=$true)]
    [string]$Query
)

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
$EncodedLib = [System.Web.HttpUtility]::UrlEncode($LibraryId)
$EncodedQuery = [System.Web.HttpUtility]::UrlEncode($Query)
$Url = "https://context7.com/api/v2/context?libraryId=$EncodedLib&query=$EncodedQuery"

# Make request
$Headers = @{}
if ($ApiKey) {
    $Headers["Authorization"] = "Bearer $ApiKey"
}

try {
    $Response = Invoke-RestMethod -Uri $Url -Headers $Headers -Method Get
    Write-Output $Response
} catch {
    Write-Error "Error: $_"
    exit 1
}
