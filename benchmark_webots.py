"""Run all 36 scenario/controller combinations in actual Webots physics."""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from src.control import Config
from src.simulation import SCENARIOS
from src.tracking import CONTROLLERS
from dataclasses import asdict

ROOT=Path(__file__).resolve().parent
WEBOTS=Path(os.environ.get('FYP_WEBOTS',r'C:\Users\User\Documents\ChatGPT\fyp\tools\Webots\msys64\mingw64\bin\webots.exe'))


def main():
    if not WEBOTS.is_file():
        raise SystemExit('Set FYP_WEBOTS to the Webots executable path.')
    out=ROOT/'results'/'webots'
    out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,FYP_BATCH='1',FYP_CAPTURE='0',FYP_VIDEO='0',FYP_SEED='0',PYTHONIOENCODING='utf-8')
    summaries=[]
    for scenario in SCENARIOS:
        for name in CONTROLLERS:
            subprocess.run([sys.executable,'prepare_world.py','--controller',name,'--scenario',scenario],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            started=time.time()
            run=subprocess.run([str(WEBOTS),'--batch','--mode=fast','--stdout','--stderr','--minimize',str(ROOT/'worlds'/f'{scenario}_{name}.wbt')],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
            output=run.stdout+'\n'+run.stderr
            (out/f'{scenario}_{name}_console.txt').write_text(output,encoding='utf-8')
            metric_path=out/f'{scenario}_{name}_metrics.json'
            if run.returncode or 'Traceback' in output or 'ERROR:' in output or 'Error:' in output or not metric_path.exists() or metric_path.stat().st_mtime < started:
                raise RuntimeError(f'Failed or stale run: {scenario}/{name}. See console log.')
            rows=list(csv.DictReader((out/f'{scenario}_{name}.csv').open(encoding='utf-8')))
            if len(rows)!=1500 or abs(float(rows[-1]['t'])-48)>0.001:
                raise RuntimeError('Incomplete Webots trace')
            summaries.append(dict(scenario=scenario,controller=name,seed=0,**json.loads(metric_path.read_text())))
            print(f'{len(summaries):02d}/36 {scenario:15} {name:20} RMSE={summaries[-1]["distance_rmse_m"]:.4f} m',flush=True)
    with (out/'comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
    provenance=dict(webots='R2025a',duration=48,seed=0,config=asdict(Config()),runs=len(summaries),
                    sensing='Simulated range/bearing with known robot localization. Ground truth used only to generate sensor returns and score results.',
                    sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/control.py',ROOT/'src/tracking.py',ROOT/'src/simulation.py',ROOT/'models/neuro_fuzzy.json',ROOT/'controllers/human_follower/human_follower.py']})
    (out/'metadata.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    lines=['# V2 Webots results','', 'Actual Webots R2025a physics: 48 seconds per run, seed 0. All baselines use the same sensor model. V2 controllers share motion estimation/feedforward; legacy retains the V1 controller.', '', '| Scenario | V1 neuro RMSE | V2 neuro RMSE | Change | V1 accel RMS | V2 accel RMS |', '|---|---:|---:|---:|---:|---:|']
    for scenario in SCENARIOS:
        group={r['controller']:r for r in summaries if r['scenario']==scenario}
        a,b=group['legacy_neuro_fuzzy'],group['neuro_fuzzy']
        gain=100*(1-b['distance_rmse_m']/a['distance_rmse_m'])
        lines.append(f"| {scenario} | {a['distance_rmse_m']:.4f} m | {b['distance_rmse_m']:.4f} m | {gain:.1f}% lower | {a['command_acceleration_rms']:.3f} m/s² | {b['command_acceleration_rms']:.3f} m/s² |")
    lines+=['','Positive percentages mean lower distance error; compare command acceleration to assess smoothness. These are development benchmarks, not independently held-out tests or evidence of general superiority. No camera detection or obstacle avoidance is implemented. Baseline tuning is preliminary.','', 'Full PID/fuzzy results and other metrics: `comparison.csv`. Console logs and raw traces accompany each run.']
    (out/'SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__': main()
