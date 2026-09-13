"""SI units; robot forward is +x, yaw is positive counterclockwise."""
from dataclasses import dataclass
import json
import math
from pathlib import Path
import numpy as np


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


@dataclass(frozen=True)
class Config:
    dt: float = 0.032
    desired_distance: float = 1.5
    wheel_radius: float = 0.08
    axle_length: float = 0.36
    max_wheel_speed: float = 14.0
    max_v: float = 0.9
    max_w: float = 1.8
    max_accel: float = 0.8
    max_alpha: float = 3.0
    stop_distance: float = 0.65
    stale_timeout: float = 0.32


def wheel_speeds(v, w, cfg=Config()):
    left = (v - w * cfg.axle_length / 2) / cfg.wheel_radius
    right = (v + w * cfg.axle_length / 2) / cfg.wheel_radius
    scale = max(1.0, abs(left) / cfg.max_wheel_speed, abs(right) / cfg.max_wheel_speed)
    return left / scale, right / scale


def body_speeds(left, right, cfg=Config()):
    return cfg.wheel_radius * (left + right) / 2, cfg.wheel_radius * (right - left) / cfg.axle_length


class PID:
    """Parallel distance/bearing PID with bounded integral and filtered derivative."""
    def __init__(self):
        self.integral = np.zeros(2)
        self.previous = None
        self.derivative = np.zeros(2)

    def step(self, error, bearing, dt):
        x = np.array([error, bearing])
        if self.previous is not None:
            difference = x - self.previous
            difference[1] = wrap(difference[1])
            self.derivative = 0.85 * self.derivative + 0.15 * difference / dt
        self.previous = x
        self.integral = np.clip(self.integral + x * dt, -0.5, 0.5)
        v, w = np.array([0.85, 2.1]) * x + np.array([0.14, 0.04]) * self.integral + np.array([0.06, 0.08]) * self.derivative
        return float(v), float(w)


class Fuzzy:
    """25-rule zero-order Sugeno network; product Gaussian firing and weighted sum.

    Inputs are distance error / 2 m and bearing / pi, clipped to [-1, 1].
    Fixed rule consequents are the plain fuzzy baseline. Training adjusts the
    Gaussian premises and rule consequents in exactly this network.
    """
    def __init__(self):
        self.centers = np.array([[a, b] for a in np.linspace(-1, 1, 5) for b in np.linspace(-1, 1, 5)])
        self.log_widths = np.full((25, 2), math.log(0.30))
        self.consequents = np.array([[np.clip(1.6*a, -0.3, 0.9), np.clip(5*b, -1.8, 1.8)] for a, b in self.centers])

    def features(self, inputs):
        x = np.clip(np.asarray(inputs, dtype=float) / [2.0, math.pi], -1, 1)
        delta = x[:, None, :] - self.centers[None, :, :]
        width = np.exp(self.log_widths)
        logits = -0.5 * np.sum((delta / width) ** 2, axis=2)
        exp = np.exp(logits - logits.max(axis=1, keepdims=True))
        weights = exp / exp.sum(axis=1, keepdims=True)
        return weights, delta, width

    def predict(self, inputs):
        return self.features(inputs)[0] @ self.consequents

    def step(self, error, bearing, dt):
        return tuple(self.predict([[error, bearing]])[0])

    def save(self, path, metadata):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(dict(schema=1, centers=self.centers.tolist(), log_widths=self.log_widths.tolist(), consequents=self.consequents.tolist(), metadata=metadata), indent=2), encoding='utf-8')

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if data.get('schema') != 1:
            raise ValueError('Unsupported model schema')
        obj = cls()
        for key in ('centers', 'log_widths', 'consequents'):
            value = np.asarray(data[key], dtype=float)
            if value.shape != (25, 2) or not np.isfinite(value).all():
                raise ValueError('Invalid model array: ' + key)
            setattr(obj, key, value)
        return obj


def make_controller(name, model):
    if name == 'pid':
        return PID()
    if name == 'fuzzy':
        return Fuzzy()
    if name == 'neuro_fuzzy':
        return Fuzzy.load(model)
    raise ValueError('Unknown controller ' + name)


class Follower:
    """Identical command envelope for every controller, independent of training."""
    def __init__(self, controller, cfg=Config()):
        self.controller, self.cfg = controller, cfg
        self.previous = np.zeros(2)

    def step(self, distance, bearing, age=0.0):
        c = self.cfg
        if not all(math.isfinite(x) for x in (distance, bearing, age)) or distance < 0 or age > c.stale_timeout or distance <= c.stop_distance:
            self.previous[:] = 0
            if isinstance(self.controller, PID):
                self.controller = PID()
            return 0.0, 0.0
        v, w = self.controller.step(distance - c.desired_distance, bearing, c.dt)
        # Forward-only follower: turn in place when target is behind.
        v = np.clip(v, 0, c.max_v) * max(0.0, math.cos(bearing))
        desired = np.array([v, np.clip(w, -c.max_w, c.max_w)])
        limits = np.array([c.max_accel, c.max_alpha]) * c.dt
        command = self.previous + np.clip(desired - self.previous, -limits, limits)
        if abs(bearing) >= math.pi / 2:
            command[0] = 0.0
        self.previous = np.array(body_speeds(*wheel_speeds(*command, c), c))
        return tuple(self.previous)
