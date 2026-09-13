"""Animated, kinematically scripted human target; this is not a gait dynamics model."""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from controller import Supervisor
from src.simulation import human_position, SCENARIOS

robot = Supervisor()
dt = int(robot.getBasicTimeStep())
self_node = robot.getSelf()
scenario = sys.argv[1] if len(sys.argv)>1 else 'figure_eight'
if scenario not in SCENARIOS:
    raise ValueError('Unknown scenario: '+scenario)
translation = self_node.getField('translation')
rotation = self_node.getField('rotation')
joints = {name:self_node.getField(name) for name in ('leftLegAngle','rightLegAngle','leftArmAngle','rightArmAngle','leftLowerLegAngle','rightLowerLegAngle')}
phase = 0.0
while robot.step(dt) != -1:
    t = robot.getTime()
    p, ahead = human_position(t, scenario), human_position(t+dt/1000, scenario)
    speed = math.hypot(*(ahead-p))/(dt/1000)
    phase += speed*(dt/1000)*2*math.pi/1.1
    swing = 0.45*math.sin(phase) if speed>0.01 else 0
    translation.setSFVec3f([float(p[0]),float(p[1]),1.27])
    if speed>0.01:
        rotation.setSFRotation([0,0,1,math.atan2(ahead[1]-p[1],ahead[0]-p[0])])
    angles = [swing,-swing,-0.7*swing,0.7*swing,max(0,-swing),max(0,swing)]
    for field, angle in zip(joints.values(), angles):
        if field is not None:
            field.setSFFloat(float(angle))
