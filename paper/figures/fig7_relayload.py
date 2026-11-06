"""Fig. 7: cross-relay load balance — (a) per-relay QSR, (b) per-relay backhaul
power, (c) episode-level objective distribution. Sealed set, no rerun."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, ORANGE, GRAY, SINGLE_W

apply_style()
root = Path(__file__).parents[2]
box = pd.read_csv(root / "analysis" / "relay_boxplot.csv")
eps = pd.read_csv(root / "analysis" / "episode_obj_dist.csv")

METHOD_ORDER = [
    "HQC_SAC_MAIN", "HQC_SAC_NO_1SWAP", "TD3", "RECURSIVE_CREDIT_H128",
    "CDA_SAC_ADAPTED", "PPO", "HQC_SAC_NO_AGE",
]
KEY = {
    "HQC_SAC_MAIN": "Proposed",
    "HQC_SAC_NO_1SWAP": "w/o 1-swap",
    "HQC_SAC_NO_AGE": "w/o age",
    "TD3": "TD3",
    "PPO": "PPO",
    "CDA_SAC_ADAPTED": "CDA-SAC",
    "RECURSIVE_CREDIT_H128": "Recursive",
}
BOX_KW = dict(patch_artist=True, boxprops=dict(linewidth=0.7),
              whiskerprops=dict(linewidth=0.7), capprops=dict(linewidth=0.7),
              flierprops=dict(marker="o", markersize=1.8, markeredgewidth=0.4,
                              alpha=0.35),
              medianprops=dict(color="#1A1A1A", linewidth=1.0))

fig, (ax_a, ax_b, ax_c) = plt.subplots(3, 1, figsize=(SINGLE_W, 4.8),
                                       gridspec_kw={"height_ratios": [1, 1, 1.35]})

def boxes(ax, methods, offsets, colors):
    for method, off, color in zip(methods, offsets, colors):
        sub = box[box["method"] == method]
        data = [sub[sub["relay_id"] == r]["qsr" if ax is ax_a else "power"]
                for r in [1, 2, 3, 4]]
        bp = ax.boxplot(data, positions=np.arange(1, 5) + off, widths=0.26, **BOX_KW)
        for patch in bp["boxes"]:
            patch.set_facecolor(color)
            patch.set_alpha(0.55)
            patch.set_edgecolor(color)
        for med in bp["medians"]:
            med.set_color("#1A1A1A")

# ---- (a) per-relay QSR: Proposed vs TD3 ----
boxes(ax_a, ["HQC_SAC_MAIN", "TD3"], [-0.15, 0.15], [BLUE, ORANGE])
ax_a.set_xticks([1, 2, 3, 4])
ax_a.set_xticklabels(["1", "2", "3", "4"])
ax_a.set_xlim(0.4, 4.6)
ax_a.set_ylim(0.60, 1.02)
ax_a.set_ylabel("Per-relay QSR")
ax_a.set_title("(a) Per-relay service quality: Proposed vs. TD3", loc="left", pad=4)
ax_a.grid(axis="y")

# ---- (b) per-relay NOMA backhaul power: Proposed vs TD3 vs w/o age ----
boxes(ax_b, ["HQC_SAC_MAIN", "TD3", "HQC_SAC_NO_AGE"], [-0.24, 0.0, 0.24],
      [BLUE, ORANGE, GRAY])
ax_b.set_xticks([1, 2, 3, 4])
ax_b.set_xticklabels(["1", "2", "3", "4"])
ax_b.set_xlim(0.4, 4.6)
ax_b.set_ylim(0.2, 3.7)
ax_b.set_ylabel("Backhaul power (W)")
ax_b.set_xlabel("Relay index")
ax_b.set_title("(b) C-UAV NOMA backhaul power allocation", loc="left", pad=4)
ax_b.grid(axis="y")

# ---- (c) episode-level objective distribution, 7 methods ----
means = eps.groupby("method")["obj"].mean()
order = [m for m in METHOD_ORDER if m in means.index]
# boxplot position 1 is at the bottom: ascending means puts the best on top
order = sorted(order, key=lambda m: means[m])
data = [eps[eps["method"] == m]["obj"] for m in order]
bp = ax_c.boxplot(data, vert=False, widths=0.55, **BOX_KW)
for i, m in enumerate(order):
    color = BLUE if m == "HQC_SAC_MAIN" else GRAY
    for patch in bp["boxes"][i:i + 1]:
        patch.set_facecolor(color)
        patch.set_alpha(0.62 if m == "HQC_SAC_MAIN" else 0.45)
        patch.set_edgecolor(color)
    ax_c.text(max(data[i]) + 0.012, i + 1, f"{means[m]:.3f}",
              ha="left", va="center", fontsize=6,
              color="#1A1A1A", fontweight="bold" if m == "HQC_SAC_MAIN" else "normal")

ax_c.set_yticks(range(1, len(order) + 1))
ax_c.set_yticklabels([KEY[m] for m in order])
ax_c.get_yticklabels()[-1].set_fontweight("bold")
ax_c.set_xlim(-0.30, 1.06)
ax_c.set_xlabel("Episode-level obj = QSR $-$ 0.1 $\\times$ mean under-service age")
ax_c.set_title("(c) Objective distribution over 300 sealed episodes", loc="left", pad=4)
ax_c.grid(axis="x")

# legends
ax_a.legend(handles=[Line2D([], [], marker="s", linestyle="none", markerfacecolor=c,
                            markeredgecolor=c, markersize=6, label=l)
                     for c, l in [(BLUE, "Proposed"), (ORANGE, "TD3")]],
            loc="upper right", frameon=True, facecolor="white", edgecolor="none",
            handletextpad=0.3, borderaxespad=0.2)
ax_b.legend(handles=[Line2D([], [], marker="s", linestyle="none", markerfacecolor=c,
                            markeredgecolor=c, markersize=6, label=l)
                     for c, l in [(BLUE, "Proposed"), (ORANGE, "TD3"),
                                  (GRAY, "w/o age")]],
            loc="upper right", frameon=False, handletextpad=0.3, borderaxespad=0.2)

fig.tight_layout(h_pad=1.6)
save(fig, Path(__file__).parent / "fig7_relayload")
