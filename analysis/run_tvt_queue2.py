"""Second TVT queue: TD3 and PPO baselines, after the first 6 jobs finish.

Waits for Flat-Relay x3 and Joint-SAC x3, then runs TD3 x3 and PPO x3 with at
most three concurrent processes on the 8-GB GPU.
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

FIRST = [
    ("FLAT_RELAY_IMMEDIATE", 7), ("FLAT_RELAY_IMMEDIATE", 17), ("FLAT_RELAY_IMMEDIATE", 27),
    ("JOINT_SAC_PM", 7), ("JOINT_SAC_PM", 17), ("JOINT_SAC_PM", 27),
]
SECOND = [
    ("TD3", 7), ("TD3", 17), ("TD3", 27),
    ("PPO", 7), ("PPO", 17), ("PPO", 27),
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


def launch(method: str, seed: int):
    out = OUT_ROOT / method / f"seed_{seed}"
    out.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    if method in ("TD3", "PPO"):
        cmd = [sys.executable, "-u", str(ROOT / "scripts" / "train_td3_ppo.py"),
               "--algo", method.lower(), "--seed", str(seed), "--episodes", str(EPISODES),
               "--out-dir", str(out), "--device", "cuda"]
    else:
        cmd = [sys.executable, "-u", str(ROOT / "scripts" / "run_matrix_train.py"),
               "--method", method, "--seed", str(seed), "--episodes", str(EPISODES),
               "--out-dir", str(out), "--device", "cuda"]
    f = open(LOG_ROOT / f"{method}__seed_{seed}.stdout.log", "a", encoding="utf-8")
    p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT)
    return p, f


def main():
    print("[WAIT] first queue", flush=True)
    while not all(done(m, s) for m, s in FIRST):
        time.sleep(60)
    print("[START] second queue", flush=True)
    queue = [j for j in SECOND if not done(*j)]
    active = []
    while queue or active:
        while queue and len(active) < 3:
            method, seed = queue.pop(0)
            p, f = launch(method, seed)
            active.append((method, seed, p, f))
            print(f"[START] {method} seed={seed} pid={p.pid}", flush=True)
            time.sleep(5)
        time.sleep(20)
        still = []
        for method, seed, p, f in active:
            if p.poll() is None:
                still.append((method, seed, p, f))
            else:
                f.close()
                print(f"[END] {method} seed={seed} exit={p.returncode}", flush=True)
        active = still
    print("[QUEUE2] all jobs finished", flush=True)


if __name__ == "__main__":
    main()
