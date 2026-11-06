# Fig. 2 框架图分析与“实验章节 ↔ 训练 run”总表

- 日期：2026-11-03
- 参考图：你给的 GAT-MAPPO-IHEFT (GMIT) 框架图（Fig. 3）
- 你的目标：TVT full paper；Fig. 2 按“左环境 / 右上 RL / 右下调度器”三块组织。
- 本文档只做分析与设计，不画图；你确认后再决定是否画。

---

## 0. 先说结论

1. **你不缺“图”，你缺的是“图 ↔ 方法 ↔ 实验”的一一对应。** 参考图之所以好看，不是图标多，而是它把“环境、RL、调度器”三块的信息流讲清楚了。
2. **参考图可以借“信息架构”，不能借“内容”。** 它是 MEC 任务调度：DAG、GAT、task priority、IHEFT；你是 UAV 通信的 minimum-QoS 韧性：动态会话、QoS 年龄、branch credit、ROCS-0。硬套会变成“四不像”。
3. **你的 Fig. 2 应该让审稿人 10 秒内看到三件事**：
   - 左：环境是两层 UAV + 动态 QoS 会话；
   - 右上：Motion/Power 双分支 + immediate power credit（这是算法 novelty）；
   - 右下：ROCS-0 的 age weight + max-cost + 1-swap（这是 scheduler novelty）。
4. **实验章节要按 claim 组织，不按“方法名单”组织。** 下面给出一张“章节 ↔ 训练 run ↔ 评估 ↔ 图表”的总表，你可以直接拿它排论文。

---

## 1. 参考图为什么“看起来完整”

参考图 Fig. 3 的结构：

```
┌───────────────┬──────────────────────────────────────────────┐
│ System Model  │  GAT-MAPPO-IHEFT Algorithm (GMIT)            │
│ (UAVs + UEs)  │  ┌───────────────────────────────┐           │
│               │  │ DAG → GAT → features → actors │  MAPPO    │
│ Application   │  │        → global critic        │           │
│ Model (DAG)   │  └───────────────────────────────┘           │
│               │  ┌───────────────────────────────┐           │
│ UAVs/UEs      │  │ IHEFT: 3 steps                │           │
│ Dynamics      │  │ criticality → offload → exec  │           │
└───────────────┴──────────────────────────────────────────────┘
```

它做对了 5 件事：

1. **左中右三段式**：环境（左）→ 状态（中）→ 算法（右），数据流一目了然。
2. **右上/右下分层**：上面是“学习”，下面是“调度/执行”，对应两种不同的决策。
3. **每块都有输入/输出箭头**：`s_t`、`a_t`、`R_t`、`Q_t`，不是静态堆图标。
4. **调度器用 3 个 step 讲**：criticality → offloading → execution，审稿人能顺着读。
5. **颜色分区**：环境灰、RL 蓝、调度器紫/黄，视觉上不混。

它不适合直接搬的地方：

- **DAG / GAT / task priority** 是 MEC 任务图，不是你的 QoS 会话；
- **MAPPO 的 global critic + M 个 actor** 不是你的 branch-credit SAC；
- **IHEFT 的 task offloading** 不是你的 per-slot 资源分配；
- 它的 “Application Model” 是任务 DAG，你的是 **QoS 档位 + 动态会话 + 年龄**。

---

## 2. 你的 Fig. 2 应该怎么分

建议严格三段式：

```
┌──────────────────────┬─────────────────────────────────────────────┐
│ (A) Environment      │ (B) Branch-Credit SAC                       │
│  Module              │  shared relay encoder                       │
│                      │  motion actor/critic  power actor/critic    │
│  A1 System Model     │  immediate power credit / recursive motion   │
│  A2 QoS Session      ├─────────────────────────────────────────────┤
│  A3 Dynamics         │ (C) ROCS-0 Scheduler                        │
│                      │  Step1 age weight → Step2 max-cost+1swap →  │
│                      │  Step3 allocate/update                       │
└──────────────────────┴─────────────────────────────────────────────┘
```

### 2.1 左栏 (A) Environment Module

参考图左栏有三块：System Model、Application Model、UAVs/UEs Dynamics。你的对应：

**A1. System Model（系统模型）**
- 1 架 C-UAV（中心/回传汇聚），4 架 M-UAV（中继），若干 GU 簇；
- 接入链路（5 MHz）与回传链路（20 MHz）；
- 500 m × 500 m，K=4；
- 画出 C-UAV 在边界 `(250,0,150)`，M-UAV 从 `(0,0,80)` 起飞跟踪用户簇。

**A2. QoS Session Model（业务模型）**
- 动态会话：20 个持续用户 + 四阶段到达（normal→ramp→peak→recovery）；
- QoS 档位 0.7 / 2.0 / 2.5 Mbps，按 0.45/0.35/0.20 采样；
- 会话时长 45 s + Gamma(2,12.5)，截断 45–120 s；最大 130 用户；
- 画一个小的“用户数 vs 时间”曲线，标出四阶段；这比 DAG 更贴你的问题。

**A3. UAVs/UEs Dynamics（动态）**
- GU：每 0.5 s 重采样速度/方向（0–6 m/s），边界反射；
- M-UAV：QoS 加权 K-means++ + Hungarian 关联，25 m/s、5 m/s²；
- 年龄/中断更新：`O_i ← O_i + Δt` 若不满足 QoS，否则清零；
- 画出“位置 → 关联 → 年龄”的小闭环。

**A 栏输出**：
- 状态 `s_t`：C-UAV 状态、4 个 relay token、用户 QoS/年龄/负载；
- 动作 `a_t = (a_M, a_P)` 从 B 栏来；
- 调度分配 `z_t` 从 C 栏来；
- 奖励 `r_t` 回 B 栏。

> 注意：A 栏不要画 DAG、task priority、GAT；这些不是你的模型。

### 2.2 右上 (B) Branch-Credit SAC

参考图右上是 DAG→GAT→feature→actors→global critic。你的对应：

**B1. Shared Relay Set Encoder**
- 输入：4 个 relay token + 全局上下文；
- 输出：permutation-invariant 的 relay embeddings；
- 画 4 个 token 进 encoder，出 4 个 embedding（用“...”省略第 3/4 个，避免拥挤）。

**B2. Motion Branch**
- Motion actor `π_M(s)` → C-UAV 三维运动（速度/航向/爬升）；
- Motion critic `Q_M(s, a_M)`；
- 信用：**recursive long-horizon**（画一条长箭头/循环箭头）。

**B3. Power Branch**
- Power actor `π_P(s, a_M?)` → 4 个 relay 的功率分数；
- Power critic `Q_P(s, a_M, a_P)`（条件在 motion 上）；
- 信用：**immediate same-slot**（画一条短箭头，标 "same-slot"）。

**B4. SAC Update**
- 两个 replay buffer（主 replay + power replay）；
- target networks、entropy α、loss `L_Q, L_π, L_α`；
- 用一个小方框写 "SAC update"，不要展开公式。

**B 栏输出**：`a_t = (a_M, a_P)` 给 A 栏。

> 关键视觉：**Motion 长箭头 vs Power 短箭头**，一眼看出“时间尺度不同、信用不同”。这是你相对普通 SAC 的核心 novelty，必须在图上可见。

### 2.3 右下 (C) ROCS-0 Scheduler

参考图右下是 IHEFT 的 3 step。你的对应：

**C1. Step 1 — Age-weighted priority**
- 权重：`w_i = 1 + λ_s (O_i + Δt)`；
- 需求：`A_i = q_i / C_i^A`，`B_i = q_i / R_k^B`；
- 密度：`w_i / max(A_i, B_i)`；
- 画一个“用户 → 权重/需求”的小表。

**C2. Step 2 — Max-cost + 1-swap**
- 贪心可行分配（access airtime + backhaul 约束）；
- best-improvement 1-swap（画两个用户交换的示意）；
- 再按 density 回填；
- 约束：`Σ access ≤ 1`，`Σ backhaul ≤ R_k^B`，`p_k ≤ P_max`。

**C3. Step 3 — Allocate & update**
- 输出：每用户 served bits、每 relay 功率/回传、QSR；
- 更新年龄 `O_i`；
- 回到 A 栏的下一 slot。

**C 栏输出**：`z_t`（关联/资源分配）给 A 栏；`QSR/age` 给 reward。

> 关键视觉：`λ_s` 用一个小旋钮图标，标 "resilience knob"；1-swap 用两个彩色用户交换箭头。审稿人一眼看到“调度器不是黑盒”。

---

## 3. 参考图 vs 你的图：保留/替换/删除

| 参考图元素 | 你的图 | 处理 |
|---|---|---|
| System Model（UAV+UE） | 两层 UAV + GU | **保留结构**，换图标/链路 |
| Application Model（DAG） | QoS 档位 + 动态会话 | **替换** |
| UAVs/UEs Dynamics | 移动/关联/年龄 | **保留结构**，换内容 |
| Global state `s_t` | 状态 | **保留** |
| DAG → GAT | 共享 relay encoder | **替换** |
| MAPPO actors + global critic | Motion/Power actors + branch critics | **替换** |
| `a_t` | `(a_M, a_P)` | **保留** |
| IHEFT 3 steps | ROCS-0 3 steps | **保留“3 step”结构**，换内容 |
| `Q_t` | `z_t`（分配） | **替换** |
| 颜色：灰/蓝/紫 | 灰/蓝/橙 | 可沿用 |

**删除**：DAG、GAT、task priority、global critic、task offloading、execution queue。
**新增**：QoS 年龄、四阶段负载、immediate vs recursive credit、λ_s 旋钮、1-swap。

---

## 4. 建议的图注（可直接改）

> **Fig. 2.** HQC-SAC framework. (A) Two-tier UAV environment with dynamic QoS sessions, user mobility and age/outage dynamics. (B) Branch-credit SAC: a shared relay-set encoder feeds motion and power actors/critics; motion uses recursive long-horizon credit, while power uses immediate same-slot credit. (C) ROCS-0 scheduler: age-weighted priority, max-cost greedy with best-improvement 1-swap, and per-slot resource allocation.

---

## 5. 画图决策建议

**建议：先画“结构草图”，不要等所有实验跑完。**

理由：
- Fig. 2 是概念图，不依赖具体数值；
- 但**最终版**要等 2×2 和 scheduler 结果出来，确认 callout 文案（immediate vs recursive、age+1swap）与最终叙事一致；
- 现在可以先画黑白/灰阶结构，确认三栏信息流，再上色。

**不建议现在做的事**：
- 不要直接照参考图描 DAG/GAT；
- 不要在一张图里塞 4 个 relay 的全部细节（用 “...” 省略）；
- 不要把公式全写进图（只留 `w_i`、`A_i/B_i`、`1-swap` 三个关键式）。

---

## 6. 论文实验章节 ↔ 具体训练 run 总表

> 说明：`3×400` = 3 seeds × 400 EP；`30` = 9000–9029；`100` = 10000–10099。
> 状态截至 2026-11-03 23:40。

| 论文节 | 实验 | 训练 run | 评估 | 状态 | 图表 |
|---|---|---|---|---|---|
| 5.1 Setup | 协议/基线/指标/超参 | 无 | — | 可写 | Table 1 (notation) |
| 5.2 Main comparison | **E1** 7 方法 | Main 3×400；CDA 3×400；TD3 3×400（跑）；PPO 3×400（排队）；Joint-SAC 3×400（完成，但 seed27 发散）；PI 无训练 | 30 + 100 | Main/CDA/Joint-SAC 完成；TD3 跑；PPO 排队；**Joint-SAC 需稳定化** | Table 2, Fig. 3 |
| 5.3 Mechanism (2×2) | **E2** Full/Recursive/Flat-Relay/CDA | Full 3×400；Recursive 3×400；Flat-Relay 3×400（完成）；CDA 3×400 | 30 | **全部完成** | Table 3, Fig. 4 |
| 5.4 Branch ablation | **E3** Motion-only/Power-only + 强启发式 | Motion 3×400；Power 3×400；Motion+WF 3×400（未写）；Power+centroid 3×400（未写） | 30 | 现有完成；强启发式待写 | Table 3, Fig. 4 |
| 5.5 Scheduler | **E4** no-age/no-1swap + PF/Max-CQI + gap | no-age 3×400（排队）；no-1swap 3×400（排队）；PF/Max-CQI 无训练（eval） | 30 | nominal 完成；重训排队；baseline/gap 未写 | Table 4, Fig. 5 |
| 5.6 λ sensitivity | **E5** main/R005/S040/R020/LS020/no-age | 全部 3×400（完成） | 30 | **完成** | Table 5, Fig. 6 |
| 5.7 Generalization | **E6** load/speed/init/K/channel | Main + best baseline（frozen） | 10/条件 | 未跑 | Table 6, Fig. 7 |
| 5.8 Efficiency | **E7** params/latency/time/energy | 无新训练 | — | latency 完成；energy/path 部分 | Table 7, Fig. 8 |
| 5.9 Case study | **E8** per-relay/outage/trajectory | 无新训练 | 30/100 | 数据有；图未画 | Fig. 8/9 |
| 5.10 Final 100 | **E9** 7 方法 × 100 | 复用上述 | 100 | 待冻结后跑 | Table 2 最终 |

### 6.1 当前训练状态（截至 23:40）

- **完成**：Main 3、CDA 3、Recursive 3、Motion 3、Power 3、LS020 3、R005 3、R020 3、S040 3、**Flat-Relay 3**、**Joint-SAC 3**。
- **运行中**：TD3 3（约 EP 175）、PPO 3（排队）。
- **排队**：no-age 3、no-1swap 3。
- **待写代码**：Motion+WF、Power+centroid、PF/Max-CQI、async/sync、trace、MAPPO、泛化评估队列。

### 6.2 2×2 的初步结果（Flat-Relay 完成）

| 条件 | 表示 | 信用 | QSR（last-50） | P5（last-50） |
|---|---|---|---:|---:|
| Full | shared | immediate | **0.800** | **0.287** |
| Flat-Relay | flat | immediate | 0.778 | 0.188 |
| Recursive | shared | unified | 0.755 | 0.151 |
| CDA | flat | unified | 0.741 | 0.118 |

- **两个因素都有贡献**：shared 比 flat 高约 2.2 pt QSR；immediate 比 unified 高约 2.3–3.7 pt；P5 的差异更大（0.287 → 0.188 → 0.151 → 0.118）。
- 这组 2×2 是 Fig. 2 里 “immediate vs recursive” callout 的实证支撑。

### 6.3 Joint-SAC 的问题（必须处理）

- Joint-SAC 3 seeds 的 last-50 QSR：0.616 / 0.681 / 0.520；seed 27 的 critic loss 从 ~1 涨到 **1298**，明显发散。
- 这不是“主方法赢”，而是“基线没训稳”。TVT 审稿人会直接指出。
- 处理选项：
  1. 调低 lr / 加 target update / 梯度裁剪，重训 3 seeds；
  2. 换成更稳的 flat SAC 配置（hidden 297 + 目标网络更新）；
  3. 若仍不稳，**不把 Joint-SAC 当主基线**，主表用 TD3/PPO/CDA/PI，Joint-SAC 放附录并注明发散。
- 我建议先做 1 的 1-seed 诊断（~1 h），确认能稳再重训 3 seeds；否则不要把它写进主表。

---

## 7. 对 TVT 来说，你现在“缺什么”

| 缺口 | 严重度 | 说明 |
|---|---|---|
| Joint-SAC 稳定化 | **高** | 发散的基线不能进主表 |
| TD3/PPO 完成 | 高 | 正在跑 |
| Scheduler 重训 | 高 | 排队；决定 Table 4 |
| 泛化 | 高 | TVT 必问 |
| 强启发式消融 | 中 | 避免 straw man |
| PF/Max-CQI + 最优性 gap | 中 | 回应“启发式”质疑 |
| 最终 100 | 高 | 冻结后 |
| Fig. 2 | 中 | 概念图，先结构后上色 |
| trace-driven / async | 低-中 | 加分项，不是主线 |

**结论**：你不缺 Fig. 2 的“素材”；你缺的是 **Joint-SAC 稳定性 + 泛化 + scheduler 重训 + 最终 100**。Fig. 2 可以现在画结构草图，但最终版等 2×2/scheduler 结果定稿后再上色。

---

## 8. 下一步（等你确认）

1. 我先出一版 **Fig. 2 结构草图**（黑白/灰阶，三栏 + 箭头 + 3 step），你确认信息流；
2. 同时继续跑 TD3/PPO，之后 scheduler 重训；
3. Joint-SAC 先做 1-seed 稳定性诊断，决定是否重训/降级；
4. 2×2 和主表出来后，再给 Fig. 2 上色 + 写 caption。

如果你同意，我就按这个结构画草图；如果你想先改某一栏（例如左栏加“四阶段负载曲线”或右下调“1-swap”细节），告诉我，我先改结构再画。
