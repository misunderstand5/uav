"""Common-30 summary for the five core methods, with paired bootstrap vs main."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
EVAL = ROOT / "results" / "02_COMMON30_VALIDATION"
METHODS = ["HQC_SAC_MAIN", "CDA_SAC_ADAPTED", "RECURSIVE_CREDIT_H128", "MOTION_ONLY", "POWER_ONLY"]
LABEL = {
    "HQC_SAC_MAIN": "HQC-SAC (0.10/0.10)",
    "CDA_SAC_ADAPTED": "CDA-SAC-Adapted",
    "RECURSIVE_CREDIT_H128": "Recursive-Credit H128",
    "MOTION_ONLY": "Motion-only",
    "POWER_ONLY": "Power-only",
}
METRICS = {
    "QSR": "QSR",
    "Avg_SQA": "Avg-SQA",
    "P5_SQA": "P5-SQA",
    "Jain_SQA": "Jain",
    "P95_Outage_s": "P95-Outage(s)",
    "Goodput_Mbps": "Goodput(Mbps)",
}

def load(m):
    fs = sorted(EVAL.glob(f"nominal__{m}__trainseed_*__episodes.csv"))
    d = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True)
    d.columns = [c.strip() for c in d.columns]
    return d

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
        rec[name + "_sd"] = d[col].std()
    rows.append(rec)
summary = pd.DataFrame(rows)
summary.to_csv(OUT / "common30_method_summary.csv", index=False, encoding="utf-8-sig")

print("=== common-30 means (n=90 per method: 3 train seeds x 30 scenes) ===")
print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n=== paired vs main (90 scene pairs) ===")
prows = []
main = data["HQC_SAC_MAIN"].set_index(["train_seed", "eval_seed"])
for m in METHODS[1:]:
    other = data[m].set_index(["train_seed", "eval_seed"])
    for col, name in METRICS.items():
        j = pd.concat([main[col].rename("main"), other[col].rename("other")], axis=1).dropna()
        diff = j["main"] - j["other"]
        lo, hi = boot_ci(diff.values)
        prows.append({
            "contrast": f"main - {LABEL[m]}", "metric": name,
            "main": j["main"].mean(), "other": j["other"].mean(),
            "diff": diff.mean(), "ci95_low": lo, "ci95_high": hi,
            "main_win_rate": float((diff > 0).mean()), "n_pairs": len(j),
            "diff_seed7": diff.loc[7].mean() if 7 in diff.index.get_level_values(0) else None,
            "diff_seed17": diff.loc[17].mean() if 17 in diff.index.get_level_values(0) else None,
            "diff_seed27": diff.loc[27].mean() if 27 in diff.index.get_level_values(0) else None,
        })
p = pd.DataFrame(prows)
p.to_csv(OUT / "common30_paired_vs_main.csv", index=False, encoding="utf-8-sig")
print(p.to_string(index=False, float_format=lambda x: f"{x:+.4f}" if abs(x) < 10 else f"{x:+.2f}"))

print("\n=== per-seed QSR / P95 / P5 ===")
for m in METHODS:
    d = data[m]
    for s in (7, 17, 27):
        x = d[d.train_seed == s]
        print(f"{LABEL[m]:24s} seed{s:2d}: QSR={x.QSR.mean():.4f} P5={x.P5_SQA.mean():.4f} P95={x.P95_Outage_s.mean():.2f} AvgSQA={x.Avg_SQA.mean():.4f}")
