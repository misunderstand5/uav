# 经典调度器基线修复记录（E1 重做）

- 日期：2026-11-04
- 触发：Equal-share QSR=0.753 明显不合理（旧实现并非均分）。
- 结论：旧实现中 PF / Max-CQI / Max-QoS / Equal-share 全部只是 ROCS-0 机制（可行性筛选 + 完成优先 + 1-swap + 回填）在 λ_s=0 下换不同静态权重的变体；Equal-share 与 no-age 冻结策略逐位相同。对比无效。

## 修复内容

- `uavqos/scheduler.py` 新增 `classical_proportional_schedule`：每 relay 独立、按优先级比例分配接入时隙与回传速率、按需求封顶、工作守恒；**无**可行性筛选 / 完成优先 / 1-swap。
- `uavqos/env.py` `_schedule_current` 四种模式接入正确权重：
  - `equal_share`：权重全 1（等分资源，非等速率）；
  - `max_cqi`：权重 = 接入峰值速率（按 C/I 比例）；
  - `pf`：权重 = 峰值速率 / (1 + 历史平均速率/1e6)；
  - `max_qos`：权重 = 1/(当前 SQA + 0.05)（当前 SQA 最低优先）。
- 新增 `tests/test_classical_schedulers.py`（8 个用例），全套 42 测试通过。
- 旧数据备份：`results/_pre_fix_backup_E1/`（48 个文件）。
- 重跑：15 方法 × 3 seeds × 30 scenes = 1350 episodes（仅 4 个经典调度器重跑，其余 11 方法跳过）。

## 新结果（common-30，n=90，冻结主控制器）

| 调度器 | QSR | P5 | P95(s) | Jain | Goodput |
|---|---:|---:|---:|---:|---:|
| ROCS-0 (main) | **0.810** | **0.237** | **10.19** | **0.869** | **50.75** |
| no-age（重训） | 0.809 | 0.029 | 65.34 | 0.792 | 50.15 |
| no-1swap（重训） | 0.807 | 0.132 | 14.97 | 0.825 | 49.81 |
| PF | 0.398 | 0.002 | 124.64 | 0.511 | 34.34 |
| Max-CQI | 0.397 | 0.000 | 119.89 | 0.485 | 34.96 |
| Max-QoS（SQA 最低优先） | 0.278 | 0.002 | 138.92 | 0.439 | 30.38 |
| Equal-share | 0.355 | 0.000 | 129.04 | 0.427 | 31.85 |

- 完整数据：`results/02_COMMON30_VALIDATION/`；配对 bootstrap：`analysis/scheduler_comparison_classical.csv`。
- 与旧 HA-QCS 稿 Table V（PF 30.48、Equal-share 4.52，N=120）量级一致，故事自洽。

## 论文注意事项

1. 四个经典调度器共用冻结的主控制器（与 ROCS-0 共同训练）——这是"固定控制器换调度器"的标准设计，论文需显式说明。
2. "Max-QoS" 名称需在论文中定义清楚：当前实现为"当前 SQA 最低优先"（worst-served-first）。
3. 其余未决项不变：Joint-SAC seed 27 发散（E5）、λ 主配置选择（S040 P95=6.26 优于 main 需解释）。
