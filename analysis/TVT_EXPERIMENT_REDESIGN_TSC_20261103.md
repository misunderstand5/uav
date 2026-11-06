# 参考 TSC 论文后的 TVT 实验重设计

- 日期：2026-11-03
- 参考论文：X. Zhang, R. Jia, Q. Yin, Z. Zheng, M. Li, "Asynchronous Task Scheduling and Resource Allocation for UAV-Enabled Mobile Edge Computing Networks," **IEEE Transactions on Services Computing**, vol. 19, no. 1, pp. 167–180, 2026, DOI: 10.1109/TSC.2025.3645776.
- 说明：该论文在 IEEE 付费墙后，我拿到的是标题、作者、摘要、DOI、卷期页码和引用信息；**没有拿到完整实验节的 PDF**。下面不是逐字复述它的实验，而是从摘要透露的评价范式（trace-driven、energy utility、missing ratio、asynchronous/layered ablation、scalability）出发，重设计你这篇 TVT 的实验。

---

## 0. 先回答“这些实验是不是你之前的”

**部分是，而且我应该更早说清楚。**

- 你在旧工程 `uav_qos_paper/paper/registry.py` 里已经列过：
  - baselines：TD3、PPO、MAPPO、Joint-SAC (PM)、Joint-SAC (0.90M)、CDA-SAC；
  - ablations：Recursive-Power、Flat-Relay、Fixed-Power；
  - v15：Credit-N5、Credit-N20、Beta0、P.1410。
- 旧 README 的 E1–E8 也已经包含：6 个学习方法、6 种调度器 × N=20–120、动态突发、到达率 0.75–1.5、K=3/4/5/6、信道鲁棒性。
- 所以“TD3/PPO/Joint-SAC/Flat-Relay/scheduler 对比”**确实来自你之前的实验清单**，不是我从零发明的。我参考它，是因为这些就是这类论文的标准对照。

**但不能直接复用旧结果：**
- 旧工程是 domain randomization / dynamic K / 不同地图宽度的 contract；当前是 **fixed-500 m + dynamic sessions**。环境、奖励、观测、调度器都变了，旧模型不能同表。
- 旧工程用 best.pt（Dev3 选）；当前用 final EP400。协议不同。
- 旧工程的 CDA/Flat-Relay 配置与当前 `paper_cda_sac_adapted_fixed500_config` 不完全一样。

**这次真正新设计的：**
1. **2×2 因子消融**（shared/flat × immediate/unified）——旧工程有 Flat-Relay 和 Recursive-Power，但没有把它们和 CDA 组成 2×2，也没有补 Flat+immediate 这个角。
2. **λ Pareto**（main → R005 → S040；LS020 被支配）——旧工程没有这个分析。
3. **per-relay load balancing**（max BH 1.26 vs 2.22；min relay QSR 0.741 vs 0.618）——旧工程没有把它作为主机理。
4. **TSC 风格的 trace-driven / energy utility / missing ratio / async-layered 评估**——这是本文件的新设计。

> 一句话：**实验“名字”很多来自你之前的清单；实验“合同、2×2、机理指标、trace-driven 评估”是这次新设计的。** 旧结果不能直接搬，必须在新 contract 下重跑。

---

## 1. TSC 论文的实验范式（从摘要可确认的部分）

摘要明确写了：

1. **问题**：现有 MEC 调度器把全部 service provider 同步调度；实际任务随机到达、所需资源随时间变化。
2. **方法**：AL-MAPPO（asynchronous layered multi-agent PPO），多 UAV 异步执行动作，discrete-continuous layered action space。
3. **目标**：最大化 average per-UAV energy utility，最小化 missing ratio。
4. **实验**：trace-driven simulations based on **Alibaba Cluster Data V2017**，与多个 baseline 比较。

从这类 TSC 论文的通常结构，可以推断其实验节大致包含：

| 模块 | 内容 |
|---|---|
| Simulation setup | 区域、UAV 数、ED 数、任务大小、CPU、带宽、功率、噪声、时隙 |
| Trace | Alibaba Cluster Data V2017 的任务到达/资源需求 |
| Baselines | MAPPO、PPO、DDPG、SAC、贪心、随机（至少 4–6 个） |
| Main results | average per-UAV energy utility、missing ratio |
| Convergence | 训练曲线/收敛回合 |
| Ablation | asynchronous vs synchronous；layered vs flat action |
| Scalability | UAV 数、ED 数、任务到达率 |
| Runtime | 训练/推理时间、复杂度 |

**这套范式的核心不是“方法多”，而是：**
- 用 **真实 trace** 证明负载不是 toy；
- 用 **energy utility + missing ratio** 两个互补指标，而不是只刷一个吞吐；
- 用 **async/layered 消融** 证明方法的两个设计点；
- 用 **scalability** 证明不是只在某个规模有效；
- 用 **convergence/runtime** 证明可训练、可部署。

---

## 2. 映射到你的论文

你的问题不是 MEC 任务卸载，而是 **两层 UAV 的 minimum-QoS 通信韧性**。不能照搬“task/energy utility”，但可以一一映射：

| TSC 论文 | 你的论文 | 说明 |
|---|---|---|
| Task arrival trace | **GU session arrival trace** | 用 Alibaba trace 的到达强度驱动动态用户会话；比 Poisson 更真实 |
| Missing ratio | **QoS violation ratio = 1−QSR**；session outage ratio | 直接对应“没满足最低 QoS”的比例 |
| Average per-UAV energy utility | **QoS delivered per Joule**（goodput / propulsion energy）；QSR per 100 m | 你有 c/m energy、path |
| Asynchronous scheduling | **event-driven per-slot ROCS-0** vs 同步 batch scheduler（每 T 个 slot 重分配） | 你的 session 到达/离开本来就是异步；可以显式对比 |
| Layered action space | **branch-credit motion/power 分解** | 你的 2×2 就是 layered vs flat 的消融 |
| Multi-UAV cooperation | **C-UAV + 4 M-UAV + K-means/Hungarian** | 你的系统模型 |
| Scalability (UAV/ED) | **K=3/4/5/6；N=20/60/100/130；load 0.75–1.5** | 你需要补 |
| Convergence | **QSR vs EP；time-to-95%** | 你已有 |
| Baselines | **MAPPO/PPO/TD3/SAC/CDA/PI** | TD3/PPO/Joint-SAC 已在跑，MAPPO 可选 |

**关键新增（相对你之前的实验）：**
1. **trace-driven 负载**：不只 Poisson，用真实 trace 的到达强度；
2. **energy utility + missing ratio**：不只 QSR/P5/P95；
3. **async vs sync scheduling**：不只 scheduler 变体，而是“每 slot 重分配 vs 每 T slot 批量重分配”；
4. **scalability**：K、N、load 三维；
5. **2×2**：把 layered/flat 与 credit 分开。

---

## 3. 重设计后的实验矩阵（TVT 版）

### E1 主对比（Table 1）

**方法（7 个）**
1. HQC-SAC（主方法）
2. TD3
3. PPO
4. Joint-SAC (PM)
5. CDA-SAC-Adapted
6. MAPPO（可选）
7. PI-BCD-SCA（优化器）

**协议**
- 400 EP × seeds 7/17/27；fixed-500/dynamic sessions；
- 评估 9000–9029；最终 10000–10099；
- 指标：QSR、Avg-SQA、P5、P95、Jain、Goodput、**QoS violation ratio (1−QSR)**、**QoS per Joule**、C-UAV path、params、latency。

**TSC 风格补充**
- 同时报 **average per-method energy utility**（goodput / total propulsion energy）和 **missing ratio**（1−QSR）；
- 不只报“谁 QSR 高”，还报“每焦耳送多少有效 QoS”。

**现状**
- TD3/PPO/Joint-SAC 已在 `runs/TVT_20261103` 队列里训练；
- MAPPO 可选；
- PI 已有。

---

### E2 2×2 因子消融（Table 2）

| | immediate | unified |
|---|---|---|
| shared encoder | **Full（主）** | Recursive（已有） |
| flat MLP | **Flat-Relay + immediate（在跑）** | CDA（已有） |

- 3 seeds × 400 EP；评估 9000–9029；
- 指标：QSR/P5/P95/Jain/Goodput/max BH/min relay QSR；
- 目的：分离“表示”与“信用”两个因素，回答“主 vs CDA 到底是什么赢”。

**这是 TSC 论文“layered vs flat action”消融的对应物。**

---

### E3 调度器：算法级 + async/sync（Table 3）

**3.1 算法级 scheduler 消融**
- no-age（λ_s=0）× 3 seeds × 400 EP
- no-1swap（greedy）× 3 seeds × 400 EP

**3.2 async vs sync**
- ROCS-0 per-slot（异步/事件驱动）
- **batch scheduler**：每 T=5/10/20 个 slot 重新分配一次（同步批量）
- 指标：QSR/P5/P95/Jain/Goodput + 调度次数/时延
- 目的：证明“per-slot 异步”不是浪费，而是对动态到达的必要响应。

**3.3 调度器 baseline（frozen main）**
- PF、Max-CQI、Max-QoS、Equal-FDMA；
- 3 seeds × 30 scenes；
- 指标 + 单 slot 调度耗时。

**3.4 最优性 gap**
- 小规模 N=8–12、K=4；穷举/ILP 求 per-slot 最优；
- 100 slots；报 gap。

**TSC 风格补充**
- 把“asynchronous”从口号变成可测变量：per-slot vs batch T；
- 这直接对应 TSC 论文的 async vs sync 消融。

---

### E4 λ 敏感度 / Pareto（Table 4 / Fig. 6）

已完成：main、R005、LS020、S040、R020、no-age。

- Pareto：main (0.8096/10.19) → R005 (0.7966/8.33) → S040 (0.7884/6.26)；
- LS020 被 R005 支配；
- R020 被 main 支配；
- no-age 崩溃。

**TSC 风格补充**
- 加 **energy utility** 维度：QSR vs energy per episode；
- 这样 λ 不只是“均值-尾部”，还是“性能-能耗”旋钮。

---

### E5 泛化 / scalability（Table 5 / Fig. 7）

**因素**
| 因素 | 训练 | 测试 |
|---|---|---|
| 负载倍率 | 1.0 | 0.75 / 1.0 / 1.25 / 1.5 |
| 用户数 N | 20–130 | 20 / 60 / 100 / 130 |
| 速度 | 0–6 m/s | 3 / 6 / 9 |
| C-UAV 初始位置 | (250,0,150) | 中心 / 训练点 / 对边 / 角 |
| K | 4 | 3 / 4 / 5 / 6 |
| 信道 | A2G | A2G / A2A-LoS / P.1410 |

- 方法：main + 最强基线（TD3/PPO/CDA）；
- 3 seeds × 10 scenes；
- 指标：相对 nominal 的 QSR/P5/P95 退化；energy utility 退化。

**TSC 风格补充**
- 把 scalability 做成**二维热图**（K × load），而不是单条曲线；
- 这比“再跑一个 K”更有信息量。

---

### E6 Trace-driven 负载（新增，TVT 加分）

**目的**：证明不是只对 Poisson 合成负载有效。

**设计**
- 用 **Alibaba Cluster Data V2017** 的到达强度序列，重采样到 200 s episode；
- 生成 `trace_arrival_profile`（每 slot 的到达率），替换 `surge_arrival_rates_per_s`；
- main vs CDA（或最强基线），3 seeds × 10 trace segments；
- 指标：QSR、P5、P95、missing ratio、energy utility；
- 预期：trace 的突发性更强，主方法的 age-aware 调度和 load balancing 优势更大。

**实现成本**
- 需要：
  1. 下载/准备 Alibaba trace 的到达强度；
  2. 在 env 加一个 `trace_arrival_profile` 配置（或直接把 rate 序列映射到 `surge_arrival_rates_per_s` 的四阶段）；
  3. 评估脚本支持 trace。
- 约 2–4 天。

**TSC 对应**
- 这是 TSC 论文“trace-driven simulations”的直接对应，也是 TVT 审稿人很喜欢的“realism”证据。

---

### E7 效率 / 能耗 / 实时（Table 6 / Fig. 9）

- Params：main 365,451；CDA 365,245；TD3 ~372k；PPO ~363k；Joint-SAC ~368k；MAPPO ~382k。
- Latency：CPU 1.47 ms / P95 1.92；GPU 4.47/6.52（已实测）。
- Training：400 EP wall-clock；time-to-95% final。
- Energy：C-UAV path 541 vs 465 vs 609；**QoS per Joule**；QSR–path Pareto。
- 结论：实时、参数小；能量是 trade-off，不是最优。

**TSC 对应**
- “average per-UAV energy utility” → “QoS delivered per Joule”；
- 这是 TVT 很看重的 deployment 证据。

---

### E8 最终 100 + 统计（Table 1 最终）

- 7 方法 × 3 seeds × 100 scenes；
- 分层 bootstrap（scene+seed）、Holm、per-seed；
- 只跑一次，不参与调参。

---

## 4. 相对之前设计的改动

| 之前 | 现在 | 为什么 |
|---|---|---|
| 5 方法主表 | **7 方法 + energy utility/missing ratio** | TVT 要标准基线 + 互补指标 |
| 3 个消融 | **2×2 + 强启发式** | 解开表示/信用 confound；避免 straw man |
| scheduler frozen | **算法级 + async/sync + 最优性 gap** | 回应“启发式”质疑 |
| λ 只有 Pareto | **λ × energy** | 性能-能耗旋钮 |
| 泛化 3 因素 | **K/N/load/速度/初始位置/信道 + 热图** | TSC 风格 scalability |
| 无 trace | **Alibaba trace-driven** | TSC 风格 realism |
| 无 energy utility | **QoS per Joule / missing ratio** | 对齐 TSC 指标 |

---

## 5. 优先级与时间

### P0（已在跑/本周）
1. Flat-Relay ×3（2×2 缺角）——**已在 `runs/TVT_20261103` 队列**；
2. Joint-SAC ×3——**已在队列**；
3. TD3 ×3、PPO ×3——**训练器已 smoke test，队列 2 等第一队列结束后自动跑**；
4. λ Pareto —— 已完成；
5. per-relay/outage/case study —— 1–2 天画图；
6. latency —— 已完成。

### P1（2–3 周）
7. scheduler 补训 no-age/no-1swap（6 runs）；
8. async vs sync batch scheduler（T=5/10/20）；
9. 泛化 K/N/load/速度/初始位置；
10. energy utility / missing ratio 表；
11. 最优性 gap。

### P2（3–4 周）
12. Alibaba trace-driven；
13. MAPPO；
14. 信道 P.1410 / A2A-LoS；
15. 5 seeds；
16. 最终 100。

---

## 6. 一句话总结

> 你之前的实验清单是对的，但它是**旧 contract**下的；TVT 这一版要保留标准基线（TD3/PPO/Joint-SAC/MAPPO/CDA/PI），同时用 **2×2** 把“表示 vs 信用”拆开，用 **λ × energy** 把“性能-能耗”讲清楚，用 **async vs sync + trace-driven + scalability** 对齐 TSC 论文的实验范式。这样既不是重复你之前的论文，也不是“只多了几个 run”，而是**同一问题、不同 contract、不同机理、不同评价维度**的新论文。
