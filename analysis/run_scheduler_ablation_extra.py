"""Run only the two ROCS-0 counterfactual scheduler modes on frozen main models.

Nominal mode is already evaluated in results/02_COMMON30_VALIDATION, so this
script avoids re-running it.  Output schema matches
scripts/run_scheduler_ablation_diagnostic.py.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_utils import evaluate_model, parse_seeds, validate_existing_eval_files

MODES = ("rocs0_no_age", "rocs0_no_1swap")
SEEDS = parse_seeds("9000-9029")
OUT = ROOT / "results" / "03_SCHEDULER_ABLATION"
rows = []
for mode in MODES:
    d = OUT / mode
    for train_seed in (7, 17, 27):
        stem = d / f"{mode}__HQC_SAC_MAIN__trainseed_{train_seed}"
        ep = validate_existing_eval_files(stem, SEEDS)
        if ep is None:
            ep, _, _, _ = evaluate_model(
                "HQC_SAC_MAIN", train_seed, SEEDS, out_dir=d, device="cuda",
                scheduler_mode=mode, scenario_id=mode,
            )
        rows.extend(ep)
        print(f"[DONE] scheduler={mode} train_seed={train_seed} scenes={len(ep)}", flush=True)

if rows:
    keys = sorted({k for r in rows for k in r})
    with (OUT / "scheduler_ablation_extra_episodes.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
print("[SUCCESS] counterfactual scheduler evaluation complete", flush=True)
