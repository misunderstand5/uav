"""E3: controller online parameter counts and batch-1 inference latency.

Measures every frozen controller from the paper matrix (main branch-credit
SAC, TD3, PPO, CDA, recursive-credit, flat-relay, joint-SAC, motion-only,
power-only) on both CUDA and CPU.  Only the networks needed at deployment
time are counted as online parameters; critic networks are reported
separately for reference.  No training is performed.
"""
from __future__ import annotations
import csv, json, sys, time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_utils import checkpoint_path, _motion_physics
from run_matrix_train import build_config
from uavqos import runner as R
from uavqos.env import TwoTierUAVEnv

OUT_DIR = ROOT / "results" / "04_CONTROLLER_LATENCY"
TRAIN_SEED = 7
EVAL_SEED = 9000
WARMUP = 100
N_GPU = 1000
N_CPU = 500

METHODS = ("HQC_SAC_MAIN", "TD3", "PPO", "CDA_SAC_ADAPTED", "RECURSIVE_CREDIT_H128",
           "FLAT_RELAY_IMMEDIATE", "JOINT_SAC_PM", "MOTION_ONLY", "POWER_ONLY")


def _build_agent(method: str, env: TwoTierUAVEnv, device: str):
    if method == "TD3":
        from uavqos.agents.continuous_baselines import TD3Agent, TD3HyperParams
        return TD3Agent(env.observation_dim, env.max_relays, "state_u98c",
                        _motion_physics(env), TD3HyperParams(), device)
    if method == "PPO":
        from uavqos.agents.continuous_baselines import PPOAgent, PPOHyperParams
        return PPOAgent(env.observation_dim, env.max_relays, "state_u98c",
                        _motion_physics(env), PPOHyperParams(), device)
    algorithm = "sac" if method == "JOINT_SAC_PM" else "branch_credit_sac"
    return R.build_agent(algorithm, env, device=device)


def _make_policy(method: str, agent):
    if method in ("TD3", "PPO"):
        return lambda env_, obs: agent.select_action(obs, deterministic=True)
    if method == "MOTION_ONLY":
        return R.make_agent_policy(agent, motion="learned", power="equal", deterministic=True)
    if method == "POWER_ONLY":
        return R.make_agent_policy(agent, motion="fixed_circle", power="learned", deterministic=True)
    return R.make_agent_policy(agent, motion="learned", power="learned", deterministic=True)


def _count_params(method: str, agent) -> tuple[int, int, list[str]]:
    if method == "MOTION_ONLY":
        online_names = ["motion_actor"]
    elif method == "POWER_ONLY":
        online_names = ["power_actor"]
    else:
        online_names = []
        if hasattr(agent, "motion_actor"):
            online_names.append("motion_actor")
        if hasattr(agent, "power_actor"):
            online_names.append("power_actor")
        if hasattr(agent, "actor"):
            online_names.append("actor")
    critic_names = [n for n in ("critic", "power_critic") if hasattr(agent, n)]
    online = sum(sum(p.numel() for p in getattr(agent, n).parameters()) for n in online_names)
    critic = sum(sum(p.numel() for p in getattr(agent, n).parameters()) for n in critic_names)
    if hasattr(agent, "log_std"):
        online += int(agent.log_std.numel())
    return int(online), int(critic), online_names


def _measure(method: str, device: str, n: int):
    cfg = build_config(method, TRAIN_SEED, None, None)
    ckpt = checkpoint_path(method, TRAIN_SEED)
    if not ckpt.exists():
        raise FileNotFoundError(f"Missing checkpoint for {method} seed={TRAIN_SEED}: {ckpt}")
    env = TwoTierUAVEnv(cfg)
    try:
        agent = _build_agent(method, env, device)
        agent.load(str(ckpt))
        policy = _make_policy(method, agent)
        obs, _ = env.reset(seed=EVAL_SEED)
        for _ in range(WARMUP):
            policy(env, obs)
        if device == "cuda":
            torch.cuda.synchronize()
        times = []
        for _ in range(n):
            t0 = time.perf_counter()
            policy(env, obs)
            if device == "cuda":
                torch.cuda.synchronize()
            times.append((time.perf_counter() - t0) * 1000.0)
        arr = np.asarray(times)
        online, critic, online_names = _count_params(method, agent)
        return {
            "method": method, "device": device, "n": n,
            "mean_ms": float(arr.mean()), "p50_ms": float(np.quantile(arr, 0.50)),
            "p95_ms": float(np.quantile(arr, 0.95)), "p99_ms": float(np.quantile(arr, 0.99)),
            "max_ms": float(arr.max()),
            "online_params": online, "offline_critic_params": critic,
            "online_networks": "+".join(online_names),
        }
    finally:
        env.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for method in METHODS:
        row_gpu = _measure(method, "cuda", N_GPU)
        rows.append(row_gpu)
        print(f"[LATENCY] {method} cuda mean={row_gpu['mean_ms']:.3f}ms "
              f"p95={row_gpu['p95_ms']:.3f}ms online={row_gpu['online_params']}", flush=True)
        row_cpu = _measure(method, "cpu", N_CPU)
        rows.append(row_cpu)
        print(f"[LATENCY] {method} cpu   mean={row_cpu['mean_ms']:.3f}ms "
              f"p95={row_cpu['p95_ms']:.3f}ms online={row_cpu['online_params']}", flush=True)
    keys = sorted({k for r in rows for k in r})
    with (OUT_DIR / "controller_latency_params.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    (OUT_DIR / "latency_manifest.json").write_text(json.dumps({
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "torch": torch.__version__,
        "train_seed": TRAIN_SEED, "eval_seed": EVAL_SEED,
        "warmup": WARMUP, "n_gpu": N_GPU, "n_cpu": N_CPU,
        "note": "batch=1 deterministic inference; GPU timing includes cuda synchronize.",
    }, indent=2), encoding="utf-8")
    print(f"[SUCCESS] E3 latency table written to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
