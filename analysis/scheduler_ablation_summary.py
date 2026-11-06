"""ROCS-0 scheduler ablation summary: nominal vs no-age vs no-1-swap."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
NOM = ROOT / "results" / "02_COMMON30_VALIDATION"
ABL = ROOT / "results" / "03_SCHEDULER_ABLATION"
METRICS = {
    "QSR": "QSR", "Avg_SQA": "Avg-SQA", "P5_SQA": "P5-SQA",
    "Jain_SQA": "Jain", "P95_Outage_s": "P95-Outage(s)", "Goodput_Mbps": "Goodput(Mbps)",
}

def load_nominal():
    fs = sorted(NOM.glob("nominal__HQC_SAC_MAIN__trainseed_*__episodes.csv"))
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True)

def load_abl(mode):
    fs = sorted(ABL.glob(f"{mode}/*__episodes.csv"))
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True)

def boot_ci(x, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return float(np.quantile(means, .025)), float(np.quantile(means, .975))

data = {"nominal": load_nominal(), "no_age": load_abl("rocs0_no_age"), "no_1swap": load_abl("rocs0_no_1swap")}
print("counts:", {k: len(v) for k, v in data.items()})

rows = []
for name, d in data.items():
    rec = {"condition": name, "n": len(d)}
    for col, label in METRICS.items():
        rec[label] = d[col].mean()
    rows.append(rec)
print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.4f}"))

nom = data["nominal"].set_index(["train_seed", "eval_seed"])
prows = []
for mode in ("no_age", "no_1swap"):
    other = data[mode].set_index(["train_seed", "eval_seed"])
    for col, label in METRICS.items():
        j = pd.concat([nom[col].rename("nominal"), other[col].rename("abl")], axis=1).dropna()
        diff = j["nominal"] - j["abl"]
        lo, hi = boot_ci(diff.values)
        prows.append({
            "contrast": f"nominal - {mode}", "metric": label,
            "nominal": j["nominal"].mean(), "ablated": j["abl"].mean(),
            "diff": diff.mean(), "ci95_low": lo, "ci95_high": hi,
            "nominal_win_rate": float((diff > 0).mean()), "n_pairs": len(j),
        })
p = pd.DataFrame(prows)
p.to_csv(OUT / "scheduler_ablation_paired.csv", index=False, encoding="utf-8-sig")
print("\n", p.to_string(index=False, float_format=lambda x: f"{x:+.4f}" if abs(x) < 10 else f"{x:+.2f}"))

print("\n=== per training seed QSR / P5 / P95 ===")
for name, d in data.items():
    for s in (7, 17, 27):
        x = d[d.train_seed == s]
        print(f"{name:9s} seed{s:2d}: QSR={x.QSR.mean():.4f} P5={x.P5_SQA.mean():.4f} P95={x.P95_Outage_s.mean():.2f} Jain={x.Jain_SQA.mean():.4f}")
