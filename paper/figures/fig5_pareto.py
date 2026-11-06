"""Fig. 5: lambda-variant trade-off (dev set, 90 episodes) with Pareto frontier."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, GRAY, ORANGE, SINGLE_W

apply_style()

# (label, QSR, P95, marker, facecolor, edgecolor, is_frontier)
points = [
    ("(0.10, 0.40)", 0.7884, 6.26, "o", GRAY, GRAY, True),
    ("(0.05, 0.20)", 0.7966, 8.33, "o", GRAY, GRAY, True),
    ("(0.10, 0.10)\nmain", 0.8096, 10.19, "*", BLUE, BLUE, True),
    ("(0.10, 0.20)", 0.7943, 8.67, "o", "white", GRAY, False),
    ("(0.20, 0.20)", 0.7865, 10.05, "o", "white", GRAY, False),
    ("(0.10, 0.00)\nno age weight", 0.7527, 69.15, "o", "white", ORANGE, False),
]

fig, ax = plt.subplots(figsize=(SINGLE_W, 2.95))

for label, q, p95, mk, fc, ec, frontier in points:
    z = 4 if frontier else 3
    ax.plot(q, p95, marker=mk, markersize=7 if mk == "*" else 5.5,
            markerfacecolor=fc, markeredgecolor=ec, markeredgewidth=0.9,
            linestyle="none", zorder=z)

# Pareto frontier staircase (steps-post through the three non-dominated points)
fx = [p[1] for p in points if p[6]]
fy = [p[2] for p in points if p[6]]
ax.plot(fx, fy, color=GRAY, linestyle=(0, (5, 3)), linewidth=1.0,
        drawstyle="steps-post", zorder=2)

# Labels (manual offsets to avoid collisions)
labels = {
    "(0.10, 0.40)": ((0.7884, 6.26), (-0.003, -2.4), "center", "top"),
    "(0.05, 0.20)": ((0.7966, 8.33), (0.000, +1.8), "center", "bottom"),
    "(0.10, 0.10)\nmain": ((0.8096, 10.19), (0.000, +3.2), "center", "bottom"),
    "(0.10, 0.20)": ((0.7943, 8.67), (+0.0022, -1.9), "left", "top"),
    "(0.20, 0.20)": ((0.7865, 10.05), (-0.0035, 0.0), "right", "center"),
    "(0.10, 0.00)\nno age weight": ((0.7527, 69.15), (+0.0022, 0.0), "left", "center"),
}
for label, ((lx, ly), (dx, dy), ha, va) in labels.items():
    ax.text(lx + dx, ly + dy, label, fontsize=6, color="0.2",
            ha=ha, va=va, linespacing=1.15)

# "better" direction arrow (bottom-right corner: higher QSR, lower P95)
ax.annotate(
    "better", xy=(0.8152, 0.6), xytext=(0.8060, 2.0),
    fontsize=6.5, color="0.3", ha="right",
    arrowprops=dict(arrowstyle="-|>", color="0.3", lw=0.8, shrinkA=0, shrinkB=0),
)

ax.set_xlabel("QSR (service ratio, higher is better)")
ax.set_ylabel("P95 outage (s, lower is better)")
ax.set_xlim(0.742, 0.818)
ax.set_ylim(0, 75)
ax.grid(axis="both")
fig.tight_layout()
save(fig, Path(__file__).parent / "fig5_pareto")
