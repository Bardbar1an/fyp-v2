"""Run paired-seed evaluations. Results are 2D, not Webots physics measurements."""
import argparse
import csv
import json
from pathlib import Path
from dataclasses import asdict
import numpy as np
from src.control import Config
from src.tracking import CONTROLLERS
from src.simulation import SCENARIOS, run, metrics


def write_csv(path, rows):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--duration', type=float, default=48)
    p.add_argument('--model', default='models/neuro_fuzzy.json')
    p.add_argument('--output', default='results')
    a = p.parse_args()
    if a.seeds < 1 or a.duration <= 0:
        p.error('seeds and duration must be positive')
    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    summaries, playback = [], {}
    for scenario in SCENARIOS:
        playback[scenario] = {}
        for controller in CONTROLLERS:
            for seed in range(a.seeds):
                rows = run(controller, scenario, seed, a.model, a.duration)
                summaries.append(dict(scenario=scenario, controller=controller, seed=seed, **metrics(rows)))
                write_csv(out/f'{scenario}_{controller}_{seed}.csv', rows)
                if seed == 0:
                    playback[scenario][controller] = rows[::5]
        print('Evaluated', scenario)
    write_csv(out/'metrics.csv', summaries)
    aggregate = []
    for scenario in SCENARIOS:
        for controller in CONTROLLERS:
            group = [s for s in summaries if s['scenario']==scenario and s['controller']==controller]
            r = dict(scenario=scenario, controller=controller, seeds=a.seeds)
            for key in list(group[0])[3:]:
                values = [s[key] for s in group]
                r[key+'_mean'] = float(np.mean(values))
                r[key+'_std'] = float(np.std(values, ddof=1)) if a.seeds>1 else 0.0
            aggregate.append(r)
    write_csv(out/'aggregate.csv', aggregate)
    metadata = dict(simulator='2D differential-drive kinematics with 0.15 s first-order wheel lag', config=asdict(Config()), duration=a.duration, seeds=list(range(a.seeds)), model=json.loads(Path(a.model).read_text()), limitations=['No camera perception, obstacles, contact physics or stability proof', 'Deterministic scenarios repeat across seeds; only noisy_delay and outliers have stochastic variation', 'Synthetic expert imitation; PID and fuzzy gains are initial engineering choices, not equally optimized baselines'])
    (out/'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    template = Path('report_template.html').read_text(encoding='utf-8')
    (out/'report.html').write_text(template.replace('__DATA__', json.dumps(dict(playback=playback, metrics=aggregate))), encoding='utf-8')
    print('Open', out/'report.html')


if __name__ == '__main__':
    main()
