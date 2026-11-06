"""Full common-30 summary: 11 methods, paired bootstrap vs main, 2x2, scheduler."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "results" / "02_COMMON30_VALIDATION"
OUT = ROOT / "analysis"
METHODS = ["HQC_SAC_MAIN", "CDA_SAC_ADAPTED", "RECURSIVE_CREDIT_H128", "MOTION_ONLY",
           "POWER_ONLY", "FLAT_RELAY_IMMEDIATE", "JOINT_SAC_PM", "TD3", "PPO",
           "HQC_SAC_NO_AGE", "HQC_SAC_NO_1SWAP"]
LABEL = {
    "HQC_SAC_MAIN": "HQC-SAC (main)",
    "CDA_SAC_ADAPTED": "CDA-SAC",
    "RECURSIVE_CREDIT_H128": "Recursive-Credit",
    "MOTION_ONLY": "Motion-only",
    "POWER_ONLY": "Power-only",
    "FLAT_RELAY_IMMEDIATE": "Flat-Relay + immediate",
    "JOINT_SAC_PM": "Joint-SAC (PM)",
    "TD3": "TD3",
    "PPO": "PPO",
    "HQC_SAC_NO_AGE": "no-age retrained",
    "HQC_SAC_NO_1SWAP": "no-1swap retrained",
}
METRICS = {"QSR": "QSR", "Avg_SQA": "Avg-SQA", "P5_SQA": "P5", "Jain_SQA": "Jain",
           "P95_Outage_s": "P95", "Goodput_Mbps": "Goodput"}


def load(m):
    fs = sorted(EVAL.glob(f"nominal__{m}__trainseed_*__episodes.csv"))
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True)


def boot_ci(x, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return float(np.quantile(means, .025)), float(np.quantile(means, .975))


data = {m: load(m) for m in METHODS}
rows = []
for m in METHODS:
    d = data[m]
    rec = {"method": LABEL[m], "n": len(d)}
    for col, name in METRICS.items():
        rec[name] = d[col].mean()
    rows.append(rec)
summary = pd.DataFrame(rows)
summary.to_csv(OUT / "common30_all_methods.csv", index=False, encoding="utf-8-sig")
print(summary.round(4).to_string(index=False))

main = data["HQC_SAC_MAIN"].set_index(["train_seed", "eval_seed"])
prows = []
for m in METHODS[1:]:
    other = data[m].set_index(["train_seed", "eval_seed"])
    for col, name in METRICS.items():
        j = pd.concat([main[col].rename("main"), other[col].rename("other")], axis=1).dropna()
        diff = j["main"] - j["other"]
        lo, hi = boot_ci(diff.values)
        prows.append({"contrast": f"main - {LABEL[m]}", "metric": name,
                      "main": j["main"].mean(), "other": j["other"].mean(),
                      "diff": diff.mean(), "ci_low": lo, "ci_high": hi,
                      "main_win_rate": float((diff > 0).mean()), "n": len(j)})
p = pd.DataFrame(prows)
p.to_csv(OUT / "common30_paired_full.csv", index=False, encoding="utf-8-sig")
print("\n=== paired vs main (90 pairs) ===")
print(p.to_string(index=False, float_format=lambda x: f"{x:+.4f}" if abs(x) < 10 else f"{x:+.2f}"))
