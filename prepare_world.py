"""Produce a Webots world with matched human/controller scenario arguments."""
import argparse
from pathlib import Path
from src.simulation import SCENARIOS
from src.tracking import CONTROLLERS

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--controller',choices=CONTROLLERS,default='neuro_fuzzy')
p.add_argument('--scenario',choices=SCENARIOS,default='figure_eight')
p.add_argument('--duration',type=float,default=48)
a=p.parse_args()
if a.duration<=0: p.error('duration must be positive')
world=Path('worlds/human_following.wbt').read_text()
world=world.replace('controllerArgs [ "figure_eight" ]',f'controllerArgs [ "{a.scenario}" ]')
world=world.replace('controllerArgs [ "neuro_fuzzy" "figure_eight" "48" ]',f'controllerArgs [ "{a.controller}" "{a.scenario}" "{a.duration}" ]')
path=Path(f'worlds/{a.scenario}_{a.controller}.wbt')
path.write_text(world,encoding='utf-8')
print('Open in Webots:',path.resolve())
