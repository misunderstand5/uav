"""Draft Fig. 2 for the TVT paper: three-panel structure sketch.

Left  : environment model (system, QoS sessions, dynamics)
Top R : branch-credit SAC (shared relay encoder, motion/power branches)
Bottom: ROCS-0 scheduler (age weight -> max-cost+1-swap -> allocate/update)

This is a structural draft (light colors are provisional), not the final art.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "fig2_framework_draft.png"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["axes.linewidth"] = 0.8

TEXT = "#1F2933"
MUTED = "#52606D"
ENV_FC, ENV_EC = "#F3F8F7", "#5E8C86"
RL_FC, RL_EC = "#F3F6FC", "#4F6FA8"
SCH_FC, SCH_EC = "#FDF7EE", "#B07A35"
BOX_EC = "#7B8794"


def box(ax, x, y, w, h, title, lines=(), fc="white", ec=BOX_EC, lw=1.0,
        ts=9.5, bs=7.6, title_color=TEXT):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
        fc=fc, ec=ec, lw=lw, zorder=2,
    ))
    ax.text(x + 0.08, y + h - 0.12, title, fontsize=ts, fontweight="bold",
            color=title_color, ha="left", va="top", zorder=3)
    if lines:
        ax.text(x + 0.08, y + h - 0.34, "\n".join(lines), fontsize=bs,
                color=TEXT, ha="left", va="top", linespacing=1.28, zorder=3)


def arrow(ax, p0, p1, text=None, color="#374151", lw=1.15, style="-|>",
          rad=0.0, fs=7.2, tpos=0.5, toff=(0.0, 0.08), dashed=False, z=4):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle=style, mutation_scale=11, lw=lw, color=color,
        connectionstyle=f"arc3,rad={rad}", linestyle="--" if dashed else "-",
        shrinkA=1.5, shrinkB=1.5, zorder=z,
    ))
    if text:
        tx = p0[0] + (p1[0] - p0[0]) * tpos + toff[0]
        ty = p0[1] + (p1[1] - p0[1]) * tpos + toff[1]
        ax.text(tx, ty, text, fontsize=fs, color=color, ha="center", va="bottom",
                zorder=z + 1)


def poly_arrow(ax, pts, color="#374151", lw=1.15, text=None, fs=7.2,
               text_xy=None, dashed=False, z=4):
    ls = "--" if dashed else "-"
    for i in range(len(pts) - 2):
        ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch(
        pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=11, lw=lw, color=color,
        linestyle=ls, shrinkA=1.5, shrinkB=1.5, zorder=z,
    ))
    if text and text_xy:
        ax.text(text_xy[0], text_xy[1], text, fontsize=fs, color=color,
                ha="center", va="bottom", zorder=z + 1)


def quad(ax, x, y, s=0.13, color="#2F3E46", label=None, fs=6.8):
    ax.add_patch(Circle((x, y), s * 0.26, fc=color, ec=color, zorder=6))
    for dx, dy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        ax.plot([x, x + dx * s], [y, y + dy * s], color=color, lw=1.0, zorder=6)
        ax.add_patch(Circle((x + dx * s, y + dy * s), s * 0.22,
                            fc="white", ec=color, lw=0.8, zorder=7))
    if label:
        ax.text(x, y - s * 1.05, label, fontsize=fs, color=color,
                ha="center", va="top", zorder=7)


def user(ax, x, y, color="#2F3E46", s=0.07):
    ax.add_patch(Circle((x, y + s * 0.8), s * 0.55, fc="white", ec=color, lw=0.9, zorder=6))
    ax.plot([x, x], [y - s * 0.6, y + s * 0.25], color=color, lw=1.0, zorder=6)
    ax.plot([x - s * 0.5, x + s * 0.5], [y - s * 0.1, y - s * 0.1], color=color, lw=1.0, zorder=6)


fig, ax = plt.subplots(figsize=(16, 9), dpi=240)
ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
ax.add_patch(Rectangle((0, 0), 16, 9, fc="white", ec="none", zorder=0))

# ---------------------------------------------------------------- panels
ax.add_patch(FancyBboxPatch((0.10, 0.10), 4.58, 8.80,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            fc=ENV_FC, ec=ENV_EC, lw=1.3, zorder=1))
ax.text(2.39, 8.93, "A. Environment Module", fontsize=12, fontweight="bold",
        color=ENV_EC, ha="center", va="top")

ax.add_patch(FancyBboxPatch((4.95, 4.55), 10.90, 4.35,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            fc=RL_FC, ec=RL_EC, lw=1.3, zorder=1))
ax.text(15.55, 8.93, "B. Branch-Credit SAC", fontsize=12, fontweight="bold",
        color=RL_EC, ha="right", va="top")

ax.add_patch(FancyBboxPatch((4.95, 0.10), 10.90, 4.25,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            fc=SCH_FC, ec=SCH_EC, lw=1.3, zorder=1))
ax.text(15.55, 4.24, "C. ROCS-0 Scheduler", fontsize=12, fontweight="bold",
        color=SCH_EC, ha="right", va="top")

# ---------------------------------------------------------------- A1 system model
box(ax, 0.24, 5.55, 4.30, 2.70, "A1  System model", fc="white", ec=ENV_EC)
ax.text(0.36, 7.94, "500 m × 500 m, K = 4;  5/20 MHz access/backhaul",
        fontsize=6.2, color=MUTED, ha="left", va="top", zorder=4)
quad(ax, 2.39, 7.42, s=0.18, label=None)
ax.text(2.39, 7.10, "C-UAV", fontsize=7.2, color=TEXT, ha="center", va="top", zorder=7)
for x, y in ((0.95, 6.78), (3.83, 6.78), (0.95, 6.28), (3.83, 6.28)):
    quad(ax, x, y, s=0.105)
ax.text(2.39, 6.50, "M-UAV ×4", fontsize=6.8, color=TEXT, ha="center", va="center", zorder=7)
for x in (0.95, 2.39, 3.83):
    for j in range(3):
        user(ax, x - 0.20 + j * 0.20, 5.93, s=0.055)
ax.text(2.39, 5.70, "GU clusters", fontsize=6.4, color=MUTED, ha="center", va="top", zorder=7)
# links
for x, y in ((0.95, 6.78), (3.83, 6.78), (0.95, 6.28), (3.83, 6.28)):
    ax.plot([2.39, x], [7.28, y + 0.06], color="#6B9080", lw=0.8, ls=(0, (3, 2)), zorder=3)
for x, y in ((0.95, 6.28), (2.39, 6.28), (3.83, 6.28)):
    ax.plot([x, x], [y - 0.10, 6.00], color="#8AA29E", lw=0.8, zorder=3)

# ---------------------------------------------------------------- A2 QoS sessions
box(ax, 0.24, 3.12, 4.30, 2.20, "A2  QoS session model", fc="white", ec=ENV_EC)
xs = [0.38, 0.75, 1.10, 1.45, 1.85, 2.10, 2.45, 2.75]
ys = [3.42, 3.42, 3.62, 4.02, 4.32, 4.08, 3.72, 3.42]
ax.plot(xs, ys, color="#3E7C74", lw=1.3, zorder=4)
ax.fill_between(xs, 3.32, ys, color="#3E7C74", alpha=0.08, zorder=3)
for x, lab in zip((0.56, 1.27, 1.97, 2.60), ("normal", "ramp", "peak", "rec.")):
    ax.text(x, 3.24, lab, fontsize=5.7, color=MUTED, ha="center", va="bottom", zorder=5)
ax.annotate("", xy=(2.82, 3.32), xytext=(2.70, 3.32),
            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8), zorder=5)
ax.text(3.02, 4.72, "20 baseline\n→ up to 130 users", fontsize=6.6, color=TEXT,
        ha="left", va="top", zorder=5)
ax.text(3.02, 4.12, "QoS tiers\n0.7 / 2.0 / 2.5 Mbps", fontsize=6.6, color=TEXT,
        ha="left", va="top", zorder=5)
ax.text(3.02, 3.55, "session 45–120 s", fontsize=6.2, color=MUTED,
        ha="left", va="top", zorder=5)

# ---------------------------------------------------------------- A3 dynamics
box(ax, 0.24, 0.80, 4.30, 2.10, "A3  UAV / GU dynamics", fc="white", ec=ENV_EC)
ax.text(0.36, 2.56, "GU: 0–6 m/s, resampled every 0.5 s",
        fontsize=6.7, color=TEXT, ha="left", va="top", zorder=4)
ax.text(0.36, 2.26, "M-UAV: K-means++ + Hungarian,\n25 m/s, 5 m/s$^2$",
        fontsize=6.7, color=TEXT, ha="left", va="top", zorder=4)
ax.text(0.36, 1.86, "Age: $O_i \\leftarrow O_i+\\Delta t$ if QoS missed,\nelse $O_i \\leftarrow 0$",
        fontsize=6.7, color=TEXT, ha="left", va="top", zorder=4)
ax.add_patch(FancyArrowPatch((3.18, 1.30), (3.88, 1.30), arrowstyle="-|>",
                             mutation_scale=8, lw=0.9, color="#3E7C74",
                             connectionstyle="arc3,rad=-0.55", zorder=4))
ax.text(3.52, 0.98, "position →\nassociation → age", fontsize=5.6,
        color=MUTED, ha="center", va="top", zorder=5)

# state / actions
arrow(ax, (4.58, 7.32), (5.10, 7.32), " $s_t$", color="#1F5C56", lw=1.5, fs=8.2)
poly_arrow(ax, [(7.55, 7.24), (7.55, 5.96), (4.58, 5.96), (4.58, 7.02)],
           color="#1F5C56", lw=1.2, text="$a_M$", text_xy=(6.10, 5.90), fs=7.8)
poly_arrow(ax, [(10.95, 6.20), (10.95, 4.62), (8.34, 4.62), (8.34, 3.72)],
           color="#C07A2C", lw=1.5, text="$a_P$", text_xy=(10.95, 5.25), fs=8.0)
poly_arrow(ax, [(4.58, 2.88), (4.58, 4.46), (12.25, 4.46), (12.25, 6.14)],
           color="#6B4C9A", lw=1.0, text="$r_t$", text_xy=(8.10, 4.49),
           fs=7.2, dashed=True)

# ---------------------------------------------------------------- B1 encoder
box(ax, 5.10, 6.25, 2.05, 2.00, "B1  Shared relay\n     set encoder", fc="white", ec=RL_EC, ts=9.0)
for i, y in enumerate((6.55, 6.82, 7.09, 7.36)):
    ax.add_patch(Rectangle((5.22, y), 0.16, 0.16, fc="#DCE6F5", ec=RL_EC, lw=0.8, zorder=4))
ax.text(5.44, 7.44, "relay\ntokens ×4", fontsize=6.3, color=MUTED, ha="left", va="top", zorder=5)
ax.add_patch(FancyBboxPatch((5.80, 6.55), 1.10, 0.85, boxstyle="round,pad=0.02,rounding_size=0.06",
                            fc="#E8EFFA", ec=RL_EC, lw=0.9, zorder=4))
ax.text(6.35, 6.97, "permutation-\ninvariant\nencoder", fontsize=6.4, color=TEXT,
        ha="center", va="center", zorder=5)
arrow(ax, (5.40, 6.95), (5.78, 6.95), color=RL_EC, lw=1.0)
# shared embedding bus to both branches
poly_arrow(ax, [(6.92, 6.98), (7.18, 6.98), (7.18, 8.46), (8.50, 8.46), (8.50, 8.10)],
           color=RL_EC, lw=1.0)
poly_arrow(ax, [(7.18, 8.46), (10.90, 8.46), (10.90, 8.10)], color=RL_EC, lw=1.0)

# ---------------------------------------------------------------- B2 motion
box(ax, 7.55, 7.20, 1.95, 0.88, "B2  Motion branch", fc="white", ec=RL_EC, ts=8.6)
ax.text(7.63, 7.42, "$\\pi_M(s)$", fontsize=11, color=TEXT, ha="left", va="center", zorder=4)
ax.text(8.55, 7.42, "→ $a_M$", fontsize=7.4, color=MUTED, ha="left", va="center", zorder=4)
box(ax, 7.55, 6.28, 1.95, 0.80, "", fc="#F7F9FD", ec=RL_EC)
ax.text(7.63, 6.68, "$Q_M(s,a_M)$", fontsize=10.2, color=TEXT, ha="left", va="center", zorder=4)
ax.add_patch(FancyArrowPatch((8.52, 6.36), (8.52, 6.98), arrowstyle="-|>",
                             mutation_scale=9, lw=1.0, color="#6B4C9A",
                             connectionstyle="arc3,rad=0.55", zorder=5))
ax.text(8.90, 6.62, "recursive\nlong-horizon", fontsize=6.2, color="#6B4C9A",
        ha="left", va="center", zorder=5)

# ---------------------------------------------------------------- B3 power
box(ax, 9.85, 7.20, 2.10, 0.88, "B3  Power branch", fc="white", ec=RL_EC, ts=8.6)
ax.text(9.93, 7.42, "$\\pi_P(s)$", fontsize=11, color=TEXT, ha="left", va="center", zorder=4)
ax.text(10.75, 7.42, "→ $a_P$", fontsize=7.4, color=MUTED, ha="left", va="center", zorder=4)
box(ax, 9.85, 6.28, 2.10, 0.80, "", fc="#F7F9FD", ec=RL_EC)
ax.text(9.93, 6.68, "$Q_P(s,a_M,a_P)$", fontsize=9.7, color=TEXT, ha="left", va="center", zorder=4)
ax.add_patch(FancyArrowPatch((10.85, 6.36), (10.85, 6.98), arrowstyle="-|>",
                             mutation_scale=9, lw=1.0, color="#C07A2C",
                             connectionstyle="arc3,rad=-0.45", zorder=5))
ax.text(11.18, 6.62, "immediate\nsame-slot", fontsize=6.2, color="#C07A2C",
        ha="left", va="center", zorder=5)
arrow(ax, (9.52, 7.42), (9.82, 7.42), color="#6B4C9A", lw=0.9, dashed=True)
ax.text(9.67, 7.55, "$a_M$", fontsize=6.0, color="#6B4C9A", ha="center", va="bottom", zorder=5)

# ---------------------------------------------------------------- B4 update
box(ax, 12.25, 6.22, 3.40, 1.95, "B4  SAC update", fc="white", ec=RL_EC)
ax.text(12.35, 7.62, "replay buffers\n(main + power)\ntarget networks\n$L_Q,\\ L_\\pi,\\ L_\\alpha$",
        fontsize=7.2, color=TEXT, ha="left", va="top", linespacing=1.30, zorder=4)
ax.add_patch(FancyArrowPatch((11.98, 6.95), (12.22, 6.95), arrowstyle="-|>",
                             mutation_scale=9, lw=0.9, color=MUTED, linestyle="--", zorder=4))
ax.add_patch(FancyArrowPatch((11.98, 6.65), (12.22, 6.65), arrowstyle="-|>",
                             mutation_scale=9, lw=0.9, color=MUTED, linestyle="--", zorder=4))

# ---------------------------------------------------------------- C1
box(ax, 5.12, 1.70, 3.15, 1.95, "C1  Age-weighted priority", fc="white", ec=SCH_EC, ts=8.0)
ax.text(5.22, 3.30, "$w_i=1+\\lambda_s(O_i+\\Delta t)$", fontsize=8.4, color=TEXT,
        ha="left", va="top", zorder=4)
ax.text(5.22, 2.98, "$A_i=q_i/C_i^A,\\ \\ B_i=q_i/R_k^B$", fontsize=7.8, color=TEXT,
        ha="left", va="top", zorder=4)
ax.text(5.22, 2.68, "density $= w_i/\\max(A_i,B_i)$", fontsize=7.8, color=TEXT,
        ha="left", va="top", zorder=4)
ax.text(5.22, 2.36, "$\\lambda_s$: resilience knob", fontsize=6.6, color="#8A5A1E",
        ha="left", va="top", zorder=4)
# knob icon
ax.add_patch(Circle((7.86, 2.86), 0.12, fc="#F3D9B1", ec=SCH_EC, lw=0.9, zorder=5))
ax.plot([7.86, 7.86], [2.86, 3.08], color=SCH_EC, lw=1.2, zorder=6)

# ---------------------------------------------------------------- C2
box(ax, 8.45, 1.70, 3.15, 1.95, "C2  Max-cost + 1-swap", fc="white", ec=SCH_EC, ts=8.0)
ax.text(8.55, 3.30, "1) greedy feasible pass", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(8.55, 3.00, "2) 1-swap improvement", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(8.55, 2.70, "3) refill by density", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(8.55, 2.36, "access + backhaul feasible", fontsize=6.4, color=MUTED, ha="left", va="top", zorder=4)
# two users swapping
for i, (x, c) in enumerate(((10.55, "#E8A87C"), (11.05, "#F2C57C"))):
    ax.add_patch(FancyBboxPatch((x, 2.52), 0.20, 0.20, boxstyle="round,pad=0.01,rounding_size=0.03",
                                fc=c, ec=SCH_EC, lw=0.7, zorder=5))
ax.add_patch(FancyArrowPatch((10.55, 2.82), (11.05, 2.82), arrowstyle="-|>",
                             mutation_scale=8, lw=1.0, color="#8A5A1E",
                             connectionstyle="arc3,rad=-0.55", zorder=6))
ax.add_patch(FancyArrowPatch((11.05, 2.42), (10.55, 2.42), arrowstyle="-|>",
                             mutation_scale=8, lw=1.0, color="#8A5A1E",
                             connectionstyle="arc3,rad=-0.55", zorder=6))

# ---------------------------------------------------------------- C3
box(ax, 11.80, 1.70, 3.85, 1.95, "C3  Allocate & update", fc="white", ec=SCH_EC, ts=8.0)
ax.text(11.90, 3.30, "served bits $z_i$ → per-relay power", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(11.90, 3.00, "per-relay backhaul, QSR", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(11.90, 2.70, "update age $O_i$; next slot", fontsize=7.0, color=TEXT, ha="left", va="top", zorder=4)
ax.text(11.90, 2.36, "$\\sum_i$ access ≤ 1,  $\\sum_i$ backhaul ≤ $R_k^B$", fontsize=6.2, color=MUTED,
        ha="left", va="top", zorder=4)

# C arrows
arrow(ax, (8.30, 2.18), (8.43, 2.18), color=SCH_EC, lw=1.2)
arrow(ax, (11.62, 2.18), (11.78, 2.18), color=SCH_EC, lw=1.2)
poly_arrow(ax, [(13.55, 1.68), (13.55, 1.42), (4.58, 1.42), (4.58, 1.58)],
           color="#8A5A1E", lw=1.2, text="$z_t$ (allocation) → environment",
           text_xy=(9.10, 1.34), fs=6.4)

# reward / legend
ax.text(5.18, 4.66, "state $s_t$: C-UAV + relay tokens + QoS/age/load",
        fontsize=6.4, color=RL_EC, ha="left", va="bottom", zorder=5)
ax.text(12.10, 4.66, "long arrow = recursive credit;  short arrow = immediate credit",
        fontsize=6.2, color=MUTED, ha="left", va="bottom", zorder=5)
ax.text(4.70, 4.50, "$r_t$", fontsize=6.6, color="#6B4C9A", ha="left", va="bottom", zorder=5)

fig.savefig(OUT, dpi=240, bbox_inches="tight", pad_inches=0.08, facecolor="white")
fig.savefig(OUT.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08, facecolor="white")
print(f"[SAVED] {OUT}")
