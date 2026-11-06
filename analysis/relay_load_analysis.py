"""VI-I relay load-balance analysis from sealed data (zero reruns)."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parents[1]
SEALED = ROOT / "results" / "09_FINAL_TEST100_SEALED"
OUT_JSON = ROOT / "paper" / "tables" / "_chart_numbers.json"

KEY = {
    "HQC_SAC_MAIN": "Proposed",
    "HQC_SAC_NO_1SWAP": "w/o 1-swap",
    "HQC_SAC_NO_AGE": "w/o age",
    "TD3": "TD3",
    "PPO": "PPO",
    "CDA_SAC_ADAPTED": "CDA-SAC",
    "RECURSIVE_CREDIT_H128": "Recursive",
}

METHOD_ORDER = [
    "HQC_SAC_MAIN", "HQC_SAC_NO_1SWAP", "HQC_SAC_NO_AGE",
    "TD3", "PPO", "CDA_SAC_ADAPTED", "RECURSIVE_CREDIT_H128",
]


def jain(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if x.sum() <= 0:
        return float("nan")
    return float(x.sum() ** 2 / (len(x) * (x ** 2).sum()))


# ---- load per-episode per-relay aggregates ----
frames, ep_frames = [], []
for f in glob.glob(str(SEALED / "*relay_slots.csv")):
    df = pd.read_csv(f)
    frames.append(
        df.groupby(["eval_seed", "relay_id"], as_index=False).agg(
            method=("method", "first"),
            train_seed=("train_seed", "first"),
            acc_load=("relay_access_load_ratio", "mean"),
            bh_load=("relay_backhaul_load_ratio", "mean"),
            users=("relay_assigned_user_count", "mean"),
            power=("relay_power_w", "mean"),
            qsr=("relay_qsr", "mean"),
            goodput=("relay_goodput_mbps", "mean"),
        )
    )
slots = pd.concat(frames, ignore_index=True)

relay = {}
for method, g in slots.groupby("method"):
    # per-relay values averaged over 300 episodes, then Jain across the 4 relays
    per_relay = g.groupby("relay_id").mean(numeric_only=True)
    relay[method] = {
        "relay_means": {
            str(r): {
                "acc_load": round(float(per_relay.loc[r, "acc_load"]), 3),
                "bh_load": round(float(per_relay.loc[r, "bh_load"]), 3),
                "users": round(float(per_relay.loc[r, "users"]), 2),
                "power": round(float(per_relay.loc[r, "power"]), 3),
                "qsr": round(float(per_relay.loc[r, "qsr"]), 4),
                "goodput": round(float(per_relay.loc[r, "goodput"]), 2),
            }
            for r in sorted(per_relay.index)
        },
        "jain": {
            "acc_load": round(jain(per_relay["acc_load"].values), 4),
            "bh_load": round(jain(per_relay["bh_load"].values), 4),
            "users": round(jain(per_relay["users"].values), 4),
            "power": round(jain(per_relay["power"].values), 4),
            "qsr": round(jain(per_relay["qsr"].values), 4),
            "goodput": round(jain(per_relay["goodput"].values), 4),
        },
    }

# ---- backlog time series: total assigned users per step (mean/min/max over 300 eps) ----
# computed from raw relay_slots files (need step-level sums)
raw = []
for f in glob.glob(str(SEALED / "*relay_slots.csv")):
    d = pd.read_csv(f, usecols=["eval_seed", "method", "relay_assigned_user_count", "step"])
    raw.append(d.groupby(["eval_seed", "method", "step"], as_index=False)["relay_assigned_user_count"].sum())
raw = pd.concat(raw, ignore_index=True)
backlog = {}
for method in METHOD_ORDER:
    g = raw[raw["method"] == method].groupby("step")["relay_assigned_user_count"]
    backlog[method] = {
        "mean": g.mean().round(2).tolist(),
        "lo": g.min().tolist(),
        "hi": g.max().tolist(),
    }
backlog_df = pd.DataFrame({
    "step": list(range(1, 401)),
    **{f"{m}_mean": backlog[m]["mean"] for m in METHOD_ORDER},
    **{f"{m}_lo": backlog[m]["lo"] for m in METHOD_ORDER},
    **{f"{m}_hi": backlog[m]["hi"] for m in METHOD_ORDER},
})
backlog_df.to_csv(ROOT / "analysis" / "relay_backlog_bins.csv", index=False)

# ---- per-episode obj distribution from episodes.csv ----
eps = []
for f in glob.glob(str(SEALED / "*episodes.csv")):
    d = pd.read_csv(f)
    d = d.rename(columns={d.columns[0]: d.columns[0].lstrip("\ufeff")})
    d["obj"] = d["QSR"] - 0.10 * d["Mean_Under_Service_Age_s"]
    eps.append(d[["eval_seed", "train_seed", "method", "QSR", "obj", "P95_Outage_s", "Goodput_Mbps"]])
eps = pd.concat(eps, ignore_index=True)
eps.to_csv(ROOT / "analysis" / "episode_obj_dist.csv", index=False)

# sanity: per-method mean obj should match the official bootstrap means
obj_means = eps.groupby("method")["obj"].mean().round(4)
print("=== per-method mean obj (episode-mean) ===")
for m in METHOD_ORDER:
    print(f"{KEY[m]:>16} {obj_means[m]:.4f}")

# ---- per-episode per-relay QSR / power for boxplots ----
box = []
for f in glob.glob(str(SEALED / "*relay_slots.csv")):
    d = pd.read_csv(f, usecols=["eval_seed", "method", "relay_id", "relay_qsr", "relay_power_w",
                                "relay_backhaul_load_ratio"])
    box.append(
        d.groupby(["eval_seed", "method", "relay_id"], as_index=False).agg(
            qsr=("relay_qsr", "mean"),
            power=("relay_power_w", "mean"),
            bh_load=("relay_backhaul_load_ratio", "mean"),
        )
    )
box = pd.concat(box, ignore_index=True)
box.to_csv(ROOT / "analysis" / "relay_boxplot.csv", index=False)
print(f"wrote relay_boxplot.csv ({len(box)} rows)")

# ---- print Table IX candidate numbers ----
print("\n=== cross-relay Jain (per metric, per method) ===")
print(f"{'method':>16} {'acc_load':>9} {'bh_load':>9} {'users':>7} {'power':>7} {'qsr':>7} {'goodput':>8}")
for m in METHOD_ORDER:
    j = relay[m]["jain"]
    print(f"{KEY[m]:>16} {j['acc_load']:>9.4f} {j['bh_load']:>9.4f} {j['users']:>7.4f} {j['power']:>7.4f} {j['qsr']:>7.4f} {j['goodput']:>8.4f}")

print("\n=== per-relay means, MAIN ===")
for r, v in relay["HQC_SAC_MAIN"]["relay_means"].items():
    print(f"relay {r}: acc_load {v['acc_load']:.3f} bh_load {v['bh_load']:.3f} users {v['users']:.2f} power {v['power']:.3f} qsr {v['qsr']:.4f} goodput {v['goodput']:.2f}")

# ---- persist ----
chart = json.loads(OUT_JSON.read_text())
chart["relay_load"] = {
    "methods": {m: relay[m] for m in METHOD_ORDER},
    "ep_obj_means": {m: float(obj_means[m]) for m in METHOD_ORDER},
}
OUT_JSON.write_text(json.dumps(chart, indent=1))
print("\nwrote relay_load + ep_obj_means into _chart_numbers.json")
