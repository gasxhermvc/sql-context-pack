[CmdletBinding()]
param(
    [switch]$Update,
    [switch]$Repair,
    [switch]$SkipConfigure
)

$ErrorActionPreference = 'Stop'
if ($Update -and $Repair) { throw 'Choose either -Update or -Repair, not both.' }
$installedPlugin = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'plugins\sql-context-pack'
$operation = if ($Update) { 'update' } elseif ($Repair -and (Test-Path -LiteralPath $installedPlugin)) { 'update' } else { 'install' }
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

Write-Output 'Preparing the managed Windows Service. Administrator access is requested only for ProgramData ACLs and service registration.'
Write-Output 'The service binds to 127.0.0.1; no firewall rule or remote network access is requested.'
$serviceInstaller = Join-Path $PSScriptRoot 'scripts\windows-service.ps1'
& $serviceInstaller -Operation $operation -SourceRoot $PSScriptRoot -PythonExecutable $python
if ($LASTEXITCODE -ne 0) {
    Write-Output 'Package/plugin installation completed, but Windows Service installation or health verification failed.'
    exit $LASTEXITCODE
}

Write-Output 'Installation is ready in this terminal. Start normal Codex; the plugin provides MCP automatically.'
Write-Output 'Inside Codex, run: $sql-context-pack profiles, then $sql-context-pack connect <profile-name>'
if ($Update -or $Repair) {
    Write-Output 'The service and plugin files are updated. Open a new Codex room to load changed Skill content.'
}
