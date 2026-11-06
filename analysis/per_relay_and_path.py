"""Per-relay load balancing and C-UAV path/energy proxies from common-30 eval."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "results" / "02_COMMON30_VALIDATION"
OUT = ROOT / "analysis"

# --- C-UAV path length from trajectories -------------------------------------
path_rows = []
for f in EVAL.glob("nominal__*__trainseed_*__trajectories.csv"):
    d = pd.read_csv(f, encoding="utf-8-sig").sort_values(["train_seed", "eval_seed", "step"])
    method = f.name.split("__")[1]
    for (ts, es), x in d.groupby(["train_seed", "eval_seed"]):
        xyz = x[["c_x_m", "c_y_m", "c_z_m"]].to_numpy(float)
        path = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()) if len(xyz) > 1 else 0.0
        path_rows.append({"method": method, "train_seed": int(ts), "eval_seed": int(es),
                          "c_path_m": path, "avg_speed_mps": path / 200.0})
path = pd.DataFrame(path_rows)
path.to_csv(OUT / "c_uav_path_by_episode.csv", index=False, encoding="utf-8-sig")

# --- per-relay load balance ---------------------------------------------------
relay_rows = []
for f in EVAL.glob("nominal__*__trainseed_*__relay_slots.csv"):
    d = pd.read_csv(f, encoding="utf-8-sig", usecols=[
        "train_seed", "eval_seed", "relay_id", "relay_backhaul_load_ratio",
        "relay_goodput_mbps", "relay_qsr", "relay_assigned_user_count"])
    method = f.name.split("__")[1]
    g = d.groupby(["train_seed", "eval_seed", "relay_id"]).agg(
        bh=("relay_backhaul_load_ratio", "mean"),
        gp=("relay_goodput_mbps", "mean"),
        qsr=("relay_qsr", "mean"),
        users=("relay_assigned_user_count", "mean"),
    ).reset_index()
    for (ts, es), x in g.groupby(["train_seed", "eval_seed"]):
        gp = x.gp.to_numpy(float)
        jain = float((gp.sum() ** 2) / (len(gp) * (gp ** 2).sum())) if (gp ** 2).sum() > 0 else np.nan
        relay_rows.append({
            "method": method, "train_seed": int(ts), "eval_seed": int(es),
            "max_backhaul_load": float(x.bh.max()), "mean_backhaul_load": float(x.bh.mean()),
            "jain_relay_goodput": jain, "min_relay_qsr": float(x.qsr.min()),
            "max_relay_users": float(x.users.max()),
        })
relay = pd.DataFrame(relay_rows)
relay.to_csv(OUT / "per_relay_balance_by_episode.csv", index=False, encoding="utf-8-sig")

print("=== C-UAV path ===")
print(path.groupby("method").agg(path_m=("c_path_m", "mean"), speed_mps=("avg_speed_mps", "mean")).round(2).to_string())
print("\n=== per-relay balance ===")
print(relay.groupby("method").agg(
    max_bh=("max_backhaul_load", "mean"), mean_bh=("mean_backhaul_load", "mean"),
    jain_gp=("jain_relay_goodput", "mean"), min_relay_qsr=("min_relay_qsr", "mean"),
).round(3).to_string())
