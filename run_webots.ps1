param(
    [ValidateSet('legacy_neuro_fuzzy','pid','fuzzy','neuro_fuzzy')][string]$Controller = 'neuro_fuzzy',
    [ValidateSet('straight','circle','figure_eight','stop_go','noisy_delay','target_loss','wheel_mismatch','outliers','speed_change')][string]$Scenario = 'figure_eight',
    [switch]$Batch,
    [switch]$Video
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$webotsCandidates = @(
    'C:\Users\User\Documents\ChatGPT\fyp\tools\Webots\msys64\mingw64\bin\webots.exe',
    'C:\Program Files\Webots\msys64\mingw64\bin\webots.exe'
)
$webotsExecutable = $webotsCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $webotsExecutable) { throw 'Webots not found. Update the executable path in run_webots.ps1.' }
python prepare_world.py --controller $Controller --scenario $Scenario --duration 48
if ($LASTEXITCODE -ne 0) { throw 'World generation failed.' }
$env:FYP_BATCH = if ($Batch) { '1' } else { '0' }
$env:FYP_CAPTURE = '1'
$env:FYP_VIDEO = if ($Video) { '1' } else { '0' }
if ($Video -and -not $Batch) { throw 'Use -Batch with -Video for automatic recording completion.' }
$worldPath = Join-Path $PSScriptRoot "worlds\${Scenario}_${Controller}.wbt"
if ($Batch) {
    & $webotsExecutable --batch --mode=fast --stdout --stderr --minimize $worldPath
} else {
    & $webotsExecutable --mode=realtime --stdout --stderr $worldPath
}
