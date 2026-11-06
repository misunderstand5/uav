# HQC-SAC paper experiment package — one PC, three concurrent workers

**This package replaces the previous lambda-grid package.** It follows the four-stage matrix in the user's screenshot. It does not launch LS010/LS020/R005-S020/R020-S020/S040-R010 as the main training queue.

## Hardware and environment

- PyTorch must already be installed in `uav_old` with a CUDA build compatible with the installed NVIDIA GPU. Do not run a generic pip command that replaces the existing CUDA PyTorch with a CPU wheel.
- `requirements-local.txt` lists non-Torch dependencies; install only if the preflight reports a missing package.

- Preferred machine: RTX 4090 24 GB. RTX 4060 Ti 8 GB is conditionally supported: it must have at least 6 GB free at preflight and must pass the actual three-process 11-EP concurrent smoke test. This is not a guarantee of capacity; if the smoke test OOMs, do not start 400-EP jobs.
- Conda environment: `uav_old`.
- Three concurrent CUDA training subprocesses are used only after the local smoke tests pass. The entry gate is at least 7.5 GB total and 6.0 GB free VRAM; the concurrent 11-EP pilot is the definitive capacity check. The pilot must pass for all three concurrent paths before any 400-EP job starts.
- The main HQC-SAC model is already trained (seeds 7/17/27, 400 EP each) and is reused from `anchors/HQC_SAC_MAIN/`.

## Exact execution order

1. Extract this package to a local drive.
2. Open Anaconda Prompt and run:

   ```bat
   conda activate uav_old
   cd /d "path\to\HQC_SAC_PAPER_MATRIX_ONEPC_3WORKERS_20261103"
   RUN_ONEPC_PREFLIGHT.bat
   ```

3. Only if preflight ends with `[PREFLIGHT PASSED]`, run:

   ```bat
   RUN_ALL_PHASE_II_III.bat
   ```

## Three-worker assignment

- Phase II: three workers train CDA-SAC-Adapted seeds 7/17/27 concurrently. The 11-EP pilot is separate and is not warm-started into the formal 400-EP runs. After CDA completes, the CPU-only PI-BCD-SCA 50-slot runtime/feasibility pilot runs.
- Phase III: three workers run concurrently; Worker 1 trains Recursive-Credit H128 seeds 7/17/27 sequentially, Worker 2 trains Motion-only seeds 7/17/27, Worker 3 trains Power-only seeds 7/17/27.
- Phase I HQC-SAC is reused from existing checkpoints and CSVs. No main-method retraining is launched by this package.

## Commands after training

- `RUN_AUDIT_PROGRESS_NOW.bat`: refresh training/model audit tables.
- `RUN_COMMON30_EVALUATION.bat`: evaluate all five methods on common validation seeds 9000-9029 (one evaluation worker by default).
- `RUN_SCHEDULER_ABLATION_DIAGNOSTIC.bat`: compare ROCS-0 with no-age and no-1-swap variants on frozen HQC-SAC policies. This is diagnostic only; retraining is decided after seeing the effect.
- `RUN_PHASE_IV_GENERALIZATION.bat`: load, mobility and initial C-UAV position tests using frozen HQC-SAC models only.
- `RUN_LAMBDA_SCREENING_150EP.bat`: optional Phase-IV one-factor screening; not part of the current Phase-II/III queue.
- `RUN_FINAL100_EVALUATION.bat`: final sealed 100-seed RL-method test; run only after every method/configuration is frozen.
- `RUN_PI_BCD_SCA_FINAL100.bat`: final sealed 100-seed PI solver test, only if its solver/runtime gate passed.
- `RUN_RELAY_DISTRIBUTION_AGGREGATE.bat`: aggregate per-M-UAV load/service telemetry from the final 100 test trajectories.
- `RUN_FINALIZE_DATA_PACKAGE.bat`: create a categorized ZIP for later analysis.

Final test seeds 10000-10099 are not run by the common-30 scripts and must remain sealed until the algorithm and evaluation protocol are frozen.


## Final verification notes (Nov 3, 2026)

- The automatically scheduled GPU jobs are ONLY CDA-SAC-Adapted and three RL ablations (Recursive-Credit H128, Motion-only, Power-only), 400 EP × 3 seeds each.
- No LS010/LS020/R005/R020/S040 lambda-training combinations are launched in the automatic three-worker queue. Phase-IV lambda-screening is provided as an OPTIONAL and separate utility, not launched by RUN_ALL_PHASE_II_III.bat.
- HQC-SAC main is the EXISTING fully trained **(lambda_r, lambda_s)=(0.10,0.10)** checkpoint trio. The provenance file is reconstructed, not an original run_config. If LS020 later becomes the chosen main method, this comparison protocol must be re-locked and the baselines matched to its scheduler before claiming final paper fairness.
- CDA-SAC-Adapted uses flat 212-D Motion hidden and 209-D Power hidden (online actor+critic parameters 365,245 vs HQC-SAC 365,451, difference 0.0564%). The old 212/428 flat configuration had more than twice the online parameters and is NOT used.
- Missing historical per-EP P95 is not reconstructed from Reward/Avg-SQA. `plot_convergence.py` explicitly records missing data and omits the corresponding historical trace. Evaluate the frozen checkpoints on common scenarios for P95 method comparisons.
- Use `RUN_PACKAGE_CURRENT_RESULTS.bat` to export whatever experiments are finished without exposing or requiring the final 100 reserved seeds. The separate final-100 scripts remain manual-only after method freeze.
- PI-BCD-SCA is a causal project-specific finite-difference block-SCA adaptation, not a verbatim reproduction or globally certified solver.
