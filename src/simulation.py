"""Deterministic planar kinematics with actuator lag and optional sensor impairment."""
from .tracking import FollowingSystem
import math
import numpy as np
from .control import Config, Follower, make_controller, wrap, wheel_speeds, body_speeds

SCENARIOS = ('straight', 'circle', 'figure_eight', 'stop_go', 'noisy_delay', 'target_loss', 'wheel_mismatch', 'outliers', 'speed_change')


def human_position(t, scenario):
    if scenario == 'straight':
        return np.array([1.5 + 0.45*t, 0.0])
    if scenario == 'speed_change':
        return np.array([1.5+0.25*t+0.30*max(0,t-12)-0.2*max(0,t-28), 0.5*math.sin(0.12*t)])
    if scenario == 'stop_go':
        moving_time = (t // 12)*8 + min(t % 12, 8)
        return np.array([1.5 + 0.45*moving_time, 0.0])
    if scenario == 'circle':
        return np.array([1.5 + 3*math.sin(0.15*t), 3*(1-math.cos(0.15*t))])
    return np.array([1.5 + 3*math.sin(0.14*t), 1.6*math.sin(0.28*t)])


def run(name, scenario, seed, model, duration=48.0, cfg=Config()):
    if scenario not in SCENARIOS or duration <= 0:
        raise ValueError('Invalid scenario or duration')
    system = FollowingSystem(name,model,seed,cfg)
    pose, actual = np.zeros(3), np.zeros(2)
    rows = []
    for step in range(round(duration/cfg.dt)):
        t = step*cfg.dt
        human = human_position(t, scenario)
        command,info = system.step(t,pose,human,scenario)
        target_wheels = np.array(wheel_speeds(*command, cfg))
        if scenario == 'wheel_mismatch':
            target_wheels *= [0.85, 1.0]
        actual += (1-math.exp(-cfg.dt/0.15))*(target_wheels-actual)
        v, w = body_speeds(*actual, cfg)
        rows.append(dict(t=t, x=float(pose[0]), y=float(pose[1]), yaw=float(pose[2]), hx=float(human[0]), hy=float(human[1]), v=float(command[0]), w=float(command[1]), actual_v=v, actual_w=w, **info))
        # Midpoint integration of nonholonomic differential-drive model.
        pose[:2] += v*cfg.dt*np.array([math.cos(pose[2]+w*cfg.dt/2), math.sin(pose[2]+w*cfg.dt/2)])
        pose[2] = wrap(pose[2]+w*cfg.dt)
    return rows


def metrics(rows, cfg=Config()):
    e = np.array([r['error'] for r in rows])
    v = np.array([r['v'] for r in rows])
    w = np.array([r['w'] for r in rows])
    return dict(distance_rmse_m=float(np.sqrt(np.mean(e**2))), distance_mae_m=float(np.mean(abs(e))),
                max_abs_error_m=float(np.max(abs(e))), bearing_rmse_rad=float(np.sqrt(np.mean([r['bearing']**2 for r in rows]))),
                minimum_distance_m=min(r['distance'] for r in rows),
                within_025m_fraction=float(np.mean(abs(e)<=0.25)),
                close_duration_s=sum(r['close'] for r in rows)*cfg.dt,
                stale_duration_s=sum(r['stale'] for r in rows)*cfg.dt,
                command_acceleration_rms=float(np.sqrt(np.mean((np.diff(v)/cfg.dt)**2))) if len(v)>1 else 0.0,
                command_angular_acceleration_rms=float(np.sqrt(np.mean((np.diff(w)/cfg.dt)**2))) if len(w)>1 else 0.0,
                command_effort_proxy=float(np.sum(v*v+w*w)*cfg.dt))
