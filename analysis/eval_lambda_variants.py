"""Evaluate the lambda-sensitivity checkpoints on the same 9000-9029 scenes.

The matrix evaluator only knows the five core method IDs, so this script
monkeypatches its checkpoint/config hooks for each sensitivity condition.
Evaluation only; no training.
"""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import eval_utils as E
import run_matrix_train as RMT
from uavqos import paper_final_presets as PF

CONDITIONS = {
    "S040_R010": (0.10, 0.40),
    "R005_S020": (0.05, 0.20),
    "R020_S020": (0.20, 0.20),
}
SEEDS = list(range(9000, 9030))
OUT = ROOT / "results" / "04_LAMBDA_VARIANTS"

orig_ckpt = E.checkpoint_path
for cond, (lr, ls) in CONDITIONS.items():
    E.checkpoint_path = lambda method, s, _c=cond: ROOT / "runs" / "HQC_SAC_SENSITIVITY" / _c / f"seed_{s}" / "agent.pt"
    RMT.build_config = lambda method, s, a, b, _lr=lr, _ls=ls: PF.final_h128_branch_credit_sensitivity_config(
        seed=s, lambda_reward_per_s=_lr, lambda_scheduler_per_s=_ls
    )
    for train_seed in (7, 17, 27):
        d = OUT / cond
        stem = d / f"{cond}__HQC_SAC_MAIN__trainseed_{train_seed}"
        ep = E.validate_existing_eval_files(stem, SEEDS)
        if ep is None:
            ep, _, _, _ = E.evaluate_model(
                "HQC_SAC_MAIN", train_seed, SEEDS, out_dir=d, device="cuda",
                scenario_id=cond,
            )
        print(f"[DONE] {cond} train_seed={train_seed} scenes={len(ep)}", flush=True)
E.checkpoint_path = orig_ckpt
print("[SUCCESS] lambda variants evaluated", flush=True)
