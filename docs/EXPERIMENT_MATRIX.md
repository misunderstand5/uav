# HQC-SAC paper experiment matrix (authoritative plan)

This package follows the user's four-stage matrix. The earlier five-condition lambda-training grid (LS010/LS020/R005-S020/R020-S020/S040-R010) is **not** the current training queue.

| Stage | Experiment | Budget | Current handling |
|---|---|---:|---|
| I | HQC-SAC main method | 400 EP x 3 | Reuse the already-trained 3-seed main-method checkpoints and episode CSVs; do not retrain by default. |
| II | CDA-SAC-Adapted | 11-EP technical pilot, then 400 EP x 3 | Train as the external RL baseline on the same fixed-500m environment, state/action, reward and ROCS-0 scheduler. |
| II | PI-BCD-SCA | No RL training | Run the causal online solver pilot; report single-slot runtime, solver success and physical feasibility. This is a project adaptation, not a verbatim reproduction. |
| III | Recursive-Credit H128 | 400 EP x 3 | H128 mechanism ablation: replace the main method's immediate Power credit with recursive common-reward credit. |
| III | Motion-only | 400 EP x 3 | Train Motion; fix Power to equal shares. |
| III | Power-only | 400 EP x 3 | Train Power; use a predeclared, user/channel-independent fixed circular C-UAV reference trajectory. |
| III | ROCS-0 scheduler ablation | Diagnostic first | Compare no-age and no-1-swap counterfactuals on frozen policies; only then decide whether full RL retraining is justified. |
| IV | lambda sensitivity | 150-200 EP screening first | Separate, one-factor-at-a-time screen after the main comparison; full validation only for meaningful candidates. Not part of the current Stage-II/III queue. |
| IV | Load, mobility and initial-position generalization | Frozen models; test only | Reuse the frozen HQC-SAC models; change only the declared test condition. |
| IV | Four-M-UAV load/service distribution | Reuse common/final test trajectories | Use per-relay power, backhaul/access load, assigned-user, goodput and QSR telemetry. |

## Main-method anchor status

The three HQC-SAC main-method seeds are already available at `anchors/HQC_SAC_MAIN/`. Each CSV contains 400 episodes, 160,000 environment steps and 78,001 optimizer updates. The checkpoints are reused, not retrained. The per-seed configuration provenance is reconstructed because the original per-seed run_config files were not in the available archive; this limitation is recorded alongside the files.

## Fairness contract

All RL methods use the same fixed 500 m x 500 m area, four M-UAVs, 0.5-s slots, 400 slots per episode, dynamic persistent sessions, the same QoS tiers and sampling probabilities, the same current-state observation/action contract, K-means++/Hungarian association, and ROCS-0 scheduler unless the scheduler itself is the ablated factor. Training seeds are 7/17/27. Common validation seeds are 9000-9029. Final test seeds 10000-10099 remain sealed until all method/configuration choices are frozen.

## Budget rule

400 EP is the initial planned budget, not proof of convergence. If the HQC-SAC curves show that 400 EP is insufficient and the main model is extended to 800 EP, the RL baseline and RL ablation budgets must also be extended to the same budget, or the paper must explicitly frame the comparison as sample-efficiency analysis.
