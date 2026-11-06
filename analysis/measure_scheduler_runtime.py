"""E2: per-slot runtime of each scheduler mode over recorded production inputs.

Drives one frozen-policy episode per scene and records the exact inputs the
environment handed to ``_schedule_current``, then re-times all 7 scheduler
modes over those identical inputs on the CPU.  No training is performed.
"""
from __future__ import annotations
import csv, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from uavqos import paper_final_presets as PF
from uavqos import runner as R
from uavqos.env import TwoTierUAVEnv
from uavqos.scheduler import (
    age_weighted_maxcost_1swap_schedule,
    classical_proportional_schedule,
)

OUT_DIR = ROOT / "results" / "05_SCHEDULER_RUNTIME"
TRAIN_SEED = 7
EVAL_SEEDS = (9000, 9001, 9002)
REPS = 5

ROCS_MODES = ("age_weighted_maxcost_1swap", "rocs0_no_age", "rocs0_no_1swap")
CLASSICAL_MODES = ("max_cqi", "pf", "max_qos", "equal_share")
ALL_MODES = ROCS_MODES + CLASSICAL_MODES


def _record_episode(env: TwoTierUAVEnv, agent, eval_seed: int) -> list[dict]:
    policy = R.make_agent_policy(agent, motion="learned", power="learned", deterministic=True)
    obs, _ = env.reset(seed=eval_seed)
    e = env.e
    dt = float(e.dt_s)
    lam = float(
        e.age_penalty_lambda_per_s
        if e.scheduler_age_weight_lambda_per_s is None
        else e.scheduler_age_weight_lambda_per_s
    )
    records: list[dict] = []
    orig = env._schedule_current

    def wrapper(requested, association, access_peak, backhaul_capacity, active_mask, *, users=None):
        users_arr = np.zeros(0, dtype=np.int64) if users is None else np.asarray(users, dtype=np.int64)
        records.append({
            "eval_seed": eval_seed,
            "step_index": int(env.step_index),
            "dt_s": dt,
            "lambda_per_s": lam,
            "requested": np.asarray(requested, dtype=np.float64).copy(),
            "association": np.asarray(association, dtype=np.int64).copy(),
            "access_peak": np.asarray(access_peak, dtype=np.float64).copy(),
            "backhaul_capacity": np.asarray(backhaul_capacity, dtype=np.float64).copy(),
            "active_mask": np.asarray(active_mask, dtype=bool).copy(),
            "users": users_arr,
            "qos_sub": np.asarray(env.qos_bps[users_arr], dtype=np.float64).copy(),
            "outage_sub": np.asarray(env.strict_qos_outage_time_s[users_arr], dtype=np.float64).copy(),
            "cum_sub": np.asarray(env.cumulative_delivered[users_arr], dtype=np.float64).copy(),
            "age_sub": np.asarray(env.user_service_age_s[users_arr], dtype=np.float64).copy(),
            "strict_sub": np.asarray(env.strict_qos_success_time_s[users_arr], dtype=np.float64).copy(),
        })
        return orig(requested, association, access_peak, backhaul_capacity, active_mask, users=users)

    env._schedule_current = wrapper
    try:
        for _ in range(e.episode_steps):
            action = policy(env, obs)
            obs, _, terminated, truncated, _ = env.step(action)
            if terminated or truncated:
                break
    finally:
        env._schedule_current = orig
    return records


def _build_calls(mode: str, rec: dict):
    q = rec["qos_sub"]
    assoc = rec["association"]
    acc = rec["access_peak"]
    bh = rec["backhaul_capacity"]
    mask = rec["active_mask"]
    if mode == "age_weighted_maxcost_1swap":
        return lambda: age_weighted_maxcost_1swap_schedule(
            q, assoc, acc, bh, mask, outage_s=rec["outage_sub"],
            dt_s=rec["dt_s"], lambda_per_s=rec["lambda_per_s"],
            enable_1swap=True, policy_name="age_weighted_maxcost_1swap")
    if mode == "rocs0_no_age":
        return lambda: age_weighted_maxcost_1swap_schedule(
            q, assoc, acc, bh, mask, outage_s=rec["outage_sub"],
            dt_s=rec["dt_s"], lambda_per_s=0.0,
            enable_1swap=True, policy_name="rocs0_no_age_maxcost_1swap")
    if mode == "rocs0_no_1swap":
        return lambda: age_weighted_maxcost_1swap_schedule(
            q, assoc, acc, bh, mask, outage_s=rec["outage_sub"],
            dt_s=rec["dt_s"], lambda_per_s=rec["lambda_per_s"],
            enable_1swap=False, policy_name="rocs0_age_weighted_maxcost_greedy")
    if mode == "max_cqi":
        priority = np.maximum(acc, 0.0)
        label = "classical_max_cqi"
    elif mode == "pf":
        elapsed_s = max((rec["step_index"] + 1) * rec["dt_s"], rec["dt_s"])
        avg_bps = rec["cum_sub"] / elapsed_s
        priority = np.maximum(acc, 0.0) / (1.0 + avg_bps / 1.0e6)
        label = "classical_proportional_fair"
    elif mode == "max_qos":
        age_s = np.maximum(rec["age_sub"], 1e-12)
        sqa = np.clip(rec["strict_sub"] / age_s, 0.0, 1.0)
        priority = 1.0 / (sqa + 0.05)
        label = "classical_max_qos_lowest_sqa_first"
    else:
        priority = np.ones(q.size, dtype=np.float64)
        label = "classical_equal_share"
    return lambda: classical_proportional_schedule(
        q, assoc, acc, bh, mask, access_priority=priority, policy_name=label)


def main() -> None:
    cfg = PF.final_h128_branch_credit_config(seed=TRAIN_SEED)
    env = TwoTierUAVEnv(cfg)
    records: list[dict] = []
    try:
        agent = R.build_agent("branch_credit_sac", env, device="cuda")
        agent.load(str(ROOT / "anchors" / "HQC_SAC_MAIN" / f"seed_{TRAIN_SEED}" / "agent.pt"))
        for eval_seed in EVAL_SEEDS:
            records.extend(_record_episode(env, agent, eval_seed))
            print(f"[RECORD] eval_seed={eval_seed} slots={sum(1 for r in records if r['eval_seed']==eval_seed)}", flush=True)
    finally:
        env.close()
    print(f"[RECORD] total recorded scheduler calls: {len(records)}", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_slot_rows: list[dict] = []
    for mode in ALL_MODES:
        call_fn = None
        times: list[float] = []
        for rec in records:
            call_fn = _build_calls(mode, rec)
            call_fn()  # warm-up, also verifies the call is valid on this input
            best = float("inf")
            for _ in range(REPS):
                t0 = time.perf_counter_ns()
                call_fn()
                best = min(best, (time.perf_counter_ns() - t0) / 1e6)
            times.append(best)
            per_slot_rows.append({
                "mode": mode, "eval_seed": rec["eval_seed"], "step_index": rec["step_index"],
                "n_users": int(rec["users"].size), "runtime_ms": best,
            })
        arr = np.asarray(times)
        summary = {
            "mode": mode, "n_calls": int(arr.size),
            "mean_ms": float(arr.mean()), "p50_ms": float(np.quantile(arr, 0.50)),
            "p95_ms": float(np.quantile(arr, 0.95)), "p99_ms": float(np.quantile(arr, 0.99)),
            "max_ms": float(arr.max()),
        }
        print(f"[TIME] {mode}: mean={summary['mean_ms']:.4f}ms p95={summary['p95_ms']:.4f}ms max={summary['max_ms']:.4f}ms", flush=True)
        with (OUT_DIR / "scheduler_runtime_summary.csv").open("a", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(summary.keys()))
            if f.tell() == 0:
                w.writeheader()
            w.writerow(summary)
    with (OUT_DIR / "scheduler_runtime_per_slot_ms.csv").open("w", newline="", encoding="utf-8-sig") as f:
        keys = sorted({k for r in per_slot_rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(per_slot_rows)
    print(f"[SUCCESS] E2 scheduler runtime written to {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
