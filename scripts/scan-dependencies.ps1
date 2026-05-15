#!/usr/bin/env pwsh
param(
  [string]$DenylistPath = ".github/dependency-rules/payment-denylist.txt",
  [string]$ProjectPath = "ApiGateway.csproj"
)

# Fail fast on errors
$ErrorActionPreference = "Stop"

function Write-Info($msg) {
  Write-Host "[scan] $msg"
}

function Append-Summary($content) {
  if ($env:GITHUB_STEP_SUMMARY) {
    Add-Content -Path $env:GITHUB_STEP_SUMMARY -Value $content
  } else {
    # Local run fallback
    Write-Output $content
  }
}

function Load-DenylistPatterns([string]$path) {
  if (-not (Test-Path -Path $path)) {
    throw "Denylist file not found at '$path'"
  }
  $patterns = Get-Content -Path $path | ForEach-Object { $_.Trim() } | Where-Object {
    $_ -and -not $_.StartsWith("#")
  }
  return ,$patterns
}

function Test-IdAgainstDenylist([string]$id, [string[]]$patterns) {
  foreach ($pat in $patterns) {
    if ([string]::IsNullOrWhiteSpace($pat)) { continue }
    if ($id -match $pat) {
      return $true
    }
  }
  return $false
}

function Safe-ConvertFromJson([string]$json) {
  if ([string]::IsNullOrWhiteSpace($json)) { return $null }
  try {
    return $json | ConvertFrom-Json -Depth 100
  } catch {
    Write-Info "Failed to parse JSON. First 200 chars: $($json.Substring(0, [Math]::Min(200, $json.Length)))"
    throw
  }
}

# Initialize
$allowFailure = ($env:ALLOW_FAILURE -eq "true")
$repo = if ($env:GITHUB_REPOSITORY) { $env:GITHUB_REPOSITORY } else { (Get-Location).Path }
$commit = if ($env:GITHUB_SHA) { $env:GITHUB_SHA } else { "" }
$timestamp = (Get-Date).ToUniversalTime().ToString("o")

Write-Info "Starting dependency scan"
Write-Info "Override (ALLOW_FAILURE) = $allowFailure"
Write-Info "Denylist file          = $DenylistPath"
Write-Info "Project file           = $ProjectPath"

$denylist = Load-DenylistPatterns -path $DenylistPath

# Backend (.NET) scan
$backendFindings = @()
$packagesJsonPath = Join-Path -Path (Get-Location) -