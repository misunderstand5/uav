"""Third TVT queue: algorithm-level scheduler retraining (no-age, no-1swap).

Waits for the TD3/PPO queue, then runs 6 scheduler-retrain jobs (3 concurrent).
"""
from __future__ import annotations
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "runs" / "TVT_20261103"
LOG_ROOT = OUT_ROOT / "_logs"

WAIT_FOR = [("TD3", 7), ("TD3", 17), ("TD3", 27), ("PPO", 7), ("PPO", 17), ("PPO", 27)]
JOBS = [
    ("SCHED_NO_AGE", "rocs0_no_age", 7),
    ("SCHED_NO_AGE", "rocs0_no_age", 17),
    ("SCHED_NO_AGE", "rocs0_no_age", 27),
    ("SCHED_NO_1SWAP", "rocs0_no_1swap", 7),
    ("SCHED_NO_1SWAP", "rocs0_no_1swap", 17),
    ("SCHED_NO_1SWAP", "rocs0_no_1swap", 27),
]
EPISODES = 400


def done(method: str, seed: int) -> bool:
    out = OUT_ROOT / method / f"seed_{seed}"
    s = out / "train_summary.json"
    if not s.exists():
        return False
    try:
        j = json.loads(s.read_text(encoding="utf-8"))
        return int(j.get("episodes", 0)) >= EPISODES and (out / "agent.pt").exists()
    except Exception:
        return False


def launch(name: str, mode: str, seed: int):
    out = OUT_ROOT / name / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-u", str(ROOT / "scripts" / "run_matrix_train.py"),
           "--method", "HQC_SAC_MAIN", "--seed", str(seed), "--episodes", str(EPISODES),
           "--out-dir", str(out), "--device", "cuda", "--scheduler-mode", mode]
    f = open(LOG_ROOT / f"{name}__seed_{seed}.stdout.log", "w", encoding="utf-8")
    p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT)
    return p, f


def main():
    print("[WAIT] TD3/PPO queue", flush=True)
    while not all(done(m, s) for m, s in WAIT_FOR):
        time.sleep(60)
    print("[START] scheduler queue", flush=True)
    queue = [j for j in JOBS if not done(j[0], j[2])]
    active = []
    while queue or active:
        while queue and len(active) < 3:
            name, mode, seed = queue.pop(0)
            p, f = launch(name, mode, seed)
            active.append((name, seed, p, f))
            print(f"[START] {name} seed={seed} pid={p.pid}", flush=True)
            time.sleep(5)
        time.sleep(20)
        still = []
        for name, seed, p, f in active:
            if p.poll() is None:
                still.append((name, seed, p, f))
            else:
                f.close()
                print(f"[END] {name} seed={seed} exit={p.returncode}", flush=True)
        active = still
    print("[QUEUE3] all jobs finished", flush=True)


if __name__ == "__main__":
    main()
