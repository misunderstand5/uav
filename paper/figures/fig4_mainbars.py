"""Fig. 4: sealed main comparison — QSR vs obj grouped bars with bootstrap CI."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, SKY, GRAY, DOUBLE_W

apply_style()
root = Path(__file__).parents[2]
ci = json.loads((root / "paper" / "tables" / "_chart_numbers.json").read_text())["obj_ci"]

# Ordered by obj (desc). QSR values from the sealed main table (Table I).
methods = [
    ("Proposed", "HQC_SAC_MAIN", 0.8043, BLUE, SKY),
    ("w/o 1-swap", "HQC_SAC_NO_1SWAP", 0.8020, GRAY, "#D9D9D9"),
    ("TD3", "TD3", 0.7684, GRAY, "#D9D9D9"),
    ("Recursive", "RECURSIVE_CREDIT_H128", 0.7494, GRAY, "#D9D9D9"),
    ("CDA-SAC", "CDA_SAC_ADAPTED", 0.7434, GRAY, "#D9D9D9"),
    ("PPO", "PPO", 0.7380, GRAY, "#D9D9D9"),
    ("w/o age", "HQC_SAC_NO_AGE", 0.8073, GRAY, "#D9D9D9"),
]

names = [m[0] for m in methods]
qsr = np.array([m[2] for m in methods])
obj = np.array([ci[m[1]]["mean"] for m in methods])
obj_lo = np.array([ci[m[1]]["mean"] - ci[m[1]]["lo"] for m in methods])
obj_hi = np.array([ci[m[1]]["hi"] - ci[m[1]]["mean"] for m in methods])
obj_dark = [m[3] for m in methods]
qsr_light = [m[4] for m in methods]

x = np.arange(len(methods))
w = 0.36
fig, ax = plt.subplots(figsize=(DOUBLE_W, 2.55))

b_qsr = ax.bar(x - w / 2, qsr, w, color=qsr_light, edgecolor="none", zorder=2)
b_obj = ax.bar(x + w / 2, obj, w, color=obj_dark, edgecolor="none", zorder=2)
ax.errorbar(
    x + w / 2, obj, yerr=(obj_lo, obj_hi),
    fmt="none", ecolor="#1A1A1A", elinewidth=0.9, capsize=2.2, capthick=0.9, zorder=3,
)

for xi, (q, o, hi) in enumerate(zip(qsr, obj, obj_hi)):
    ax.text(xi - w / 2, q + 0.010, f"{q:.3f}", ha="center", va="bottom", fontsize=6, color="0.45")
    ax.text(xi + w / 2, o + hi + 0.012, f"{o:.3f}", ha="center", va="bottom", fontsize=6.5, color="#1A1A1A", fontweight="bold")

# Highlight the w/o age contrast: QSR alone misleads.
ax.annotate(
    "QSR alone misleads:\nhigh ratio, lowest obj",
    xy=(x[-1] + w / 2, obj[-1]),
    xytext=(x[-1] + 0.72, 0.60),
    fontsize=6, color="0.3", ha="left",
    arrowprops=dict(arrowstyle="-", color="0.55", lw=0.7),
)

ax.set_xticks(x)
ax.set_xticklabels(names, rotation=0)
ax.set_ylabel("Value")
ax.set_ylim(0, 0.92)
ax.grid(axis="y")
ax.legend(
    handles=[
        Patch(facecolor="#D9D9D9", edgecolor="none", label="QSR (session ratio)"),
        Patch(facecolor=BLUE, edgecolor="none", label="obj, proposed"),
        Patch(facecolor=GRAY, edgecolor="none", label="obj, others"),
    ],
    loc="upper left", frameon=False, handlelength=1.4, columnspacing=1.0,
)
ax.text(0.995, 0.97, "whiskers: 95% bootstrap CI of obj", transform=ax.transAxes,
        fontsize=6, color="0.45", va="top", ha="right")
fig.tight_layout()
save(fig, Path(__file__).parent / "fig4_mainbars")
