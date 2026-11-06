"""Audit every training run and every evaluation output on disk."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    ("MAIN", ROOT / "anchors" / "HQC_SAC_MAIN"),
    ("CDA", ROOT / "runs" / "PHASE_II" / "CDA_SAC_ADAPTED"),
    ("RECURSIVE", ROOT / "runs" / "PHASE_III" / "RECURSIVE_CREDIT_H128"),
    ("MOTION", ROOT / "runs" / "PHASE_III" / "MOTION_ONLY"),
    ("POWER", ROOT / "runs" / "PHASE_III" / "POWER_ONLY"),
    ("LS020", ROOT / "runs" / "HQC_SAC_FIXED500_B_LS020_400EP"),
    ("R005_S020", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R005_S020"),
    ("R020_S020", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "R020_S020"),
    ("S040_R010", ROOT / "runs" / "HQC_SAC_SENSITIVITY" / "S040_R010"),
    ("FLAT_RELAY", ROOT / "runs" / "TVT_20261103" / "FLAT_RELAY_IMMEDIATE"),
    ("JOINT_SAC", ROOT / "runs" / "TVT_20261103" / "JOINT_SAC_PM"),
    ("TD3", ROOT / "runs" / "TVT_20261103" / "TD3"),
    ("PPO", ROOT / "runs" / "TVT_20261103" / "PPO"),
    ("SCHED_NO_AGE", ROOT / "runs" / "TVT_20261103" / "SCHED_NO_AGE"),
    ("SCHED_NO_1SWAP", ROOT / "runs" / "TVT_20261103" / "SCHED_NO_1SWAP"),
]

rows = []
for name, root in GROUPS:
    if not root.exists():
        continue
    for sd in sorted(root.glob("seed_*")):
        if not sd.is_dir():
            continue
        ep = sd / "episodes.csv"
        ts = sd / "train_summary.json"
        ap = sd / "agent.pt"
        n = -1
        last_ep = None
        last_qsr = None
        last_critic = None
        last5_qsr = None
        if ep.exists():
            d = pd.read_csv(ep, encoding="utf-8-sig")
            n = len(d)
            if "episode" in d:
                last_ep = int(d.episode.max())
            if "strict_service" in d:
                last_qsr = float(d.strict_service.iloc[-1])
                last5_qsr = float(d.strict_service.tail(5).mean())
            if "critic_loss" in d:
                last_critic = float(d.critic_loss.iloc[-1])
        summary = {}
        if ts.exists():
            try:
                summary = json.loads(ts.read_text(encoding="utf-8"))
            except Exception:
                summary = {}
        complete = n >= 400 and ap.exists() and bool(summary)
        rows.append({
            "group": name, "seed": sd.name.replace("seed_", ""),
            "rows": n, "last_ep": last_ep,
            "episodes_meta": summary.get("episodes"),
            "steps_meta": summary.get("steps"),
            "updates_meta": summary.get("updates"),
            "agent": ap.exists(), "summary": bool(summary),
            "early_stop": summary.get("early_stop_reason"),
            "last_qsr": last_qsr, "last5_qsr": last5_qsr,
            "last_critic": last_critic,
            "status": "COMPLETE" if complete else "INCOMPLETE",
        })

df = pd.DataFrame(rows)
df.to_csv(ROOT / "analysis" / "experiment_audit_training.csv", index=False, encoding="utf-8-sig")
print("=== TRAINING ===")
print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print("\nstatus counts:", df.status.value_counts().to_dict())
bad = df[df.status != "COMPLETE"]
print("incomplete:", bad[["group", "seed", "rows", "agent", "summary"]].to_dict("records"))

# evaluation inventory
print("\n=== EVALUATION ===")
def count_eps(pattern_dir: Path, pattern: str):
    fs = sorted(pattern_dir.glob(pattern)) if pattern_dir.exists() else []
    total = 0
    seeds = set()
    for f in fs:
        try:
            d = pd.read_csv(f, encoding="utf-8-sig")
            total += len(d)
            if "eval_seed" in d:
                seeds |= set(d.eval_seed.astype(int).tolist())
        except Exception:
            pass
    return len(fs), total, len(seeds)

for label, d, pat in [
    ("common30 core", ROOT / "results" / "02_COMMON30_VALIDATION", "nominal__*__trainseed_*__episodes.csv"),
    ("scheduler frozen", ROOT / "results" / "03_SCHEDULER_ABLATION", "*/*__trainseed_*__episodes.csv"),
    ("lambda variants", ROOT / "results" / "04_LAMBDA_VARIANTS", "*/*__trainseed_*__episodes.csv"),
]:
    files, eps, seeds = count_eps(d, pat)
    print(f"{label:20s} files={files:3d} episodes={eps:4d} scenes={seeds:3d} dir={d.relative_to(ROOT)}")

pi = ROOT / "results" / "02_PI_BCD_SCA" / "full_common30"
if pi.exists():
    seeds = [x.name for x in pi.glob("seed_*")]
    print(f"PI common30          seeds={len(seeds)} dir={pi.relative_to(ROOT)}")
else:
    print("PI common30          MISSING")

for label, d in [
    ("generalization", ROOT / "results" / "05_GENERALIZATION"),
    ("final test100", ROOT / "results" / "08_FINAL_TEST100"),
    ("common30 new methods", ROOT / "results" / "02_COMMON30_VALIDATION"),
]:
    print(f"{label:20s} exists={d.exists()} dir={d.relative_to(ROOT)}")
