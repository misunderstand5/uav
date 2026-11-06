"""Small 3-worker queue for the TVT supplemental runs on one 8-GB GPU.

Runs the 2x2 missing corner (Flat-Relay + immediate) first, then the
parameter-matched Joint-SAC baseline.  Each job is a separate process; at most
three run concurrently (preflight-validated on the RTX 4060 Ti).
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "runs" / "TVT_20261103"
LOG_ROOT = OUT_ROOT / "_logs"

JOBS = [
    ("FLAT_RELAY_IMMEDIATE", 7),
    ("FLAT_RELAY_IMMEDIATE", 17),
    ("FLAT_RELAY_IMMEDIATE", 27),
    ("JOINT_SAC_PM", 7),
    ("JOINT_SAC_PM", 17),
    ("JOINT_SAC_PM", 27),
]


def done(method: str, seed: int, episodes: int) -> bool:
    out = OUT_ROOT / method / f"seed_{seed}"
    s = out / "train_summary.json"
    if not s.exists():
        return False
    try:
        j = json.loads(s.read_text(encoding="utf-8"))
        return int(j.get("episodes", 0)) >= episodes and (out / "agent.pt").exists()
    except Exception:
        return False


def launch(method: str, seed: int, episodes: int):
    out = OUT_ROOT / method / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    log = LOG_ROOT / f"{method}__seed_{seed}.log"
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-u", str(ROOT / "scripts" / "run_matrix_train.py"),
        "--method", method, "--seed", str(seed), "--episodes", str(episodes),
        "--out-dir", str(out), "--device", "cuda", "--log-file", str(log),
    ]
    f = open(LOG_ROOT / f"{method}__seed_{seed}.stdout.log", "w", encoding="utf-8")
    p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT)
    return p, f, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=400)
    ap.add_argument("--max-workers", type=int, default=3)
    a = ap.parse_args()
    queue = [j for j in JOBS if not done(j[0], j[1], a.episodes)]
    active = []
    print(f"[QUEUE] {len(queue)} jobs, max_workers={a.max_workers}", flush=True)
    while queue or active:
        while queue and len(active) < a.max_workers:
            method, seed = queue.pop(0)
            p, f, log = launch(method, seed, a.episodes)
            active.append((method, seed, p, f, log))
            print(f"[START] {method} seed={seed} pid={p.pid}", flush=True)
            time.sleep(5)  # stagger CUDA context creation
        time.sleep(20)
        still = []
        for method, seed, p, f, log in active:
            if p.poll() is None:
                still.append((method, seed, p, f, log))
            else:
                f.close()
                print(f"[END] {method} seed={seed} exit={p.returncode} log={log}", flush=True)
        active = still
    print("[QUEUE] all jobs finished", flush=True)


if __name__ == "__main__":
    main()
