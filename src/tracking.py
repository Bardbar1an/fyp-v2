"""Timestamped sensor simulation and causal alpha-beta target tracking.

No future human samples or ground-truth target velocities enter the controller.
Robot localization is assumed known, including its pose at measurement time.
"""
from collections import deque
import math
import numpy as np
from .control import Config, Follower, Fuzzy, make_controller, wrap

CONTROLLERS = ('legacy_neuro_fuzzy', 'pid', 'fuzzy', 'neuro_fuzzy')


class TargetTracker:
    def __init__(self, alpha=0.30, beta=0.025, timeout=0.32):
        self.alpha, self.beta, self.timeout = alpha, beta, timeout
        self.position = None
        self.velocity = np.zeros(2)
        self.stamp = -math.inf
        self.rejected = 0

    def update(self, position, stamp):
        position = np.asarray(position, dtype=float)
        if position.shape != (2,) or not np.isfinite(position).all() or not math.isfinite(stamp) or stamp <= self.stamp:
            self.rejected += 1
            return False
        dt = stamp-self.stamp
        if self.position is None or dt > self.timeout:
            self.position, self.velocity, self.stamp = position.copy(), np.zeros(2), stamp
            return True
        prediction = self.position+self.velocity*dt
        innovation = position-prediction
        if np.linalg.norm(innovation) > 0.75+1.5*dt:
            self.rejected += 1
            return False
        self.position = prediction+self.alpha*innovation
        self.velocity += self.beta*innovation/dt
        speed = np.linalg.norm(self.velocity)
        if speed > 1.4:
            self.velocity *= 1.4/speed
        self.stamp = stamp
        return True

    def estimate(self, now):
        age = now-self.stamp
        if self.position is None or age < 0 or age > self.timeout:
            return None
        return self.position+self.velocity*age, self.velocity.copy(), age


class FeedforwardController:
    """Common motion compensation around any of the three feedback controllers."""
    def __init__(self, controller, cfg):
        self.controller, self.cfg = controller, cfg
        self.radial = self.transverse = 0.0
        self.distance = cfg.desired_distance
        self.filtered_command = np.zeros(2)
        # Remove fixed singleton bias at the reference equilibrium.
        self.offset = np.array(controller.step(0, 0, cfg.dt)) if isinstance(controller,Fuzzy) else np.zeros(2)

    def step(self, error, bearing, dt):
        feedback = np.array(self.controller.step(error,bearing,dt))-self.offset
        v = float(feedback[0]+self.radial)
        applied_v = np.clip(v,0,self.cfg.max_v)*max(0,math.cos(bearing))
        d = max(self.distance, self.cfg.stop_distance)
        w = float(feedback[1]+(self.transverse+applied_v*math.sin(bearing))/d)
        # Suppress estimator noise before the shared acceleration/wheel limits.
        blend = 1-math.exp(-dt/0.16)
        self.filtered_command += blend*(np.array([v,w])-self.filtered_command)
        return tuple(self.filtered_command)


class FollowingSystem:
    def __init__(self, name, model, seed=0, cfg=Config()):
        if name not in CONTROLLERS:
            raise ValueError('Unknown controller '+name)
        self.name, self.cfg = name,cfg
        self.legacy = name=='legacy_neuro_fuzzy'
        self.base_name = 'neuro_fuzzy' if self.legacy else name
        self.model = model
        self.tracker = TargetTracker(timeout=cfg.stale_timeout)
        self.rng = np.random.default_rng(seed)
        self.pending = deque()
        self.last = (math.nan,0.0,-math.inf)
        self.state = 'ACQUIRING'
        self.was_stale = True
        self._reset_controller()

    def _reset_controller(self):
        base = make_controller(self.base_name,self.model)
        self.compensation = FeedforwardController(base,self.cfg) if not self.legacy else None
        self.follower = Follower(self.compensation if self.compensation else base,self.cfg)

    def step(self, t, pose, human, scenario):
        pose,human = np.asarray(pose),np.asarray(human)
        delta = human-pose[:2]
        truth_distance = float(np.linalg.norm(delta))
        truth_bearing = wrap(math.atan2(delta[1],delta[0])-pose[2])
        noisy = scenario in ('noisy_delay','outliers')
        lost = scenario=='target_loss' and 12<=t%24<14
        if not lost:
            d = max(0,truth_distance+self.rng.normal(0,0.06 if noisy else 0))
            b = wrap(truth_bearing+self.rng.normal(0,0.03 if noisy else 0))
            # Occasional corrupt returns; clean data is not passed to the tracker.
            if scenario=='outliers' and int(round(t/self.cfg.dt))%97==0:
                d += 2.0
            measured = pose[:2]+d*np.array([math.cos(pose[2]+b),math.sin(pose[2]+b)])
            self.pending.append((t+(0.128 if noisy else 0),d,b,t,measured))
        while self.pending and self.pending[0][0]<=t+1e-9:
            _,d,b,stamp,point = self.pending.popleft()
            self.last = (d,b,stamp)
            self.tracker.update(point,stamp)
        estimate = self.tracker.estimate(t)
        age = t-self.last[2] if self.legacy else t-self.tracker.stamp
        if self.legacy:
            d,b,_ = self.last
            command = self.follower.step(d,b,age)
        elif estimate is None:
            command = self.follower.step(math.nan,0,age)
            d,b = math.nan,0
        else:
            position,velocity,age = estimate
            direction = position-pose[:2]
            d = float(np.linalg.norm(direction))
            b = wrap(math.atan2(direction[1],direction[0])-pose[2])
            if self.was_stale:
                self._reset_controller()
            unit = direction/max(d,1e-9)
            self.compensation.radial = float(velocity@unit)
            self.compensation.transverse = float(velocity@np.array([-unit[1],unit[0]]))
            self.compensation.distance = d
            command = self.follower.step(d,b,age)
        stale = not math.isfinite(d) or age>self.cfg.stale_timeout
        self.was_stale = stale
        self.state = 'LOST — STOP' if stale else 'CLOSE — STOP' if d<=self.cfg.stop_distance else 'ALIGNING' if abs(b)>math.pi/2 else 'FOLLOWING'
        velocity = self.tracker.velocity
        info = dict(distance=truth_distance,bearing=truth_bearing,error=truth_distance-self.cfg.desired_distance,
                    stale=int(stale),close=int(truth_distance<self.cfg.stop_distance),state=self.state,
                    estimate_distance=float(d) if math.isfinite(d) else None,
                    estimate_speed=float(np.linalg.norm(velocity)),rejected_measurements=self.tracker.rejected)
        return command,info
