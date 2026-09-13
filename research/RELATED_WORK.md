# Related work and a focused direction for the FYP

Research checked on 10 September 2026. This is a targeted research brief, not a systematic or exhaustive review. Bibliographic dates below come from publication records, rather than search-engine crawl dates. Some publisher full texts were inaccessible; the evidence level is stated for each entry. The implementation is original prototype code, not a reproduction of these papers.

## Recommended research question

**Under identical sensing and actuator constraints, does a learned neuro-fuzzy controller improve the accuracy–smoothness trade-off of differential-drive human following compared with tuned PID and fixed fuzzy control, including conditions not used during tuning?**

This is an achievable evaluation contribution. Human following, fuzzy control, and adaptive-network fuzzy learning all have substantial prior work. Claiming novelty simply because a neural network is combined with fuzzy logic would be difficult to defend. The proposed contribution should be a reproducible implementation, a justified learning method, and carefully controlled experiments. This assessment is a synthesis of the sources below, not a verified claim that no similar benchmark exists.

## Core reading list

| Priority | Reference and verified source | What it contributes | How to use it / limits |
|---|---|---|---|
| 1 | Andrea Eirale, Mauro Martini, Marcello Chiaberge (2025), **Human Following and Guidance by Autonomous Mobile Robots: A Comprehensive Review**, IEEE Access. [Institutional record](https://iris.polito.it/handle/11583/2998224), [DOI](https://doi.org/10.1109/ACCESS.2025.3548134) | Organizes human following and guidance across perception, tracking, planning, control and interaction. | Structure your literature review around these separate modules. Evidence: institutional abstract and indexed manuscript excerpts; the full PDF could not be fetched through the research tool. |
| 2 | **Lightweight Two-Layer Control Architecture for Human-Following Robot** (2024), Sensors 24(23), 7796. [Publisher](https://www.mdpi.com/1424-8220/24/23/7796), [full-text archive](https://pmc.ncbi.nlm.nih.gov/articles/PMC11644850/), [DOI](https://doi.org/10.3390/s24237796) | Combines a fuzzy behavior layer with embedded low-level control; the published description prioritizes angular alignment over forward motion. | A close architectural comparator for separating following decisions and wheel actuation. It uses fixed fuzzy behavior, so learning inside your fuzzy controller is a distinct design choice. Evidence: indexed publisher sections; direct full-text retrieval was blocked. Verify full experimental details before reproducing it. |
| 3 | Yin Yin Aye, Kyaw Thiha, Mi Mi Myint Pyu, Keigo Watanabe (2019), **A Deep Neural Network Based Human Following Robot with Fuzzy Control**, ROBIO 2019, pp. 720–725. [University record](https://okayama.elsevierpure.com/en/publications/a-deep-neural-network-based-human-following-robot-with-fuzzy-cont/), [DOI](https://doi.org/10.1109/ROBIO49542.2019.8961577) | Uses a neural detector with RealSense depth and fuzzy velocity/steering control on a four-wheel-steered platform. | Explain the difference between neural perception plus fuzzy control and a neuro-fuzzy controller whose rules/membership parameters are trained. Its vehicle model is not your differential-drive model. Evidence: university abstract and bibliographic record. |
| 4 | Nguyen Van Toan, Minh Do Hoang, Phan Bui Khoi, Soo-Yeong Yi (2023), **The Human-Following Strategy for Mobile Robots in Mixed Environments**, Robotics and Autonomous Systems 160, 104317. [Publisher](https://www.sciencedirect.com/science/article/pii/S0921889022002068), [DOI](https://doi.org/10.1016/j.robot.2022.104317) | Integrates target following and environment-dependent behaviors, with hedge-algebra inference for mapped and unmapped spaces. | Supports treating obstacle handling and environmental rules as separate behavior requirements. This is not an ANFIS paper. Evidence: publisher abstract and section excerpts. The DOI contains 2022, but the volume publication is February 2023. |
| 5 | Jyh-Shing Roger Jang (1993), **ANFIS: Adaptive-Network-Based Fuzzy Inference System**, IEEE Transactions on Systems, Man, and Cybernetics 23(3), 665–685. [Institutional record](https://scholars.lib.ntu.edu.tw/entities/publication/3b716e7c-a2e7-4ff2-9c28-2faf9ced327e), [DOI](https://doi.org/10.1109/21.256541) | Establishes adaptive-network implementation of fuzzy inference and hybrid learning from examples and rules. | Foundation for the learning architecture chapter. Our zero-order Sugeno/Adam implementation is a simpler variant, not the complete original first-order ANFIS hybrid algorithm. Evidence: abstract and bibliographic record. |
| 6 | **Development of a Worker-Following Robot System: Worker Position Estimation and Motion Control under Measurement Uncertainty** (2023), Machines 11(3), 366. [Publisher](https://www.mdpi.com/2075-1702/11/3/366), [DOI](https://doi.org/10.3390/machines11030366) | Studies worker position uncertainty and following control, including a spring–damper formulation on a Mecanum platform. | Motivates noise/delay experiments and separate evaluation of estimation versus control. Different drive geometry; do not transfer conclusions directly. Evidence: indexed publisher abstract/sections. |
| 7 | Jianwei Peng, Zhelin Liao, Zefan Su, Hanchen Yao, Yadan Zeng, Houde Dai (2024), **A Dual Closed-Loop Control Strategy for Human-Following Robots Respecting Social Space**, ICRA 2024. [Author-hosted paper](https://jian-wei-peng.github.io/files/icra2024.pdf) | Explicitly considers the target person's social space in human-following control. | Useful motivation for clearance and smoothness alongside error. A fixed 1.5 m reference in our prototype is an engineering setting, not a universal social-comfort threshold. Evidence: author PDF, including title, authors and abstract. |
| 8 | **A Human-Following Motion Planning and Control Scheme for Collaborative Robots Based on Human Motion Prediction** (2021), Sensors 21(24), 8229. [Publisher](https://www.mdpi.com/1424-8220/21/24/8229), [DOI](https://doi.org/10.3390/s21248229) | Uses predicted human motion and model-predictive trajectory planning in a collaborative supply task. | Provides a model-based alternative and motivation for a future predictive/feedforward baseline. It is broader than a direct distance/bearing controller. Evidence: indexed publisher abstract. |

## What the literature changes in your design

**Separate tracking from following.** Tracking estimates the selected person's state; following commands the robot to maintain a useful spatial relationship. The 2019 neural-detector/fuzzy-control paper makes this separation clear. Start by assuming reliable relative position, then introduce uncertainty. If time allows, add RGB-D detection later and measure its own failures.

**Separate learning from rule-based inference.** A neural network used only for detecting a person does not make the motion controller neuro-fuzzy. In this prototype, Gaussian membership centers and widths and Sugeno rule outputs are trainable. Plot the before/after membership functions and document which parameters are learned.

**Treat smoothness and personal space as objectives.** Distance error alone can reward aggressive motion. Include minimum separation, time under a chosen clearance threshold, and acceleration statistics. Social-space work supports considering comfort, but our simulation cannot establish subjective comfort without a separate human study.

**Do not mix following with complete navigation.** Mixed-environment work includes collision avoidance and environment constraints. This prototype's obstacle-free world keeps the initial control experiment manageable. Add an identical obstacle-handling layer to all controllers as a separate extension, rather than silently comparing controllers with different navigation capabilities.

**Use model-based alternatives to interpret the results.** Neuro-fuzzy improvement may come from an expert's stronger nonlinear gain rather than the learning architecture. Compare the synthetic teacher itself and a tuned nonlinear proportional controller before attributing improvements to neuro-fuzzy learning. MPC/prediction papers are useful context but not necessarily required implementation scope for this FYP.

## Suggested literature review structure

1. Differential-drive kinematics and human-relative control variables.
2. Human detection, target identity and state estimation (clearly separated from your control scope).
3. Classical following control: PID, nonlinear proportional or spring–damper methods.
4. Fuzzy following control: rule design, membership functions, behavioral priority.
5. Neuro-fuzzy learning: Sugeno networks, offline versus online adaptation, interpretability.
6. Evaluation: accuracy, smoothness, loss recovery, uncertainty and simulator limitations.
7. Your bounded research question and experimental contribution.

## Simulator references

- [Webots Humans guide](https://www.cyberbotics.com/doc/guide/humans?version=R2025a): Pedestrian model, scripted gait and configurable trajectories.
- [Official Pedestrian source](https://github.com/cyberbotics/webots/blob/R2025a/projects/humans/pedestrian/controllers/pedestrian/pedestrian.py): useful API reference for human pose/joint animation. Our animation uses its own simple sinusoidal gait, not copied gait tables.
- [Webots Cylinder reference](https://cyberbotics.com/doc/reference/cylinder?version=R2025a): cylinder central axis along local z; wheel geometries must be rotated to align with the axle.

Further search leads include robust fuzzy behavior under unknown environments, person re-identification after occlusion, and controller tuning under uncertainty. The 2025 review's bibliography is a good starting point. Read and verify full papers before adding detailed comparative numerical claims to the dissertation.
