"""Single-process per-slot inference latency for the frozen main policy."""
from __future__ import annotations
from pathlib import Path
import json
import sys
import time

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from uavqos import paper_final_presets as PF
from uavqos import runner as R
from uavqos.env import TwoTierUAVEnv

OUT = ROOT / "analysis" / "latency_summary.json"
CFG = PF.final_h128_branch_credit_config(seed=7)

def measure(device: str, n: int = 2000):
    env = TwoTierUAVEnv(CFG)
    try:
        agent = R.build_agent("branch_credit_sac", env, device=device)
        agent.load(str(ROOT / "anchors" / "HQC_SAC_MAIN" / "seed_7" / "agent.pt"))
        obs, _ = env.reset(seed=9000)
        # warmup
        for _ in range(100):
            agent.select_action(obs, deterministic=True)
        if device == "cuda":
            torch.cuda.synchronize()
        times = []
        for _ in range(n):
            t0 = time.perf_counter()
            agent.select_action(obs, deterministic=True)
            if device == "cuda":
                torch.cuda.synchronize()
            times.append((time.perf_counter() - t0) * 1000.0)
        times = np.asarray(times)
        params = sum(
            sum(p.numel() for p in getattr(agent, name).parameters())
            for name in ("motion_actor", "power_actor", "critic", "power_critic")
            if hasattr(agent, name)
        )
        return {
            "device": device,
            "n": n,
            "mean_ms": float(times.mean()),
            "p50_ms": float(np.quantile(times, 0.50)),
            "p95_ms": float(np.quantile(times, 0.95)),
            "p99_ms": float(np.quantile(times, 0.99)),
            "max_ms": float(times.max()),
            "online_parameters": int(params),
        }
    finally:
        env.close()

if __name__ == "__main__":
    result = {"gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
              "torch": torch.__version__,
              "measurements": [measure("cuda"), measure("cpu")]}
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
