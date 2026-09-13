# FYP V2 — predictive human following in Webots

An improved version of the original FYP prototype, saved separately in **B:\vs code project\fyp_v2**. The original `fyp` folder is preserved.

## Open the 3D demonstration

**Double-click `START_3D.cmd`.** Webots opens the default neuro-fuzzy figure-eight scene in real time. The view follows the robot and human, with a ground grid and live distance, speed, steering and state labels. The world pauses after 48 simulated seconds; reload the world to repeat it.

The launcher uses the Webots installation already created at `C:\Users\User\Documents\ChatGPT\fyp\tools\Webots`. It is shared with V1, rather than duplicated into this folder. Internet access may be needed to fetch the official Pedestrian asset on first use.

Other runs from PowerShell:

```powershell
Set-Location -LiteralPath 'B:\vs code project\fyp_v2'
.\run_webots.ps1 -Controller neuro_fuzzy -Scenario stop_go
.\run_webots.ps1 -Controller pid -Scenario noisy_delay
.\run_webots.ps1 -Batch -Video
```

If local PowerShell policy blocks scripts, `START_3D.cmd` provides the default interactive demo without changing policy. The Python scripts can also be run directly.

## What changed

| V1 limitation | V2 improvement |
|---|---|
| Reacts to the distance error after the human has moved | Estimates human velocity from past observations and adds velocity feedforward |
| Uses delayed/noisy samples directly | Timestamp-aware alpha-beta position/velocity tracker with bounded prediction |
| Corrupt position samples directly disturb following | Innovation gate rejects large outliers; target speed estimate is bounded |
| No explicit reacquisition reset | Stops after 0.32 s without an accepted sample; resets velocity/controller state on reacquisition |
| Velocity feedforward can amplify measurement noise | 0.16 s command smoothing before the existing acceleration and wheel limits |
| Sparse static camera view | Moving camera, one-metre floor grid, live telemetry and 720p recordings |
| Seven test conditions | Nine conditions, adding corrupt sensor returns and changing human speed |
| Only one 3D path verified | Automated nine-scenario, four-controller Webots benchmark, with trace completeness checks |

V2 retains the original trained 25-rule Sugeno network and its training provenance. It improves the surrounding estimation/control architecture; it does not pretend that the neural network was newly trained or that feedforward is itself neuro-fuzzy learning. Fuzzy and PID receive the same estimator and motion compensation. `legacy_neuro_fuzzy` is the original V1 control configuration, retained as an ablation.

## Results and artifacts

- `results/webots/SUMMARY.md`: measured V1 versus V2 accuracy and smoothness from Webots.
- `results/webots/comparison.csv`: all four configurations across nine 3D scenarios.
- `results/webots/figure_eight_neuro_fuzzy_3d.mp4`: recorded V2 demonstration.
- `results/webots/figure_eight_neuro_fuzzy_3d.png`: snapshot of the running 3D scene.
- `results/report.html`: offline animated **2D** experiment report, with a V1/V2 selector.
- `results/aggregate.csv`: 2D means and sample SD across five seeds.
- `research/IMPROVEMENTS.md`: controller equations, design choices and limitations.

The 2D evaluation contains 180 runs (nine scenarios × four configurations × five seeds). The Webots benchmark contains 36 runs with seed 0, each lasting 48 simulated seconds. Noise is stochastic in `noisy_delay` and `outliers`; the remaining conditions are deterministic, so repeated seeds do not create independent evidence there.

## Reproduce the experiments

Requires Python 3.10+ with NumPy. Tested with Python 3.11, NumPy 1.26.4 and Webots R2025a.

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python evaluate.py --seeds 5
python benchmark_webots.py
```

For a different Webots installation, set `FYP_WEBOTS` before running the Python benchmark. Update `START_3D.cmd` or the executable candidates in `run_webots.ps1` for interactive use. Results with the same scenario/controller name are overwritten on rerun; retain a copy when comparing revisions. Webots supplies its `controller` Python module; do not install an unrelated PyPI package with that name.

## Scope and limits

Human sensing is a simulated range/bearing measurement, generated from Supervisor position. Robot localization is assumed known. The controller receives no future human positions or true target velocities, but **there is no image-based person detector, identity tracker or obstacle avoidance**. Rendered occlusion does not cause sensor loss; blackout intervals are scripted. Human walking is an animated kinematic model. Support casters use low-friction sphere contacts.

The objective is radial separation with angular alignment, not a guaranteed position behind the human's heading. The robot can cut corners. It moves forward or turns in place and cannot reverse to recover an undershoot while the human is stationary. The 1.5 m target and 0.65 m close threshold are engineering settings, not validated social-comfort or safety standards. Command stops have a physical braking transient.

Lower RMSE does not imply smoother motion, safer behavior or general superiority. The saved summaries show command acceleration too. These scenarios were used during development, so they are not independent final-test evidence. PID/fuzzy gains still need equal-budget tuning, and a future final study should include unseen paths/speeds and a direct nonlinear-expert baseline.

The copied related-work notes provide context. `research/WEBOTS_VALIDATION.md` describes the historical V1 run, not V2 performance; use the current `results/webots/SUMMARY.md` for V2 measurements.
