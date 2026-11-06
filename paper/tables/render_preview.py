"""Render the eight LaTeX tables as an IEEE-styled HTML preview, then screenshot via Chrome."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).parent / "tables_preview.html"

CSS = """
body { font-family: 'Times New Roman', serif; margin: 24px; color: #111; }
h1 { font-size: 15px; margin: 4px 0 12px; }
table { border-collapse: collapse; margin: 0 0 10px; font-size: 11px; }
caption { caption-side: top; text-align: left; font-size: 10px; margin-bottom: 4px; }
th, td { padding: 2px 9px; text-align: center; }
th { border-top: 1.6px solid #000; border-bottom: 0.8px solid #000; font-weight: normal; font-style: italic; }
tr:last-child td { border-bottom: 1.6px solid #000; }
td.l, th.l { text-align: left; }
b { font-weight: bold; }
.note { font-size: 9px; text-align: left; margin: 0 0 18px; max-width: 820px; line-height: 1.35; }
.subhead td { text-align: left; font-style: italic; border: none; font-size: 10px; padding-top: 8px; }
"""


def row(cells, left=False):
    first = f'<td class="l">{cells[0]}</td>' if left else f"<td>{cells[0]}</td>"
    return "<tr>" + first + "".join(f"<td>{c}</td>" for c in cells[1:]) + "</tr>"


def subhead(text):
    return f'<tr class="subhead"><td colspan="10">{text}</td></tr>'


t1 = ["Method", "QSR", "Avg. SQA", "P5 SQA", "P95 outage (s)", "obj", "Goodput (Mbps)"]
r1 = [
    ["<b>ROCS-0 + HQC-SAC (proposed)</b>", "0.8043", "<b>0.7353</b>", "<b>0.2387</b>", "<b>10.10</b>", "<b>0.7733</b>", "<b>50.93</b>"],
    ["w/o 1-swap", "0.8020", "0.7122", "0.1283", "14.79", "0.7478", "49.96"],
    ["w/o age term", "<b>0.8073</b>", "0.7116", "0.0326", "66.24", "0.4281", "50.53"],
    ["TD3", "0.7684", "0.6884", "0.1676", "13.69", "0.7221", "47.01"],
    ["PPO", "0.7380", "0.6502", "0.1035", "20.34", "0.6613", "43.53"],
    ["CDA-SAC (flat)", "0.7434", "0.6714", "0.1243", "17.93", "0.6757", "45.17"],
    ["Recursive-credit H128", "0.7494", "0.6758", "0.1540", "17.05", "0.6900", "45.64"],
]

t2 = ["Scheduler", "QSR", "P5 SQA", "P95 outage (s)", "Goodput (Mbps)"]
r2 = [
    ["<b>ROCS-0 (proposed)</b>", "<b>0.8096</b>", "<b>0.2369</b>", "<b>10.19</b>", "<b>50.75</b>"],
    ["Equal-share", "0.3548", "0.0000", "129.04", "31.85"],
    ["Max-CQI", "0.3970", "0.0001", "119.89", "34.95"],
    ["Proportional-fair", "0.3985", "0.0015", "124.64", "34.34"],
    ["Max-QoS", "0.2776", "0.0025", "138.92", "30.37"],
]

t3 = ["Variant", "QSR", "obj", "P95 outage (s)", "Goodput (Mbps)"]
r3 = [
    ["<b>Proposed</b>", "0.8043", "<b>0.7733</b>", "<b>10.10</b>", "<b>50.93</b>"],
    ["w/o 1-swap", "0.8020", "0.7478", "14.79", "49.96"],
    ["w/o age term", "<b>0.8073</b>", "0.4281", "66.24", "50.53"],
]
r3b = [
    ["<b>Proposed (motion + power)</b>", "<b>0.8096</b>", "<b>0.7787</b>", "<b>10.19</b>", "<b>50.75</b>"],
    ["Motion-only (fixed power)", "0.7126", "0.6010", "24.69", "40.99"],
    ["Power-only (fixed position)", "0.5142", "0.1524", "48.54", "27.51"],
]

t4 = ["Method", "Seed 7", "Seed 17", "Seed 27"]
r4 = [
    ["<b>Proposed</b>", "<b>0.7643</b>", "<b>0.7637</b>", "<b>0.7917</b>"],
    ["w/o 1-swap", "0.7139", "0.7503", "0.7792"],
    ["w/o age term", "0.4518", "0.3965", "0.4361"],
]
r4b = [
    ["<b>Proposed</b>", "<b>10.58</b>", "<b>10.07</b>", "<b>9.65</b>"],
    ["w/o 1-swap", "16.46", "14.67", "13.23"],
    ["w/o age term", "66.69", "67.64", "64.39"],
    ["TD3", "12.26", "16.92", "11.89"],
    ["PPO", "16.32", "25.38", "19.31"],
    ["Recursive-credit H128", "20.16", "18.52", "12.46"],
]

t5 = ["Method", "Online params", "Offline params", "Total", "CPU mean (ms)", "CPU P95 (ms)"]
r5 = [
    ["<b>ROCS-0 + HQC-SAC (proposed)</b>", "<b>123,271</b>", "242,180", "365,451", "1.36", "1.66"],
    ["TD3", "104,068", "268,034", "372,102", "1.03", "1.30"],
    ["PPO", "229,835", "0", "229,835", "2.01", "2.43"],
    ["CDA-SAC (flat)", "121,897", "243,348", "365,245", "0.85", "1.05"],
    ["Recursive-credit H128", "123,271", "242,180", "365,451", "1.36", "1.68"],
    ["Motion-only", "61,062", "242,180", "303,242", "1.34", "1.55"],
    ["Power-only", "62,209", "242,180", "304,389", "1.40", "1.65"],
]

t6 = ["Scheduler", "Mean (ms)", "P50 (ms)", "P95 (ms)", "Max (ms)"]
r6 = [
    ["<b>ROCS-0 (proposed)</b>", "<b>0.534</b>", "0.394", "1.182", "1.690"],
    ["w/o age term", "0.403", "0.346", "0.712", "0.936"],
    ["w/o 1-swap", "0.283", "0.279", "0.415", "0.589"],
    ["Max-CQI", "0.228", "0.223", "0.373", "0.654"],
    ["Proportional-fair", "0.230", "0.225", "0.376", "0.441"],
    ["Max-QoS", "0.206", "0.199", "0.343", "0.440"],
    ["Equal-share", "0.210", "0.199", "0.347", "0.465"],
]

t7 = ["Method", "Total energy (kJ)", "C-UAV phys. (kJ)", "M-UAV (kJ)", "C-UAV path (m)", "bits/J"]
r7 = [
    ["<b>ROCS-0 + HQC-SAC (proposed)</b>", "220.9", "88.9", "132.0", "541", "<b>45,955</b>"],
    ["TD3", "221.8", "89.8", "132.0", "568", "41,715"],
    ["CDA-SAC (flat)", "<b>220.8</b>", "88.9", "132.0", "<b>465</b>", "40,127"],
    ["PPO", "222.3", "90.3", "132.0", "796", "38,530"],
]

t8 = ["Config (lambda_age, lambda_s)", "QSR", "Avg. SQA", "P5 SQA", "Jain", "P95 outage (s)", "Goodput (Mbps)"]
r8 = [
    ["<b>(0.10, 0.10) main</b>", "<b>0.8096</b>", "<b>0.7338</b>", "<b>0.2369</b>", "<b>0.8693</b>", "10.19", "<b>50.75</b>"],
    ["(0.10, 0.40)", "0.7884", "0.7063", "0.2228", "0.8536", "<b>6.26</b>", "48.70"],
    ["(0.05, 0.20)", "0.7966", "0.7169", "0.2204", "0.8552", "8.33", "49.26"],
    ["(0.10, 0.20)", "0.7943", "0.7057", "0.2089", "0.8472", "8.67", "48.45"],
    ["(0.20, 0.20)", "0.7865", "0.6873", "0.1704", "0.8300", "10.05", "47.15"],
    ["(0.10, 0.00)", "0.7527", "0.6662", "0.0352", "0.7668", "69.15", "45.97"],
]

def table(cap, head, rows, note):
    h = "<tr>" + "".join(f'<th class="l">{c}</th>' if i == 0 else f"<th>{c}</th>"
                          for i, c in enumerate(head)) + "</tr>"
    body = "\n".join(row(r, left=True) for r in rows)
    return (f'<table><caption>{cap}</caption>{h}{body}</table>\n'
            f'<p class="note">{note}</p>\n')

EM = "\u2014"  # em dash
MINUS = "\u2212"
MULT = "\u00d7"
DELTA = "\u0394"

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><h1>Paper tables preview (IEEE booktabs style) {EM} bold = best per column</h1>
{table("Table I {EM} Sealed final-100 main comparison (7 methods, 300 episodes each).", t1, r1,
f"obj = QSR {MINUS} 0.10 {MULT} mean under-service age (service term of the trained reward). P95 outage is a telemetry KPI (scenario-mean of session-level P95, right-censored), not a hard constraint. Paired bootstrap (20,000 resamples) vs proposed: w/o age term {DELTA}obj = +0.345 [0.331, 0.359]; w/o 1-swap +0.025 [0.022, 0.029]; win rate 1.000 in all pairwise comparisons.")}
{table(f"Table II {EM} Scheduler comparison under the frozen proposed controller (dev set, 90 episodes).", t2, r2,
f"Only the per-relay scheduler is substituted; motion/power control identical across rows. Equal-share P5 SQA = 0.000 because a proportional split always leaves at least one session with a near-zero share {EM} a property of the policy, not an artifact.")}
{table(f"Table III {EM} Ablations: (a) scheduler on sealed set, (b) controller branches on dev set.", t3, r3 + r3b,
f"w/o age term keeps QSR nearly unchanged while its objective collapses {EM} the age penalty is the binding term. Motion-only / power-only fix the other branch to its trained mean behavior.")}
{table(f"Table IV {EM} Per-seed results on the sealed set: (a) objective obj, (b) P95 outage (s).", t4, r4 + r4b,
"Proposed wins under all three seeds on obj and keeps P95 below 12 s in every seed; TD3 (seed 17) and PPO (seed 17) show marked per-seed sensitivity.")}
{table(f"Table V {EM} Controller complexity and single-step inference latency (batch 1, CPU).", t5, r5,
"Online = deployed actor networks; offline critics are training-only. GPU batch-1 latency is higher (e.g., 3.9 ms vs 1.4 ms CPU for the proposed method) due to kernel-launch overhead; CPU is the deployment reference.")}
{table(f"Table VI {EM} Per-slot scheduler runtime (1,200 recorded slots, best of 5 runs).", t6, r6,
"Whole network, K = 4 relays scheduled sequentially; 200 ms slot budget leaves >2 orders of magnitude headroom. The 1-swap stage accounts for most of the proposed scheduler's cost.")}
{table(f"Table VII {EM} Energy decomposition and efficiency (dev set, 90 episodes, 200 s each).", t7, r7,
"Total energy is nearly identical (fixed duration, low-speed induced-dominated regime, relays dominate); efficiency differences concentrate in bits/J and C-UAV travel: proposed delivers 19% more bits/J than PPO while flying 32% less; CDA flies slightly less but delivers 13% fewer bits/J.")}
{table(f"Table VIII {EM} Effect of reward age-penalty weight and scheduler age weight (dev set, 90 episodes).", t8, r8,
"Main config (0.10, 0.10) is the frozen setting for all prior comparison experiments; it attains the best QSR and P5 SQA, while (0.10, 0.40) trades 2.2 pp of QSR for P95 6.26 s. Disabling the scheduler age weight collapses the tail (69.15 s).")}
</body></html>"""

OUT.write_text(html, encoding="utf-8")
print("wrote", OUT)
