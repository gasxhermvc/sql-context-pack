[CmdletBinding()]
param(
    [switch]$Update,
    [switch]$SkipConfigure
)

$ErrorActionPreference = 'Stop'
$operation = if ($Update) { 'update' } else { 'install' }
$installer = Join-Path $PSScriptRoot 'scripts\install-global.ps1'

& $installer -Operation $operation -Mode plugin
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$preflightOutput = & (Join-Path $PSScriptRoot 'scripts\python-preflight.ps1')
if ($LASTEXITCODE -ne 0) {
    $preflightOutput | Write-Output
    exit $LASTEXITCODE
}
$python = ($preflightOutput | ConvertFrom-Json).executable

if (-not $SkipConfigure) {
    $profileState = & $python -m sqlctx.cli profile list | ConvertFrom-Json
    if ($profileState.configured -eq 0) {
        Write-Output 'No database profile exists; starting secure interactive setup.'
        & $python -m sqlctx.cli.configure
        if ($LASTEXITCODE -ne 0) {
            Write-Output 'The package is installed, but profile connection validation did not pass.'
            Write-Output 'Correct the reported owner-side connection setting, then run:'
            Write-Output "& '$python' -m sqlctx.cli profile test <profile-name>"
            exit $LASTEXITCODE
        }
    }
}

Write-Output 'Installation is ready. Start the complete owner-controlled workflow with:'
Write-Output "& '$python' -m sqlctx.cli profile list"
Write-Output "& '$python' -m sqlctx.cli launch --harness codex --profile <profile-name>"
