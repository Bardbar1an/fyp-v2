# V2 Webots results

Actual Webots R2025a physics: 48 seconds per run, seed 0. All baselines use the same sensor model. V2 controllers share motion estimation/feedforward; legacy retains the V1 controller.

| Scenario | V1 neuro RMSE | V2 neuro RMSE | Change | V1 accel RMS | V2 accel RMS |
|---|---:|---:|---:|---:|---:|
| straight | 0.2940 m | 0.0217 m | 92.6% lower | 0.058 m/s² | 0.102 m/s² |
| circle | 0.2599 m | 0.0232 m | 91.1% lower | 0.058 m/s² | 0.102 m/s² |
| figure_eight | 0.2052 m | 0.0350 m | 82.9% lower | 0.093 m/s² | 0.132 m/s² |
| stop_go | 0.2349 m | 0.0993 m | 57.7% lower | 0.168 m/s² | 0.255 m/s² |
| noisy_delay | 0.2101 m | 0.0580 m | 72.4% lower | 0.733 m/s² | 0.530 m/s² |
| target_loss | 0.2520 m | 0.1044 m | 58.6% lower | 0.363 m/s² | 0.416 m/s² |
| wheel_mismatch | 0.2224 m | 0.0369 m | 83.4% lower | 0.100 m/s² | 0.137 m/s² |
| outliers | 0.2096 m | 0.0580 m | 72.3% lower | 0.733 m/s² | 0.529 m/s² |
| speed_change | 0.2726 m | 0.0194 m | 92.9% lower | 0.057 m/s² | 0.097 m/s² |

Positive percentages mean lower distance error; compare command acceleration to assess smoothness. These are development benchmarks, not independently held-out tests or evidence of general superiority. No camera detection or obstacle avoidance is implemented. Baseline tuning is preliminary.

Full PID/fuzzy results and other metrics: `comparison.csv`. Console logs and raw traces accompany each run.