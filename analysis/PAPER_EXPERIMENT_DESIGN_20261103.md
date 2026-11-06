# 论文实验设计与补充实验方案

- 日期：2026-11-03
- 配套报告：`analysis/PROJECT_SUMMARY_AND_DECISION_20261103.md`
- 目标：把现有 27 个训练 run + common-30 评估，转化为一篇可投稿论文的完整实验设计；明确“现在能证明什么、还缺什么、补什么、怎么补”。

---

## 0. 结论摘要

### 0.1 现有实验能支撑什么

**已经很强、可以直接写进论文的：**

1. **主方法 vs CDA 的全面优势**（common-30，90 对）：
   - QSR 0.8096 vs 0.7390（+7.06 pt，胜率 98.9%）
   - P5 0.2369 vs 0.1304（主方法约为 1.82 倍）
   - P95 10.19 s vs 18.05 s（−43.5%）
   - Avg-SQA、Jain、Goodput 也全部显著更好
   - 参数量 365,451 vs 365,245（差 0.0564%），不是“模型更大”赢的
2. **机制消融严格单调**：
   - Full 0.8096 > Recursive 0.7523 > Motion-only 0.7126 > Power-only 0.5142
   - P5 / P95 同样单调
3. **调度器消融效应巨大**（frozen-policy）：
   - no-age：P95 69.15 s vs 10.19 s（6.8 倍），P5 0.035 vs 0.237
   - no-1-swap：QSR/Goodput 不变，P5 −8.83 pt，P95 +3.68 s
4. **种子级支配**：
   - 主方法最差种子 QSR 0.7954 > 所有基线最好种子（CDA 0.7555 / Recursive 0.7625 / Motion 0.7172 / Power 0.5143）
   - P5、P95 同样成立
5. **机理证据**（本次新算）：
   - 主方法 max backhaul load 1.257 vs CDA 2.222（−43%）
   - 4 relay 的 goodput Jain 0.965 vs 0.922
   - 最差 relay 的 QSR 0.741 vs 0.618
   - 说明主方法不是“某个 relay 特别强”，而是**把回传负载压平了**
6. **实时性**：
   - PI-BCD-SCA：均值 21 ms、P95 30 ms、成功率 1.0，满足 0.5 s 时隙
   - 主方法 400 EP 收敛，150 EP 平台化
7. **λ Pareto（common-30 已补）**：
   - main (0.10/0.10) 0.8096 / 10.19 → R005 (0.05/0.20) 0.7966 / 8.33 → S040 (0.10/0.40) 0.7884 / 6.26
   - LS020 (0.10/0.20) 被 R005 全面支配，不是 Pareto 点
   - 这说明 λ_s 是真实的 mean-tail 旋钮，且 S040 是尾部优先点

### 0.2 现有实验不能支撑什么

**审稿人会直接攻击的：**

1. **外部 RL 基线只有 CDA 一个**。CDA 还是 adapted，不是 verbatim。对期刊来说，TD3/PPO/Joint-SAC 至少要有，MAPPO 更好。
2. **Power-only 是 fixed circle、Motion-only 是 equal power**，容易被说成“straw man ablation”。需要“强启发式”版本：
   - Power-only 用 **load-weighted centroid / cluster-centroid** 的 C-UAV 运动，而不是固定圆；
   - Motion-only 用 **backhaul-aware waterfilling / max-min power**，而不是简单均分。
3. **调度器消融是 frozen-policy**，不是算法级。要补训 no-age / no-1-swap，否则只能写成“部署时诊断”。
4. **没有泛化**：负载、速度、初始位置、信道、K。论文若叫“resilience”，必须有 stress test。
5. **没有效率表**：参数量、推理时延、训练时间、能耗/航程。主方法 C-UAV path 541 m vs CDA 465 m，**主方法更耗能**，不能声称“全面更优”。
6. **λ 敏感度已补 common-30，但网格是“十字”不是 OFAT**：λ_r 只在 λ_s=0.2 上测了 0.05/0.1/0.2，λ_s 只在 λ_r=0.1 上测了 0.1/0.2/0.4；论文要如实写“two-factor screen”，不能写 one-factor-at-a-time。
7. **没有最终 100 测试**，也没有统计校正、per-seed CI、效应量。
8. **没有定性 case study**：轨迹、回传负载、outage 时间线。

### 0.3 一句话判断

> **核心结果足够强，但实验设计还没跟上 claim。** 现在这组数据可以支撑一篇“聚焦机制”的会议/应用期刊论文；要投较强的期刊，必须补 **外部 RL 基线 + 强消融 + 算法级 scheduler + 泛化 + 效率 + 最终 100**。λ 不是瓶颈。

---

## 1. 现有实验的整体分析

### 1.1 证据金字塔

| 论文 claim | 现有证据 | 强度 | 缺什么 |
|---|---|---|---|
| C1 主方法优于 flat CDA | common-30，90 对，6 指标全胜 | **强** | 只有 1 个外部基线 |
| C2 branch credit 必要 | Recursive-Credit 掉 5.73 pt QSR、8.48 pt P5 | **强** | 需要 credit horizon 消融（n-step） |
| C3 Motion 分支必要 | Motion-only 掉 9.70 pt QSR | **中强** | equal power 是弱启发式，需 waterfilling 版 |
| C4 Power 分支必要 | Power-only 掉 29.54 pt QSR | **中** | fixed circle 太弱，需 centroid/load-aware 版 |
| C5 ROCS-0 age 权重必要 | no-age P95 69.15 s | **强（部署）** | 算法级需补训 |
| C6 1-swap 必要 | no-1-swap P5 −8.83 pt、P95 +3.68 s，吞吐不变 | **强（部署）** | 算法级需补训 |
| C7 λ_s 是 mean-tail 旋钮 | common-30：main/R005/S040 三点 Pareto，S040 P95 6.26 | **强** | 网格是十字，需如实描述 |
| C8 泛化/韧性 | 无 | **弱** | 负载/速度/初始位置/信道 |
| C9 实时/高效 | PI runtime；主方法参数 0.365M | **中** | 主方法推理时延、能耗/航程 |
| C10 统计可信 | 90 对 bootstrap | **中** | 分层 bootstrap、Holm、per-seed CI |

### 1.2 审稿人视角的 8 个问题

1. “Only one RL baseline? Why not TD3/PPO/SAC/MAPPO?”
2. “Power-only with fixed circle is a straw man; a simple centroid heuristic would do much better.”
3. “The scheduler ablation is evaluated with a policy trained for the nominal scheduler; retrain it.”
4. “No generalization to load/mobility/initial position; the title says resilience.”
5. “The proposed method flies 16% farther than CDA; what about energy efficiency?”
6. “λ_s was selected on the same 30 scenes used for testing; is it post-hoc?”
7. “Only 3 training seeds; show per-seed results and confidence intervals.”
8. “CDA is adapted, not the original; how fair is the comparison?”

### 1.3 现有数据的“意外收获”（应该写进论文）

**A. 回传负载压平是主方法的核心机理，不只是“分数更高”。**

| 方法 | max BH load | mean BH load | relay Jain | min relay QSR |
|---|---:|---:|---:|---:|
| **Main** | **1.257** | **0.972** | **0.965** | **0.741** |
| CDA | 2.222 | 1.377 | 0.922 | 0.618 |
| Recursive | 1.910 | 1.248 | 0.941 | 0.645 |
| Motion-only | 2.498 | 1.472 | 0.894 | 0.566 |
| Power-only | 7.691 | 4.304 | 0.902 | 0.425 |

这张表比“QSR 高 7 个点”更有说服力：主方法把最坏 relay 的回传从 2.22× 压到 1.26×，把最差 relay 的 QSR 从 0.618 提到 0.741。论文应该用“**max-load / min-relay-QSR**”讲机制，而不是只讲平均 QSR。

**B. 1-swap 不是吞吐优化，是公平/尾部机制。**

no-1-swap 的 QSR 只掉 0.18 pt、Goodput 完全不变，但 P5 掉 8.83 pt、Jain 掉 3.15 pt、P95 涨 3.68 s。这个“零吞吐代价换公平”的结果非常适合写成 scheduler 的设计动机。

**C. 能量 trade-off 必须诚实写。**

| 方法 | C-UAV path (m) | 平均速度 (m/s) |
|---|---:|---:|
| Main | 541.1 | 2.71 |
| CDA | 465.3 | 2.33 |
| Recursive | 609.2 | 3.05 |
| Motion-only | 524.4 | 2.62 |
| Power-only | 875.1 | 4.38 |

主方法比 CDA 多飞 16%，但比 Recursive 少飞 11%、比 Power-only 少飞 38%。正确写法：
- 主方法在“性能–能耗”Pareto 上优于 Recursive/Motion/Power；
- 相对 CDA 是“用 16% 航程换 7 pt QSR / 10.6 pt P5 / −7.9 s P95”的 trade-off；
- 不要写“主方法最节能”。

**D. 种子级支配。**

主方法最差种子 > 所有基线最好种子。这是很强的描述性证据，但要注明 n=3 seeds，不是显著性检验。

---

## 2. 论文叙事：五步故事线

不要把论文写成“我们堆了一个 SAC + 一个调度器，然后比了 7 个方法”。建议用“诊断 → 分解 → 调度 → 调参 → 压力测试”的因果链：

### Step 1 诊断：瓶颈是回传负载不均衡，不是平均速率

- 用 CDA 的 max BH 2.22×、min relay QSR 0.618 说明：峰值负载下，某个 relay 被压垮，拉低整体最低 QoS。
- 用主方法的 1.26× / 0.741 说明：把负载压平，才能提升 minimum-QoS 韧性。
- 对应图：per-relay load box/CDF；对应表：per-relay balance。

### Step 2 分解：branch credit 解决 motion/power 的信用干扰

- Motion 是长时程（轨迹），Power 是短时程（每 slot），放在一个 flat actor 里会互相干扰。
- 主方法：Motion 用 recursive long-horizon credit，Power 用 immediate same-slot branch credit。
- 证据：Recursive-Credit（把 Power 也改成 recursive）掉 5.73 pt QSR、max BH 从 1.26 升到 1.91。
- 对应表：机制消融。

### Step 3 调度：ROCS-0 的 age 权重防尾部崩溃，1-swap 买公平

- no-age：P95 69.15 s、P5 0.035，说明“不按年龄优先”会让老会话饿死。
- no-1-swap：吞吐不变但 P5/Jain/P95 变差，说明 1-swap 是“公平/尾部”机制。
- 对应表：scheduler ablation；对应图：outage CDF / P5-P95。

### Step 4 调参：λ_s 是可部署的 resilience knob

- 0.1：均值/P5/公平性最优（主方法）；
- 0.2/0.4：用 1–3 pt 均值换 15–40% P95 尾部；
- 不是“越大越好”，而是“按任务选点”。
- 对应图：λ_s–QSR–P95 Pareto；对应表：λ sensitivity。

### Step 5 压力测试：负载/速度/初始位置/信道下退化更慢

- 主方法 + 最强基线（CDA 或 TD3/PPO）在 4 组条件下的 QSR/P5/P95 退化曲线。
- 对应图：generalization；对应表：stress test。

**这条故事线的优点**：每个 claim 都有独立的实验，不依赖“总分更高”；审稿人即使质疑某个基线，也不会推翻整篇论文。

---

## 3. 实验到论文的映射

| 论文元素 | 内容 | 现有实验 | 状态 | 需要补 |
|---|---|---|---|---|
| Fig. 1 | 场景 + 两层 UAV + 动态用户 | 无图 | 缺 | 画示意图 |
| Fig. 2 | 方法架构（双分支 + scheduler） | 代码 | 缺 | 画架构图 |
| Table 1 | 主对比（7 方法 × 6 指标） | 5 方法 | 中 | TD3/PPO/Joint-SAC |
| Fig. 3 | 收敛曲线（QSR vs EP） | 5 方法 400 EP | 中 | 加新基线 |
| Table 2 | 机制消融 | 3 消融 | 中强 | 强启发式版本 |
| Fig. 4 | 消融柱状图 | 有数据 | 可画 | — |
| Table 3 | 调度器消融 | frozen 2 变体 | 中 | 补训版 + PF/max-CQI |
| Fig. 5 | P5/P95 vs scheduler | 有数据 | 可画 | — |
| Table 4 | λ 敏感度 | 训练曲线 | 中 | common-30 评估 |
| Fig. 6 | λ_s Pareto | **已完成 common-30** | **强** | 画图即可 |
| Table 5 | 泛化 | 无 | 弱 | 4 组 stress test |
| Fig. 7 | 泛化曲线/热图 | 无 | 弱 | 同上 |
| Table 6 | 效率（params/latency/path） | 部分 | 中 | 推理时延 + 能耗 |
| Fig. 8 | per-relay load | 本次已算 | **强** | 画图 |
| Fig. 9 | case study 轨迹/outage | 无 | 弱 | 2 个场景 |
| Table 7 | 最终 100 | 无 | 缺 | 冻结后跑 |

---

## 4. 补充实验设计

### E1 外部 RL 基线（最高优先级）

**目的**：把“只赢 CDA”变成“赢一组标准 RL 基线”。

**方法**：
- TD3（twin critic + deterministic actor + target smoothing）
- PPO（on-policy，GAE，clip）
- Joint-SAC (PM)（flat joint actor/critic，参数匹配 ~0.368M）
- CDA-SAC-Adapted（已有）
- PI-BCD-SCA（已有，非 RL）
- 可选：MAPPO（adapted，C-UAV + per-M-UAV agents）

**协议**：
- 同一 fixed-500/dynamic-user contract；
- 400 EP × seeds 7/17/27；
- 同一 observation/action/reward/scheduler；
- 同一 9000–9029 评估，同一 10000–10099 最终测试；
- 参数量控制在 0.36–0.38M。

**实现现状**：
- `uavqos/agents/continuous_baselines.py` 已有 `TD3Agent`、`PPOAgent`；
- `uavqos/runner.py::build_agent` 只支持 `sac` / `branch_credit_sac`，需要加 TD3/PPO adapter；
- 旧工程 `uav_qos_paper/paper/trainers.py` 已有 `train_td3` / `train_ppo` / `train_mappo`，可移植；
- Joint-SAC 可以直接用 `SACAgent`，只需在 `run_matrix_train.py` 里加一个 method entry。

**成本**：
- 代码：TD3/PPO adapter + smoke，约 1–2 天；Joint-SAC entry 约 0.5 天。
- 训练：3 方法 × 3 seeds = 9 runs；4060 Ti 3 workers ≈ 7.5 h。
- 评估：9 runs × 30 scenes ≈ 15 min（与主方法一起跑）。

**预期/判定**：
- 主方法 QSR/P5/P95 仍优于 TD3/PPO/Joint-SAC；如果 TD3/PPO 很近，论文仍有“更稳定/更省参”的卖点；
- 如果主方法输给某个基线，必须分析原因，不能藏。

**论文位置**：Table 1、Fig. 3、最终 100。

---

### E2 更强的机制消融（避免 straw man，并补 2×2 因子设计）

**目的**：证明“学 Motion / 学 Power / branch credit / shared encoder”本身有贡献，而不是“把另一个分支换成故意很差的策略”。

**现有**：
- Motion-only = learned motion + **equal power**
- Power-only = learned power + **fixed circle motion**
- CDA = flat encoder + **unified n-step**；Recursive = shared encoder + **unified n-step**；Full = shared encoder + **immediate**

**关键问题：CDA 同时改了“表示”和“信用”，不能单独归因。** 现有三组正好缺一个 2×2 的角：

| | immediate power credit | unified n-step |
|---|---|---|
| **shared relay encoder** | **Full（主方法）** | Recursive-Credit（已有） |
| **flat MLP** | **Flat-Relay + immediate（缺）** | CDA（已有） |

补上 **Flat-Relay + immediate**（只把 shared encoder 换成参数匹配的 flat MLP，保留 immediate credit），就能干净地做 2×2：
- 表示效应：Full vs Flat-Relay；
- 信用效应：Full vs Recursive；
- 交互：CDA 是两者都关掉。

**建议新增消融**：

| 消融 | 表示 | 信用 | Motion | Power | 作用 |
|---|---|---|---|---|---|
| Full | shared | immediate | learned | learned | 主方法 |
| Recursive-Credit | shared | unified | learned | learned | 信用消融（已有） |
| **Flat-Relay + immediate** | **flat** | **immediate** | learned | learned | **表示消融（缺）** |
| CDA | flat | unified | learned | learned | 两者都关（已有） |
| Motion-only + equal | shared | immediate | learned | equal | 现有 |
| **Motion-only + WF** | shared | immediate | learned | **waterfilling / max-min** | 强 Power 启发式 |
| Power-only + fixed circle | shared | immediate | fixed circle | learned | 现有（弱） |
| **Power-only + centroid** | shared | immediate | **load-weighted centroid** | learned | 强 Motion 启发式 |
| **Credit-N5 / N20** | shared | n-step | learned | learned | 测 credit horizon |

**设计**：
- 每个 3 seeds × 400 EP；seed 7/17/27；
- 评估 9000–9029；
- 指标：QSR/Avg-SQA/P5/P95/Jain/Goodput/max BH load/min relay QSR；
- 预期：Full > Motion-only+WF > Motion-only+equal；Full > Power-only+centroid > Power-only+fixed circle；Flat-Relay 变差。

**成本**：
- 4 个新条件 × 3 seeds = 12 runs ≈ 10 h；
- 代码：Power-only centroid hook + waterfilling power + flat-relay preset，约 2–3 天。

**论文位置**：Table 2、Fig. 4。

---

### E3 调度器：算法级 + 调度器基线

**目的**：把“frozen-policy diagnostic”升级为“算法级 scheduler ablation”，并和经典调度器比。

**3.1 补训版（算法级）**
- no-age（λ_s=0）× 3 seeds × 400 EP
- no-1-swap（greedy）× 3 seeds × 400 EP
- 同一架构、同一 budget、同一评估
- 成本：6 runs ≈ 5 h

**3.2 调度器基线（frozen main policy，eval only）**
- ROCS-0（nominal）
- no-age
- no-1-swap
- Proportional Fair (PF)
- Max-CQI / max-SINR
- Max-QoS / max-min
- Equal-FDMA / round-robin
- 成本：4 个新 scheduler × 3 seeds × 30 scenes = 360 episodes ≈ 30–40 min（需实现 scheduler 接口）

**指标**：QSR、P5、P95、Jain、Goodput、单时隙调度耗时。

**预期**：
- ROCS-0 的 P5/P95 最好；
- PF 的 Jain 可能接近，但 QSR/P95 更差；
- Max-CQI 的 Goodput 可能最高，但尾部最差。
- 这能说明“吞吐最优 ≠ 韧性最优”，强化论文动机。

**论文位置**：Table 3、Fig. 5。

---

### E4 λ 敏感度 / Pareto（已完成 common-30）

**目的**：证明 λ_s 是平滑的 mean-tail 旋钮，主方法 0.1 是合理选择。

**已完成（9000–9029，n=90/条件）**：

| 条件 | λ_r | λ_s | QSR | Avg-SQA | P5 | Jain | P95(s) | Goodput |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **main** | 0.10 | 0.10 | **0.8096** | **0.7338** | **0.2369** | **0.8693** | 10.19 | **50.75** |
| R005 | 0.05 | 0.20 | 0.7966 | 0.7169 | 0.2204 | 0.8552 | 8.33 | 49.26 |
| LS020 | 0.10 | 0.20 | 0.7943 | 0.7057 | 0.2089 | 0.8472 | 8.67 | 48.45 |
| S040 | 0.10 | 0.40 | 0.7884 | 0.7063 | 0.2228 | 0.8536 | **6.26** | 48.70 |
| R020 | 0.20 | 0.20 | 0.7865 | 0.6873 | 0.1704 | 0.8300 | 10.05 | 47.15 |
| no-age | 0.10 | 0.00 | 0.7527 | 0.6662 | 0.0352 | 0.7668 | 69.15 | 45.97 |

**Pareto 前沿（QSR vs P95）**：main → R005 → S040。
- main：均值/P5/公平性/吞吐最好；
- R005：轻微尾部优先，QSR −1.30 pt，P95 −18%；
- S040：尾部优先，QSR −2.12 pt，P95 −39%；
- **LS020 被 R005 全面支配**（QSR/P5/Jain/Goodput 更高、P95 更低），不是 Pareto 点；
- R020 被 main 全面支配；no-age 崩溃。

**图/表**：
- 图：x=P95，y=QSR；x=P95，y=P5；标注 main/R005/S040/LS020/R020/no-age。
- 表：λ_r × λ_s 的 QSR/P5/P95。

**注意**：
- 实际是“十字网格”，不是 OFAT；论文要如实写“two-factor screen”。
- 不要用训练 P95 代替评估 P95。
- 不要只报 3-seed 平均；给 per-seed 点。
- **不要用 LS020 当“尾部代表”**；它是被支配点。

**论文位置**：Table 4、Fig. 6。

---

### E5 泛化 / 压力测试

**目的**：支撑“resilience”，而不是“nominal 性能”。

**因素与水平（一次一个因素）**：

| 因素 | 训练值 | 测试水平 | 说明 |
|---|---|---|---|
| 负载倍率 | 1.0 | 0.75 / 1.0 / 1.25 / 1.5 | 同时报实际平均用户数 |
| 用户速度 | 0–6 m/s | 3 / 6 / 9 m/s | 9 是外推 |
| C-UAV 初始位置 | (250,0,150) | 中心 (0,0,180) / 训练点 (250,0,150) / 对边 (-250,0,150) / 角 (250,250,150) | 包含训练点 |
| 信道 | A2G | A2G / A2A-LoS / P.1410 | 若代码支持 |
| K（中继数） | 4 | 3 / 4 / 5 / 6 | 若代码支持；否则写“fixed K=4”限制 |

**方法**：主方法 + 最强基线（CDA 或 E1 的赢家）；可选 PI。
**场景**：每个条件 10 scenes（9000–9009），3 seeds。
**成本**：2 方法 × 3 水平 × 3 seeds × 10 scenes = 180 episodes/因素 ≈ 20–30 min；4 因素约 2 h。
**指标**：相对 nominal 的 QSR/P5/P95 退化；绝对值和相对退化都报。
**预期**：主方法退化更慢；高负载/高速下优势更大（因为负载均衡和 age 调度更重要）。
**论文位置**：Table 5、Fig. 7。

---

### E6 效率 / 实时性 / 能耗

**目的**：证明“可部署”，并诚实处理 energy trade-off。

**内容**：
1. 参数量表：main 365,451；CDA 365,245；TD3 ~372k；PPO ~363k；Joint-SAC ~368k；PI N/A。
2. 推理时延：batch=1，2000 次 forward，mean/P95。
   - **实测（4060 Ti）**：CUDA mean **4.47 ms** / P95 **6.52 ms**；CPU mean **1.47 ms** / P95 **1.92 ms**；在线参数 365,451。
   - CPU 更快是因为网络很小、batch=1，GPU 有 kernel/传输开销；两者都远低于 500 ms 时隙。
3. 训练时间：400 EP 的 wall-clock；达到 95% final QSR 所需 EP。
   - 现有：main 约 EP 70，CDA 76，Recursive 76，Motion 72。差距不大，**不要把 sample efficiency 当主要卖点**，只说明 400 EP 足够。
4. 能耗/航程：C-UAV path 541 m（main）vs 465 m（CDA）vs 609 m（Recursive）；QSR per 100 m；画 QSR–path Pareto。
5. GPU 显存：单进程/三进程。

**成本**：时延 10 min；其余从现有数据算。
**论文位置**：Table 6、Fig. 9。

---

### E7 最终 100 测试（冻结后）

**目的**：论文最终表，避免 dev/test 污染。

**设计**：
- 场景 10000–10099（100 seeds）；
- 方法：main + CDA + TD3 + PPO + Joint-SAC + PI（+ 可选 MAPPO）；
- 3 training seeds × 100 scenes；
- 预注册主指标（QSR）和次指标（P5/P95/Jain/Goodput/Path）；
- 统计：paired by scene，分层 bootstrap，Holm。

**成本**：6 方法 × 3 seeds × 100 = 1800 episodes；2 workers 约 1.5–2 h；PI 单独 100 scenes 约 10 min。
**论文位置**：Table 1 最终版；所有主图。

---

### E8 机理图 / case study

**目的**：让审稿人“看见”方法为什么有效。

**内容**：
1. **per-relay load box/CDF**：4 个 relay 的 backhaul load、goodput、QSR；主方法 vs CDA。
2. **outage CDF**：session longest outage 的 CDF；主方法 vs CDA。
3. **case study**：选 2 个场景：
   - 一个主方法成功、CDA 失败的峰值场景；
   - 一个主方法也出现长 outage 的场景（诚实展示边界）。
   - 画 C-UAV 轨迹、每 relay 功率/负载、active users、outage 时间线。
4. **λ Pareto 图**（E4）。

**成本**：从现有 trajectories/relay_slots 画图，1–2 天。
**论文位置**：Fig. 8、Fig. 10。

---

### E9 统计与可复现性（不是实验，但必须做）

- 主指标预注册：QSR；次指标：P5、P95、Jain、Goodput、Path。
- 配对：同一 scene、同一 training seed。
- 分层 bootstrap：scene + seed；10k–20k 次。
- 效应量：paired Cohen's dz；win rate。
- 多重比较：Holm-Bonferroni（6 指标 × 4 基线）。
- 报 per-seed，不只报 pooled。
- 右删失：episode 结束仍活跃的 session 标记，不伪装完整生命周期。
- 代码/配置 hash、随机种子、硬件、PyTorch 版本。
- 声明：CDA adapted；PI adapted；final checkpoint 不是 best-of-test。

---

## 5. 统计规范（建议直接写进论文）

1. **Primary metric**：Avg-QSR（或 Avg-SQA，二选一，不能两个都叫 primary）。
2. **Secondary**：P5-SQA、P95-Outage、Jain、Goodput、C-UAV path。
3. **Paired design**：同 scene 同 seed；90 对（3 seeds × 30 scenes）。
4. **95% CI**：bootstrap 20k，按 scene 重采样；报告 mean diff、CI、win rate。
5. **Effect size**：Cohen's dz；不要只报 p。
6. **Multiple comparison**：Holm 校正；或明确“primary 只有 1 个，其余 exploratory”。
7. **Per-seed**：每个 training seed 单独报 QSR/P5/P95；避免“平均好看、某个 seed 崩”。
8. **Final 100**：独立、冻结后只跑一次；不参与调参。

---

## 6. 图表清单（建议）

### 表

- **Table 1** 主对比：7 方法 × QSR/Avg-SQA/P5/P95/Jain/Goodput/Path/Params。
- **Table 2** 机制消融：Full / Recursive / Motion-only+equal / Motion-only+WF / Power-only+circle / Power-only+centroid / Flat-Relay。
- **Table 3** 调度器：nominal / no-age / no-1-swap（补训版）+ PF / Max-CQI / Max-QoS（frozen）。
- **Table 4** λ 敏感度：λ_r × λ_s 的 QSR/P5/P95。
- **Table 5** 泛化：负载/速度/初始位置/信道。
- **Table 6** 效率：params、latency、training time、path、QSR/100m。
- **Table 7** 最终 100：主表复测。

### 图

- **Fig. 1** 场景示意图（C-UAV、4 M-UAV、GU、回传/接入）。
- **Fig. 2** 方法架构（shared relay encoder + motion/power branches + ROCS-0）。
- **Fig. 3** 收敛曲线（QSR vs EP，5–8 方法）。
- **Fig. 4** 消融柱状图（QSR/P5/P95）。
- **Fig. 5** 调度器：P5/P95 对比 + outage CDF。
- **Fig. 6** λ_s Pareto（QSR vs P95，P5 vs P95）。
- **Fig. 7** 泛化曲线/热图。
- **Fig. 8** per-relay load box/CDF（max BH、min relay QSR）。
- **Fig. 9** 效率：params vs QSR、path vs QSR、latency。
- **Fig. 10** case study 轨迹 + outage 时间线。

---

## 7. 时间表 / 算力（4060 Ti 3 workers + 4090 可用）

### 最小可发表集（会议/应用期刊，约 10–12 天）

| 天 | 任务 | 产出 |
|---|---|---|
| 1 | E4 λ eval；E8 per-relay/outage 图；E6 latency | 3 张图/表 |
| 2–3 | E3 补训 no-age/no-1swap（6 runs） | Table 3 |
| 4–5 | E1 Joint-SAC（3 runs）+ TD3/PPO adapter + smoke | 代码 |
| 6–7 | E1 TD3/PPO（6 runs） | Table 1 |
| 8 | E5 泛化（main vs CDA） | Table 5 |
| 9 | 冻结 + E7 最终 100 | Table 7 |
| 10–12 | 统计、图表、写作 | 初稿 |

### 强集（期刊，约 3–4 周）

- 上述 + E2 强消融（12 runs）+ E3 调度器基线（4 个）+ E5 信道/K + 5 seeds（可选）+ case study。
- 4090 可以并行跑 TD3/PPO，4060 Ti 跑 eval/小训练。

### 算力估算

- 400 EP/run ≈ 2.5 h（4060 Ti，单进程）；3 workers 并行，9 runs ≈ 7.5 h。
- 30-scene eval/seed ≈ 1.5–2 min；90 episodes ≈ 10–15 min。
- 最终 100：6 方法 × 3 seeds × 100 ≈ 1800 episodes ≈ 1.5–2 h（2 workers）。
- E5 泛化：4 因素 × 2 方法 × 3 seeds × 10 scenes ≈ 2 h。

---

## 8. 目标 venue 与 claim 校准

| 目标 | 需要的最低实验 | 当前差距 |
|---|---|---|
| 会议（Globecom/ICC/WCNC） | 5 方法 + 3 消融 + scheduler + 最终 100 | 补 scheduler 重训 + 最终 100；CDA 可接受 |
| 应用期刊（IoT-J/TVT/Ad Hoc Networks） | + TD3/PPO/Joint-SAC + 泛化 + 效率 | 约 2 周 |
| 较强期刊（TWC/TMC/JSAC） | + MAPPO + 信道/K + 5 seeds + 理论/更强 novelty | 约 1–2 个月；当前 novelty 可能不够 |

**建议**：先按“应用期刊”设计，把 E1/E3/E5/E6/E7 做扎实；如果时间允许，再加 MAPPO 和信道鲁棒性。不要一开始就追求 13 个方法，容易每个都不深。

---

## 9. 不要做的事

1. **不要只报 3-seed 平均**：seed 7 的 LS020 均值打平、尾部更好；必须报 per-seed。
2. **不要把训练 P95 和评估 P95 混表**：CDA 训练 P95 19.3 s、评估 18.05 s；主方法训练 CSV 没有 P95。
3. **不要用 fixed circle 的 Power-only 当唯一证据**：加 centroid/load-aware 版。
4. **不要声称“全面最优/最节能”**：主方法 path 541 m > CDA 465 m。
5. **不要用 10-scene 旧主方法均值比 30-scene 新结果**：统一重评。
6. **不要在最终 100 之前调 λ/scheduler/checkpoint**：最终 100 只跑一次。
7. **不要把 CDA 写成 verbatim**：明确 adapted + 参数匹配。
8. **不要用“best checkpoint on test”**：当前统一 final EP400，写清楚。

---

## 10. 下一步（本周就能做）

**P0（不需要新训练）**
- [x] common-30 五方法（已完成）
- [x] scheduler frozen 消融（已完成）
- [x] E4：S040/R005/R020 common-30 评估（已完成）
- [ ] E8：per-relay load / outage CDF / QSR–path Pareto（1–2 天画图）
- [ ] E6：推理时延（10 min）
- [ ] 统计表：per-seed + 分层 bootstrap + Holm

**P0（需要小代码/训练）**
- [ ] E3：补训 no-age/no-1swap（6 runs，5 h）
- [ ] E1：Joint-SAC（3 runs，代码 0.5 天）
- [ ] E2：Power-only + centroid（3 runs，代码 1 天）

**P1**
- [ ] E1：TD3/PPO adapter + 6 runs（2–3 天）
- [ ] E5：泛化 main vs CDA（2 h）
- [ ] E3：PF/max-CQI scheduler 基线（1–2 天代码）

**P2**
- [ ] MAPPO、信道、K、5 seeds
- [ ] case study
- [ ] 最终 100（冻结后）

---

## 11. 一句话总结

> 现有数据已经证明“**双分支信用 + ROCS-0 能把回传负载压平，从而提升最低 QoS 韧性**”，这是论文的核心；但要用它发一篇较强的论文，必须补 **标准 RL 基线（TD3/PPO/Joint-SAC）、强启发式消融、算法级 scheduler、泛化、效率、最终 100**。λ 保持 (0.10,0.10)，把 R005/S040 写成 resilience knob 的 Pareto 证据（LS020 是被支配点，不要当尾部代表），而不是换主方法。
