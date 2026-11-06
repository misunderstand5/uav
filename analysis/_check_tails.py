import pathlib
import numpy as np
import pandas as pd

groups = {
    "SCHED_NO_AGE": "runs/TVT_20261103/SCHED_NO_AGE",
    "SCHED_NO_1SWAP": "runs/TVT_20261103/SCHED_NO_1SWAP",
    "FLAT_RELAY": "runs/TVT_20261103/FLAT_RELAY_IMMEDIATE",
    "JOINT_SAC": "runs/TVT_20261103/JOINT_SAC_PM",
    "TD3": "runs/TVT_20261103/TD3",
    "PPO": "runs/TVT_20261103/PPO",
}
for name, p in groups.items():
    q, p5, p95 = [], [], []
    for d in sorted(pathlib.Path(p).glob("seed_*")):
        f = d / "episodes.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f, encoding="utf-8-sig").tail(50)
        q.append(df.strict_service.mean())
        p5.append(df.lifecycle_strict_p05.mean())
        if "lifecycle_strict_max_outage_p95_s" in df:
            p95.append(df.lifecycle_strict_max_outage_p95_s.mean())
    print(f"{name:16s} QSR {np.mean(q):.3f} P5 {np.mean(p5):.3f} "
          f"P95 {np.mean(p95) if p95 else float('nan'):.2f} seeds={len(q)}")
