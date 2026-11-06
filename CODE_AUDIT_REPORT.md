# Code audit report — paper matrix / one PC / three workers

## What was changed

1. Removed the previous five-condition lambda training grid from the current main execution queue.
2. Replaced it with the four-stage experiment matrix from the user's screenshot.
3. Added a fixed-500m CDA-SAC-Adapted preset that inherits the same environment, radio, reward and observation contract as the HQC-SAC mainline, changing only the controller architecture and common long-horizon SAC credit semantics.
4. Added generic method/seed training with output protection and exact-resume support.
5. Added a three-worker phase-aware orchestrator: Phase II trains CDA seeds in parallel; Phase III assigns one ablation to each worker and runs its three seeds sequentially.
6. Added Motion-only (learned Motion + equal Power) and Power-only (learned Power + predeclared fixed-circle Motion) interventions using the existing runner hooks.
7. Added a project-specific causal PI-BCD-SCA adaptation and a 0.5-s slot runtime/feasibility diagnostic.
8. Added two ROCS-0 counterfactual scheduler modes: no-age and no-1-swap. They are evaluation-only diagnostics first; full retraining is not automatically launched.
9. Added per-M-UAV telemetry to environment `info` without changing the reward or transition equations.
10. Added common-30 evaluation, session-level right-censor flags, convergence plots, generalization tests, relay-distribution aggregation and a categorized data packager.

## Checks actually performed in the build environment

- `compileall` over all Python source, scripts and tests: PASS.
- Scheduler-ablation, PI solver and fixed-500 preset tests: 10/10 PASS.
- Main checkpoint hashes against archived provenance: PASS for seeds 7/17/27.
- Main episode CSVs: 400 rows, EP 400, 160,000 steps and 78,001 updates for all three seeds: PASS.
- Main episode CSV last-five reward/QSR statistics against archived `three_seed_summary.csv`: exact match for all three seeds.
- CDA fixed-500 preset: same environment/reward/radio contract as HQC-SAC main; 400 slots x 0.5 s; hidden dims 212/209; common n-step Power credit: PASS at config inspection.
- Python CLI help for training, worker orchestrator and PI solver benchmark: PASS.
- BAT scan: 16 launchers, no `necho` typo.

## Checks not performed here

The build environment does not have Gymnasium or an NVIDIA CUDA device. Therefore the complete project pytest suite, actual CUDA checkpoint loading, 11-EP smoke runs and three concurrent RTX 4090 training processes have **not** been executed here. `RUN_ONEPC_PREFLIGHT.bat` performs those checks locally and writes `results/00_AUDIT_PROGRESS/PREFLIGHT_PASSED.json`. No 400-EP training is authorized until that preflight passes.

## Important methodological caveats

- The three existing HQC-SAC main checkpoints and CSVs are reused. Their original per-seed `run_config.json` files were not present in the available artifacts; reconstructed provenance is labelled as such. The model hashes and episode CSV summary statistics match the archived frozen-checkpoint records.
- `CDA-SAC-Adapted` is a fair project adaptation, not a verbatim reproduction of the cited paper.
- The PI-BCD-SCA implementation is a causal project adaptation using an exact current-slot P1 preview and a diagonal quadratic local SCA surrogate. It must pass the runtime and feasibility gate before being described as real-time or used as a final baseline.
- Episode-end active sessions are right-censored. The evaluator flags them and does not silently present them as fully observed lifetimes.
- Final seeds 10000–10099 are not run by the common-30 validation scripts. They remain reserved until method, parameters, code and metric definitions are frozen.

CDA online parameter matching corrected to 365245 versus main 365451, target networks excluded.


## 4060 Ti 8-GB compatibility patch (Nov 3, 2026)

- The original >=16 GB total / >=12 GB free preflight gate incorrectly rejected the user's RTX 4060 Ti 8-GB machine before running any workload.
- Both preflight and long-run launcher now use an entry gate of >=7.5 GB total and >=6.0 GB free.
- This does NOT assert that three 400-EP jobs will fit. The actual three-process 11-EP GPU smoke is mandatory and is the definitive memory-capacity gate. Any CUDA OOM or failed optimizer smoke blocks long training.
- Batch size, replay capacity, optimizer settings, network widths and training protocol are unchanged.
- Local RTX 4060 Ti concurrent smoke remains unverified until the user runs RUN_ONEPC_PREFLIGHT.bat.
