# IEEE TVT 投稿方案：从现有实验到可接收的 Transactions 论文

- 日期：2026-11-03
- 目标期刊：**IEEE Transactions on Vehicular Technology (TVT)**
- 现有资产：27 个 400 EP 训练 run；5 方法 common-30；调度器 frozen 消融；λ Pareto；per-relay 负载；CPU/GPU 时延。
- 结论先行：**现有数据可以支撑 TVT 的“应用型机制论文”，但按现在的基线数量和 novelty，直接投会被拒。** 需要补 3 类东西：**标准 RL 基线（TD3/PPO/Joint-SAC）、2×2 因子消融（表示 × 信用）、泛化 + 最终 100 + 调度器最优性 gap**；同时把 novelty 从“SAC + 启发式调度器”提升为“**时间尺度感知的 branch-credit 分解 + age-aware 调度器协同设计 + 可部署的 resilience knob**”。

---

## 0. TVT 的评审口味（先对齐）

TVT 是 IEEE 车辆技术领域的旗舰期刊之一，审稿人通常来自**无线通信 / 无人机网络 / 资源分配 / RL** 几个方向。它接受“学习型资源分配”论文，但有几个硬门槛：

1. **系统模型要真实**：UAV 移动、空口/回传、动态用户、QoS 约束、能耗；不能是 toy model。
2. **问题要有通信意义**：不是“换个 RL 算法刷分”，而是解决一个通信/网络问题。
3. **Baseline 要够**：至少 TD3/PPO/SAC 这类标准 RL，加上领域 baseline（CDA/优化器/启发式）。只有 1 个外部 RL 基线会被直接质疑。
4. **Ablation 要干净**：不能有“表示 + 信用”混在一起的 confound；不能把另一个分支换成故意很差的策略。
5. **泛化/鲁棒性**：负载、速度、初始位置、信道、K 至少覆盖几项。
6. **复杂度/实时性**：参数量、推理时延、训练成本；TVT 很看重“可部署”。
7. **统计可信**：多种子、置信区间、显著性；不能只报均值。
8. **写作**：14 页双栏，故事线清晰，贡献点可验证。

**TVT 的 acceptance 不是“分数高”就够，而是“问题重要 + 方法有 insight + 实验闭环”。**

---

## 1. 现有工作对 TVT 的适配度评分

| 维度 | 现状 | 评分（1–5） | 说明 |
|---|---|---:|---|
| 系统模型 | 两层 UAV、动态用户、QoS、回传、能耗 | **5** | 细节足够，TVT 会认 |
| 问题意义 | 最低 QoS 韧性、动态高负载 | **4** | 比“最大化吞吐”更有通信意义 |
| 算法 novelty | branch-credit SAC + ROCS-0 | **3** | 需要“时间尺度”论证 + 2×2 + 分析 |
| 外部基线 | 只有 CDA + PI | **2** | TVT 硬伤 |
| 消融 | 3 个，但有 confound / straw man | **3** | 需要 2×2 + 强启发式 |
| 调度器 | frozen 消融效应大 | **4** | 补训 + 最优性 gap 后 5 |
| 泛化 | 无 | **1** | 必须补 |
| 效率/实时 | CPU 1.47 ms、0.365M | **5** | 强卖点 |
| 统计 | 90 对 bootstrap | **3** | 补分层/Holm/per-seed |
| 写作 | 未开始 | — | 需要按 TVT 结构重写 |

**判断**：系统模型和效率是强项；基线和泛化是硬伤；novelty 需要“分析 + 2×2”来抬。

---

## 2. TVT 论文的 novelty 定位

不要写成“我们提出了一个 SAC 变体 + 一个调度器”。建议三条贡献，每条对应一个独立实验：

### Contribution 1：问题与机理

**“动态高负载两层 UAV 网络中，最低 QoS 韧性的瓶颈是回传负载不均衡，而不是平均速率。”**

- 现有数据：CDA max BH load 2.22×、min relay QSR 0.618；主方法 1.26×、0.741。
- 这是 TVT 喜欢的“system insight”：不是刷分，而是指出瓶颈。
- 对应实验：per-relay load / min relay QSR / max BH load（已有，补图）。

### Contribution 2：时间尺度感知的 branch-credit SAC

**“Motion 是长时程（轨迹），Power 是短时程（每 slot）；把两者放在 flat actor 里会产生信用干扰。我们提出 branch-credit 分解：Motion 用 recursive long-horizon credit，Power 用 immediate same-slot credit，并用 shared relay set encoder 处理变长 relay 集合。”**

- 需要 2×2 因子实验：shared/flat × immediate/unified。
- 需要“时间尺度”论证：可以写一个 design rationale + 小 Proposition（TD target variance / credit horizon mismatch）。
- 对应实验：Full / Recursive / Flat-Relay / CDA；Motion-only / Power-only 强启发式版。

### Contribution 3：age-aware 调度器协同设计 + 可部署 resilience knob

**“ROCS-0 用 age-weighted max-cost + best-improvement 1-swap 近似 P1 的 slot-level 服务目标；λ_s 是运行时可调的 mean-tail 旋钮。”**

- 需要：scheduler 补训（算法级）、no-age/no-1swap、PF/max-CQI 对比、**最优性 gap**（小规模 exhaustive/ILP）、复杂度分析。
- λ Pareto：main → R005 → S040；S040 是尾部点。
- 对应实验：Table 3 + Fig. 5/6 + 最优性 gap 表。

### 可选 Contribution 4：部署性

**“0.365M 参数、CPU 1.47 ms/slot、8 GB GPU 可训练；λ_s 可在运行时切换。”**

- TVT 喜欢“可部署”，这可以作为 application contribution，但不要单独吹成理论贡献。

---

## 3. TVT 必须补的实验（按优先级）

### 3.1 P0：没有这些会被拒

| # | 实验 | 具体设计 | n | 成本 | 论文位置 |
|---|---|---|---|---:|---|
| 1 | **TD3 / PPO / Joint-SAC** | 同一 fixed-500 contract；400 EP × seeds 7/17/27；参数 0.36–0.38M；同 9000–9029 评估 | 9 runs | 代码 2–3 d + 7.5 h | Table 1, Fig. 3 |
| 2 | **2×2 因子消融** | Full（shared+immediate）、Recursive（shared+unified）、**Flat-Relay+immediate（缺）**、CDA（flat+unified）；3 seeds × 400 EP | 3 new runs | 代码 0.5 d + 2.5 h | Table 2 |
| 3 | **调度器补训** | no-age（λ_s=0）、no-1swap（greedy）× 3 seeds × 400 EP | 6 runs | 5 h | Table 3 |
| 4 | **泛化** | 负载 0.75/1.0/1.25/1.5；速度 3/6/9；初始位置 4 点；信道 A2G/A2A-LoS/P.1410（若支持）；main + 最强基线；3 seeds × 10 scenes | ~240 episodes/因素 | 2–4 h | Table 5, Fig. 7 |
| 5 | **最终 100** | 10000–10099；6–7 方法 × 3 seeds | ~1800–2100 eps | 2–3 h | Table 1 最终 |
| 6 | **调度器最优性 gap** | 小规模（N=8–12, K=4）穷举/ILP 求 per-slot 最优；100 个 slot；比较 ROCS-0 | 100 slots | 代码 1–2 d + 1 h | Table 3 / 附录 |
| 7 | **统计** | 分层 bootstrap（scene+seed）、Holm、per-seed、效应量 | — | 1–2 d | 所有表 |
| 8 | **per-relay / case study** | max BH、min relay QSR、outage CDF、2 个轨迹案例 | — | 1–2 d 画图 | Fig. 8/10 |
| 9 | **效率** | params、CPU/GPU latency（已有）、path/QSR–path、训练时间 | — | 0.5 d | Table 6, Fig. 9 |

### 3.2 P1：TVT 审稿人会追问

| # | 实验 | 设计 | 成本 | 作用 |
|---|---|---|---|---:|
| 10 | **强启发式消融** | Motion-only + waterfilling；Power-only + load-weighted centroid；各 3 seeds × 400 EP | 代码 2–3 d + 5 h | 避免 straw man |
| 11 | **调度器 baseline** | PF / Max-CQI / Max-QoS / Equal-FDMA，frozen main，3 seeds × 30 | 代码 1–2 d + 40 min | 证明“吞吐最优 ≠ 韧性最优” |
| 12 | **MAPPO** | adapted CTDE，C-UAV + per-M-UAV agents；3 seeds × 400 EP | 代码 1 周 + 2.5 h | 多智能体基线（可选但加分） |
| 13 | **K 可扩展性** | K=3/4/5/6；若代码支持，main + CDA；3 seeds × 10 scenes | 代码 2–3 d + 2 h | TVT 会问 scalability |
| 14 | **5 seeds** | 主方法 + 最强 2 个基线，加 seeds 37/47 | +6 runs ≈ 5 h | 统计更强 |

---

## 4. 关键实验的具体设计

### E1 主对比（Table 1）

**方法（7 个）**：
1. HQC-SAC（主方法，0.365M）
2. TD3（0.372M）
3. PPO（0.363M）
4. Joint-SAC / SAC（0.368M）
5. CDA-SAC-Adapted（0.365M）
6. PI-BCD-SCA（优化器，非 RL）
7. MAPPO（可选，0.382M）

**协议**：
- 400 EP × seeds 7/17/27；同一 observation/action/reward/scheduler；
- 评估 9000–9029（dev/val）；最终 10000–10099；
- 指标：QSR、Avg-SQA、P5、P95、Jain、Goodput、C-UAV path、Params、Latency。

**统计**：
- 每个方法 90 个 episode（3 seeds × 30 scenes）；
- 配对 bootstrap 95% CI；Holm 校正；
- 报 per-seed。

**预期**：
- 主方法 QSR/P5/P95 仍最好；TD3/PPO 可能接近，但主方法参数更少/更稳；
- 如果 TD3/PPO 某一项更好，如实写，并分析原因（例如 TD3 的确定性策略在稳定场景更好）。

### E2 2×2 因子消融（Table 2）

| 条件 | 表示 | 信用 | 作用 |
|---|---|---|---|
| Full | shared | immediate | 主方法 |
| Recursive | shared | unified | 信用效应 |
| **Flat-Relay** | **flat** | **immediate** | **表示效应（缺）** |
| CDA | flat | unified | 两者都关 |

- 3 seeds × 400 EP；评估 9000–9029；
- 指标：QSR/P5/P95/Jain/Goodput/max BH/min relay QSR；
- 预期：Full > Recursive ≈ Flat-Relay > CDA；如果 Flat-Relay 掉得比 Recursive 多，说明表示更重要；反之信用更重要。
- 这张表能直接把“主 vs CDA”的 confound 解开，是 TVT 审稿人最想看的。

### E3 调度器（Table 3）

**3.1 算法级**
- no-age（λ_s=0）× 3 seeds × 400 EP
- no-1swap（greedy）× 3 seeds × 400 EP
- 评估 9000–9029；指标 QSR/P5/P95/Jain/Goodput。

**3.2 调度器 baseline（frozen main）**
- ROCS-0、no-age、no-1swap、PF、Max-CQI、Max-QoS、Equal-FDMA；
- 3 seeds × 30 scenes；
- 指标同上 + 单 slot 调度耗时。

**3.3 最优性 gap**
- 小规模 N=8–12、K=4；穷举/ILP 求 per-slot 最优 `max Σ z_i w_i`；
- 100 个随机 slot；比较 ROCS-0 与最优的目标值；
- 报 gap mean/P95、运行时间。
- 这直接回答“启发式调度器凭什么”。

### E4 λ 敏感度（Table 4 / Fig. 6）

- 已完成：main、R005、LS020、S040、R020、no-age；
- Pareto：main → R005 → S040；
- 结论：λ_s 是真实旋钮；S040 是尾部点；LS020 被 R005 支配，不要当尾部代表。

### E5 泛化（Table 5 / Fig. 7）

| 因素 | 训练 | 测试 | 说明 |
|---|---|---|---|
| 负载倍率 | 1.0 | 0.75/1.0/1.25/1.5 | 报实际平均用户数 |
| 速度 | 0–6 m/s | 3/6/9 | 9 是外推 |
| 初始位置 | (250,0,150) | 中心/训练点/对边/角 | 含训练点 |
| 信道 | A2G | A2G/A2A-LoS/P.1410 | 若代码支持 |
| K | 4 | 3/4/5/6 | 若代码支持；否则写限制 |

- 方法：main + 最强基线（TD3/PPO/CDA）；3 seeds × 10 scenes；
- 指标：相对 nominal 的 QSR/P5/P95 退化；
- 预期：主方法退化更慢，高负载/高速优势更大。

### E6 效率（Table 6 / Fig. 9）

- Params：main 365,451；CDA 365,245；TD3 ~372k；PPO ~363k；Joint-SAC ~368k；MAPPO ~382k。
- Latency：CPU 1.47 ms / P95 1.92；GPU 4.47/6.52（已实测）。
- Training：400 EP wall-clock；sample efficiency（main ~EP70 到 95% final）。
- Path/energy：main 541 m；CDA 465 m；Recursive 609 m；QSR–path Pareto。
- 结论：主方法实时、参数小；能量不是最优，是 trade-off。

### E7 最终 100（Table 1 最终）

- 冻结代码/配置/指标/checkpoint；
- 10000–10099；
- 7 方法 × 3 seeds × 100 = 2100 episodes；
- 2 workers 约 2–3 h；
- 只跑一次，不参与调参。

---

## 5. TVT 论文结构（14 页双栏）

| 章节 | 内容 | 页数 |
|---|---|---|
| I. Introduction | 场景、挑战、gap、贡献 | 1.5 |
| II. Related Work | UAV QoS、RL 资源分配、调度器 | 1.5 |
| III. System Model | 两层 UAV、信道、动态用户、QoS、能耗 | 2.0 |
| IV. Problem Formulation | P1、约束、指标 | 1.0 |
| V. Method | branch-credit SAC、ROCS-0、算法框 | 3.0 |
| VI. Analysis | 复杂度、调度器近似、credit rationale | 1.0 |
| VII. Experiments | E1–E7 | 3.5 |
| VIII. Conclusion | 总结、限制 | 0.5 |
| References | 40–60 篇 | 1.0 |

**必须有的图**：
- Fig. 1 场景示意图。
- Fig. 2 方法架构（shared encoder + motion/power branches + scheduler）。
- Fig. 3 收敛曲线。
- Fig. 4 消融柱状图。
- Fig. 5 调度器 P5/P95 + outage CDF。
- Fig. 6 λ Pareto。
- Fig. 7 泛化。
- Fig. 8 per-relay load。
- Fig. 9 效率/能耗。
- Fig. 10 case study。

**必须有的表**：
- Table 1 主对比。
- Table 2 2×2 消融。
- Table 3 调度器。
- Table 4 λ。
- Table 5 泛化。
- Table 6 效率。
- Table 7 最终 100（可合并到 Table 1）。

---

## 6. 8 周时间表（4060 Ti + 4090）

### Week 1：代码 + 启动训练
- TD3/PPO adapter + Joint-SAC entry + Flat-Relay preset；
- 启动 TD3/PPO/Joint-SAC 9 runs（4090 + 4060 Ti 并行）；
- 启动 scheduler 补训 6 runs；
- 跑 Flat-Relay 3 runs。

### Week 2：完成训练 + 评估
- 完成 18 runs；
- common-30 评估新方法；
- 泛化 main vs 最强基线；
- 调度器最优性 gap 代码 + 实验；
- per-relay/outage 图。

### Week 3：统计 + 图表
- 分层 bootstrap、Holm、per-seed；
- 全部表格/图；
- 最终 100（冻结后）。

### Week 4：写作
- 初稿；
- 方法/系统模型/实验；
- 补充材料。

### Week 5：内部 review + 润色
- 找同组/导师读；
- 检查 claim-evidence 对齐；
- 语言润色。

### Week 6：投稿
- TVT 格式、页数、参考文献；
- cover letter；
- 提交。

### Week 7–8：buffer
- 审稿意见准备；
- 补充实验（MAPPO/K/信道）。

---

## 7. TVT 审稿人 Q&A 预演

| 审稿人问题 | 你的回答/实验 |
|---|---|
| “Why not MAPPO/PPO?” | PPO/TD3/SAC 已加；MAPPO 作为 optional；若不做，说明 C-UAV 集中控制、M-UAV 由聚类跟踪，MAPPO 的动作接口不同 |
| “Scheduler is a heuristic; what is the optimality gap?” | E3.3 小规模穷举/ILP；报 gap 和复杂度 |
| “Only simulation?” | 高保真系统模型 + 实测 CPU 1.47 ms；承认无 testbed，写入 limitations |
| “Fixed K=4; scalability?” | K=3/4/5/6 实验或明确写“fixed fleet”限制 |
| “Energy efficiency?” | path 541 vs 465；QSR–path Pareto；不声称最节能 |
| “Why λ=0.1?” | 预注册 + λ Pareto；0.1 是均值优先，S040 是尾部点 |
| “Statistical significance?” | 分层 bootstrap + Holm + per-seed |
| “Novelty vs SAC?” | 时间尺度感知 branch credit + 2×2 + scheduler co-design + load-balancing insight |
| “Why age penalty?” | no-age P95 69 s；age 权重防 starvation |
| “Reproducibility?” | code/config/hash/seeds/hardware；补充材料 |

---

## 8. 风险与缓解

| 风险 | 概率 | 缓解 |
|---|---|---|
| 被认为“SAC + 启发式调度器，incremental” | 高 | 2×2 + 时间尺度论证 + 最优性 gap + load-balancing insight |
| 基线太少/太弱 | 高 | TD3/PPO/Joint-SAC；同 budget；dev 调参 |
| Ablation straw man | 中 | Motion-only+WF、Power-only+centroid |
| 泛化不足 | 中 | E5 四因素 |
| 只仿真 | 中 | 高保真 + 实时性 + limitations |
| 能量不优 | 中 | 诚实写 trade-off；QSR–path Pareto |
| 写作太长/太散 | 中 | 7 方法、6 表、10 图；补充材料放 K/信道/MAPPO |

---

## 9. 现在就能做的三件事（最高 ROI）

1. **Scheduler 补训**（6 runs，5 h）：把 frozen diagnostic 升级为算法级，直接回应“启发式”质疑。
2. **Joint-SAC + Flat-Relay+immediate**（6 runs，5 h + 1 d code）：补第二个标准基线和 2×2 的关键角。
3. **泛化 + 最终 100**（4 h）：TVT 的“resilience”必须有 stress test 和 sealed test。

这三件做完，论文的“机制链”和“实验闭环”就基本完整；TD3/PPO 和 MAPPO 是加分项，不是第一步。

---

## 10. 一句话总结

> TVT 要的不是“更多方法”，而是“**一个通信问题 + 一个可解释的机制 + 一组干净的对照 + 可部署的证据**”。你现在的系统模型、per-relay 机理、CPU 1.47 ms 时延是强项；补齐 **TD3/PPO/Joint-SAC、2×2、scheduler 补训+最优性 gap、泛化、最终 100**，TVT 是可以冲的。
