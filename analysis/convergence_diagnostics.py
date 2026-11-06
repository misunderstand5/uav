"""Convergence / seed-variance diagnostics for the local training CSVs."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"

RUNS = {
    "MAIN(0.10/0.10)": ROOT / "anchors" / "HQC_SAC_MAIN",
    "LS020(0.10/0.20)": ROOT / "runs" / "HQC_SAC_FIXED500_B_LS020_400EP",
    "CDA": ROOT / "runs" / "PHASE_II" / "CDA_SAC_ADAPTED",
    "RECURSIVE": ROOT / "runs" / "PHASE_III" / "RECURSIVE_CREDIT_H128",
    "MOTION_ONLY": ROOT / "runs" / "PHASE_III" / "MOTION_ONLY",
    "POWER_ONLY": ROOT / "runs" / "PHASE_III" / "POWER_ONLY",
    "R005_S020": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R005_S020",
    "R020_S020": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R020_S020",
    "S040_R010": ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "S040_R010",
}
BINS = [(1, 50), (51, 100), (101, 150), (151, 200), (201, 250), (251, 300), (301, 350), (351, 400)]

rows = []
for method, root in RUNS.items():
    for sd in sorted(root.glob("seed_*")):
        f = sd / "episodes.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]
        seed = int(sd.name.split("_")[1])
        for a, b in BINS:
            w = df[(df.episode >= a) & (df.episode <= b)]
            if w.empty:
                continue
            rows.append({
                "method": method, "seed": seed, "bin": f"{a}-{b}",
                "n": len(w),
                "reward": w.reward.mean(), "strict_service": w.strict_service.mean(),
                "lifecycle_strict_mean": w.lifecycle_strict_mean.mean() if "lifecycle_strict_mean" in w else None,
                "p05": w.lifecycle_strict_p05.mean() if "lifecycle_strict_p05" in w else None,
                "p95_outage": w.lifecycle_strict_max_outage_p95_s.mean() if "lifecycle_strict_max_outage_p95_s" in w else None,
            })
b = pd.DataFrame(rows)
b.to_csv(OUT / "convergence_bins.csv", index=False, encoding="utf-8-sig")

# per-seed last-100 and last-50, plus rising delta
seedrows = []
for method, root in RUNS.items():
    for sd in sorted(root.glob("seed_*")):
        f = sd / "episodes.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]
        seed = int(sd.name.split("_")[1])
        def m(a, b, col):
            w = df[(df.episode >= a) & (df.episode <= b)][col]
            return float(w.mean()) if len(w) else None
        seedrows.append({
            "method": method, "seed": seed,
            "strict_1_100": m(1, 100, "strict_service"),
            "strict_201_300": m(201, 300, "strict_service"),
            "strict_301_400": m(301, 400, "strict_service"),
            "strict_351_400": m(351, 400, "strict_service"),
            "delta_301_350_vs_351_400": (m(351, 400, "strict_service") or 0) - (m(301, 350, "strict_service") or 0),
            "reward_351_400": m(351, 400, "reward"),
        })
s = pd.DataFrame(seedrows)
s.to_csv(OUT / "seed_lastwindow.csv", index=False, encoding="utf-8-sig")

print("=== 50-EP bin means of strict_service (mean over seeds) ===")
p = b.pivot_table(index="method", columns="bin", values="strict_service", aggfunc="mean")
p = p[[f"{a}-{c}" for a, c in BINS if f"{a}-{c}" in p.columns]]
print(p.round(3).to_string())
print("\n=== per-seed late-window strict service ===")
print(s.round(3).to_string(index=False))
print("\n=== late-window delta (351-400 minus 301-350); |d|>0.01 means not flat ===")
print(s.groupby("method")["delta_301_350_vs_351_400"].agg(["mean", "std"]).round(4).to_string())
