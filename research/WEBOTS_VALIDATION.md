# Webots 3D validation — 10 September 2026

Webots R2025a Windows, Python 3.11, 32 ms timestep. Each controller completed 48 simulated seconds of the same figure-eight human path, from a fresh world. This is actual Webots motor/contact physics, not the 2D harness. Position sensing uses Supervisor ground truth.

| Controller | Distance RMSE (m) | Minimum separation (m) |
|---|---:|---:|
| PID | 0.2759 | 1.4375 |
| Plain fuzzy | 0.3611 | 1.4283 |
| Neuro-fuzzy | 0.2052 | 1.5000 |

Desired separation: 1.5 m. All runs had zero time below the configured 0.65 m close threshold. That is a distance check, not a physical collision or safety certification. Baseline tuning is still preliminary; these runs do not establish general superiority.

Fixes made through actual execution:

- Changed the Pedestrian EXTERNPROTO to the official HTTPS asset URL used by current Webots distributions.
- Added physics properties to the two support skids/casters.
- Converted all animated joint values to Python floats, including zero values.
- Corrected the viewpoint for R2025a coordinates and widened its field of view.
- Added automatic batch termination, snapshot capture, optional MP4 recording and a PowerShell launcher.

Artifacts in `results/webots/`: three CSV logs, three metrics JSON files, 3D snapshots, and `figure_eight_neuro_fuzzy_3d.mp4`. The MP4 was verified with ffprobe: H.264, 960×540, 1,500 frames, 48 seconds. Webots reported recording success; its encoder emitted a target-bitrate convergence warning for this visually simple scene, but produced a valid video.

Webots is installed at `C:\Users\User\Documents\ChatGPT\fyp\tools\Webots`. The launcher searches that location and the usual Program Files location. To run:

```powershell
Set-Location -LiteralPath 'B:\vs code project\fyp'
.\run_webots.ps1
# Automatically finish and record:
.\run_webots.ps1 -Batch -Video
# Another controller:
.\run_webots.ps1 -Batch -Controller pid
```

Only the figure-eight scenario has been validated in 3D so far. Other scenarios remain available for testing. The robot has no implemented image-based person detector or obstacle avoidance. Human walking is scripted animation, and the casters use low-friction sphere contacts rather than detailed swivel mechanics.
