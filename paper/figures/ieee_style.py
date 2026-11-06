"""Shared IEEE publication style for paper figures."""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# Okabe-Ito colorblind-safe palette
BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
YELLOW = "#E69F00"
SKY = "#56B4E9"
GRAY = "#808080"

SINGLE_W = 3.5  # inches, single column
DOUBLE_W = 7.16  # inches, double column


def apply_style() -> None:
    mpl.rcParams.update({
        "font.family": "Arial",
        "font.size": 7,
        "axes.titlesize": 7,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "grid.linewidth": 0.4,
        "grid.alpha": 0.35,
        "grid.linestyle": "--",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,  # embed as TrueType, not Type3
        "ps.fonttype": 42,
        "figure.dpi": 150,
    })


def save(fig: mpl.figure.Figure, path: Path) -> None:
    fig.savefig(str(path.with_suffix(".pdf")), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(str(path.with_suffix(".png")), bbox_inches="tight", pad_inches=0.02, dpi=600)
    plt.close(fig)
    print(f"saved {path.stem}.pdf / .png")
