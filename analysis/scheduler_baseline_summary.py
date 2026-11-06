"""Scheduler-baseline summary: ROCS-0 vs classical schedulers (post-fix)."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "results" / "02_COMMON30_VALIDATION"
OUT = ROOT / "analysis"

SCHED_METHODS = [
    "HQC_SAC_MAIN",
    "HQC_SAC_NO_AGE",
    "HQC_SAC_NO_1SWAP",
    "HQC_SAC_PF",
    "HQC_SAC_MAX_CQI",
    "HQC_SAC_MAX_QOS",
    "HQC_SAC_EQUAL",
]
LABEL = {
    "HQC_SAC_MAIN": "ROCS-0 (main)",
    "HQC_SAC_NO_AGE": "ROCS-0 no-age (retrained)",
    "HQC_SAC_NO_1SWAP": "ROCS-0 no-1swap (retrained)",
    "HQC_SAC_PF": "PF (frozen main controller)",
    "HQC_SAC_MAX_CQI": "Max-CQI (frozen main controller)",
    "HQC_SAC_MAX_QOS": "Max-QoS lowest-SQA-first (frozen main controller)",
    "HQC_SAC_EQUAL": "Equal-share (frozen main controller)",
}
METRICS = {"QSR": "QSR", "P5_SQA": "P5", "P95_Outage_s": "P95(s)",
           "Jain_SQA": "Jain", "Goodput_Mbps": "Goodput"}


def load(m):
    fs = sorted(EVAL.glob(f"nominal__{m}__trainseed_*__episodes.csv"))
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in fs], ignore_index=True)


def boot_paired(main: np.ndarray, other: np.ndarray, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(main), size=(n, len(main)))
    d = (other - main)[idx].mean(axis=1)
    return float(np.quantile(d, .025)), float(np.quantile(d, .975))


def main():
    frames = {m: load(m) for m in SCHED_METHODS}
    main_df = frames["HQC_SAC_MAIN"]
    rows = []
    for m in SCHED_METHODS:
        d = frames[m]
        row = {"method": LABEL[m], "n": len(d)}
        for col, name in METRICS.items():
            row[name] = float(d[col].mean())
        if m != "HQC_SAC_MAIN":
            for col, name in METRICS.items():
                a = main_df[col].to_numpy(float)
                b = d[col].to_numpy(float)
                lo, hi = boot_paired(a, b)
                row[f"d_{name}"] = float(b.mean() - a.mean())
                row[f"ci95_{name}"] = f"[{lo:.4f},{hi:.4f}]"
                row[f"win_{name}"] = float((b > a).mean())
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "scheduler_comparison_classical.csv", index=False, encoding="utf-8-sig")
    print(out[["method", "n", "QSR", "P5", "P95(s)", "Jain", "Goodput"]].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print("saved:", OUT / "scheduler_comparison_classical.csv")


if __name__ == "__main__":
    main()
