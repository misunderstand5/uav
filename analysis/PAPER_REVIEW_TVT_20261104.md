# HQC_SAC_V2.pdf 详细审稿分析与 TVT 修改方案

- 日期：2026-11-04
- 稿件：`C:\Users\admin\Desktop\HQC_SAC_V2.pdf`
- 标题：*History-Aware Minimum-QoS Scheduling and Deep Reinforcement Learning-Based Control for Two-Tier UAV Networks*
- 作者：Yangyang Zeng, Xiuling Zhang, Riheng Jia
- 当前格式：**IEEE Transactions on Wireless Communications (TWC)**（页眉写的是 TWC）
- 目标：**IEEE Transactions on Vehicular Technology (TVT)**

> 说明：PDF 是文字型，但提取时部分空格/连字丢失；下面的分析基于可读的正文、表 IV–VI、图 2/3/4/5/6 的图注和实验节。个别数字/行如果与你的源文件不一致，以源文件为准。

---

## 0. 一句话判断

**这篇论文有完整、可发表的核心故事：动态高负载两层 UAV、HA-QCS 调度器、branch-credit SAC；但当前版本是“TWC 风格”的算法+仿真论文，直接投 TVT 会碰到三个硬问题：**

1. **方法-代码-实验不一致**：论文的调度器是 **HA-QCS**（feasibility → guarded rescue → cost-ordered → residual filling），而当前实验包/我之前分析的是 **ROCS-0**（age-weighted max-cost + 1-swap）。两者不是同一个调度器。论文的表 IV/V 数字（QSR 82.10、P95 27.62 等）来自 HA-QCS 实现，不是包里的 ROCS-0。**这是第一优先级。**
2. **TVT 适配度**：稿件按 TWC 写（NOMA 回传、P1 机会约束、算法细节），TVT 审稿人会更关心 **系统级韧性、可部署性、可扩展性、与经典调度器的对比**。需要重写 framing，而不是只改模板。
3. **实验闭环不足**：缺 CDA 行（表 IV 只有 6 行，图 4 图例有 CDA）、Joint-SAC 两个变体没标清、缺调度器阶段消融（guard/rescue/cost/residual）、缺 K/信道/干扰扩展、缺控制器时延/参数量、缺最终 sealed test。

---

## 1. 论文在做什么（准确复述）

### 1.1 问题

- 两层 UAV 下行：1 架 C-UAV 通过 **NOMA 回传** 服务多架 M-UAV（relay），M-UAV 通过 **正交接入** 服务地面用户（GU）。
- GU 会话在 episode 内随机到达/离开/移动；每个会话有固定最小速率 `R_min ∈ {0.7, 2.0, 2.5} Mbit/s`。
- 目标 P1：最大化每时隙平均 minimum-QoS completion ratio（QSR），同时约束“每个会话最长连续欠服务时长”的 95 分位不超过 `T_out=15 s`（等价于 P95 outage ≤ 15 s，ε=0.05）。
- 决策：C-UAV 轨迹、NOMA 回传功率、M-UAV 关联、接入份额、交付速率。

### 1.2 方法

**HA-QCS（调度器，在每个 relay 上独立运行）：**
1. **Feasibility screening**：`a_req = R_min / C_A ≤ 1` 的 GU 进入 eligible set `F_k`；完成子集需满足 access share 和 backhaul rate 两个预算。
2. **Guarded rescue**：先救 `O_i ≥ T_guard=10 s` 的 overdue GU，每个 relay 每 slot 最多 1 个；按 `O_i` 最长、`S_i` 最低、`ℓ_i` 最低排序。
3. **Cost-ordered completion**：其余 eligible GU 按 `ℓ_i = R_min/C_A + R_min/R_B` 升序完成。
4. **Residual filling**：剩余资源按 `w_i ∝ 1 + O_i/5 + (1-S_i)/10` 做 history-weighted PF。

**HQC-SAC（控制器）：**
- 状态：14 维全局 + K 个 14 维 relay token（K_max=6），共 98 维。
- 动作：motion `a_M`（3 维：速度/极角/方位角）+ power `a_P`（K 维 softmax 分数）。
- 网络：shared relay encoder + masked pooling；motion actor/critic（recursive soft Bellman）、power actor（same-slot utility，无 target critic）。
- 训练：motion replay + power replay；3 seeds；width 128；400 episodes。

### 1.3 实验

- **Table IV（C-UAV controller）**：HQC-SAC 82.10 QSR / 8.61 P5 / 10.39 P95 / 203.19 energy；TD3 77.53 / 6.27 / 11.85 / 203.02；PPO 74.67 / 4.87 / 11.19 / 202.79；Rule-DCM 74.85 / 4.57 / 10.52 / 200.89；Joint-SAC 67.31 / 4.30 / 16.21 / 203.09；Joint-SAC 68.67 / 4.35 / 18.02 / 203.81。
- **Table V（N=120 scheduler）**：HA-QCS 45.38 / 4.12 / 27.62；Completion-first 48.17 / 0 / 200；PF 30.48 / 5.38 / 79.29；M-LWDF-A 20.64 / 7.53 / 56.10；Equal-WC 6.53 / 0 / 200；Equal-share 4.52 / 0 / 200。
- **Table VI（ablation）**：HQC-SAC 82.10 / 8.61；Recursive power 77.68 / 5.92；Flat-relay 77.48 / 6.05；Fixed power 73.28 / 4.51；No Jain 81.75 / 7.34；Motion n=5 81.24 / 7.98；Motion n=20 79.37 / 6.57。
- **动态负载/资源变化**：四阶段到达 + 固定 N∈{20,40,…,120} 扫描；50 个评估场景；95% t 区间。

---

## 2. 对 TVT 的适配度评估

| 维度 | 现状 | TVT 评分（1–5） | 说明 |
|---|---|---:|---|
| 系统模型 | 两层 UAV、NOMA 回传、正交接入、动态 GU | **5** | TVT 会认这个系统 |
| 问题意义 | 最小 QoS + 连续欠服务尾部 | **4** | 比“最大化吞吐”更有意义 |
| 方法 novelty | HA-QCS + branch-credit SAC + set encoder | **3–4** | 需要“为什么不是普通 SAC/调度器”的更强论证 |
| 与 TVT 的相关性 | 应急通信/服务恢复，但没写“vehicular” | **3** | 需要明确车载/应急场景，否则像 TWC 稿件 |
| 实验闭环 | controller/scheduler/ablation/load | **3** | 缺阶段消融、K/信道、时延、sealed test |
| 可部署性 | scheduler 2.5 ms/slot；无 controller latency | **3** | 补参数量/推理时延/训练成本 |
| 统计 | 3 seeds、50 scenarios、95% t | **4** | 补多重比较/配对检验 |
| 写作 | TWC 风格、密集 | **3** | TVT 需要更清晰的故事线 |

**结论**：**TVT 可投，但必须从“TWC 算法论文”改成“TVT 系统/应用论文”**。TVT 不要求 NOMA 理论深度，但要求：
- 问题来自车辆/应急通信场景；
- 方法有系统级 insight；
- 实验覆盖可扩展性、可部署性、与经典调度器对比；
- 写作更关注“为什么这样设计”，而不是堆公式。

---

## 3. 关键问题清单（按严重程度）

### P0：不修会直接影响可信度/拒稿

#### 3.1 论文的 HA-QCS 与实验包的 ROCS-0 不是同一个调度器

- 论文：feasibility screening → guarded rescue → cost-ordered completion → residual filling；`T_guard=10 s`、每 relay 每 slot 最多 1 个 rescue。
- 我之前的实验包/分析：`age_weighted_maxcost_1swap`（age weight `w_i=1+λ_s(O_i+Δt)` + max-cost + 1-swap）。
- 两者的排序、约束、超参、输出都不同。**论文的 Table IV/V 数字来自 HA-QCS，不能拿包里的 ROCS-0 结果去支撑。**
- 影响：如果代码/实验/图/正文不一致，审稿人一旦复现就会发现。
- 修法：
  1. **确认论文的 HA-QCS 实现是唯一事实来源**；把包里的 ROCS-0 实验标记为旧版/不作为论文结果。
  2. 如果要用新实验（2×2、scheduler retrain），必须 **按 HA-QCS 重新实现/重跑**，或把论文改成 ROCS-0 并重写方法节。
  3. Fig. 2 必须画 HA-QCS，不能画 ROCS-0。

#### 3.2 Table IV 缺 CDA-SAC 行

- 图 4 图例有 `CDA-SAC`，Table IV 只有 6 行：HQC-SAC、TD3、PPO、Rule-DCM、Joint-SAC、Joint-SAC。没有 CDA。
- 如果 CDA 被合并进两个 Joint-SAC 之一，必须改名；如果是漏行，必须补。
- 影响：审稿人会问“你说对比了 CDA，表里没有”。

#### 3.3 Joint-SAC 两个变体没有标清

- Table IV 两行都叫 `Joint-SAC`；正文说“Joint-SAC is parameter-matched … and Joint-SAC has about 2.5 times as many parameters.” 这句话自相矛盾。
- 应该是 `Joint-SAC (PM)` 和 `Joint-SAC (large, 2.5×)`；表里必须标清参数量。
- 影响：基线公平性会被质疑。

#### 3.4 P1 是机会约束，HA-QCS 没有可行性保证

- P1 约束 `Pr(Õ_i > T_out) ≤ ε`；HA-QCS 是启发式，论文也承认“does not guarantee a bounded outage”。
- 但 P1 的写法让人以为方法满足约束；Table V 在 N=120 时 P95=27.62 s > 15 s，**P1 约束被违反**。
- 修法：
  - 明确写“HA-QCS is a heuristic; P1 is not guaranteed; we evaluate the empirical tail”。
  - 或把 P1 改成“soft constraint / design target”，不要用 `Pr ≤ ε` 的硬约束表述。
  - 在 Table V 标注“constraint violated at N=120”并解释。

#### 3.5 缺少调度器阶段消融

- 现在只有 HA-QCS vs Completion-first/PF/M-LWDF-A/Equal-WC/Equal-share；没有：
  - guard on/off（`T_guard=10` vs 0/∞）；
  - rescue quota 0/1/2；
  - cost order vs random order；
  - residual PF vs equal residual。
- 这会让人怀疑“提升到底来自 guard、cost order 还是 residual filling”。
- 修法：加 4 个单因素消融，Table V 旁边加小表或 Fig. 5 子图。

### P1：TVT 审稿人会追问

#### 3.6 缺少 K 可扩展性

- 系统写 K_max=6，但实验 nominal K=4；没有 K=3/4/5/6 扫描。
- TVT 会问“多 relay 时还成立吗？”
- 修法：K=3/4/5/6，main + 最强 baseline，3 seeds × 10 scenarios；报 QSR/P95/时延。

#### 3.7 缺少信道/干扰鲁棒性

- Table III 只有一组 path loss/LoS/NLoS/噪声/干扰参数；没有变化。
- 修法：至少 2 组：路径损耗指数 ±、干扰强度 0/0.25/0.5、NOMA SIC 不完美（残余干扰）。
- 如果时间有限，做“干扰强度 0/0.25/0.5”一组即可。

#### 3.8 缺少控制器复杂度/时延

- 论文只给 scheduler 2.5 ms/slot；没有 controller 参数量、推理时延、训练时间。
- TVT 很看重可部署性。
- 修法：加 Table：params、CPU/GPU latency、training time、scheduler time；主方法 CPU 1–5 ms、GPU <5 ms 是强卖点。

#### 3.9 缺少最终 sealed test

- 50 个评估场景同时用于 controller/scheduler/ablation；没有独立 test。
- 修法：训练/验证/测试分开；最后用 100 个 sealed scenarios 复测主表。
- 如果时间不够，至少用 50 个新场景复测 HQC-SAC vs TD3。

#### 3.10 缺少优化 baseline / 最优性 gap

- HA-QCS 是 2D knapsack 贪心；没有近似比或 gap。
- 修法：小规模 N=8–12、K=4 穷举/ILP 求 per-slot 最优，报 gap；或加 “HA-QCS vs exhaustive on small instances”。

#### 3.11 统计多重比较/配对检验不够明确

- 现在 95% t 区间；没有说明是否配对、是否 Holm。
- 修法：paired by scenario；报 paired difference CI；对 6 个 controller × 4 metrics 做 Holm 或明确 primary/secondary。

#### 3.12 缺少 case study / 机理解释

- 论文有 per-relay? 没有明显 per-relay load 图；TVT 喜欢“为什么有效”的机理解释。
- 修法：加 2 个 case：一个 HA-QCS 救回 overdue GU，一个 completion-first 造成长 outage；画 timeline/trajectory。

### P2：写作/图表/引用

#### 3.13 当前 Fig. 2 是 5 panel 流程图，信息密度过高

- 图注：association preprocessing、learned control、two-hop capacity、HA-QCS、service feedback。
- 问题：5 个 panel + 大量公式/箭头，7.16 in 下字会很小；审稿人看不清。
- 修法：改成 3 panel（环境 / controller / HA-QCS），把 5 个功能映射进去；feedback 用箭头。
- **不要画 ROCS-0 的 λ_s/1-swap；画 HA-QCS 的 guard/cost/residual。**

#### 3.14 图 1/3/4/5/6 的风格不统一

- 需要统一字体、线宽、配色、箭头；Fig. 4 的 “upper-left better” 坐标图是好的，但图例/标注要统一。
- 所有图输出 PDF 矢量；字体 Arial 7–9 pt；色盲安全。

#### 3.15 标题/摘要太 TWC

- 标题 “History-Aware Minimum-QoS Scheduling and Deep Reinforcement Learning-Based Control for Two-Tier UAV Networks” 没有“vehicular/emergency”。
- TVT 版建议：
  - “Resilient Minimum-QoS Scheduling and Branch-Credit Learning for Emergency Two-Tier UAV Networks”
  - 或 “Age-/History-Aware Minimum-QoS Resilience for UAV-Assisted Vehicular Communications”
- 摘要要突出：动态高负载、连续欠服务尾部、HA-QCS、branch credit、可部署时延。

#### 3.16 贡献点太长

- 三个贡献各 5–8 行；TVT 建议每个 2–3 行，加一个“设计 insight”句。
- 贡献要对应实验：模型/P1、HA-QCS、branch-credit controller；每条后面给一个数字。

#### 3.17 限制/讨论不足

- 需要明确：HA-QCS heuristic、无 P1 保证、固定 K=4、仿真、无 testbed、NOMA SIC 理想化。
- TVT 审稿人喜欢“limitations”段；不要藏。

#### 3.18 参考文献/最新 TVT 工作

- 需要补 2024–2026 TVT/TWC 的 UAV QoS/DRL 工作；Table I 的对比要准确。
- 检查 “Zhao et al. [1]” 等引用是否最新、是否支撑“two-tier NOMA backhaul”。

---

## 4. TVT 版的重构建议

### 4.1 故事线（建议）

1. **场景**：灾害/应急/车载临时覆盖，两层 UAV，动态高负载，最小速率保障。
2. **瓶颈**：不是平均吞吐，而是“谁被反复落下”——连续欠服务尾部。
3. **方法**：
   - HA-QCS：guard rescue + cost-ordered + residual PF，把“尾部”变成可调的 guard 阈值；
   - branch-credit SAC：motion 长时程、power 短时程；shared relay set encoder。
4. **证据**：
   - 主表：QSR/P5/P95/energy；
   - 调度器：HA-QCS vs Completion-first/PF/M-LWDF-A/Equal；
   - 消融：credit/representation/power/fairness；
   - 扩展：K、干扰、时延；
   - 部署：params/latency。
5. **洞察**：guard 阈值是“完成率-尾部”旋钮；branch credit 比 joint SAC 更省参数/更稳；relay set encoder 对变 K 关键。

### 4.2 章节调整（TVT 14 页）

| 章节 | 现状 | TVT 版建议 |
|---|---|---|
| I Intro | TWC 风格，贡献长 | 加应急/车载场景；贡献 3 条，每条 2–3 行 |
| II Related | 4 条线，Table I | 保留；补 TVT 近期工作；把“vehicular”点出来 |
| III System | 详细 NOMA/接入 | 保留核心；把 NOMA 细节压缩到 1 页内；加“为什么两层” |
| IV Method | HA-QCS + MDP + branch credit | 拆成 IV-A HA-QCS、IV-B controller、IV-C complexity；加算法框 |
| V Experiments | controller/scheduler/ablation/load | 加 K/干扰/时延；加 scheduler 阶段消融；加 case study |
| VI Discussion | 有 insights/limitations | 强化“设计 insight + 限制” |
| VII Conclusion | 有 | 精简 |

### 4.3 必须补的实验（按优先级）

| 优先级 | 实验 | 设计 | 目的 |
|---|---|---|---|
| P0 | 调度器阶段消融 | HA-QCS / no-guard / rescue=0/2 / random-cost / equal-residual；3 seeds × 20 scenarios | 证明每个 stage 的贡献 |
| P0 | K 可扩展性 | K=3/4/5/6；HQC-SAC + TD3；3 seeds × 10 scenarios | TVT scalability |
| P0 | 控制器时延/参数 | params、CPU/GPU latency、training time | 可部署性 |
| P1 | 干扰鲁棒性 | interference 0/0.25/0.5；HQC-SAC + TD3 | 鲁棒性 |
| P1 | 最优性 gap | N=8–12 穷举/ILP；100 slots | 回应“贪心”质疑 |
| P1 | sealed test | 50 新场景；HQC-SAC vs TD3/PPO | 防过拟合 |
| P2 | trace-driven load | 真实到达 trace vs 四阶段 | realism |
| P2 | case study | overdue rescue / long outage | 机理解释 |

### 4.4 必须修的表格/图

- **Table IV**：补 CDA-SAC；Joint-SAC 标 PM/large + params；加 controller latency/params 列。
- **Table V**：加 HA-QCS 阶段消融；标注 N=120 时 P95=27.62 > 15 s（P1 违反）。
- **Table VI**：加 “no guard / rescue=0” 消融；加 per-variant 参数量。
- **Fig. 2**：重画 3 panel（见第 5 节）。
- **Fig. 4**：统一图例/颜色；标出 upper-left better；加 CDA。
- **Fig. 5**：加 scheduler 阶段消融子图；标 censored 200 s。
- **Fig. 6**：统一 ablation 颜色；加 95% CI。

---

## 5. Fig. 2 重画方案（按论文真实方法）

### 5.1 三栏映射

```
┌──────────────────────┬─────────────────────────────────────────────┐
│ A. Environment       │ B. Branch-Credit Controller                 │
│  A1 Network model    │  B1 Relay-set encoder + masked pooling      │
│  A2 Dynamic sessions │  B2 Motion branch (recursive)               │
│  A3 Association      │  B3 Power branch (same-slot utility)        │
│                      ├─────────────────────────────────────────────┤
│                      │ C. HA-QCS Scheduler                         │
│                      │  C1 Eligibility + guarded rescue            │
│                      │  C2 Cost-ordered completion                 │
│                      │  C3 Residual history-weighted PF            │
└──────────────────────┴─────────────────────────────────────────────┘
```

### 5.2 每栏内容

**A. Environment**
- A1：C-UAV（NOMA 回传 20 MHz/5 W）→ 4 M-UAV（正交接入 5 MHz/1 W）→ GU 簇；500×500 m，K=4。
- A2：四阶段到达曲线；20→130 GU；`R_min=0.7/2.0/2.5`。
- A3：rate-weighted clustering + Hungarian → `x_{i,k}`, `U_k`；M-UAV 跟踪。

**B. Controller**
- B1：14+K tokens → shared relay encoder → masked pooling → 全局+relay embedding。
- B2：motion actor `π_M` + twin critics `Q_M`；recursive soft Bellman；motion replay `D_M`。
- B3：power actor `π_P`；same-slot utility `u_P`；no target critic；power replay `D_P`。
- B4：projection/mapping；`a_M=(v,θ,φ)`, `a_P` softmax → `p^B_k`。

**C. HA-QCS**
- C1：eligibility `F_k={C_A≥R_min}`；guarded rescue `O_i≥T_guard`，≤1/relay。
- C2：cost `ℓ_i=R_min/C_A+R_min/R_B` 升序完成。
- C3：residual filling `w_i∝1+O_i/5+(1-S_i)/10`。
- 约束：`Σa_req≤1`、`ΣR_min≤R_B`。

**Feedback**
- `s_n` A→B；`a_M,a_P` B→A；`C_A,R_B` A→C；`D_i` C→A；`S_i,O_i` A→B（next slot）；`r_n` A→B（training）。

### 5.3 设计规范

- 画布 **7.16×4.55 in**；Arial；panel 8.5 pt、box 7.5 pt、body 7 pt。
- 配色：环境 teal `#00796B`、controller blue `#0072B2`、scheduler vermillion `#D55E00`；浅底 `#F2F8F6/#F2F7FC/#FDF3E7`。
- 箭头：实线主流程、虚线反馈；正交路由；不交叉。
- 图标：线框 UAV/用户；不要 3D/阴影。
- 输出 PDF 矢量 + 600 dpi PNG；字体嵌入。

---

## 6. 建议的下一步（按顺序）

1. **先确认 HA-QCS 是论文唯一版本**：把论文的 HA-QCS 代码/实验与包里的 ROCS-0 分开；不要混用数字。
2. **修 Table IV/V/VI 的硬伤**：CDA、Joint-SAC 标签、P1 违反标注。
3. **补 P0 实验**：scheduler 阶段消融、K、时延。
4. **重画 Fig. 2**：按 HA-QCS 三栏；用 HTML/CSS + Chrome 出 PDF。
5. **重写 Intro/Abstract**：TVT 版（应急/车载、设计 insight）。
6. **补 P1 实验**：干扰、最优性 gap、sealed test。
7. **统一所有图**：字体/颜色/线宽/图例。
8. **最后通读**：contributions ↔ experiments ↔ figures 一一对应。

---

## 7. 一句话总结

> 这篇论文的“科学故事”是成立的：**HA-QCS 用 guard 阈值控制尾部，branch-credit SAC 用不同时间尺度分配信用**。但当前版本有三个致命的不一致：**HA-QCS vs ROCS-0、Table IV 缺 CDA/Joint-SAC 标签、P1 约束在 N=120 被违反**。TVT 版要先修这三处，再把“可扩展性/可部署性/与经典调度器对比”补齐，最后重画 Fig. 2。图不是装饰，它必须让审稿人 10 秒内看到“环境 → branch-credit → HA-QCS → feedback”的闭环。
