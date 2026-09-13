$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python -c "import numpy"
if ($LASTEXITCODE -ne 0) { throw 'Install requirements first: python -m pip install -r requirements.txt' }
if (-not (Test-Path -LiteralPath 'models/neuro_fuzzy.json')) {
    python train.py --epochs 180
    if ($LASTEXITCODE -ne 0) { throw 'Training failed.' }
}
python evaluate.py --seeds 5
if ($LASTEXITCODE -ne 0) { throw 'Evaluation failed.' }
Invoke-Item -LiteralPath (Join-Path $PSScriptRoot 'results/report.html')
