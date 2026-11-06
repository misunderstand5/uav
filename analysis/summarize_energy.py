"""Aggregate E4 energy re-evaluation into per-method efficiency metrics."""
from __future__ import annotations
import csv, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

IN_DIR = ROOT / "results" / "06_ENERGY"
OUT = ROOT / "analysis" / "energy_summary_20261104.csv"

METHODS = ("HQC_SAC_MAIN", "TD3", "CDA_SAC_ADAPTED", "PPO")


def load_episodes() -> list[dict]:
    rows: list[dict] = []
    for m in METHODS:
        for s in (7, 17, 27):
            path = IN_DIR / f"nominal__{m}__trainseed_{s}__episodes.csv"
            if not path.exists():
                raise FileNotFoundError(f"Missing energy episode CSV: {path}")
            with path.open("r", newline="", encoding="utf-8-sig") as f:
                rows.extend(csv.DictReader(f))
    return rows


def main() -> None:
    rows = load_episodes()
    per_episode = []
    for r in rows:
        energy = float(r["total_energy_j"])
        qsr = float(r["QSR"])
        goodput = float(r["Goodput_Mbps"])
        duration = float(r["duration_s"])
        bits = goodput * 1e6 * duration
        per_episode.append({
            "method": r["method"], "train_seed": int(r["train_seed"]),
            "eval_seed": int(r["eval_seed"]),
            "QSR": qsr, "Goodput_Mbps": goodput,
            "c_phys_energy_j": float(r["c_phys_energy_j"]),
            "m_energy_j": float(r["m_energy_j"]),
            "total_energy_j": energy, "c_path_m": float(r["c_path_m"]),
            "QSR_per_J": qsr / max(energy, 1e-12),
            "bits_per_J": bits / max(energy, 1e-12),
        })
    summary = []
    for m in METHODS:
        sub = [r for r in per_episode if r["method"] == m]
        if not sub:
            continue
        for metric in ("QSR", "Goodput_Mbps", "c_phys_energy_j", "m_energy_j",
                       "total_energy_j", "c_path_m", "QSR_per_J", "bits_per_J"):
            vals = np.asarray([r[metric] for r in sub])
            summary.append({"method": m, "metric": metric,
                            "mean": float(vals.mean()), "std": float(vals.std()),
                            "n": int(vals.size)})
        summary.append({"method": m, "metric": "c_phys_energy_share",
                        "mean": float(np.mean([r["c_phys_energy_j"] / max(r["total_energy_j"], 1e-12) for r in sub])),
                        "std": float(np.std([r["c_phys_energy_j"] / max(r["total_energy_j"], 1e-12) for r in sub])),
                        "n": len(sub)})
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["method", "metric", "mean", "std", "n"])
        w.writeheader()
        w.writerows(summary)
    print(f"[SUCCESS] energy summary written to {OUT} ({len(per_episode)} episodes)", flush=True)
    for s in summary:
        if s["metric"] in ("QSR", "Goodput_Mbps", "total_energy_j", "c_path_m",
                           "QSR_per_J", "bits_per_J", "c_phys_energy_share"):
            print(f"  {s['method']:18s} {s['metric']:20s} {s['mean']:.6g}", flush=True)


if __name__ == "__main__":
    main()
