"""Paired comparison of HQC-SAC main (lambda 0.10/0.10) vs LS020 (0.10/0.20)
on identical evaluation scenes.

Main: original 400EP run's heldout_eval_episodes.csv (10 scenes, 9000-9009)
      plus, once available, results/02_COMMON30_VALIDATION (30 scenes).
LS020: runs/HQC_SAC_FIXED500_B_LS020_400EP/seed_*/heldout_eval_episodes.csv.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
ORIG = Path(r"C:\Users\admin\Desktop\HQC_SAC_FIXED500_DYNAMIC_USERS_QOS_B_400EP_Seeds_7_17_27"
            r"\HQC_SAC_FIXED500_DYNAMIC_USERS_B_400EP_Seeds_7_17_27"
            r"\runs\HQC_SAC_FIXED500_B_400EP")
LS020 = ROOT / "runs" / "HQC_SAC_FIXED500_B_LS020_400EP"

METRICS = {
    "strict_service": "QSR",
    "lifecycle_strict_mean": "Avg_SQA",
    "lifecycle_strict_p05": "P5_SQA",
    "lifecycle_strict_fairness": "Jain",
    "lifecycle_strict_max_outage_p95_s": "P95_Outage",
    "aggregate_goodput_mbps_mean": "Goodput",
    "age_objective": "AgeObj",
    "c_path_m": "C_Path",
}

def load_dir(root, n_seeds):
    frames = []
    for s in (7, 17, 27):
        f = root / f"seed_{s}" / "heldout_eval_episodes.csv"
        if not f.exists():
            print("missing", f)
            continue
        d = pd.read_csv(f, encoding="utf-8-sig")
        d.columns = [c.strip() for c in d.columns]
        d["train_seed"] = s
        # normalise scene column
        scene = "seed" if "seed" in d.columns else "eval_seed"
        d = d.rename(columns={scene: "scene"})
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def boot_ci(x, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return float(np.quantile(means, .025)), float(np.quantile(means, .975))

def compare(main_df, ls_df, tag):
    print(f"\n===== {tag}: paired scenes {sorted(set(main_df.scene) & set(ls_df.scene))} =====")
    rows = []
    for col, name in METRICS.items():
        if col not in main_df or col not in ls_df:
            print(f"  skip {name} (missing column)")
            continue
        m = main_df.set_index(["train_seed", "scene"])[col]
        l = ls_df.set_index(["train_seed", "scene"])[col]
        j = pd.concat([m.rename("main"), l.rename("ls020")], axis=1).dropna()
        if j.empty:
            continue
        diff = j["main"] - j["ls020"]
        lo, hi = boot_ci(diff.values)
        rows.append({
            "metric": name,
            "main_mean": j["main"].mean(), "ls020_mean": j["ls020"].mean(),
            "paired_diff(main-ls020)": diff.mean(),
            "ci95_low": lo, "ci95_high": hi,
            "main_win_rate": float((diff > 0).mean()),
            "n_pairs": len(j),
            "diff_by_trainseed": "; ".join(f"{s}:{diff.loc[s].mean():+.4f}" for s in (7, 17, 27) if s in diff.index.get_level_values(0)),
        })
    t = pd.DataFrame(rows)
    print(t.to_string(index=False, float_format=lambda x: f"{x:+.4f}" if abs(x) < 10 else f"{x:.2f}"))
    return t

main10 = load_dir(ORIG, 10)
ls30 = load_dir(LS020, 30)
common10 = sorted(set(main10.scene) & set(ls30.scene))
t10 = compare(main10[main10.scene.isin(common10)], ls30[ls30.scene.isin(common10)], "MAIN(0.1/0.1) vs LS020(0.1/0.2) on 9000-9009")
t10.to_csv(OUT / "main_vs_ls020_10scenes.csv", index=False, encoding="utf-8-sig")

# 30-scene main eval, if the background evaluation has finished
main30_dir = ROOT / "results" / "02_COMMON30_VALIDATION"
if main30_dir.exists():
    frames = []
    for s in (7, 17, 27):
        f = main30_dir / f"nominal__HQC_SAC_MAIN__trainseed_{s}__episodes.csv"
        if f.exists():
            d = pd.read_csv(f, encoding="utf-8-sig")
            d.columns = [c.strip() for c in d.columns]
            d["train_seed"] = s
            frames.append(d.rename(columns={"eval_seed": "scene"}))
    if len(frames) == 3:
        main30 = pd.concat(frames, ignore_index=True)
        main30 = main30.rename(columns={
            "QSR": "strict_service", "Avg_SQA": "lifecycle_strict_mean",
            "P5_SQA": "lifecycle_strict_p05", "Jain_SQA": "lifecycle_strict_fairness",
            "P95_Outage_s": "lifecycle_strict_max_outage_p95_s",
            "Goodput_Mbps": "aggregate_goodput_mbps_mean",
        })
        t30 = compare(main30, ls30, "MAIN(0.1/0.1) vs LS020(0.1/0.2) on 9000-9029")
        t30.to_csv(OUT / "main_vs_ls020_30scenes.csv", index=False, encoding="utf-8-sig")
    else:
        print("\n[30-scene main eval not complete yet]")
