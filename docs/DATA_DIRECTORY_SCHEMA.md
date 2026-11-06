# Categorized output directory

```text
runs/
  00_PILOT/                         # 11-EP technical smoke runs; never used as final models
  PHASE_II/CDA_SAC_ADAPTED/         # CDA-SAC-Adapted x 3 seeds
  PHASE_III/RECURSIVE_CREDIT_H128/  # Recursive-Credit H128 x 3 seeds
  PHASE_III/MOTION_ONLY/            # Motion-only x 3 seeds
  PHASE_III/POWER_ONLY/             # Power-only x 3 seeds
  PHASE_IV_LAMBDA_SCREEN/           # optional 150-EP screening

results/
  00_AUDIT_PROGRESS/                # worker logs, anchor audit, progress snapshots
  01_CONVERGENCE/                   # 5 training curves, raw + 20-EP MA
  02_PI_BCD_SCA/                    # solver slot timing and feasibility diagnostics
  02_COMMON30_VALIDATION/           # paired 30-scene method evaluation
  03_SCHEDULER_ABLATION/            # frozen-policy ROCS-0 counterfactuals
  05_GENERALIZATION/                # load, mobility, initial position
  06_RELAY_DISTRIBUTION/            # per-M-UAV load/power/goodput/QSR/fairness
  09_ANALYSIS_PACKAGE/              # final categorized analysis ZIP
```

Each training seed directory contains `agent.pt`, `episodes.csv`, `run_config.json`, `config_snapshot.json`, `training_runtime_contract.json`, `training_intervention.json`, `runtime_environment.json`, `summary.json`, `train_summary.json`, `exact_resume.pt`, and `train_console.log` (as applicable). Exact resume states stay in the working run folders and are excluded from the smaller analysis ZIP unless explicitly requested.
