"""Fig. 3: training convergence (per-slot reward and strict service ratio)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from ieee_style import apply_style, save, BLUE, ORANGE, GREEN, DOUBLE_W

apply_style()
df = pd.read_csv(Path(__file__).parents[2] / "analysis" / "convergence_bins.csv")
df["ep_mid"] = df["bin"].str.split("-").str[1].astype(int)

curves = {
    "Proposed (ROCS-0 + HQC-SAC)": ("MAIN(0.10/0.10)", BLUE),
    "CDA-SAC (flat)": ("CDA", ORANGE),
    "Recursive-credit H128": ("RECURSIVE", GREEN),
}

fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_W, 2.45))
for ax, col, ylab, fmt in (
    (axes[0], "reward", "Per-slot reward", "{:.1f}"),
    (axes[1], "strict_service", "Strict-QoS service ratio", "{:.2f}"),
):
    for label, (method, color) in curves.items():
        g = df[df["method"] == method].groupby("ep_mid")[col]
        mean, lo, hi = g.mean(), g.min(), g.max()
        ax.plot(mean.index, mean.values, color=color, label=label, linewidth=1.3)
        ax.fill_between(mean.index, lo.values, hi.values, color=color, alpha=0.12, linewidth=0)
        final = mean.values[-1]
        ax.annotate(
            fmt.format(final),
            xy=(mean.index[-1], final),
            xytext=(3, 0),
            textcoords="offset points",
            color=color,
            fontsize=6,
            va="center",
            fontweight="bold",
        )
    ax.set_xlabel("Training episode")
    ax.set_ylabel(ylab)
    ax.set_xlim(0, 400)
    ax.grid(axis="y")

axes[0].legend(loc="lower right", frameon=False)
axes[0].set_title("(a) Training reward", loc="left", pad=4)
axes[1].set_title("(b) Strict-QoS service ratio", loc="left", pad=4)
fig.tight_layout(w_pad=1.6)
save(fig, Path(__file__).parent / "fig3_convergence")
