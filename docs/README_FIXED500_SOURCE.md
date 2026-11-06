# HQC-SAC Main Algorithm — Fixed 500 m × 500 m, Dynamic GU Workload

**Training plan:** seeds `7, 17, 27` × `400 EP` each, on the existing Windows Conda environment `uav_old`.

## 1. Locked experiment contract

- Main algorithm: `branch_credit_sac`, final H128 Shared-Relay BranchCredit configuration.
- Scheduler: `age_weighted_maxcost_1swap`, with the linear outage-age weight
  \(w_i=1+\lambda(O_i+\Delta t)\), max-cost ordering, and best-improvement feasible 1-swap.
- Service reward: `age_penalized_v1`, \(C_n-\lambda\bar O_{n+1}\), with \(\lambda=0.10\,s^{-1}\).
- Fixed service area: **500 m × 500 m**. Map-width and topology exposure randomization are disabled.
- Fleet: exactly **4 M-UAVs** for the full episode. Elastic Fleet/relay-count changes are disabled.
- Episode: 400 slots × 0.5 s = **200 s**.
- GU workload: 20 persistent initial users; dynamic session arrivals/departures; maximum capacity 130.
- QoS tiers: 0.7 / 2.0 / 2.5 Mbps, independently sampled per session with probabilities 0.45 / 0.35 / 0.20. These are probabilities, not exact quotas; a session's tier stays fixed until departure.
- GU positions: uniform over the fixed square. Mobility: `paper_iid_slot`, speed 0–6 m/s and heading resampled each 0.5 s slot, with boundary reflection.
- M-UAV tracking: QoS-demand-weighted K-means plus Hungarian identity matching and acceleration-limited tracking.
- Radio: 5 MHz Access, 20 MHz Backhaul, 1 W Access transmit power per M-UAV, 5 W total Backhaul power, and access-interference leakage \(\xi=0\).
- No 1.8× requested-rate bursts and no inter-M-UAV access interference.

The stochastic GU workload intentionally varies across episodes. For training seed \(s\) and episode \(e\), the environment reset seed is exactly `s * 100000 + e`.

See `DYNAMIC_USER_QOS_CONTRACT.md` and `AUDIT_FIXED500.json` for the workload details.

## 2. Start training on Windows

The launchers activate the existing `uav_old` Conda environment. They do **not** create a new environment, reinstall PyTorch, or replace the CUDA build.

1. Extract the ZIP to a normal local folder.
2. Double-click `CHECK_ENV.bat` first. It activates `uav_old`, checks CUDA and all locked settings, then performs a short environment/actor/replay/optimizer smoke test.
3. If the check passes, double-click `RUN_ALL_3_SEEDS.bat`.

The three seeds run sequentially, each for 400 EP. The launcher stops if preflight or any seed fails; it does not silently skip a failed seed. To run one seed separately, use `RUN_SEED_7.bat`, `RUN_SEED_17.bat`, or `RUN_SEED_27.bat`.

If Conda is installed in a non-standard directory and the launcher cannot find `conda.bat`, open Anaconda Prompt, run `conda activate uav_old`, change to the extracted project folder, and run the same `.bat` file again. The activation script will detect the already-active environment.

## 3. Outputs and convergence metrics

Default output directory:

```text
runs/HQC_SAC_FIXED500_B_400EP/
  seed_7/
  seed_17/
  seed_27/
  three_seed_summary.csv
  three_seed_summary.json
```

Each seed directory contains:

- `train_console.log`: live console output mirrored to a UTF-8 log.
- `PROGRESS_LATEST.json`: latest completed episode and core metrics, overwritten every EP.
- `episodes.csv`: episode history, atomically refreshed after every EP. It remains inspectable if the process stops before training finishes.
- `agent_epXXXX.pt` and `exact_resume.pt`: periodic model and exact-resume checkpoints.
- `agent.pt`, `summary.json`, `train_summary.json`: final model and summaries.
- `heldout_eval_episodes.csv` and `heldout_eval_summary.json`: deterministic evaluation on the same held-out environment seeds 9000–9009.

`episodes.csv` includes the main convergence and resilience metrics:

1. `strict_service` — per-slot minimum-QoS completion ratio averaged over the episode.
2. `mean_under_service_age_s` and `age_objective` — the age term and the actual P1 service objective.
3. `lifecycle_strict_mean` — episode-final session-level Strict-QoS completion ratio.
4. `lifecycle_strict_p05` and `lifecycle_strict_fairness` — session-level lower-tail performance and Jain fairness.
5. `lifecycle_strict_max_outage_p95_s` — P95 across sessions of each session's longest consecutive under-service interval.

The `*_stepavg` lifecycle columns are a different diagnostic: they are averages of the per-slot projected lifecycle metrics. They are deliberately named separately from the episode-final session metrics so the two definitions are not mixed.

## 4. Checkpoint and resume rules

- Exact-resume state is saved every **20 episodes** and at the requested final episode. It includes actor/critic and optimizer states, replay buffers, RNG states, counters, and episode history.
- If a run is interrupted and `exact_resume.pt` exists, use the matching `RESUME_SEED_7.bat`, `RESUME_SEED_17.bat`, or `RESUME_SEED_27.bat`.
- Resume on the same `uav_old` environment and the same CUDA device-count configuration. Do not resume from a weights-only `agent.pt` checkpoint.
- If interrupted before the first exact checkpoint, `episodes.csv` and `PROGRESS_LATEST.json` still show completed progress, but exact continuation is unavailable. For a formally comparable run, move that partial seed directory aside and restart that seed from scratch.
- A completed seed directory is protected against accidental overwrite. Move it aside only if a deliberate fresh run is intended.

## 5. Validation performed on this package

- Python syntax compilation of all package and script files.
- Unit tests for the fixed-map/dynamic-user contract, scheduler feasibility/1-swap behavior, P1 reward consistency, and episode metric persistence.
- One-episode CPU smoke training through the actual training entry point.
- One environment step, BranchCredit actor forward pass, and one synthetic replay/optimizer update in the preflight smoke test.

The authoring container does not contain the user's `uav_old` Conda environment or CUDA GPU. The smoke tests used a minimal Gymnasium API shim only because Gymnasium was not installed in the authoring container. The package does not ship that shim; the Windows preflight requires the real `gymnasium` package and CUDA-enabled PyTorch.

## 6. Known modeling choices intentionally not changed in this training package

- C-UAV initial position is `(250, 0, 150) m`, on the positive-x boundary; M-UAVs initialize at `(0, 0, 80) m` and then track their matched GU clusters. This is explicitly recorded rather than silently altered during the fixed-map correction.
- The age observation remains normalized by 10 s and clipped according to the preset. It is not changed as part of the training-launcher work.
- The stochastic workload stage boundaries vary within the fixed physical-time ranges. They are part of the dynamic traffic process, not map or fleet randomization.

## 7. What to send back for convergence analysis

After the three seeds finish, send these files (you do not need to upload the large model checkpoints for the first analysis):

- `seed_7/episodes.csv`, `seed_17/episodes.csv`, `seed_27/episodes.csv`
- each seed's `train_summary.json`
- each seed's `heldout_eval_episodes.csv` and `heldout_eval_summary.json`
- `three_seed_summary.csv` and `three_seed_summary.json`
- if there was any warning or interruption, the corresponding `train_console.log`, `PROGRESS_LATEST.json`, and `exact_resume.pt.json`

I can then assess reward/critic convergence, per-seed variance, QSR/SQA/P05/Jain trends, age-objective behavior, and long-tail outage resilience without needing the `.pt` model files initially.
