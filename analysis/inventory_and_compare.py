"""Compact inventory + training-metric comparison over all local HQC-SAC runs.

Reads every episodes.csv under anchors/ and runs/, computes the mean over the
last 50 episodes of the key training metrics, and writes a tidy CSV plus a
markdown table.  Pure CPU / pandas; does not import torch or the simulator.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
OUT.mkdir(exist_ok=True)

RUNS = {
    "HQC_SAC_MAIN(0.10/0.10)": ROOT / "anchors" / "HQC_SAC_MAIN",
    "LS020(0.10/0.20)": ROOT / "runs" / "HQC_SAC_FIXED500_B_LS020_400EP",
    "CDA_SAC_ADAPTED": ROOT / "runs" / "PHASE_II" / "CDA_SAC_ADAPTED",
    "RECURSIVE_CREDIT_H128": ROOT / "runs" / "PHASE_III" / "RECURSIVE_CREDIT_H128",
    "MOTION_ONLY": ROOT / "runs" / "PHASE_III" / "MOTION_ONLY",
    "POWER_ONLY": ROOT / "runs" / "PHASE_III" / "POWER_ONLY",
    "R005_S020(0.05/0.20)": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R005_S020",
    "R020_S020(0.20/0.20)": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R020_S020",
    "S040_R010(0.10/0.40)": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "S040_R010",
}

METRICS = [
    "reward", "strict_service", "mean_satisfaction", "p05_satisfaction",
    "age_objective", "mean_under_service_age_s",
    "lifecycle_strict_mean", "lifecycle_strict_p05", "lifecycle_strict_fairness",
    "lifecycle_strict_max_outage_p95_s", "session_longest_under_service_mean_s",
    "aggregate_goodput_mbps_mean", "c_path_m",
]

rows = []
for method, root in RUNS.items():
    for seed_dir in sorted(root.glob("seed_*")):
        f = seed_dir / "episodes.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]
        tail = df.tail(50)
        rec = {
            "method": method, "seed": int(seed_dir.name.split("_")[1]),
            "episodes": int(df["episode"].max()) if "episode" in df else len(df),
            "rows": len(df),
        }
        for m in METRICS:
            rec[m] = float(tail[m].mean()) if m in df.columns and tail[m].notna().any() else None
        # final episode snapshot
        if "episode" in df:
            last = df.loc[df["episode"].idxmax()]
            if "lifecycle_strict_max_outage_p95_s" in df:
                rec["last_p95_outage_s"] = float(last["lifecycle_strict_max_outage_p95_s"])
        rows.append(rec)

raw = pd.DataFrame(rows)
raw.to_csv(OUT / "run_inventory_raw.csv", index=False, encoding="utf-8-sig")

agg = raw.groupby("method").agg(
    seeds=("seed", "nunique"),
    ep_min=("episodes", "min"),
    ep_max=("episodes", "max"),
    **{m: (m, "mean") for m in METRICS},
    **{f"{m}_sd": (m, "std") for m in ["reward", "strict_service", "lifecycle_strict_p05",
                                      "lifecycle_strict_max_outage_p95_s"]},
).reset_index()
order = list(RUNS)
agg["__o"] = agg["method"].map({m: i for i, m in enumerate(order)})
agg = agg.sort_values("__o").drop(columns="__o")
agg.to_csv(OUT / "run_inventory_aggregate.csv", index=False, encoding="utf-8-sig")

cols = ["method", "seeds", "ep_min", "ep_max", "reward", "strict_service",
        "lifecycle_strict_mean", "lifecycle_strict_p05",
        "lifecycle_strict_max_outage_p95_s", "age_objective", "c_path_m"]
print(agg[cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))

# held-out eval summaries (only some runs have them)
eval_rows = []
for method, root in RUNS.items():
    for seed_dir in sorted(root.glob("seed_*")):
        f = seed_dir / "heldout_eval_summary.json"
        if f.exists():
            j = json.loads(f.read_text(encoding="utf-8"))
            rec = {"method": method, "seed": seed_dir.name}
            for k, v in j.items():
                if isinstance(v, (int, float)):
                    rec[k] = v
            eval_rows.append(rec)
if eval_rows:
    ev = pd.DataFrame(eval_rows)
    ev.to_csv(OUT / "heldout_eval_raw.csv", index=False, encoding="utf-8-sig")
    print("\n=== held-out eval ===")
    print(ev.to_string(index=False))
