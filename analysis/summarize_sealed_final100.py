"""Official sealed final-100 statistics: paired bootstrap vs main method.

Consumes results/09_FINAL_TEST100_SEALED exactly once after the sealed run
completes.  Pairing is by (train_seed, eval_seed); bootstrap n=20000 seed=0.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

IN_DIR = ROOT / "results" / "09_FINAL_TEST100_SEALED"
OUT = ROOT / "analysis" / "sealed_final100_comparison_20261104.csv"
MAIN = "HQC_SAC_MAIN"
METHODS = ("HQC_SAC_MAIN", "CDA_SAC_ADAPTED", "RECURSIVE_CREDIT_H128",
           "TD3", "PPO", "HQC_SAC_NO_AGE", "HQC_SAC_NO_1SWAP")
METRICS = ("QSR", "P5_SQA", "P95_Outage_s", "Jain_SQA", "Goodput_Mbps",
           "Mean_Longest_Outage_s")
N_BOOT = 20000
RNG = np.random.default_rng(0)


def load() -> dict[str, list[dict]]:
    data: dict[str, list[dict]] = {}
    for m in METHODS:
        rows: list[dict] = []
        for s in (7, 17, 27):
            path = IN_DIR / f"nominal__{m}__trainseed_{s}__episodes.csv"
            if not path.exists():
                raise FileNotFoundError(f"Missing sealed episode CSV: {path}")
            with path.open("r", newline="", encoding="utf-8-sig") as f:
                rows.extend(csv.DictReader(f))
        if len(rows) != 300:
            raise RuntimeError(f"Sealed set for {m} has {len(rows)} episodes, expected 300")
        data[m] = rows
    return data


def paired_bootstrap(base: np.ndarray, other: np.ndarray) -> dict[str, float]:
    """Diff = base - other; positive favors base (main)."""
    d = base - other
    n = d.size
    means = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = RNG.integers(0, n, n)
        means[i] = float(np.mean(d[idx]))
    return {
        "d": float(np.mean(d)),
        "ci95_lo": float(np.quantile(means, 0.025)),
        "ci95_hi": float(np.quantile(means, 0.975)),
        "win": float(np.mean(means > 0.0)),
    }


def main() -> None:
    data = load()
    rows = []
    for m in METHODS:
        rows.append({"method": m, **{f"mean_{k}": float(np.mean([float(r[k]) for r in data[m]])) for k in METRICS}, "n": 300})
    main_rows = data[MAIN]
    for m in METHODS:
        if m == MAIN:
            continue
        other_rows = data[m]
        pair = {(int(r["train_seed"]), int(r["eval_seed"])): r for r in main_rows}
        other_map = {(int(r["train_seed"]), int(r["eval_seed"])): r for r in other_rows}
        keys = sorted(pair.keys())
        for metric in METRICS:
            base = np.asarray([float(pair[k][metric]) for k in keys])
            other = np.asarray([float(other_map[k][metric]) for k in keys])
            boot = paired_bootstrap(base, other)
            row = next(r for r in rows if r["method"] == m)
            row[f"d_{metric}"] = boot["d"]
            row[f"ci95lo_{metric}"] = boot["ci95_lo"]
            row[f"ci95hi_{metric}"] = boot["ci95_hi"]
            row[f"win_{metric}"] = boot["win"]
    keys = sorted({k for r in rows for k in r})
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"[SUCCESS] sealed statistics written to {OUT}", flush=True)
    for r in rows:
        print(f"  {r['method']:22s} QSR={r['mean_QSR']:.4f} P5={r['mean_P5_SQA']:.4f} "
              f"P95={r['mean_P95_Outage_s']:.2f}s Jain={r['mean_Jain_SQA']:.4f} "
              f"Goodput={r['mean_Goodput_Mbps']:.2f}", flush=True)
        if r["method"] != MAIN:
            print(f"    vs main: d_QSR={r['d_QSR']:+.4f} CI=[{r['ci95lo_QSR']:+.4f},{r['ci95hi_QSR']:+.4f}] "
                  f"win={r['win_QSR']:.3f} | d_P95={r['d_P95_Outage_s']:+.2f}s CI=[{r['ci95lo_P95_Outage_s']:+.2f},{r['ci95hi_P95_Outage_s']:+.2f}] win={r['win_P95_Outage_s']:.3f}", flush=True)


if __name__ == "__main__":
    main()
