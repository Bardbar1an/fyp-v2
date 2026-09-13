import math
from pathlib import Path
import tempfile
import unittest
import numpy as np
from src.control import Config, Follower, Fuzzy, PID, body_speeds, wheel_speeds, wrap
from src.simulation import run


class ControlTests(unittest.TestCase):
    def test_kinematic_sign_and_round_trip(self):
        for v,w in ((0.4,0),(0,1),(0.4,-0.8)):
            left,right=wheel_speeds(v,w)
            np.testing.assert_allclose(body_speeds(left,right),(v,w),atol=1e-12)
        self.assertLess(*wheel_speeds(0,1))
        self.assertAlmostEqual(wrap(2*math.pi+0.2),0.2)

    def test_wheel_saturation_preserves_curvature(self):
        left,right=wheel_speeds(2,3)
        self.assertLessEqual(max(abs(left),abs(right)),14)
        v,w=body_speeds(left,right)
        self.assertAlmostEqual(w/v,1.5)

    def test_invalid_stale_close_and_behind(self):
        for controller in (PID(),Fuzzy()):
            f=Follower(controller)
            for _ in range(40): f.step(3,0)
            self.assertEqual(f.step(3,0,0.5),(0,0))
            self.assertEqual(f.step(float('nan'),0),(0,0))
            self.assertEqual(f.step(0.6,0),(0,0))
            self.assertEqual(f.step(3,math.pi)[0],0)

    def test_fuzzy_partition_and_serialization(self):
        model=Fuzzy()
        x=np.array([[0,0],[-100,-100],[100,100],[1,0.3]])
        weights,_,_=model.features(x)
        np.testing.assert_allclose(weights.sum(axis=1),1)
        self.assertTrue(np.isfinite(model.predict(x)).all())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'model.json'; model.save(p,{})
            np.testing.assert_allclose(Fuzzy.load(p).predict(x),model.predict(x))

    def test_turn_direction_and_command_limits(self):
        for c in (PID(),Fuzzy(),Fuzzy.load('models/neuro_fuzzy.json')):
            f=Follower(c)
            for _ in range(50):
                v,w=f.step(4,0.5)
                self.assertGreater(w,0)
                self.assertTrue(0<=v<=Config().max_v)
                self.assertLessEqual(abs(w),Config().max_w)

    def test_reproducible_noise_and_lost_target_stop(self):
        args=('neuro_fuzzy','noisy_delay',3,'models/neuro_fuzzy.json')
        a,b=run(*args,duration=2),run(*args,duration=2)
        self.assertEqual(a,b)
        rows=run('pid','target_loss',0,'models/neuro_fuzzy.json',duration=15)
        stale=[r for r in rows if r['stale']]
        self.assertTrue(stale)
        self.assertTrue(all(r['v']==0 and r['w']==0 for r in stale))

    def test_training_changes_premises_and_improves_fit(self):
        import json
        trained=Fuzzy.load('models/neuro_fuzzy.json')
        self.assertFalse(np.allclose(trained.centers,Fuzzy().centers))
        m=json.loads(Path('models/neuro_fuzzy.json').read_text())['metadata']
        self.assertLess(m['validation_mse'],m['initial_validation_mse'])


if __name__=='__main__': unittest.main()
