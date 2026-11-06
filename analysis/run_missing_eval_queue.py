"""Wait for common-30, then run generalization and a provisional 100-seed test.

The 100-seed run is deliberately written to a *_PROVISIONAL directory: the
official sealed set remains results/08_FINAL_TEST100 until the method is frozen.
"""
from __future__ import annotations
import subprocess
import sys
import time
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "results" / "00_AUDIT_PROGRESS" / "missing_eval_queue.log"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


def common30_done() -> bool:
    d = ROOT / "results" / "02_COMMON30_VALIDATION"
    methods = ["FLAT_RELAY_IMMEDIATE", "JOINT_SAC_PM", "TD3", "PPO",
               "HQC_SAC_NO_AGE", "HQC_SAC_NO_1SWAP"]
    for m in methods:
        for s in (7, 17, 27):
            f = d / f"nominal__{m}__trainseed_{s}__episodes.csv"
            if not f.exists():
                return False
            try:
                if len(pd.read_csv(f, encoding="utf-8-sig")) < 30:
                    return False
            except Exception:
                return False
    return True


def run(cmd: list[str], tag: str):
    log(f"[START] {tag}: {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=str(ROOT), text=True)
    log(f"[END] {tag} exit={p.returncode}")
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def main():
    log("=== missing-eval queue start ===")
    while not common30_done():
        time.sleep(30)
    log("[OK] common-30 new methods complete")

    run([sys.executable, "-u", str(ROOT / "scripts" / "run_generalization_matrix.py"),
         "--methods", "HQC_SAC_MAIN,TD3,CDA_SAC_ADAPTED",
         "--seeds", "9000-9009", "--device", "cuda",
         "--out-dir", str(ROOT / "results" / "05_GENERALIZATION")],
        "generalization main/TD3/CDA, 9 scenarios x 10 scenes")

    run([sys.executable, "-u", str(ROOT / "scripts" / "evaluate_common30_matrix.py"),
         "--methods", "HQC_SAC_MAIN,CDA_SAC_ADAPTED,RECURSIVE_CREDIT_H128,MOTION_ONLY,POWER_ONLY,FLAT_RELAY_IMMEDIATE,TD3,PPO",
         "--seeds", "10000-10099", "--device", "cuda", "--workers", "3",
         "--out-dir", str(ROOT / "results" / "08_FINAL_TEST100_PROVISIONAL")],
        "provisional 100-seed test (not the sealed set)")

    log("=== missing-eval queue complete ===")


if __name__ == "__main__":
    main()
