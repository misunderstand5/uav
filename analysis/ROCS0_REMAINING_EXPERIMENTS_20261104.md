# 改用 ROCS-0 后：还需要跑什么实验（TVT 版）

- 日期：2026-11-04
- 决策：**论文主方法改用 ROCS-0；旧 HA-QCS 不再使用。**
- 已有数据：45 个训练 run、common-30 990 episodes、泛化 810 episodes、provisional final100 2400 episodes。
- 本文只回答：**在 ROCS-0 下，TVT 论文还缺哪些实验、每个实验怎么设计、要多少时间。**

---

## 0. 一句话结论

> **主表、2×2、λ、泛化、final100 已经够了；真正还缺的是“ROCS-0 vs 经典调度器”“调度器/控制器运行时”“能耗”“Joint-SAC 处理”四块。**  
> 其中 **PF/Max-CQI 对比** 和 **运行时/能耗** 是 TVT 审稿人最可能追问的；K/信道是加分项，不是第一优先。

---

## 1. 已有、不用再跑

| 类别 | 内容 | 规模 |
|---|---|---|
| 训练 | main / CDA / Recursive / Motion / Power / Flat-Relay / Joint-SAC / TD3 / PPO / LS020 / R005 / R020 / S040 / no-age / no-1swap | 45 runs × 400 EP |
| common-30 | 11 方法 × 3 seeds × 30 scenes | 990 episodes |
| 2×2 | Full / Flat-Relay / Recursive / CDA | 360 episodes |
| λ | main / R005 / S040 / R020 / LS020 / no-age | 已评估 |
| 调度器 | nominal / no-age / no-1swap（算法级重训） | 270 episodes |
| 泛化 | load 0.8/1.0/1.2、mobility 1/2/3、init 3 点；main/TD3/CDA | 810 episodes |
| final100（provisional） | main/CDA/Recursive/Motion/Power/Flat/TD3/PPO × 100 scenes | 2400 episodes |
| PI | common-30 | 30 scenes |
| 主方法时延 | CPU 1.47 ms / P95 1.92；GPU 4.47/6.52 | 已完成 |
| per-relay 负载 | max BH、Jain、min relay QSR | 已计算 |

**这些都不需要重跑。**

---

## 2. 必须补的实验（P0，投稿前）

### E1. 经典调度器对比（ROCS-0 vs PF / Max-CQI / Max-QoS / Equal）

**为什么必须做**：现在只有 no-age/no-1swap 两个 ROCS-0 变体，没有和经典调度器比。TVT 审稿人会问：“为什么不用 PF / max-CQI？ROCS-0 到底比它们好在哪？”

**设计**：
- 冻结同一个 main controller；
- 调度器：ROCS-0、no-age、no-1swap、**PF**、**Max-CQI**、**Max-QoS**、**Equal-share**（至少 4 个）；
- 3 seeds × 30 scenes = 90 episodes/调度器；
- 6–7 个调度器 ≈ **540–630 episodes**；
- 指标：QSR、P5、P95、Jain、Goodput、**单 slot 调度耗时**。

**代码量**：当前 `uavqos/scheduler.py` 只有 ROCS-0；需要移植/实现 PF、Max-CQI、Max-QoS、Equal-share。旧工程 `uav_qos_paper/paper/schedulers_extra.py` 有 PF/M-LWDF-A/Equal-FDMA 可参考。**约 1–2 天。**

**运行时间**：约 **30–40 min**（2 workers）。

**论文位置**：Table V（scheduler comparison）、Fig. 5。

---

### E2. 调度器运行时（ROCS-0 + baselines）

**为什么必须做**：TVT 很看重实时性。主方法 controller 时延已有，但 **ROCS-0 的 per-slot 调度耗时**还没测。

**设计**：
- 单进程、batch=1，测 `_schedule_current` 的 mean/P95/max；
- 对比 no-age、no-1swap、PF、Max-CQI；
- 目标 < 500 ms（大概率 < 5 ms）。

**代码量**：0.5 天（instrument scheduler）。
**运行时间**：10 min。
**论文位置**：Table VI（efficiency）。

---

### E3. 控制器参数量/时延表

**为什么必须做**：现在只有 main 的 CPU/GPU 时延；TD3/PPO/CDA/Joint 没有。

**设计**：
- 参数量：main 365,451；CDA 365,245；TD3 ~372k；PPO ~363k；Joint ~368k；
- 单时隙推理时延（CPU/GPU，batch=1，1000 次）；
- 训练时间（400 EP）。

**代码量**：0.5 天（复用 `analysis/measure_latency.py`，支持多 agent）。
**运行时间**：10–15 min。
**论文位置**：Table VI。

---

### E4. 能耗 / 能量效率

**为什么必须做**：主方法 C-UAV path 541 m vs CDA 465 m；审稿人会问“性能提升是不是靠多飞”。现在 eval episodes 没有 energy 字段。

**设计**：
- 在 `evaluate_model` 里累加 `c_physical_propulsion_energy_j`、`m_energy_j`；
- 对 main/TD3/CDA/PPO 在 9000–9029 重跑（4×3×30 = **360 episodes**）；
- 指标：QSR per Joule、goodput per Joule、C-UAV path/energy；
- 画 QSR–path / QSR–energy Pareto。

**代码量**：0.5 天。
**运行时间**：约 **20 min**。
**论文位置**：Table VI、Fig. 9。

---

### E5. Joint-SAC：修稳或删除（二选一）

**现状**：seed 27 critic loss 1582，QSR 0.52；seed 7/17 也只有 0.62/0.68。作为 flat SAC 基线不可用。

**选项**：
- **A. 修稳**：降 lr、加 target update/梯度裁剪，重训 3 seeds；约 1–2 天调参 + 1 h 训练。
- **B. 删除**：主表用 TD3/PPO/CDA/PI；Joint-SAC 放附录并注明“训练不稳定，未纳入主表”。TVT 仍可接受，因为已有 3 个 RL 基线。

**建议**：如果时间紧，选 **B**；主方法已经不缺“flat SAC”对照（CDA 就是 flat 双 actor）。

---

### E6. final100 统计（不用跑）

- 对 provisional final100 做 paired bootstrap / Holm / per-seed；
- 主表：main vs TD3/PPO/CDA/Recursive/Flat/Motion/Power；
- 产出 Table II + Fig. 3/4。
- **不要重跑 final100**，除非主方法/主表方法变更。建议现在冻结 main + 7 个方法，把 10000–10099 当作 held-out test，并在论文中写明“main/baselines frozen before test”。

---

## 3. 强烈建议补的实验（P1）

### E7. 高负载固定 N=120 的调度器对比

**为什么**：论文的 P1 是“尾部约束”，最终要证明 ROCS-0 在高负载下仍能压住 P95；common-30 有峰值，但没有固定 N=120 的 controlled comparison。

**设计**：
- 固定 N=20/60/120（关闭动态到达/离开，或固定用户数）；
- 6 个调度器 ×3 个 N ×3 seeds ×10 scenes = **540 episodes**；
- 指标：QSR、P5、P95、Jain；标出 T_out=15 s 是否满足。

**代码量**：当前 env 是 dynamic sessions；需要 fixed-N config/预设，约 1 天。
**运行时间**：约 **30 min**。
**论文位置**：Table V 子表、Fig. 5。

---

### E8. 信道/干扰鲁棒性

**为什么**：TVT 会问“换信道/干扰还行吗”。现在只有 nominal 参数。

**设计**：
- 3 个变体：access interference 0 / 0.25 / 0.5；或 noise PSD ×1 / ×2 / ×5；
- main/TD3/CDA ×3 seeds ×30 scenes = **270 episodes**；
- 指标：QSR/P5/P95 相对退化。

**代码量**：0.5 天（config mutator；`RadioConfig.access_interference_leakage`/`noise_psd_w_hz`）。
**运行时间**：约 **15 min**。
**论文位置**：Table VII / Fig. 10。

---

### E9. K 可扩展性（K=3/4/5/6）

**为什么**：论文声称 variable K / K_max=6，但实验只有 K=4。TVT 会问 scalability。

**现实**：当前 main 是 K=4 训练的；不能直接换 K。需要：
- 用 K_max=6 + mask 的 variable-K 模型重训 3 seeds（400 EP）；
- 或明确写“fixed K=4，variable-K 是架构支持、未做实验”，放 limitations。

**代码/训练量**：3–5 天 + 3–4 h 训练。
**建议**：如果时间不够，**不要声称 K 可扩展**；写 fixed K=4，reviewer 问再补。

---

## 4. 可选加分（P2）

| 实验 | 设计 | 成本 | 价值 |
|---|---|---|---|
| trace-driven 负载 | Alibaba trace 到达强度 vs 四阶段 | 2–4 天 | realism |
| case study | 2 个场景：ROCS-0 救回 vs completion-first 长 outage | 1–2 天画图 | 机理解释 |
| per-relay 负载图 | max BH、min relay QSR、Jain | 已有数据，1 天画图 | 机制证据 |
| 5 seeds | main + TD3/PPO/CDA 加 seeds 37/47 | 6 runs ×1 h | 统计更强 |

---

## 5. 论文重写（不是实验，但比实验更急）

当前 PDF 还是 **HA-QCS**；改成 ROCS-0 后，以下全部要改：

1. **Abstract**：HA-QCS/guard rescue → ROCS-0/age weight + 1-swap；替换 82.10/45.38/27.62 等旧数字。
2. **Intro contributions**：HA-QCS 贡献改为 ROCS-0；保留 branch-credit。
3. **Section IV-A / Algorithm 1**：HA-QCS 的 feasibility/guard/cost/residual → ROCS-0 的 `w_i=1+λ_s(O_i+Δt)`、max-cost density、best-improvement 1-swap、refill。
4. **Section IV-E complexity**：ROCS-0 复杂度。
5. **Table IV**：用 common-30/final100 新数字；补 CDA、Joint-SAC 标签。
6. **Table V**：ROCS-0 vs no-age/no-1swap + PF/Max-CQI。
7. **Table VI ablation**：2×2 + branch ablations 新数字。
8. **Fig. 2**：改成 ROCS-0 三栏（environment / branch-credit / ROCS-0 3 steps），删掉 guard/rescue/cost/residual。
9. **Fig. 5/6**：scheduler/λ 新图。
10. **P1/T_guard**：删除 guard 阈值；改成 λ_s 的 mean-tail 设计目标；no-age/no-1swap 的尾部违反作为证据。
11. **Title**：可改为 “Age-Aware Minimum-QoS Scheduling and Branch-Credit Learning for Two-Tier UAV Networks”。

---

## 6. 推荐的最小 TVT 集（约 1 周）

| 顺序 | 任务 | 代码 | 运行 |
|---|---|---|---|
| 1 | 冻结 main + 7 方法；final100 统计 | 0 | 1 h 分析 |
| 2 | E1 调度器 baselines（PF/Max-CQI/Max-QoS/Equal） | 1–2 d | 30–40 min |
| 3 | E2 调度器 runtime | 0.5 d | 10 min |
| 4 | E3 控制器 cost 表 | 0.5 d | 15 min |
| 5 | E4 能耗重评 | 0.5 d | 20 min |
| 6 | E5 Joint-SAC：删除或修稳 | 0–2 d | 0–1 h |
| 7 | 论文重写 + Fig. 2 ROCS-0 | 3–5 d | — |

**合计：约 6–8 个工作日**（不含 K/信道/trace）。

---

## 7. 强 TVT 集（约 2–3 周）

最小集 + E7 高负载 N=120 + E8 信道 + E9 K + case study + per-relay 图 + 5 seeds。

---

## 8. 一句话总结

> **ROCS-0 版最缺的不是“再跑主表”，而是“和经典调度器比 + 运行时 + 能耗 + Joint-SAC 处理”。** 主表/2×2/λ/泛化/final100 已经够；补 E1–E4、处理 E5，再重写 HA-QCS→ROCS-0，TVT 的实验闭环就基本完整。K/信道是加分项；fixed K=4 写清楚即可。
