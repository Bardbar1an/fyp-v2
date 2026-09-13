"""Webots physics adapter. Supervisor pose is an explicit idealized sensing input."""
from collections import deque
import csv
import json
import math
import os
from pathlib import Path
import sys
import time
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from controller import Supervisor
from src.control import Config, Follower, make_controller, wheel_speeds, wrap
from src.simulation import metrics, SCENARIOS
from src.tracking import FollowingSystem

robot = Supervisor()
dt = int(robot.getBasicTimeStep())
cfg = Config(dt=dt/1000)
name = sys.argv[1] if len(sys.argv)>1 else 'neuro_fuzzy'
scenario = sys.argv[2] if len(sys.argv)>2 else 'figure_eight'
duration = float(sys.argv[3]) if len(sys.argv)>3 else 48.0
if scenario not in SCENARIOS or duration <= 0:
    raise ValueError('Invalid scenario or duration')
system = FollowingSystem(name, ROOT/'models/neuro_fuzzy.json', int(os.environ.get('FYP_SEED','0')), cfg)
human, me = robot.getFromDef('HUMAN'), robot.getSelf()
if human is None:
    raise RuntimeError('World must contain DEF HUMAN')
motors = [robot.getDevice(n) for n in ('left wheel motor','right wheel motor')]
for motor in motors:
    motor.setPosition(float('inf'))
    motor.setVelocity(0)
rows = []
viewpoint = robot.getFromDef('VIEW')
view_position = viewpoint.getField('position') if viewpoint else None
batch = os.environ.get('FYP_BATCH') == '1'
capture = os.environ.get('FYP_CAPTURE') == '1'
capture_dir = ROOT/'results'/'webots'
capture_dir.mkdir(parents=True,exist_ok=True)
captured = False
record_video = os.environ.get('FYP_VIDEO') == '1'
if record_video:
    robot.movieStartRecording(str(capture_dir/f'{scenario}_{name}_3d.mp4'), 1280, 720, 0, 45, 1, False)
print(f'FYP V2 {name}: supervisor-position sensing; scenario {scenario}; {duration}s')
try:
    while robot.step(dt) != -1:
        t = robot.getTime()
        if capture and not captured and t >= 12:
            robot.exportImage(str(capture_dir/f'{scenario}_{name}_3d.png'), 95)
            captured = True
        if t>duration:
            break
        p, h, orientation = me.getPosition(), human.getPosition(), me.getOrientation()
        yaw = math.atan2(orientation[3],orientation[0])
        (v,w),info = system.step(t,[p[0],p[1],yaw],[h[0],h[1]],scenario)
        left,right = wheel_speeds(v,w,cfg)
        if scenario=='wheel_mismatch':
            left *= 0.85
        motors[0].setVelocity(left)
        motors[1].setVelocity(right)
        velocity = me.getVelocity()
        rows.append(dict(t=t,x=p[0],y=p[1],yaw=yaw,hx=h[0],hy=h[1],v=v,w=w,actual_v=velocity[0]*math.cos(yaw)+velocity[1]*math.sin(yaw),actual_w=velocity[5],**info))
        if view_position:
            # Presentation only: camera follows the midpoint; it does not feed control.
            mid = [(p[0]+h[0])/2,(p[1]+h[1])/2]
            view_position.setSFVec3f([mid[0]-5.5,mid[1]-5.5,6.2])
        if len(rows)%4==0:
            robot.setLabel(0,'HUMAN FOLLOWING  /  V2',0.025,0.025,0.07,0x54e6bf)
            robot.setLabel(1,f'{name.upper()}  |  {scenario}  |  {t:05.1f} s',0.025,0.095,0.045,0xffffff)
            robot.setLabel(2,f'Distance {info["distance"]:.2f} m  /  target 1.50 m',0.025,0.15,0.045,0xffffff)
            robot.setLabel(3,f'v {v:.2f} m/s   |   yaw rate {w:.2f} rad/s',0.025,0.205,0.042,0xc5d8e3)
            robot.setLabel(4,system.state.replace('—','-'),0.025,0.26,0.042,0xffcb77)
            robot.setLabel(5,'Physics simulation  |  Position sensor model',0.025,0.93,0.035,0xc5d8e3)

finally:
    for motor in motors:
        motor.setVelocity(0)
    if rows:
        out = ROOT/'results'/'webots'
        out.mkdir(parents=True,exist_ok=True)
        path = out/f'{scenario}_{name}.csv'
        with path.open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        (out/f'{scenario}_{name}_metrics.json').write_text(json.dumps(metrics(rows,cfg),indent=2),encoding='utf-8')
        print('Saved Webots physics log:',path)
if batch:
    if record_video:
        robot.movieStopRecording()
        deadline = time.monotonic()+45
        while not robot.movieIsReady() and not robot.movieFailed() and time.monotonic()<deadline:
            if robot.step(dt) == -1:
                break
        print('Video ready:', robot.movieIsReady(), 'failed:', robot.movieFailed())
    robot.simulationQuit(0)
# Pause the whole interactive demonstration at completion.
if not batch:
    robot.setLabel(4, 'RUN COMPLETE - reload world to repeat', 0.025, 0.26, 0.042, 0xffcb77)
    robot.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
while robot.step(dt) != -1:
    pass
