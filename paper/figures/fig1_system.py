"""Fig. 1: two-tier UAV system model schematic (vector, IEEE style)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, GRAY, DOUBLE_W

apply_style()
fig, ax = plt.subplots(figsize=(DOUBLE_W, 2.45))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.06)
ax.axis("off")

GU_DARK = "#3B3B3B"
GU_LIGHT = "#A8A8A8"
COVER = "#8C8C8C"

def drone(x, y, r=0.021, color=GRAY, face="white"):
    ax.add_patch(Circle((x, y), r, facecolor=face, edgecolor=color, lw=1.1, zorder=6))
    ax.plot([x - r * 1.7, x + r * 1.7], [y, y], color=color, lw=1.0, zorder=7,
            solid_capstyle="round")
    ax.plot([x - r * 0.55, x + r * 0.55], [y - r * 0.9, y - r * 0.9], color=color, lw=0.8, zorder=7)

# ground
ax.add_patch(Rectangle((0.0, 0.0), 1.0, 0.07, facecolor="#EDEDED", edgecolor="none", zorder=1))
ax.plot([0, 1], [0.07, 0.07], color="0.55", lw=0.7, zorder=2)
ax.text(0.5, 0.024, "500 m \u00d7 500 m area \u2014 GU sessions arrive, move, and depart",
        ha="center", va="center", fontsize=6.3, color="0.25")

xc = [0.15, 0.38, 0.62, 0.85]
rng = np.random.default_rng(4)
for k, x in enumerate(xc, start=1):
    # GU cluster
    pts = rng.uniform([x - 0.055, 0.145], [x + 0.055, 0.215], size=(6, 2))
    for j, (gx, gy) in enumerate(pts):
        ax.add_patch(Circle((gx, gy), 0.009, facecolor=GU_DARK if j == 0 else GU_LIGHT,
                            edgecolor="none", zorder=4))
    # coverage + M-UAV + access link
    ax.add_patch(Circle((x, 0.52), 0.135, fill=False, ls=(0, (4, 3)), lw=0.8,
                        edgecolor=COVER, zorder=2))
    ax.plot([x, x], [0.235, 0.50], color=GRAY, lw=1.0, zorder=3)
    drone(x, 0.52, color=GRAY)
    ax.text(x, 0.56, f"M-UAV {k}", ha="center", va="bottom", fontsize=6.5, color="0.15")

# C-UAV
cx, cy = 0.5, 0.86
drone(cx, cy, r=0.028, color=BLUE, face="#D9EDF7")
ax.text(cx, cy + 0.055, "C-UAV", ha="center", va="bottom", fontsize=6.8, color="0.1", weight="bold")
ax.text(cx, cy - 0.065, "(motion $a_M$, backhaul power $a_P$)", ha="center", va="top",
        fontsize=5.8, color="0.3")
# backhaul links (NOMA)
for x in xc:
    ax.plot([cx, x], [cy - 0.03, 0.545], color=BLUE, lw=0.9, alpha=0.85, zorder=2)
ax.text(0.265, 0.705, "NOMA backhaul", fontsize=6.2, color=BLUE, rotation=24)
ax.text(0.16, 0.385, "orthogonal\naccess", fontsize=6.0, color=GRAY, ha="center")
# motion arc (top-left free area, clear of the C-UAV label)
ax.add_patch(FancyArrowPatch((0.28, 0.985), (0.42, 0.985),
                             connectionstyle="arc3,rad=-0.45", lw=0.9,
                             arrowstyle="-|>", mutation_scale=8, color="0.35", zorder=5))
ax.text(0.35, 1.02, "trajectory", ha="center", va="bottom", fontsize=5.8, color="0.35")
# arrivals annotation
ax.annotate("", xy=(0.15, 0.13), xytext=(0.10, 0.06),
            arrowprops=dict(arrowstyle="->", color="0.45", lw=0.8))
ax.text(0.025, 0.10, "arrivals /\ndepartures", fontsize=5.8, color="0.4", va="center")

fig.tight_layout(pad=0.1)
save(fig, Path(__file__).parent / "fig1_system")
