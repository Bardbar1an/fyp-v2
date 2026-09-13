# Notes on your B:\Study\FYP references

Reviewed title/abstract/summary material extracted from six PDFs, and the rendered title page of one scanned PDF. This is an initial relevance assessment, not a full technical review of every chapter. Source PDFs were not modified or copied into the prototype. Temporary text extraction remains in the working workspace and is excluded from the deliverable copy.

| File | Identified work | Relevance |
|---|---|---|
| `FYP Report Final Repo.pdf` | Yeoh Guan Wei, **Modelling, Control and Simulation of a Mobile Robot for Obstacle Avoidance**, AY 2023/2024, supervised by Prof. Hu Guoqiang | Strong local precedent: differential-drive model, MATLAB/Simulink evaluation, potential fields and fuzzy obstacle avoidance. Use the modeling/evaluation structure as context; your moving-human reference and Webots implementation are different. |
| `MC022.pdf` | Yao Xiling, **Design and Implementation of a Human Tracking and Following Capability for a Robotic Avatar**, 2012–2013 | Most directly relevant task: Kinect tracking, target re-identification, back/side following and potential-field obstacle avoidance. Its abstract reports weaker side-by-side stability. Supports starting with back following and separating perception from motion control. |
| `FYP Report_Lee Yong Liang_2014.pdf` | Lee Yong Liang, **Further Development of a Human Tracking and Motion Interaction Capability for a Robotic Avatar**, 2013–2014 | Extends following toward front guiding and a rotating Kinect. Highlights distance-dependent speed and tracking-response limitations. A useful distinction between successful detection and responsive motion. |
| `EEE-THESES_1084.pdf` | K. R. Sarath Kodagoda, **Intelligent Control of a Mobile Robot**, 2000, MEng | Fuzzy longitudinal/lateral vehicle control, rule design and stability analysis. Useful control background; its steering/speed vehicle formulation is not automatically interchangeable with a two-wheel differential drive. |
| `FooSeeSoon1995.pdf` | Foo See Soon, **Development of a Robotic Controller Using Fuzzy Logic and Neural Networks**, 1995, MEng | Fuzzy/neural learning, interpretability and online learning for a two-link manipulator. Relevant to learning methodology, not direct human-following validation. |
| `EEE_THESES_206.pdf` | Tin Aung Win, **Industrial Robot Performance Simulation Using a Fuzzy Logic/Neural Network Controller**, 1996, MSc | Fuzzy/neural learning and SCARA simulation; useful historical context for imitation versus online improvement. Manipulator dynamics differ substantially from mobile following. |
| `ThidaKhinSaw08.pdf` | Thida Khin Saw, **Dynamic Modelling and Intelligent Control of a Mobile Robot**, 2008, MSc | Title/year verified visually. Most extracted text was repeated copyright notices, so the technical content needs OCR or manual reading before detailed claims can be made. |

## How to use these responsibly

The older neuro-fuzzy theses provide foundations and terminology. The human-following reports provide task decomposition and practical failure modes. The 2024 obstacle-avoidance report provides local project context. Add contemporary published research from `RELATED_WORK.md` so the dissertation is not based only on historical theses and previous FYP reports.

Do not reuse another student's results as your own or assume their fuzzy rule tables suit your robot. Cite specific sections after reading them; reproduce the equations independently and validate any adopted parameters. This prototype does not inherit performance claims from those reports.
