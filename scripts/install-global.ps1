[CmdletBinding()]
param(
    [ValidateSet('install', 'update', 'status', 'remove')]
    [string]$Operation = 'install',

    [ValidateSet('plugin', 'skill')]
    [string]$Mode = 'plugin',

    [switch]$SkipPackageInstall,

    [switch]$SkipPathUpdate,

    [switch]$SkipCodexRegister,

    [switch]$Yes
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$preflightOutput = & (Join-Path $PSScriptRoot 'python-preflight.ps1')
if ($LASTEXITCODE -ne 0) {
    $preflightOutput | Write-Output
    exit $LASTEXITCODE
}
$preflight = $preflightOutput | ConvertFrom-Json
if ($Operation -in @('install', 'update') -and -not $SkipPackageInstall) {
    & $preflight.executable -m pip install --user $repositoryRoot
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

$userScripts = & $preflight.executable -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))"
if ($LASTEXITCODE -ne 0 -or -not $userScripts) {
    throw 'Unable to resolve the selected host Python user Scripts directory.'
}
$userScripts = [System.IO.Path]::GetFullPath(($userScripts | Select-Object -First 1).Trim())
if ($Operation -in @('install', 'update') -and -not $SkipPathUpdate) {
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $pathParts = @($userPath -split ';' | Where-Object { $_ })
    if (-not ($pathParts | Where-Object { [System.IO.Path]::GetFullPath($_.TrimEnd('\')) -eq $userScripts.TrimEnd('\') })) {
        $updatedUserPath = (($pathParts + $userScripts) -join ';')
        [Environment]::SetEnvironmentVariable('Path', $updatedUserPath, 'User')
    }
    if (-not (($env:PATH -split ';') -contains $userScripts)) {
        $env:PATH = "$userScripts;$env:PATH"
    }
}

$arguments = @(
    (Join-Path $PSScriptRoot 'global_install.py'),
    $Operation,
    '--mode',
    $Mode,
    '--source-root',
    $repositoryRoot
)
if ($SkipCodexRegister) {
    $arguments += '--skip-codex-register'
}
if ($Yes) {
    $arguments += '--yes'
}
& $preflight.executable @arguments
$installerExit = $LASTEXITCODE
if ($installerExit -eq 0 -and $Operation -in @('install', 'update') -and -not $SkipPackageInstall) {
    $serverLauncher = Join-Path $userScripts 'sqlctx-server.exe'
    $cliLauncher = Join-Path $userScripts 'sqlctx.exe'
    if (-not (Test-Path -LiteralPath $serverLauncher) -or -not (Test-Path -LiteralPath $cliLauncher)) {
        throw 'Global package entry points were not created in the selected host Python user Scripts directory.'
    }
    & $serverLauncher --help | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'sqlctx-server entry point failed its post-install smoke test.'
    }
    Write-Output "PATH-independent diagnostic server command: & '$serverLauncher' --host 127.0.0.1 --port 8765"
    Write-Output 'The current PowerShell process PATH is ready. A new Codex room is required only when plugin content changed.'
}
exit $installerExit
