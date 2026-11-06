"""Table X: generalization summary from results/05_GENERALIZATION (dev-only).

Protocol: per condition, 3 train seeds x 10 eval seeds = 30 episodes per method.
Writes per-condition per-method stats into _chart_numbers.json ("generalization").
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parents[1]
SRC = ROOT / "results" / "05_GENERALIZATION" / "generalization_all_episodes.csv"

d = pd.read_csv(SRC)
d["obj"] = d["QSR"] - 0.10 * d["Mean_Under_Service_Age_s"]

METHODS = ["HQC_SAC_MAIN", "TD3", "CDA_SAC_ADAPTED"]
out = {}
for method in METHODS:
    sub = d[d["method"] == method]
    out[method] = {}
    for cond, g in sub.groupby("scenario_id"):
        out[method][cond] = {
            "n": int(len(g)),
            "QSR": round(float(g["QSR"].mean()), 4),
            "obj": round(float(g["obj"].mean()), 4),
            "P95_Outage_s": round(float(g["P95_Outage_s"].mean()), 2),
            "P5_SQA": round(float(g["P5_SQA"].mean()), 4),
            "Goodput_Mbps": round(float(g["Goodput_Mbps"].mean()), 2),
        }

spread = {}
for method in METHODS:
    qsrs = [v["QSR"] for v in out[method].values()]
    p95s = [v["P95_Outage_s"] for v in out[method].values()]
    spread[method] = {
        "QSR_min": round(min(qsrs), 4), "QSR_max": round(max(qsrs), 4),
        "QSR_span": round(max(qsrs) - min(qsrs), 4),
        "P95_max": round(max(p95s), 2),
    }

store = ROOT / "paper" / "tables" / "_chart_numbers.json"
numbers = json.loads(store.read_text(encoding="utf-8"))
numbers["generalization"] = {"methods": out, "spread": spread}
store.write_text(json.dumps(numbers, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(spread, indent=1))
print("wrote generalization key into _chart_numbers.json")
