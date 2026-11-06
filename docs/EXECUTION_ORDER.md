# Execution order and decision gates

## Gate 0 — Phase-I main anchor audit

Reuse the 3 existing HQC-SAC main checkpoints. Require 400 episode rows, 160,000 steps, correct SHA256, and successful CPU checkpoint load. The original per-seed config metadata is reconstructed and clearly marked.

## Gate 1 — local preflight

Require `uav_old`, CUDA, Gymnasium, >=7.5 GB total and >=6.0 GB free VRAM (8-GB GPUs only proceed if all concurrent pilots pass), unit tests, 4 x 11-EP method-path pilots (CDA, Recursive, Motion-only, Power-only), and a 5-slot PI solver pilot. No 400-EP job starts before this gate passes.

## Stage II

CDA-SAC-Adapted: 11-EP technical pilot, then 400 EP x 3 seeds from scratch. The pilot is not a warm start. PI-BCD-SCA: 50-slot CPU solver/runtime pilot, no RL training.

## Stage III

Three workers concurrently train Recursive-Credit H128, Motion-only, and Power-only; each method runs seeds 7/17/27 at 400 EP. Exact checkpoints are saved every 20 EP. Complete runs are skipped; exact-resume runs are resumed; partial directories without exact resume are protected and stop the launcher.

## Stage IV

Only after model selection: (i) lambda sensitivity screen at 150-200 EP, with full training validation only if needed; (ii) load/mobility/initial-position tests reusing frozen models; (iii) per-M-UAV load/service analysis using common/final test trajectories.

## Final freeze

Before the 100-seed final test, freeze algorithm variants, parameters, code hashes, environment contracts, metric definitions and evaluation scripts. Then run all methods on the same 100 seeds 10000-10099.
