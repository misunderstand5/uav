"""Fig. 6: per-seed stability — (a) P95 log dot plot, (b) obj dot plot."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, SKY, ORANGE, PURPLE, SINGLE_W

apply_style()
root = Path(__file__).parents[2]
ps = json.loads((root / "paper" / "tables" / "_chart_numbers.json").read_text())["per_seed"]
ci = json.loads((root / "paper" / "tables" / "_chart_numbers.json").read_text())["obj_ci"]

SEED_COLORS = {7: SKY, 17: ORANGE, 27: PURPLE}
MEAN_COLOR = "#1A1A1A"
KEY = {
    "HQC_SAC_MAIN": "Proposed",
    "HQC_SAC_NO_1SWAP": "w/o 1-swap",
    "HQC_SAC_NO_AGE": "w/o age",
    "TD3": "TD3",
    "PPO": "PPO",
    "CDA_SAC_ADAPTED": "CDA-SAC",
    "RECURSIVE_CREDIT_H128": "Recursive",
}

# ---- (a) P95 outage, log scale, 7 methods ordered by mean P95 desc ----
rows_a = sorted(
    ps.items(),
    key=lambda kv: np.mean([v["P95"] for v in kv[1].values()]),
    reverse=True,
)
fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(SINGLE_W, 4.35), gridspec_kw={"height_ratios": [0.62, 0.38]})

for i, (key, seeds) in enumerate(rows_a):
    label = KEY[key]
    for seed, v in seeds.items():
        ax_a.plot(v["P95"], i, marker="o", markersize=4.2,
                  markerfacecolor=SEED_COLORS[int(seed)], markeredgecolor="none",
                  linestyle="none", zorder=3)
    mean = np.mean([v["P95"] for v in seeds.values()])
    ax_a.plot(mean, i, marker="D", markersize=4.6, markerfacecolor="none",
              markeredgecolor=MEAN_COLOR, markeredgewidth=1.0, linestyle="none", zorder=4)
    if label == "Proposed":
        ax_a.axhspan(i - 0.42, i + 0.42, color=BLUE, alpha=0.07, zorder=0)

ax_a.set_yticks(range(len(rows_a)))
ax_a.set_yticklabels([KEY[k] for k, _ in rows_a])
for tick_label in ax_a.get_yticklabels():
    if tick_label.get_text() == "Proposed":
        tick_label.set_fontweight("bold")
ax_a.set_xscale("log")
ax_a.set_xlim(6, 100)
ax_a.set_ylim(-0.55, len(rows_a) - 0.45)
ax_a.set_xlabel("P95 outage (s), log scale")
ax_a.grid(axis="x", which="both")
ax_a.grid(axis="x", which="minor", alpha=0.12)
ax_a.set_title("(a) P95 outage per training seed", loc="left", pad=4)

# ---- (b) obj per seed, three scheduler variants ----
rows_b = ["HQC_SAC_NO_AGE", "HQC_SAC_NO_1SWAP", "HQC_SAC_MAIN"]
for i, key in enumerate(rows_b):
    for seed, v in ps[key].items():
        ax_b.plot(v["obj"], i, marker="o", markersize=4.2,
                  markerfacecolor=SEED_COLORS[int(seed)], markeredgecolor="none",
                  linestyle="none", zorder=3)
    m = ci[key]["mean"]
    ax_b.plot(m, i, marker="D", markersize=4.6, markerfacecolor="none",
              markeredgecolor=MEAN_COLOR, markeredgewidth=1.0, linestyle="none", zorder=4)
    ax_b.text(m, i + 0.30, f"{m:.3f}", ha="center", va="bottom",
              fontsize=6, color=MEAN_COLOR)
    if key == "HQC_SAC_MAIN":
        ax_b.axhspan(i - 0.42, i + 0.42, color=BLUE, alpha=0.07, zorder=0)

ax_b.set_yticks(range(len(rows_b)))
ax_b.set_yticklabels([KEY[k] for k in rows_b])
ax_b.get_yticklabels()[2].set_fontweight("bold")
ax_b.set_xlim(0.35, 0.85)
ax_b.set_ylim(-0.55, len(rows_b) - 0.45)
ax_b.set_xlabel("obj = QSR $-$ 0.1 $\\times$ mean under-service age")
ax_b.grid(axis="x")
ax_b.set_title("(b) Objective per training seed", loc="left", pad=4)

# Seed legend in panel (a)
from matplotlib.lines import Line2D
handles = [Line2D([], [], marker="o", linestyle="none", markerfacecolor=c,
                  markeredgecolor="none", markersize=4.5, label=f"Seed {s}")
           for s, c in SEED_COLORS.items()]
handles.append(Line2D([], [], marker="D", linestyle="none", markerfacecolor="none",
                      markeredgecolor=MEAN_COLOR, markeredgewidth=1.0, markersize=4.5,
                      label="Mean"))
ax_a.legend(handles=handles, loc="lower left", frameon=False, ncol=2,
            columnspacing=1.0, handletextpad=0.4)

fig.tight_layout(h_pad=1.8)
save(fig, Path(__file__).parent / "fig6_perseed")
