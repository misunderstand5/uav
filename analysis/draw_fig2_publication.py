"""Publication-size Fig. 2 for the TVT paper.

Canvas is exactly the IEEE two-column width (7.16 in), so font sizes are the
final print sizes (body 6.6-7 pt, titles 7.2-8.5 pt).  Vector PDF + 600 dpi PNG.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "fig2_framework_publication.png"

plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 7
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.linewidth"] = 0.6

TEXT = "#1A1A1A"
MUTED = "#555555"
ENV = "#00796B"; ENV_FC = "#F2F8F6"
RL = "#0072B2"; RL_FC = "#F2F7FC"
SCH = "#D55E00"; SCH_FC = "#FDF3E7"
ACC = "#E69F00"
BOX_EC = "#7A7A7A"


def box(x, y, w, h, title=None, lines=(), fc="white", ec=BOX_EC, lw=0.6,
        ts=7.2, bs=6.6, tc=TEXT, pad=0.06):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.012,rounding_size=0.03",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    if title:
        ax.text(x + pad, y + h - 0.045, title, fontsize=ts, fontweight="bold",
                color=tc, ha="left", va="top", zorder=3)
    if lines:
        ax.text(x + pad, y + h - 0.20, "\n".join(lines), fontsize=bs,
                color=TEXT, ha="left", va="top", linespacing=1.20, zorder=3)


def arrow(p0, p1, color="#333333", lw=0.8, style="-|>", ms=5.5,
          dashed=False, rad=0.0, z=4):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms,
                                 lw=lw, color=color, linestyle="--" if dashed else "-",
                                 connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=0.8, shrinkB=0.8, zorder=z))


def poly(pts, color="#333333", lw=0.8, dashed=False, ms=5.5, z=4):
    ls = "--" if dashed else "-"
    for i in range(len(pts) - 2):
        ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=ms,
                                 lw=lw, color=color, linestyle=ls,
                                 shrinkA=0.5, shrinkB=0.5, zorder=z))


def label(x, y, s, color=TEXT, fs=6.6, ha="center", va="bottom", weight="normal", z=6):
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va,
            fontweight=weight, zorder=z)


def quad(x, y, s=0.06, color="#2B2B2B"):
    ax.add_patch(Circle((x, y), s * 0.24, fc=color, ec=color, zorder=6))
    for dx, dy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        ax.plot([x, x + dx * s], [y, y + dy * s], color=color, lw=0.7, zorder=6)
        ax.add_patch(Circle((x + dx * s, y + dy * s), s * 0.20,
                            fc="white", ec=color, lw=0.55, zorder=7))


def user(x, y, s=0.03, color="#2B2B2B"):
    ax.add_patch(Circle((x, y + s * 0.75), s * 0.50, fc="white", ec=color, lw=0.55, zorder=6))
    ax.plot([x, x], [y - s * 0.55, y + s * 0.20], color=color, lw=0.65, zorder=6)
    ax.plot([x - s * 0.45, x + s * 0.45], [y - s * 0.10, y - s * 0.10], color=color, lw=0.65, zorder=6)


fig, ax = plt.subplots(figsize=(7.16, 4.55), dpi=600)
ax.set_xlim(0, 7.16); ax.set_ylim(0, 4.55); ax.axis("off")
ax.add_patch(Rectangle((0, 0), 7.16, 4.55, fc="white", ec="none", zorder=0))

# ============================================================ panels
ax.add_patch(FancyBboxPatch((0.04, 0.04), 2.14, 4.47,
                            boxstyle="round,pad=0.01,rounding_size=0.04",
                            fc=ENV_FC, ec=ENV, lw=0.8, zorder=1))
label(0.10, 4.50, "A. Environment", color=ENV, fs=8.4, ha="left", va="top", weight="bold")

ax.add_patch(FancyBboxPatch((2.24, 2.34), 4.88, 2.17,
                            boxstyle="round,pad=0.01,rounding_size=0.04",
                            fc=RL_FC, ec=RL, lw=0.8, zorder=1))
label(7.06, 4.45, "B. Branch-Credit SAC", color=RL, fs=8.4, ha="right", va="top", weight="bold")

ax.add_patch(FancyBboxPatch((2.24, 0.04), 4.88, 2.24,
                            boxstyle="round,pad=0.01,rounding_size=0.04",
                            fc=SCH_FC, ec=SCH, lw=0.8, zorder=1))
label(7.06, 2.22, "C. ROCS-0 Scheduler", color=SCH, fs=8.4, ha="right", va="top", weight="bold")

# ============================================================ A1
box(0.10, 2.96, 2.02, 1.30, "A1  System model", ec=ENV, ts=7.0)
label(0.16, 4.12, "500 m,  K = 4", fs=5.9, color=MUTED, ha="left", va="top")
quad(1.11, 3.94, s=0.070)
label(1.11, 3.84, "C-UAV", fs=5.9, color=TEXT, va="top")
for x in (0.50, 0.90, 1.32, 1.72):
    quad(x, 3.55, s=0.040)
for x in (0.58, 1.11, 1.64):
    for j in range(3):
        user(x - 0.05 + j * 0.05, 3.14, s=0.021)
for x in (0.50, 0.90, 1.32, 1.72):
    ax.plot([1.11, x], [3.87, 3.62], color=ENV, lw=0.55, ls=(0, (2, 1.5)), zorder=3)
for x in (0.58, 1.11, 1.64):
    ax.plot([x, x], [3.49, 3.20], color=ENV, lw=0.55, alpha=0.7, zorder=3)

# ============================================================ A2
box(0.10, 1.60, 2.02, 1.18, "A2  QoS sessions", ec=ENV, ts=7.0)
xs = [0.17, 0.32, 0.46, 0.60, 0.76, 0.88, 1.00, 1.08]
ys = [1.70, 1.70, 1.82, 2.03, 2.20, 2.08, 1.88, 1.70]
ax.plot(xs, ys, color=ENV, lw=0.9, zorder=4)
ax.fill_between(xs, 1.66, ys, color=ENV, alpha=0.07, zorder=3)
label(1.14, 2.40, "20 → 130 users", fs=6.1, ha="left", va="top")
label(1.14, 2.16, "QoS 0.7 / 2 / 2.5", fs=6.1, ha="left", va="top")
label(1.14, 1.92, "45–120 s", fs=5.9, color=MUTED, ha="left", va="top")

# ============================================================ A3
box(0.10, 0.10, 2.02, 1.42, "A3  Dynamics", ec=ENV, ts=7.0)
label(0.17, 1.28, "GU: 0–6 m/s, every 0.5 s", fs=6.0, ha="left", va="top")
label(0.17, 1.04, "M-UAV: 25 m/s, 5 m/s$^2$", fs=6.0, ha="left", va="top")
label(0.17, 0.80, "Age: $O_i \\leftarrow O_i+\\Delta t$", fs=6.0, ha="left", va="top")
label(0.17, 0.56, "K-means++ + Hungarian", fs=5.6, color=MUTED, ha="left", va="top")

# ============================================================ B1
box(2.32, 2.90, 1.08, 1.25, "B1  Encoder", ec=RL, ts=6.8)
for y in (3.12, 3.30, 3.48):
    ax.add_patch(Rectangle((2.38, y), 0.09, 0.09, fc="#DCE8F5", ec=RL, lw=0.45, zorder=4))
label(2.50, 3.62, "tokens ×4", fs=5.2, color=MUTED, ha="left", va="top")
ax.add_patch(FancyBboxPatch((2.66, 3.16), 0.58, 0.42,
                            boxstyle="round,pad=0.01,rounding_size=0.02",
                            fc="#E4EEF9", ec=RL, lw=0.5, zorder=4))
label(2.95, 3.37, "encoder", fs=5.8, color=TEXT)
arrow((2.47, 3.35), (2.64, 3.35), color=RL, lw=0.6)

# ============================================================ B2
box(3.55, 3.45, 0.90, 0.55, "B2  Motion", ec=RL, ts=6.6)
label(3.61, 3.70, "$\\pi_M$", fs=7.4, ha="left", va="center")
box(3.55, 2.90, 0.90, 0.45, "", fc="#F7FAFE", ec=RL)
label(3.61, 3.12, "$Q_M(s,a_M)$", fs=6.4, ha="left", va="center")
arrow((3.90, 2.98), (3.90, 3.40), color="#6A3D9A", lw=0.55, rad=0.55)
label(3.63, 3.24, "recursive", fs=5.0, color="#6A3D9A", ha="left", va="center")

# ============================================================ B3
box(4.75, 3.45, 0.90, 0.55, "B3  Power", ec=RL, ts=6.6)
label(4.81, 3.70, "$\\pi_P$", fs=7.4, ha="left", va="center")
box(4.75, 2.90, 0.90, 0.45, "", fc="#F7FAFE", ec=RL)
label(4.81, 3.12, "$Q_P(s,a_M,a_P)$", fs=5.5, ha="left", va="center")
arrow((5.10, 2.98), (5.10, 3.40), color=ACC, lw=0.55, rad=-0.45)
label(4.83, 3.24, "immediate", fs=5.0, color="#A65E00", ha="left", va="center")

# ============================================================ B4
box(5.80, 2.90, 1.25, 1.20, "B4  SAC update", ec=RL, ts=6.8)
label(5.86, 3.84, "replay + targets", fs=5.9, ha="left", va="top")
label(5.86, 3.60, "$L_Q,\\ L_\\pi$", fs=6.4, ha="left", va="top")
label(5.86, 3.36, "entropy $\\alpha$", fs=5.8, ha="left", va="top")

# shared encoder bus
poly([(3.24, 3.37), (3.50, 3.37), (3.50, 4.18), (4.00, 4.18), (4.00, 4.02)], color=RL, lw=0.55)
poly([(3.50, 4.18), (5.20, 4.18), (5.20, 4.02)], color=RL, lw=0.55)

# ============================================================ action bus
poly([(4.00, 4.02), (4.00, 4.30), (2.12, 4.30), (2.12, 3.78)], color=ENV, lw=0.9)
label(3.05, 4.33, "$a_t=(a_M,a_P)$", fs=6.4, color=ENV, ha="center", va="bottom")
arrow((2.12, 3.96), (2.30, 3.96), color=ENV, lw=0.8)
label(2.21, 3.99, "$s_t$", fs=6.2, color=ENV, ha="center", va="bottom")

# a_P to scheduler
poly([(5.20, 2.88), (5.20, 2.26), (3.92, 2.26), (3.92, 2.12)], color=ACC, lw=0.9)
label(5.26, 2.52, "$a_P$", fs=6.4, color="#A65E00", ha="left", va="center")

# ============================================================ C1
box(2.32, 0.65, 1.55, 1.45, "C1  Age priority", ec=SCH, ts=6.9)
label(2.38, 1.82, "$w_i=1+\\lambda_s(O_i+\\Delta t)$", fs=6.6, ha="left", va="top")
label(2.38, 1.58, "$A_i=q_i/C_i^A,\\ B_i=q_i/R_k^B$", fs=6.2, ha="left", va="top")
label(2.38, 1.34, "$\\lambda_s$: resilience knob", fs=5.8, color="#A65E00", ha="left", va="top")
ax.add_patch(Circle((3.62, 1.64), 0.06, fc="#F3D9B1", ec=SCH, lw=0.5, zorder=5))
ax.plot([3.62, 3.62], [1.64, 1.76], color=SCH, lw=0.7, zorder=6)

# ============================================================ C2
box(3.97, 0.65, 1.55, 1.45, "C2  Max-cost + 1-swap", ec=SCH, ts=6.9)
label(4.03, 1.84, "greedy feasible pass", fs=6.2, ha="left", va="top")
label(4.03, 1.60, "1-swap improvement", fs=6.2, ha="left", va="top")
label(4.03, 1.36, "refill by density", fs=6.2, ha="left", va="top")
for x, c in ((5.00, "#E8A87C"), (5.24, "#F2C57C")):
    ax.add_patch(FancyBboxPatch((x, 1.12), 0.10, 0.10,
                                boxstyle="round,pad=0.005,rounding_size=0.01",
                                fc=c, ec=SCH, lw=0.4, zorder=5))
ax.add_patch(FancyArrowPatch((5.02, 1.26), (5.24, 1.26), arrowstyle="-|>",
                             mutation_scale=4.5, lw=0.5, color="#A65E00",
                             connectionstyle="arc3,rad=-0.55", zorder=6))
ax.add_patch(FancyArrowPatch((5.24, 1.08), (5.02, 1.08), arrowstyle="-|>",
                             mutation_scale=4.5, lw=0.5, color="#A65E00",
                             connectionstyle="arc3,rad=-0.55", zorder=6))

# ============================================================ C3
box(5.62, 0.65, 1.40, 1.45, "C3  Allocate", ec=SCH, ts=6.9)
label(5.68, 1.84, "served bits → power", fs=6.2, ha="left", va="top")
label(5.68, 1.60, "backhaul, QSR", fs=6.2, ha="left", va="top")
label(5.68, 1.36, "age update; next slot", fs=6.2, ha="left", va="top")

# C arrows
arrow((3.89, 1.40), (3.95, 1.40), color=SCH, lw=0.7)
arrow((5.54, 1.40), (5.60, 1.40), color=SCH, lw=0.7)

# z_t feedback
poly([(5.62, 0.61), (5.62, 0.48), (2.12, 0.48), (2.12, 1.22)], color="#8A5A1E", lw=0.8)
label(3.75, 0.52, "$z_t$ → environment", fs=5.8, color="#8A5A1E", ha="center", va="bottom")

# r_t is described in the caption; a dashed arrow here would cross the C panel.


fig.savefig(OUT, dpi=600, bbox_inches="tight", pad_inches=0.02, facecolor="white")
fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02, facecolor="white")
print(f"[SAVED] {OUT}")
