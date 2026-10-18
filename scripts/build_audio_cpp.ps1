[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$AudioCppRoot,
    [string]$CudaArchitectures = "auto",
    [ValidateRange(1, 64)][int]$Jobs = 4
)
$ErrorActionPreference = "Stop"
$taskRoot = (Resolve-Path -LiteralPath $AudioCppRoot).Path
$taskHelper = Join-Path $taskRoot 'scripts\build_windows.ps1'
if (-not (Test-Path -LiteralPath $taskHelper -PathType Leaf)) { throw 'audio.cpp build helper not found.' }
$taskRevision = & git -C $taskRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $taskRevision.Trim() -ne 'ace630deedf60b9c2ff7ec2277a9cdfb1f37f69f') {
    throw 'Use the audio.cpp commit documented in README.md for this build recipe.'
}
$taskVswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path -LiteralPath $taskVswhere)) { throw 'Install Visual Studio C++ build tools 2022 or newer.' }
$taskVisualStudio = & $taskVswhere -latest -products '*' -version '[17.0,)' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $taskVisualStudio) { throw 'Visual Studio C++ build tools 2022 or newer were not found.' }
& $taskHelper -Preset windows-cuda-release -ModelSet custom -Models fish_drama3 -Target audiocpp_server `
    -Jobs $Jobs -CudaArchitectures $CudaArchitectures -CpuArch baseline -DeploymentBuild -VsInstall $taskVisualStudio
if ($LASTEXITCODE -ne 0) { throw 'audio.cpp build failed. Check the compiler/CUDA diagnostics above.' }
