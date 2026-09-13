# V2 control architecture

## Measurement and estimation

The sensor adapter samples relative range and bearing, with the robot pose at the acquisition timestamp. A delayed sample is transformed into world coordinates using that historical pose. It is not transformed using the newer robot pose when the sample arrives. Noise is added before this transformation. The estimator then receives only this noisy reconstructed point and its timestamp.

For successive accepted measurement timestamps separated by dt:

```
p_pred = p_est + v_est * dt
innovation = measured_position - p_pred
p_est = p_pred + 0.30 * innovation
v_est = v_est + 0.025 * innovation / dt
```

The velocity magnitude is bounded to 1.4 m/s. An innovation larger than `0.75 + 1.5*dt` metres is rejected. Current position is predicted from the most recent accepted timestamp, only while sample age is at most 0.32 s. A longer gap stops commands and the next observation resets position and velocity. No target future state is read. Known robot localization remains a substantial simulation assumption.

The first observation and first post-loss observation cannot be reliably rejected based on motion history alone. V2 accepts them as initialization. The outlier scenario deliberately includes a corrupt initial sample; later returns allow recovery. A robust real perception system would need confidence and identity checks.

## Feedback plus motion feedforward

Let d be estimated separation, b the relative bearing, `u` the world unit vector from robot to estimated human, and `v_h` the estimated human velocity. Compute:

```
radial = dot(v_h, u)
transverse = dot(v_h, [-u_y, u_x])
v_raw = feedback_v(d - 1.5, b) + radial
v_approx = clip(v_raw, 0, 0.9) * max(0, cos(b))
w_raw = feedback_w(d - 1.5, b) + (transverse + v_approx*sin(b))/d
```

The angular feedforward follows the derivative of the target bearing. The forward command is a conservative heading-gated approximation; it avoids dividing by cos(b) near 90 degrees. Neither is a formal stability guarantee. Division by d is bounded by the close-distance threshold.

For the fuzzy networks, subtract the controller output at zero error/bearing to remove the fixed singleton equilibrium bias. This does not change membership parameters or train new weights. Apply first-order smoothing with a 0.16 s time constant to the two raw outputs, then use the same V1 speed, acceleration and wheel limits. Stale and close-range stops override smoothing. On reacquisition, filter, PID and command state reset together.

All V2 feedback choices use this same estimator/feedforward path. Legacy neuro-fuzzy bypasses it and uses the original delayed relative observations directly. Thus a V1-to-V2 comparison measures a package of estimation, equilibrium correction, feedforward and smoothing changes. It does not isolate the benefit of any single addition. Individual ablations would be needed for that claim.

## Validation additions

- Unit tests for causal velocity prediction, invalid/old packet rejection, outlier rejection, stale expiration, reacquisition reset, shared stopping and reproducibility.
- Regression check for reduced lag on a moving straight-line target.
- A new speed-change path and a sensor-outlier condition.
- A Webots batch runner that checks process/console failures, fresh output timestamps, 1,500 logged samples and a final timestamp of 48 s.
- Source/model hashes in the Webots benchmark metadata.
- An original-project hash manifest so delivery can confirm V1 files were preserved.

The development benchmark must be distinguished from a final held-out study. Before an FYP superiority claim, freeze this implementation, tune competing baselines fairly, and evaluate new paths, speeds and independently randomized measurement sequences.
