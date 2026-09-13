import unittest
import numpy as np
from src.tracking import TargetTracker, FollowingSystem
from src.simulation import run,metrics


class TrackingTests(unittest.TestCase):
    def test_constant_velocity_prediction(self):
        tracker=TargetTracker()
        for t in np.arange(0,6,0.032):
            tracker.update([0.4*t,-0.2*t],float(t))
        position,velocity,age=tracker.estimate(6.05)
        np.testing.assert_allclose(velocity,[0.4,-0.2],atol=0.005)
        np.testing.assert_allclose(position,[0.4*6.05,-0.2*6.05],atol=0.005)

    def test_outliers_and_old_packets_do_not_move_track(self):
        tracker=TargetTracker()
        tracker.update([1.5,0],0.0)
        self.assertFalse(tracker.update([10,10],0.032))
        self.assertFalse(tracker.update([1,1],-1.0))
        self.assertFalse(tracker.update([np.nan,0],0.032))
        np.testing.assert_allclose(tracker.position,[1.5,0])
        self.assertEqual(tracker.rejected,3)

    def test_stale_prediction_expires_and_reacquisition_resets_velocity(self):
        tracker=TargetTracker()
        tracker.update([1.5,0],0.0)
        self.assertIsNone(tracker.estimate(0.33))
        self.assertTrue(tracker.update([3,1],0.5))
        np.testing.assert_allclose(tracker.velocity,[0,0])

    def test_all_v2_controllers_stop_during_measurement_loss(self):
        for name in ('pid','fuzzy','neuro_fuzzy'):
            rows=run(name,'target_loss',0,'models/neuro_fuzzy.json',duration=15)
            stale=[r for r in rows if r['stale']]
            self.assertTrue(stale)
            self.assertTrue(all(r['v']==0 and r['w']==0 for r in stale))
            self.assertFalse(rows[-1]['stale'])

    def test_speed_feedforward_reduces_straight_following_lag(self):
        old=metrics(run('legacy_neuro_fuzzy','straight',0,'models/neuro_fuzzy.json',duration=12))
        new=metrics(run('neuro_fuzzy','straight',0,'models/neuro_fuzzy.json',duration=12))
        self.assertLess(new['distance_rmse_m'],0.5*old['distance_rmse_m'])

    def test_sensor_noise_is_reproducible(self):
        a=run('neuro_fuzzy','noisy_delay',4,'models/neuro_fuzzy.json',duration=1)
        b=run('neuro_fuzzy','noisy_delay',4,'models/neuro_fuzzy.json',duration=1)
        self.assertEqual(a,b)


if __name__=='__main__': unittest.main()
