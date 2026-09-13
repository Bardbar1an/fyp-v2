# Proposed FYP evaluation plan

## Bounded scope

Maintain a nominal 1.5 m radial separation from one scripted human using a differential-drive robot on level ground. Compare PID, fixed fuzzy and trained neuro-fuzzy controllers under identical relative-position measurements and command constraints. The current objective is distance/bearing following, not guaranteed placement behind the person's heading: a robot can cut corners while satisfying radial distance. Heading-relative following can be a later extension.

## Research questions

1. After fair tuning, which controller offers the best separation-error versus command-smoothness trade-off?
2. How does performance change with distance/bearing noise, latency, temporary target loss and wheel asymmetry?
3. Do conclusions from the 2D plant hold in Webots contact/motor physics?
4. Does learning improve over the untrained fuzzy network on held-out conditions, and how much of the improvement is explained by the teacher's control law?

## Current prototype parameters

| Item | Current value |
|---|---|
| Desired radial distance | 1.5 m |
| Close-distance command stop | 0.65 m; engineering threshold, not a validated safety standard |
| Sample time | 32 ms |
| Body command bounds | 0–0.9 m/s; ±1.8 rad/s |
| Wheel radius / track width | 0.08 m / 0.36 m |
| Forward / angular command acceleration limit | 0.8 m/s² / 3 rad/s², with immediate stop/behind overrides |
| Wheel lag in 2D | 0.15 s first-order lag |
| Noisy scenario | Independent Gaussian distance SD 0.06 m and bearing SD 0.03 rad; 0.128 s delay |
| Loss scenario | Measurement blackout on [12,14) s of every 24 s cycle; command stops when sample age exceeds 0.32 s |
| Wheel mismatch | Left-wheel command multiplied by 0.85 |
| Runtime / repeats | 48 s per run; five seeds; 105 runs total |

Values are prototype choices, not paper-derived calibrated sensor specifications. Time zero places the human at (1.5,0) and robot at (0,0,0). Straight/stop-go speed is 0.45 m/s. Circle radius is 3 m at 0.15 rad/s. Figure-eight coordinates are x=1.5+3sin(0.14t), y=1.6sin(0.28t). Impairment cases use the figure-eight path.

## Fair-comparison protocol for the final report

The code currently uses initial baseline gains and an offline-trained neuro-fuzzy model. It does not yet implement an equal-budget tuning study.

1. Define training, tuning and final-test conditions before optimization. Vary path geometry, speeds and initial headings; do not tune repeatedly on the final benchmark.
2. Give PID and fuzzy scaling/membership parameters the same number of validation evaluations as the learned controller's hyperparameter search. Publish parameter ranges, seeds and selection criteria. Include a nonlinear proportional/expert baseline to control for teacher design.
3. Train neuro-fuzzy parameters only on training data. Keep validation checkpoint selection distinct from final evaluation. Log input distribution, output units, training seed and loss.
4. Freeze every controller. Apply identical noise samples, trajectories, bounds and stop logic. Use matched random seeds for paired comparisons.
5. Use genuinely different randomized conditions for uncertainty estimates. Repeating deterministic paths with new unused seeds does not produce independent trials. In the current code, only `noisy_delay` changes with seed.
6. Report all scenarios, including cases where neuro-fuzzy is worse. Report mean ± SD, paired differences, and confidence intervals when the independent trial count is sufficient. Avoid significance tests on repeated copies of deterministic traces.
7. Repeat selected tests in Webots. Record Webots/Python version, robot geometry/mass/friction, timestep and motor settings. Do not label 2D results as Webots results.

## Metrics and plots

Primary: distance RMSE and MAE, signed separation-error trace and maximum absolute error. Secondary: bearing error, fraction of time within ±0.25 m, minimum separation, time below close threshold, velocity and angular velocity, and command acceleration. Show top-down human/robot trajectories for every scenario.

When adding obstacles, log actual contacts separately from threshold violations. When adding visual sensing, log detection availability, target-identity switches and position-estimation error. Define loss recovery time explicitly, for example time from first valid post-loss observation to continuously meeting an error band for two seconds. It is not computed by this prototype yet.

The current effort metric integrates v²+omega² and is only a dimensionally mixed command proxy. Do not label it energy efficiency. Use motor torque × angular velocity integration if physical energy becomes a research objective.

## Ablations worth doing

- Untrained versus trained fuzzy network: already available.
- Consequent-only versus centers/widths/consequents training: proposed extension.
- Synthetic teacher directly versus its learned approximation: proposed extension.
- Ideal sensing versus the same noise/delay/loss conditions: partially available through base/impairment scenarios.
- Shared stopping/limiting layer held constant across all controllers: already implemented.

## Development sequence

1. Explain and validate the existing kinematics, fuzzy inference and training gradients.
2. Run the Webots world, verify forward/turn signs, ground contact and logged units.
3. Add equal-budget tuning and additional held-out human paths/speeds.
4. Add membership-function plots, paired statistics and loss-recovery metrics.
5. If schedule permits, add RGB-D person detection/selection and an identical obstacle layer for all controllers.
6. Write the dissertation around your own measured results and their limitations.

The appropriate initial claim is: **a reproducible prototype for comparing classical, fuzzy and learned fuzzy human-following control**. A claim of improved robustness or safety requires the later evidence above.
