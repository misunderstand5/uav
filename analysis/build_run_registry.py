"""Build a single, machine-checkable registry for the two-PC merge.

Every training run that matters is listed with: source GPU (from
runtime_environment.json), lambda_r/lambda_s, seed, completeness, checkpoint
hash and episode-CSV hash.  This is the canonical join table for analysis;
it does not move or rename any run directory.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
OUT.mkdir(exist_ok=True)

GROUPS = [
    ("MAIN(0.10/0.10)", ROOT / "anchors" / "HQC_SAC_MAIN"),
    ("LS020(0.10/0.20)", ROOT / "runs" / "HQC_SAC_FIXED500_B_LS020_400EP"),
    ("CDA_SAC_ADAPTED(0.10/0.10)", ROOT / "runs" / "PHASE_II" / "CDA_SAC_ADAPTED"),
    ("RECURSIVE_CREDIT_H128(0.10/0.10)", ROOT / "runs" / "PHASE_III" / "RECURSIVE_CREDIT_H128"),
    ("MOTION_ONLY(0.10/0.10)", ROOT / "runs" / "PHASE_III" / "MOTION_ONLY"),
    ("POWER_ONLY(0.10/0.10)", ROOT / "runs" / "PHASE_III" / "POWER_ONLY"),
    ("R005_S020(0.05/0.20)", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R005_S020"),
    ("R020_S020(0.20/0.20)", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R020_S020"),
    ("S040_R010(0.10/0.40)", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "S040_R010"),
]

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

rows = []
for condition, root in GROUPS:
    for sd in sorted(root.glob("seed_*")):
        seed = int(sd.name.split("_")[1])
        cfg = read_json(sd / "run_config.json")
        if not cfg:
            cfg = read_json(sd / "run_config_reconstructed.json")
        contract = cfg.get("contract", cfg)
        lr = contract.get("lambda_reward_per_s", contract.get("lambda_per_s"))
        ls = contract.get("lambda_scheduler_per_s", contract.get("lambda_per_s"))
        rt = read_json(sd / "runtime_environment.json")
        eps = sd / "episodes.csv"
        n = 0
        last = {}
        if eps.exists():
            d = pd.read_csv(eps, encoding="utf-8-sig")
            d.columns = [c.strip() for c in d.columns]
            n = len(d)
            tail = d.tail(5)
            last = {"last5_reward": float(tail.reward.mean()),
                    "last5_strict_service": float(tail.strict_service.mean())}
        summary = read_json(sd / "train_summary.json")
        rec = {
            "condition": condition, "seed": seed,
            "source_gpu": rt.get("gpu_name", "unknown"),
            "python": rt.get("python", "").split("|")[0].strip(),
            "lambda_r": lr, "lambda_s": ls,
            "episodes": n,
            "steps": summary.get("steps"),
            "updates": summary.get("updates"),
            "status": "COMPLETE" if n >= 400 and (sd / "agent.pt").exists() else "INCOMPLETE",
            "agent_sha256": sha(sd / "agent.pt") if (sd / "agent.pt").exists() else "",
            "episodes_csv_sha256": sha(eps) if eps.exists() else "",
            "has_heldout_eval": (sd / "heldout_eval_episodes.csv").exists(),
            **last,
            "path": str(sd.relative_to(ROOT)),
        }
        rows.append(rec)

reg = pd.DataFrame(rows)
reg.to_csv(OUT / "run_registry.csv", index=False, encoding="utf-8-sig")
print(reg.to_string(index=False))
print(f"\n[REGISTRY] {len(reg)} seed-runs -> {OUT / 'run_registry.csv'}")
print(reg.groupby("condition").agg(runs=("seed", "nunique"), complete=("status", lambda s: (s == "COMPLETE").sum()),
                                   gpu=("source_gpu", lambda s: ",".join(sorted(set(s))))).to_string())
