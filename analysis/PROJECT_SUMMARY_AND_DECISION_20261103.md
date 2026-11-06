# HQC-SAC 论文项目：现状、λ 参数与双机结果合并分析

- 日期：2026-11-03
- 工作区：`HQC_SAC_PAPER_MATRIX_ONEPC_3WORKERS_4060TI_8GB_20261103`
- 数据口径：训练指标一律为 **最后 50 个 episode 的均值**；评估指标另行标注为 common-30（9000–9029）。
- 结论先行：**主方法保持 (λ_r, λ_s) = (0.10, 0.10)**；LS020=(0.10,0.20) 只赢 P95 极端尾部，均值/QSR/P5/公平性/吞吐均更差，且换参会导致 Phase II/III 全部基线需要重训。

---

## 0. 一页结论

1. **两个参数确认**
   - λ_r = `age_penalty_lambda_per_s` = **0.10 s⁻¹**：奖励侧年龄惩罚，服务奖励为 `C_n − λ_r·平均欠服务年龄`。
   - λ_s = `scheduler_age_weight_lambda_per_s` = **0.10 s⁻¹**：ROCS-0/HA-QCS 调度器年龄权重，`w_i = 1 + λ_s(O_i + Δt)`。
   - 主 anchor 的原始 `run_config.json` 只有一个 `lambda_per_s = 0.1`，新代码把同一个 0.1 拆成 λ_r 与 λ_s，因此主方法是 **(0.10, 0.10)**，不是事后调出来的。

2. **当前各实验的 λ**
   - 主方法、CDA、Recursive、Motion-only、Power-only：全部 **(0.10, 0.10)**。
   - LS020：**(0.10, 0.20)**。
   - 敏感度：R005_S020=(0.05,0.20)、R020_S020=(0.20,0.20)、S040_R010=(0.10,0.40)。

3. **主参数该选谁（30 个公共场景、3 训练种子、90 对配对样本）**
   - 主方法 (0.10,0.10) 相对 LS020 (0.10,0.20)：
     - QSR **+1.53 pt**（95% CI +0.96~+2.11）
     - Avg-SQA **+2.81 pt**（+2.15~+3.49）
     - P5-SQA **+2.80 pt**（+1.60~+3.98）
     - Jain **+2.21 pt**（+1.58~+2.86）
     - Goodput **+2.31 Mbps**（+1.68~+2.96）
     - **P95 最长中断差 1.52 s**（10.19 vs 8.67 s，主方法更差；CI +0.84~+2.24）
   - **补跑 S040/R005/R020 的 common-30 后，λ 的真正 Pareto 是 main → R005 → S040**：
     - main (0.10,0.10)：QSR 0.8096 / P5 0.2369 / P95 10.19
     - R005 (0.05,0.20)：QSR 0.7966 / P5 0.2204 / P95 8.33
     - S040 (0.10,0.40)：QSR 0.7884 / P5 0.2228 / P95 6.26
     - **LS020 (0.10,0.20) 被 R005 全面支配**（R005 的 QSR/P5/Jain/Goodput 更高、P95 更低），不应作为“尾部代表”。
   - 结论：主方法保持 (0.10,0.10) 作为均值优先点；如果论文要一个“尾部优先”配置，选 **S040 (0.10,0.40)**，不是 LS020。**除非论文把 P95 极端尾部当作唯一主指标，否则不换主参数。**

4. **结果是否对论文有利（common-30，5 方法 × 3 seeds × 30 scenes = 450 episodes）**
   - 主方法 QSR **0.8096**；CDA 0.7390（−7.06 pt）、Recursive 0.7523（−5.73）、Motion-only 0.7126（−9.70）、Power-only 0.5142（−29.54）。
   - 主方法 P5 **0.2369**，CDA 0.1304（主方法约为其 1.82 倍）、Recursive 0.1521、Motion 0.0641、Power 0.0146。
   - 主方法 P95 **10.19 s**，CDA 18.05 s、Recursive 17.59 s、Motion 24.69 s、Power 48.54 s；主方法在全部 4 个基线上都显著更低。
   - **主方法最差种子（0.7954）仍高于所有基线的最好种子（CDA 0.7555 / Recursive 0.7625 / Motion 0.7172 / Power 0.5143）**，P5 与 P95 同样成立。
   - **调度器消融（frozen-policy，9000–9029）**：no-age 的 P95 从 **10.19 s 崩到 69.15 s**，P5 从 0.237 掉到 0.035；no-1-swap 的 QSR/Goodput 基本不变，但 P5 −8.83 pt、Jain −3.15 pt、P95 +3.68 s。ROCS-0 的 age 权重与 1-swap 都有独立、可解释的贡献。
   - 有利：消融严格单调、CDA 全面落后、PI 实时但 QSR 仅 0.52、调度器消融成立、400 EP 已收敛。
   - 不利/缺口：泛化未跑、外部 RL 基线只有 CDA、最终 100 未跑、scheduler 消融还需“重训版”才能做算法级 claim。**这些比换 λ 更影响论文成败。**

5. **双机合并**
   - 4090 上只有 LS020（3 seeds）；其余全部在 4060 Ti 上。LS020 目录与 `.rar` 已经在本工作区。
   - 已生成 `analysis/run_registry.csv`：27 个完整 seed-run 的 GPU 来源、λ、hash、状态一张表。
   - 不要移动/改名原目录；用登记表 join。打包脚本原先漏掉 LS020 和 sensitivity，**本次已补**。

---

## 1. 项目是什么

### 1.1 场景

两层无人机应急/中继通信网络：

- **C-UAV（中心无人机）**：负责回传汇聚与全局决策，初始位置 `(250, 0, 150) m`，在 500 m 正方形边界上。
- **4 架 M-UAV（中继无人机）**：为地面用户（GU）提供接入与回传中继；初始在 `(0,0,80) m`，按 QoS 需求加权 K-means++ 聚类 + Hungarian 身份匹配跟踪用户簇，速度 ≤25 m/s、加速度 ≤5 m/s²。
- **服务区域**：固定 `[-250,250] × [-250,250] m`，地图宽度与中继数量不做域随机化（固定 K=4）。
- **动态高负载 GU**：
  - 初始 20 个持续用户；四阶段非齐次 Poisson 到达（normal→ramp→peak→recovery），峰值到达率 1.35 用户/s，最大 130 用户；
  - 会话时长 `45 s + Gamma(2, 12.5 s)`，截断到 `[45,120] s`；
  - QoS 档位 0.7 / 2.0 / 2.5 Mbps，按 0.45 / 0.35 / 0.20 独立采样，会话期间固定；
  - 用户每个 0.5 s 时隙重采样速度和方向（0–6 m/s），边界反射。
- **无线**：5 MHz 接入、20 MHz 回传、每 M-UAV 1 W 接入、5 W 总回传功率、接入干扰泄漏 ξ=0。
- **Episode**：400 个时隙 × 0.5 s = 200 s。

### 1.2 要解决的问题

在动态高负载、用户移动、回传受限的条件下，联合决定：

1. C-UAV 的 3D 轨迹（motion branch）；
2. 每个 M-UAV 的回传功率分配（power branch）；
3. 用户关联与逐时隙调度（ROCS-0 / HA-QCS）。

目标不是单纯最大化吞吐，而是 **最小 QoS 约束下的韧性**：让尽可能多的会话持续满足各自的最低速率，同时压低欠服务年龄、尾部中断和会话间不公平。

P1 服务目标（代码 `age_penalized_v1`）：

```
C_n = 第 n 时隙的严格 QoS 完成率 / 服务收益
J   = mean_n [ C_n − λ_r · mean_under_service_age_{n+1} ]
```

总奖励还包含能耗、安全投影、接入/回传过载等惩罚项；λ_r 只作用于服务奖励项。

### 1.3 主方法

- 项目内名称 **HQC-SAC**；代码算法名 `branch_credit_sac`；旧论文工程中称 **SSBC-SAC（Shared-relay Set-Branch Credit SAC）**。
- 结构：共享中继集合编码器 + **双分支 actor**（Motion / Power）+ 双 critic；主方法使用 **immediate power credit**（功率分支即时信用），不是 common n-step。
- 调度器：`age_weighted_maxcost_1swap`（ROCS-0 / HA-QCS）
  - 权重 `w_i = 1 + λ_s(O_i + Δt)`；
  - 最大化 `Σ z_i w_i`，资源需求 `A_i=q_i/C_i^A`、`B_i=q_i/R_k^B`，贪心密度 `w_i / max(A_i,B_i)`；
  - 贪心可行解后做 **best-improvement 1-swap**，再按 max-cost 密度回填；
  - 确定性低复杂度启发式，不是精确二维背包。
- 关联：QoS 需求加权 K-means++ + Hungarian。
- 安全：速度/加速度/高度/边界投影与 rescue。

### 1.4 论文目的（应证明的因果链）

1. **相对外部 RL 基线**：在参数量几乎相同的前提下，双分支信用 SAC 比 flat CDA-SAC-Adapted 的 QSR/P5/公平性更好。
2. **相对非学习优化器**：PI-BCD-SCA 能满足 0.5 s 实时门，但在动态高负载下 QSR 明显低于学习策略，说明“学出来的策略 + 调度器”有优势。
3. **机制消融**：
   - 去掉双分支信用（Recursive-Credit H128）→ 变差；
   - 只学 Motion、Power 均分（Motion-only）→ 变差；
   - 只学 Power、Motion 固定圆（Power-only）→ 大幅变差。
4. **调度器贡献**：no-age / no-1-swap 应使 P95 中断与公平性变差（**尚未跑**）。
5. **参数合理性**：λ_s 增大应形成“均值换尾部”的平滑 Pareto，而不是随机波动（部分证据）。
6. **泛化/韧性**：负载 ×0.8/1.0/1.2、用户速度 1/2/3 m/s、C-UAV 初始位置偏移下不崩（**尚未跑**）。

### 1.5 指标口径

| 指标 | 含义 | 方向 |
|---|---|---|
| QSR / strict_service | 逐时隙严格 QoS 完成率的 episode 均值 | 越高越好 |
| Avg-SQA / lifecycle_strict_mean | 会话级严格 QoS 完成率均值 | 越高越好 |
| P5-SQA | 会话级完成率的第 5 百分位（下尾韧性） | 越高越好 |
| Jain-SQA | 会话间 Jain 公平性 | 越高越好 |
| P95-Outage | 各会话最长连续欠服务时长的 P95 | 越低越好 |
| Goodput | 聚合有效吞吐 Mbps | 越高越好 |
| C-Path / Energy | C-UAV 航程 / 推进能耗 | 越低越好 |
| Runtime | 单时隙求解/前向时延 | 越低越好 |

注意：`lifecycle_strict_*` 是 episode 结束时按会话统计的最终口径；`*_stepavg` 是逐时隙投影诊断，两者不能混用。episode 结束时仍活跃的会话是右删失，评估器会标记，不应伪装成完整生命周期。

---

## 2. 两个 λ 参数确认

### 2.1 定义

| 符号 | 代码字段 | 作用 | 主值 | 单位 |
|---|---|---|---|---|
| λ_r | `env.age_penalty_lambda_per_s` | 服务奖励 `C_n − λ_r·平均欠服务年龄` | **0.10** | s⁻¹ |
| λ_s | `env.scheduler_age_weight_lambda_per_s` | ROCS-0 权重 `w_i = 1 + λ_s(O_i+Δt)` | **0.10**（`None` 时回退到 λ_r） | s⁻¹ |

两者语义不同：
- λ_r 改变 **RL 的奖励函数**，影响策略学什么；
- λ_s 改变 **调度器的优先级**，影响同一策略下资源分给谁。
主方法数值相同（都是 0.1），但不是同一个参数。

### 2.2 原始主方法证据

从 `Desktop/HQC_SAC_FIXED500_DYNAMIC_USERS_QOS_B_400EP_Seeds_7_17_27` 找到原始训练产物：

```json
"contract": {
  "algorithm": "branch_credit_sac",
  "scheduler_mode": "age_weighted_maxcost_1swap",
  "service_reward_mode": "age_penalized_v1",
  "lambda_per_s": 0.1,
  "motion_hidden_dim": 128,
  "power_hidden_dim": 128,
  "power_credit_mode": "immediate"
}
```

- 原始代码只有一个 `lambda_per_s=0.1`，奖励和调度器共用；新代码拆成两个后，重建记录写为 `(0.10, 0.10)`，与原始一致。
- 原始 `runtime_environment.json`：`NVIDIA GeForce RTX 4060 Ti`，Python 3.11.5，torch 2.5.1+cu121。
- 因此“主方法 provenance 是重建的”这一 caveat 可以降级：原始 run_config 已找回，已复制为 `anchors/HQC_SAC_MAIN/seed_*/run_config_original.json` 与 `runtime_environment_original.json`。

### 2.3 当前实验实际用的 λ

| 实验组 | λ_r | λ_s | 备注 |
|---|---:|---:|---|
| HQC-SAC main（anchor） | 0.10 | 0.10 | 原始单一 0.1 |
| CDA-SAC-Adapted | 0.10 | 0.10 | 与主方法同调度器 |
| Recursive-Credit H128 | 0.10 | 0.10 | 信用消融 |
| Motion-only | 0.10 | 0.10 | 固定 Power 均分 |
| Power-only | 0.10 | 0.10 | 固定圆轨迹 |
| LS020（S020_R010） | 0.10 | 0.20 | 4090 训练 |
| R005_S020 | 0.05 | 0.20 | 4060 Ti |
| R020_S020 | 0.20 | 0.20 | 4060 Ti |
| S040_R010 | 0.10 | 0.40 | 4060 Ti |

**重要修正**：文档里写的是 one-factor-at-a-time（R005_S010、R020_S010、R010_S000、R010_S020、R010_S040），但实际训练的是“十字网格”：

```
             λ_s=0.10   λ_s=0.20   λ_s=0.40
λ_r=0.05        -          ✓          -
λ_r=0.10        ✓(main)    ✓(LS020)   ✓(S040)
λ_r=0.20        -          ✓          -
```

它仍然能干净地看：
- λ_s 效应（固定 λ_r=0.10）：0.10 / 0.20 / 0.40；
- λ_r 效应（固定 λ_s=0.20）：0.05 / 0.10 / 0.20。

但论文/文档不能再说“OFAT”。λ_s=0（no-age）没有重训，由调度器 no-age 反事实诊断覆盖。

---

## 3. 实验完成情况

### 3.1 已完成

| 阶段 | 方法/条件 | runs | EP | GPU | 状态 |
|---|---|---:|---:|---|---|
| I | HQC-SAC main | 3 | 400 | 4060 Ti | 完成，hash 校验通过 |
| II | CDA-SAC-Adapted | 3 | 400 | 4060 Ti | 完成 |
| II | PI-BCD-SCA | 30 scenes | 400 slots | CPU | common-30 完成 |
| III | Recursive-Credit H128 | 3 | 400 | 4060 Ti | 完成 |
| III | Motion-only | 3 | 400 | 4060 Ti | 完成 |
| III | Power-only | 3 | 400 | 4060 Ti | 完成 |
| IV | LS020 | 3 | 400 | **4090** | 完成，已复制到本机 |
| IV | R005_S020 | 3 | 400 | 4060 Ti | 完成 |
| IV | R020_S020 | 3 | 400 | 4060 Ti | 完成 |
| IV | S040_R010 | 3 | 400 | 4060 Ti | 完成 |

合计 **27 个完整 seed-run**（9 个条件 × 3 seeds），每个 160,000 steps、78,001 updates。`analysis/run_registry.csv` 已登记 GPU 来源与 SHA256。

### 3.2 未完成/待跑

| 项目 | 状态 | 影响 |
|---|---|---|
| common-30 全部 5 方法评估 | **已完成**：450 episodes | 论文主表 |
| 调度器消融（no-age / no-1-swap） | **已完成（frozen-policy，2 modes × 3 seeds × 30 scenes）** | 已支撑 ROCS-0 贡献；算法级需补训 |
| λ 敏感度 common-30 评估 | **未跑**（只有训练曲线） | Pareto 图 |
| 泛化（负载/速度/初始位置） | **未跑** | 韧性/鲁棒性主张 |
| 推理时延测量 | **未跑** | 实时性主张 |
| 最终 100 seeds（10000–10099） | **封存未跑** | 最终测试 |
| 外部 RL 基线 TD3/PPO/MAPPO/Joint-SAC | 本包没有 | 基线单薄风险 |

---

## 4. 训练结果对比

### 4.1 最后 50 EP 的训练指标

| 方法 | QSR | Avg-SQA | P5-SQA | P95-Outage(s) | Reward | 相对主方法 QSR |
|---|---:|---:|---:|---:|---:|---:|
| **Main (0.10/0.10)** | **0.800** | **0.742** | **0.287** | —（旧 CSV 无此列） | 130.7 | — |
| LS020 (0.10/0.20) | 0.778 | 0.718 | 0.259 | —（旧 CSV 无此列） | 121.4 | −2.2 pt |
| CDA-SAC-Adapted | 0.741 | 0.665 | 0.118 | 19.3 | 86.5 | −5.9 pt |
| Recursive-Credit | 0.755 | 0.682 | 0.151 | 16.3 | 100.1 | −4.5 pt |
| Motion-only | 0.713 | 0.624 | 0.067 | 25.0 | 64.8 | −8.7 pt |
| Power-only | 0.505 | 0.424 | 0.014 | 46.3 | −64.2 | −29.5 pt |
| S040_R010 (0.10/0.40) | 0.786 | 0.708 | 0.217 | 6.38 | 127.1 | −1.4 pt |
| R005_S020 (0.05/0.20) | 0.785 | 0.709 | 0.203 | 8.78 | 129.4 | −1.5 pt |
| R020_S020 (0.20/0.20) | 0.786 | 0.693 | 0.180 | 9.83 | 116.5 | −1.4 pt |

说明：
- 这是 **训练分布最后 50 EP**，不是 held-out；只能用来判断方向和收敛，不能当论文主表。
- Main/LS020 的旧格式 CSV 没有逐 EP 的 `lifecycle_strict_max_outage_p95_s`，所以 P95 留空，不能拿 CDA 的 19.3 s 与主方法比较。
- Reward 跨 λ_s 不完全可比（调度器改变了数据分布），只作参考。
- P5 的差距很大：主方法 0.287 vs CDA 0.118，接近 2.4 倍；这是“韧性下尾”最强的训练证据。
- **权威对比以 §5 的 common-30 held-out 为准**：CDA 的 QSR 差距扩大到 −7.06 pt，P5 差距扩大到 −10.65 pt。

### 4.2 收敛与种子稳定性

主方法每 50 EP 的 QSR：

| 1–50 | 51–100 | 101–150 | 151–200 | 201–250 | 251–300 | 301–350 | 351–400 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.521 | 0.782 | 0.798 | 0.803 | 0.806 | 0.800 | 0.804 | 0.800 |

- 150 EP 后基本平台化；351–400 相对 301–350 的变化仅 **−0.004**（种子间 std 0.002），不是“还在涨”。
- 三个种子的 late-window QSR：0.804 / 0.785 / 0.812，均值 0.800，种子间 std ≈0.013。
- CDA 平台约 0.741（0.733–0.750），Recursive 0.755，Motion 0.713，Power 0.505。
- **结论：400 EP 预算足够支撑“已收敛”的表述**；不需要为了收敛把主方法扩到 800 EP。如果审稿人要求 sample-efficiency 曲线，现有 8 个 bin 可以直接画。

### 4.3 消融序

```
Full 0.800  >  Recursive-Credit 0.755  >  Motion-only 0.713  >  Power-only 0.505
        (−4.5)              (−4.2)              (−20.8)
```

- 信用消融（immediate → unified n-step）掉 4.5 pt；
- 再去掉 Power 学习（Motion-only）再掉 4.2 pt；
- 只保留 Power、Motion 固定圆（Power-only）崩到 0.505。
- 这个单调序是论文最有力的机制证据：**Motion 分支是主贡献，Power 分支是必要补充，信用设计有独立贡献**。

---

## 5. common-30 评估：5 方法 + 主参数决策

### 5.1 评估设置

- 场景：`9000–9029`，30 个公共验证场景；训练种子 7/17/27 → 每方法 **90 个 episode**（3 seeds × 30 scenes）。
- 5 个核心方法统一在本包评估器上重跑：`results/02_COMMON30_VALIDATION`，共 **450 episodes**。
- LS020 使用它在 4090 上训练时自带的 30-scene held-out 评估（同 9000–9029）。
- 配对 bootstrap 20,000 次，按场景重采样；CI 为 95% 百分位。
- 交叉校验：主方法重评 9000–9009 的每种子 QSR = 0.8100 / 0.8092 / 0.8354，与原始 10-scene summary 的 0.81002 / 0.809215 / 0.835367 几乎逐位一致 → 新评估器口径与旧评估一致。

### 5.2 五方法主表（mean ± sd，n=90）

| 方法 | QSR | Avg-SQA | P5-SQA | Jain | P95-Outage(s) | Goodput(Mbps) |
|---|---:|---:|---:|---:|---:|---:|
| **HQC-SAC (0.10/0.10)** | **0.8096 ± 0.0421** | **0.7338 ± 0.0473** | **0.2369 ± 0.0859** | **0.8693 ± 0.0387** | **10.19 ± 4.29** | **50.75 ± 3.16** |
| CDA-SAC-Adapted | 0.7390 ± 0.0536 | 0.6651 ± 0.0569 | 0.1304 ± 0.0744 | 0.8084 ± 0.0530 | 18.05 ± 7.63 | 44.30 ± 4.16 |
| Recursive-Credit H128 | 0.7523 ± 0.0454 | 0.6730 ± 0.0525 | 0.1521 ± 0.0675 | 0.8208 ± 0.0435 | 17.59 ± 7.20 | 45.37 ± 3.05 |
| Motion-only | 0.7126 ± 0.0377 | 0.6192 ± 0.0433 | 0.0641 ± 0.0356 | 0.7661 ± 0.0384 | 24.69 ± 3.69 | 40.99 ± 2.35 |
| Power-only | 0.5142 ± 0.0470 | 0.4367 ± 0.0348 | 0.0146 ± 0.0052 | 0.6449 ± 0.0385 | 48.54 ± 9.70 | 27.51 ± 1.99 |

主方法在 **全部 6 个指标、全部 4 个基线上都占优**；不是“均值好、尾部差”的权衡。

### 5.3 配对检验（main − baseline，90 对；负 P95 表示主方法中断更短）

| 对比 | 指标 | 差值 | 95% CI | 主方法胜率 |
|---|---|---:|---|---:|
| vs CDA | QSR | **+0.0706** | +0.0611 ~ +0.0808 | 98.9% |
| vs CDA | Avg-SQA | **+0.0687** | +0.0594 ~ +0.0785 | 95.6% |
| vs CDA | P5-SQA | **+0.1065** | +0.0877 ~ +0.1249 | 88.9% |
| vs CDA | Jain | **+0.0609** | +0.0511 ~ +0.0715 | 92.2% |
| vs CDA | P95-Outage | **−7.86 s** | −9.62 ~ −6.17 | 86.7%（主更低） |
| vs CDA | Goodput | **+6.45 Mbps** | +5.67 ~ +7.27 | 96.7% |
| vs Recursive | QSR | **+0.0573** | +0.0523 ~ +0.0622 | 100% |
| vs Recursive | Avg-SQA | **+0.0608** | +0.0557 ~ +0.0658 | 100% |
| vs Recursive | P5-SQA | **+0.0848** | +0.0728 ~ +0.0967 | 91.1% |
| vs Recursive | Jain | **+0.0485** | +0.0438 ~ +0.0533 | 100% |
| vs Recursive | P95-Outage | **−7.40 s** | −8.84 ~ −5.92 | 90.0%（主更低） |
| vs Recursive | Goodput | **+5.38 Mbps** | +4.94 ~ +5.82 | 100% |
| vs Motion-only | QSR | **+0.0970** | +0.0906 ~ +0.1036 | 100% |
| vs Motion-only | Avg-SQA | **+0.1145** | +0.1080 ~ +0.1214 | 100% |
| vs Motion-only | P5-SQA | **+0.1728** | +0.1570 ~ +0.1888 | 100% |
| vs Motion-only | Jain | **+0.1032** | +0.0966 ~ +0.1096 | 100% |
| vs Motion-only | P95-Outage | **−14.50 s** | −15.51 ~ −13.42 | 98.9%（主更低） |
| vs Motion-only | Goodput | **+9.76 Mbps** | +9.21 ~ +10.32 | 100% |
| vs Power-only | QSR | **+0.2954** | +0.2896 ~ +0.3014 | 100% |
| vs Power-only | Avg-SQA | **+0.2970** | +0.2914 ~ +0.3026 | 100% |
| vs Power-only | P5-SQA | **+0.2223** | +0.2051 ~ +0.2402 | 100% |
| vs Power-only | Jain | **+0.2244** | +0.2185 ~ +0.2302 | 100% |
| vs Power-only | P95-Outage | **−38.34 s** | −40.51 ~ −36.19 | 100%（主更低） |
| vs Power-only | Goodput | **+23.24 Mbps** | +22.74 ~ +23.75 | 100% |

相对幅度：
- vs CDA：QSR **+9.6%**、Avg-SQA **+10.3%**、P5 **+81.7%**、Jain **+7.5%**、P95 **−43.5%**、Goodput **+14.6%**。
- vs Recursive：QSR **+7.6%**、P5 **+55.8%**、P95 **−42.1%**。
- vs Motion-only：QSR **+13.6%**、P5 **+269.6%**、P95 **−58.7%**。
- vs Power-only：QSR **+57.5%**、P5 **+1522%**、P95 **−79.0%**。

### 5.4 分种子（强结论：主方法最差种子仍优于所有基线的最好种子）

| 方法 | seed 7 QSR / P5 / P95 | seed 17 QSR / P5 / P95 | seed 27 QSR / P5 / P95 |
|---|---|---|---|
| **Main** | 0.8056 / 0.2012 / 10.63 | 0.7954 / 0.2458 / 10.05 | 0.8277 / 0.2637 / 9.89 |
| CDA | 0.7555 / 0.1587 / 15.99 | 0.7404 / 0.1332 / 17.34 | 0.7211 / 0.0994 / 20.83 |
| Recursive | 0.7456 / 0.1223 / 20.82 | 0.7489 / 0.1429 / 18.58 | 0.7625 / 0.1910 / 13.38 |
| Motion-only | 0.7125 / 0.0642 / 24.72 | 0.7172 / 0.0655 / 24.70 | 0.7083 / 0.0625 / 24.65 |
| Power-only | 0.5141 / 0.0144 / 49.88 | 0.5140 / 0.0152 / 45.86 | 0.5143 / 0.0140 / 49.88 |

- 主方法最差种子 QSR = **0.7954**（seed 17），仍高于 CDA 最好种子 0.7555、Recursive 最好 0.7625、Motion 最好 0.7172、Power 最好 0.5143。
- 主方法最差种子 P5 = **0.2012**（seed 7），仍高于 CDA 最好 0.1587、Recursive 最好 0.1910、Motion 最好 0.0655、Power 最好 0.0152。
- 主方法最差种子 P95 = **10.63 s**（seed 7），仍低于 CDA 最好 15.99、Recursive 最好 13.38、Motion 最好 24.65、Power 最好 45.86。
- 这是描述性“种子级支配”，不是显著性检验（n=3 seeds）；但配合 5.3 的 90 对场景检验，证据非常强。

### 5.5 λ 的五点 Pareto（common-30，n=90/条件）

| 条件 | λ_r | λ_s | QSR | Avg-SQA | P5 | Jain | P95(s) | Goodput |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **main** | 0.10 | 0.10 | **0.8096** | **0.7338** | **0.2369** | **0.8693** | 10.19 | **50.75** |
| R005 | 0.05 | 0.20 | 0.7966 | 0.7169 | 0.2204 | 0.8552 | 8.33 | 49.26 |
| LS020 | 0.10 | 0.20 | 0.7943 | 0.7057 | 0.2089 | 0.8472 | 8.67 | 48.45 |
| S040 | 0.10 | 0.40 | 0.7884 | 0.7063 | 0.2228 | 0.8536 | **6.26** | 48.70 |
| R020 | 0.20 | 0.20 | 0.7865 | 0.6873 | 0.1704 | 0.8300 | 10.05 | 47.15 |
| no-age | 0.10 | 0.00 | 0.7527 | 0.6662 | 0.0352 | 0.7668 | 69.15 | 45.97 |

**Pareto 前沿（QSR vs P95）**：main → R005 → S040。

- **main (0.10,0.10)**：QSR/P5/Jain/Goodput 最高，P95 10.19 s。
- **R005 (0.05,0.20)**：QSR −1.30 pt，P95 −1.86 s（−18%），P5 −1.65 pt；是“轻微尾部优先”的中间点。
- **S040 (0.10,0.40)**：QSR −2.12 pt，P95 −3.93 s（−39%），P5 −1.41 pt；是“尾部优先”点。
- **LS020 (0.10,0.20) 被 R005 全面支配**：R005 的 QSR +0.23 pt、P5 +1.15 pt、Jain +0.80 pt、Goodput +0.81 Mbps、P95 −0.34 s。**LS020 不是 Pareto 点，不应作为“尾部代表”写进论文。**
- **R020 (0.20,0.20) 被 main 全面支配**：提高 λ_r 到 0.2 没有带来任何尾部收益，反而全面变差。
- **no-age (λ_s=0) 崩溃**：P95 69.15 s、P5 0.035，说明 λ_s 不能为 0。

主方法 vs LS020 的逐项对比（仍保留，作为“为什么不用 LS020”的证据）：

| 指标 | Main (0.10/0.10) | LS020 (0.10/0.20) | 配对差 (Main−LS020) | 95% CI | Main 胜率 |
|---|---:|---:|---:|---|---:|
| QSR | **0.8096** | 0.7943 | **+0.0153** | +0.0096 ~ +0.0211 | 66.7% |
| Avg-SQA | **0.7338** | 0.7057 | **+0.0281** | +0.0215 ~ +0.0349 | 75.6% |
| P5-SQA | **0.2369** | 0.2089 | **+0.0280** | +0.0160 ~ +0.0398 | 65.6% |
| Jain | **0.8693** | 0.8472 | **+0.0221** | +0.0158 ~ +0.0286 | 74.4% |
| P95-Outage (s) | 10.19 | **8.67** | +1.52（主更差） | +0.84 ~ +2.24 | 28.9% |
| Goodput (Mbps) | **50.75** | 48.45 | **+2.31** | +1.68 ~ +2.96 | 72.2% |

分种子（说明“均值 vs 尾部”是种子相关的，必须报 per-seed）：

| 训练种子 | Main QSR | LS020 QSR | Main P95 | LS020 P95 |
|---|---:|---:|---:|---:|
| 7 | 0.8056 | 0.8057 | 10.63 | **8.34** |
| 17 | **0.7954** | 0.7932 | 10.05 | **8.11** |
| 27 | **0.8277** | 0.7839 | 9.90 | **9.57** |

### 5.6 决策建议

**保持 (0.10, 0.10) 作为主方法。** 理由按优先级：

1. **公平性**：Phase II/III 的 CDA 和三个消融全部用 (0.10,0.10) 训练。如果主方法改成 0.20/0.40，主方法与基线的 **调度器本身不同**，QSR 差异会混入 scheduler confound。包内文档也明确警告：若换 main 的 λ，必须重新锁定协议并让基线匹配其 scheduler。
2. **指标**：主方法赢 QSR、Avg-SQA、P5、Jain、Goodput 五项；P5 是“韧性下尾”，比 P95 更稳健（P95 只由最坏 5% 会话决定，方差大）。主方法对全部 4 个基线的 P95 也更好，说明“主方法不擅长尾部”只相对于 λ 变体成立，不相对于基线成立。
3. **预注册**：主 anchor 在敏感度实验之前就已用 0.1 训练完成；0.1 不是“看了测试结果再挑的”。这是对抗“调参过拟合”质疑的最强论据。
4. **成本**：换 0.20/0.40 需要把 CDA + Recursive + Motion + Power 共 **9 个 400 EP run** 全部重训（约 1–2 天/3 workers），否则基线不公平；再加重评。
5. **叙事**：λ_s 写成“韧性旋钮”，主方法 0.1 是均值优先点，R005 是中间点，S040 是尾部优先点。**不要用 LS020 当尾部代表**——它被 R005 支配。

**如果论文要一个“尾部优先”配置**：
- 选 **S040 (0.10,0.40)**：P95 6.26 s（比 main −39%），代价是 QSR −2.12 pt、P5 −1.41 pt、Goodput −2.05 Mbps。
- 但只能作为 sensitivity / deployable mode 写，不能直接当主方法；否则基线要全部重训。
- 目前不建议把 S040 当主方法：它会让论文从“全面更优”变成“尾部特化”。

**不要做的事**：
- 不要只挑 seed 7 报“LS020 不损均值还降尾部”——这是种子挑选。
- 不要把训练 P95（CDA 19.3、S040 6.38）与评估 P95（Main 10.19、LS020 8.67、S040 6.26）混在一张表。
- 不要用 10-scene 的旧主方法均值去比 30-scene 的新结果；本文已经统一重评。
- 不要把 LS020 说成“尾部最优”；它被 R005 全面支配。

### 5.7 调度器消融（ROCS-0 的必要性）

在同一批 frozen main 策略上，只改调度器，跑 9000–9029：

| 条件 | QSR | Avg-SQA | P5-SQA | Jain | P95-Outage(s) | Goodput |
|---|---:|---:|---:|---:|---:|---:|
| **nominal（age + 1-swap）** | **0.8096** | **0.7338** | **0.2369** | **0.8693** | **10.19** | **50.75** |
| no-age（λ_s=0） | 0.7527 | 0.6662 | 0.0352 | 0.7668 | 69.15 | 45.97 |
| no-1-swap（仅贪心） | 0.8078 | 0.7216 | 0.1486 | 0.8378 | 13.87 | 50.79 |

配对差（nominal − ablated，90 对）：

| 对比 | 指标 | 差值 | 95% CI | nominal 胜率 |
|---|---|---:|---|---:|
| vs no-age | QSR | **+0.0569** | +0.0446 ~ +0.0699 | 92.2% |
| vs no-age | Avg-SQA | **+0.0676** | +0.0583 ~ +0.0770 | 100% |
| vs no-age | P5-SQA | **+0.2017** | +0.1892 ~ +0.2142 | 100% |
| vs no-age | Jain | **+0.1025** | +0.0929 ~ +0.1124 | 100% |
| vs no-age | P95-Outage | **−58.96 s** | −61.66 ~ −56.28 | 100%（nominal 更低） |
| vs no-age | Goodput | **+4.79 Mbps** | +3.87 ~ +5.73 | 92.2% |
| vs no-1-swap | QSR | **+0.0018** | +0.0009 ~ +0.0028 | 66.7% |
| vs no-1-swap | Avg-SQA | **+0.0121** | +0.0106 ~ +0.0138 | 96.7% |
| vs no-1-swap | P5-SQA | **+0.0883** | +0.0800 ~ +0.0968 | 100% |
| vs no-1-swap | Jain | **+0.0315** | +0.0295 ~ +0.0336 | 100% |
| vs no-1-swap | P95-Outage | **−3.68 s** | −4.22 ~ −3.17 | 97.8%（nominal 更低） |
| vs no-1-swap | Goodput | **−0.03 Mbps** | −0.15 ~ +0.10 | 44.4%（无差异） |

解读：

1. **no-age 是灾难性的**：P5 从 0.237 掉到 0.035（约 1/6.7），P95 从 10.19 s 涨到 69.15 s（约 6.8 倍），QSR −5.7 pt，Jain −10.3 pt。λ_s 的年龄权重不是“锦上添花”，而是 ROCS-0 的核心。
2. **no-1-swap 是“不花吞吐买公平/尾部”**：QSR 只掉 0.18 pt，Goodput 完全不变（CI 跨 0），但 P5 −8.83 pt（相对 −37%）、Jain −3.15 pt、P95 +3.68 s（+36%）。这说明 1-swap 的作用不是提高吞吐，而是把资源从“当前最优”重排给被压制的会话——正是论文要的韧性/公平机制。
3. **对 λ_s 的旁证**：no-age 等价于 λ_s=0；它比 0.1 差得多，说明主方法选 0.1 而不是 0 是合理的。λ_s 从 0.1 继续加到 0.2/0.4 是“均值换尾部”的边际权衡，而不是“越大越好”。

**重要 caveat**：这是 **frozen-policy counterfactual**，策略本身是在 nominal 调度器下训练的。它证明“部署时调度器很关键”，但不等于“用 no-age 重新训练后仍差 6.8 倍”。包内决策规则是“effect material → retrain the affected scheduler ablation”。当前效应非常大，建议至少补训 **no-age × 3 seeds**（3 × 400 EP，约 2.5–3 h/3 workers），最好连 no-1-swap 一起（6 runs，约 5–6 h）。补训后才是算法级 scheduler ablation；不补训则只能写成“frozen-policy diagnostic”。

**实现修复（必须记录）**：原 `uavqos/env.py` 的 `_validate_contract_modes()` 把 `scheduler_mode` 锁死为 `age_weighted_maxcost_1swap`，导致 `RUN_SCHEDULER_ABLATION_DIAGNOSTIC.bat` 根本无法构造 no-age / no-1-swap 环境（会直接抛 `ValueError`）。本次已把三个模式加入白名单；nominal 路径不变，仅放宽校验。该修复是跑通 §5.7 的前提，论文附录/代码可用性声明里应注明。

---

## 6. 两台电脑的结果合并

### 6.1 现状

从 `runtime_environment.json` 的 `gpu_name` 可以确定：

| 机器 | 产出 |
|---|---|
| RTX 4090 | **只有 LS020**（3 seeds） |
| RTX 4060 Ti | 主 anchor、CDA、Recursive、Motion、Power、R005/R020/S040 全部 |

- LS020 目录 `runs/HQC_SAC_FIXED500_B_LS020_400EP` 和 `runs/HQC_SAC_FIXED500_B_LS020_400EP.rar` 已经在本工作区，**不需要再传**。
- 合并工作剩下的是：登记、校验、补齐打包脚本遗漏、统一评估。

### 6.2 已生成的登记表

`analysis/run_registry.csv`（27 行）：

| 字段 | 用途 |
|---|---|
| condition, seed | 唯一键 |
| source_gpu, python | 证明结果来自哪台机器 |
| lambda_r, lambda_s | 防止把不同 λ 的 run 混表 |
| episodes, steps, updates | 完整性 |
| status | COMPLETE/INCOMPLETE |
| agent_sha256, episodes_csv_sha256 | 传输校验 |
| has_heldout_eval | 是否已有评估 |
| path | 原始相对路径 |

汇总：

| 条件 | runs | 完整 | GPU |
|---|---:|---:|---|
| MAIN(0.10/0.10) | 3 | 3 | 4060 Ti（原始 runtime 已找回） |
| LS020(0.10/0.20) | 3 | 3 | **4090** |
| CDA(0.10/0.10) | 3 | 3 | 4060 Ti |
| Recursive(0.10/0.10) | 3 | 3 | 4060 Ti |
| Motion-only | 3 | 3 | 4060 Ti |
| Power-only | 3 | 3 | 4060 Ti |
| R005_S020 | 3 | 3 | 4060 Ti |
| R020_S020 | 3 | 3 | 4060 Ti |
| S040_R010 | 3 | 3 | 4060 Ti |

### 6.3 如果还要从 4090 再传一次：传什么/不传什么

**必须传**：
```
seed_*/agent.pt                      # 评估用
seed_*/episodes.csv                  # 训练曲线
seed_*/run_config.json               # λ / 合同
seed_*/config_snapshot.json          # 完整配置
seed_*/summary.json
seed_*/train_summary.json
seed_*/runtime_environment.json      # 证明 GPU 来源
seed_*/training_intervention.json
seed_*/training_runtime_contract.json
seed_*/heldout_eval_episodes.csv     # 已有评估
seed_*/heldout_eval_summary.json
```

**不要传**：
- `exact_resume.pt`（约 275 MB/seed，和机器/RNG/优化器状态绑定；除非要在 4060 Ti 上续训，否则只用于归档）
- `agent_ep0020.pt … agent_ep0380.pt`（中间 checkpoint，分析不需要）
- `train_console.log`（可选，排错时再传）

**传输后校验**：
1. `agent.pt` SHA256 与源端一致；
2. `episodes.csv` 行数 = 400，`episode.max()=400`，`steps=160000`，`updates=78001`；
3. `run_config.json` 的 `method_id/seed/lambda_*` 与登记表一致；
4. 不要覆盖同名 seed 目录；用 `run_id` 或先 `agent.pt` 改名备份。

### 6.4 目录策略

**不建议**为了“好看”把 LS020 移进 `runs/PHASE_IV_LAMBDA/` 并改 seed 目录名——这会破坏现有脚本的相对路径与已写好的 run_config 对照。

推荐：
- 保持 `runs/HQC_SAC_FIXED500_B_LS020_400EP` 原路径；
- 在 `analysis/run_registry.csv` 里把它映射为 `PHASE_IV_LAMBDA/LS020`；
- 打包时把它和 `runs/HQC_SAC_SENSITIVITY` 一起收进去。

**当前打包脚本的漏洞（已修）**：`scripts/package_results_for_analysis.py` 原先只收 `anchors/HQC_SAC_MAIN`、`runs/PHASE_II`、`runs/PHASE_III`、`runs/00_PILOT`，**漏掉 LS020 和 sensitivity**，直接打 ZIP 会丢 λ 证据。已在本次修复中加入：

```python
copytree(Path('runs/HQC_SAC_FIXED500_B_LS020_400EP'),
         '01_TRAINING_RAW/PHASE_IV_LAMBDA/LS020')
copytree(Path('runs/HQC_SAC_SENSITIVITY'),
         '01_TRAINING_RAW/PHASE_IV_LAMBDA/SENSITIVITY')
```

并把 `analysis/run_registry.csv`、`results/02_COMMON30_VALIDATION`、`results/03_SCHEDULER_ABLATION` 一并收进去。

### 6.5 合并后的一键分析顺序（4060 Ti，8 GB）

按优先级与预计时间（单卡，评估约 3–5 s/episode）：

1. **common-30 全 5 方法**（已完成，450 episodes）
   ```bat
   conda activate uav_old
   python scripts\evaluate_common30_matrix.py --seeds 9000-9029 --device cuda --workers 2
   ```
   产物：`results/02_COMMON30_VALIDATION/method_metric_summary.csv`、`all_methods_common_scenes_episode_metrics.csv`。

2. **主方法 vs LS020 配对统计**（已完成）
   ```bat
   python analysis\main_vs_ls020.py
   ```
   产物：`analysis/main_vs_ls020_30scenes.csv`。

3. **调度器消融**（已完成，frozen-policy，约 13 min）
   ```bat
   python analysis\run_scheduler_ablation_extra.py
   ```
   产物：`results/03_SCHEDULER_ABLATION/`、`analysis/scheduler_ablation_paired.csv`。
   注意：这会跑两个反事实模式（no-age / no-1-swap），nominal 直接复用 `02_COMMON30_VALIDATION`。
   若要算法级消融，需用同一训练脚本从零训练 no-age / no-1-swap（见 §5.7 的 caveat）。

4. **敏感度 common-30**（约 15–20 min；需要给评估器加 λ/checkpoint 变体入口）
   - 目标：把 S040/R005/R020 也放到 9000–9029，画 λ_s–QSR–P95 Pareto。
   - 目前 `eval_utils.METHODS` 不包含这些条件，需要扩展 `build_config`/`checkpoint_path`，或写一个独立 variant 脚本。

5. **泛化**（约 1–2 h）
   ```bat
   python scripts\run_generalization_matrix.py
   ```
   三组：负载 ×0.8/1.0/1.2、速度 1/2/3 m/s、C-UAV 初始位置三个点；frozen main。

6. **推理时延**（约 10 min）
   - 单进程、batch=1，测 actor forward 的 mean/P95；确认 <500 ms（大概率 <10 ms）。
   - 不要用并行评估时记录的时延当实时性证据。

7. **冻结 → 最终 100**
   - 冻结代码 hash、配置、指标定义、检查点选择规则；
   - 5 方法 × 3 seeds × 100 scenes ≈ 1500 episodes，2 workers 约 1.5–2 h；
   - PI-BCD-SCA 单独跑 100 seeds；
   - 最终 100 之前不要再改 λ 或 scheduler。

---

## 7. 目前结果是否有利于论文

### 7.1 有利证据（可以直接写）

1. **消融单调且幅度大（common-30，n=90/方法）**
   - QSR：Full **0.8096** > Recursive 0.7523 > Motion-only 0.7126 > Power-only 0.5142。
   - P5：Full **0.2369** > Recursive 0.1521 > Motion 0.0641 > Power 0.0146。
   - P95：Full **10.19 s** < Recursive 17.59 < Motion 24.69 < Power 48.54。
   - 这说明 Motion 分支、Power 分支、immediate branch credit 三者都有独立贡献，不是“换个名字的 SAC”。

2. **CDA 基线在参数量匹配下全面落后**
   - CDA 365,245 vs 主方法 365,451 在线参数（差 0.0564%）。
   - common-30：QSR 0.7390 vs **0.8096**（−7.06 pt，相对 −9.6%）；Avg-SQA −6.87 pt；P5 **0.1304 vs 0.2369**（主方法约为其 1.82 倍）；P95 **18.05 vs 10.19 s**（−43.5%）；Goodput −6.45 Mbps。
   - 配对胜率：QSR 98.9%、Avg-SQA 95.6%、P5 88.9%、Jain 92.2%、P95 86.7%、Goodput 96.7%。
   - 这不是“模型更大”赢的，是信用/结构赢的。

3. **种子级支配（很强的描述性证据）**
   - 主方法最差种子 QSR 0.7954 > CDA 最好 0.7555 / Recursive 最好 0.7625 / Motion 最好 0.7172 / Power 最好 0.5143。
   - 主方法最差种子 P5 0.2012 > 所有基线最好种子；最差 P95 10.63 s < 所有基线最好种子。
   - 不是显著性检验（n=3 seeds），但配 90 对场景 CI，证据链完整。

4. **PI-BCD-SCA 实时但性能低；主方法推理也实时**
   - PI-BCD-SCA common-30：均值 21 ms、P95 30 ms、成功率 1.0、0.5 s 门通过；QSR 约 0.52。
   - 主方法单时隙推理（batch=1，2000 次）：CUDA mean **4.47 ms** / P95 **6.52 ms**；CPU mean **1.47 ms** / P95 **1.92 ms**；在线参数 365,451。两者都远低于 500 ms。
   - 这给论文一个很好的“real-time optimizer vs learned policy”对照：优化器能算，但在动态高负载下不够好；学习策略既快又强。

5. **ROCS-0 调度器消融成立（frozen-policy）**
   - no-age：P95 **69.15 s vs 10.19 s**（6.8 倍），P5 **0.035 vs 0.237**，QSR −5.7 pt，Jain −10.3 pt；所有指标都显著变差。
   - no-1-swap：QSR/Goodput 基本不变，但 P5 −8.83 pt（−37%）、Jain −3.15 pt、P95 +3.68 s（+36%）。
   - 这说明 age 权重是“防尾部崩溃”的核心，1-swap 是“不花吞吐买公平/尾部”的机制；两者都不是装饰。

6. **收敛与种子稳定性**
   - 150 EP 平台化；400 EP 后 late delta −0.004；种子间 std 0.013。
   - 400 EP 的统一预算站得住；不需要解释“还没训完”。

7. **λ 响应是平滑的，不是噪声（common-30 评估已补）**
   - Pareto：main (0.10/0.10) QSR 0.8096 / P95 10.19 → R005 (0.05/0.20) 0.7966 / 8.33 → S040 (0.10/0.40) 0.7884 / 6.26。
   - 主方法在均值/P5 上最好，S040 在尾部最好；这是可解释的 Pareto，不是随机跳变。
   - **LS020 (0.10/0.20) 被 R005 全面支配**：R005 的 QSR/P5/Jain/Goodput 更高、P95 更低；论文不要把 LS020 当尾部代表。

8. **工程可信度**
   - 4060 Ti 8 GB 三进程 preflight 通过（6.9 GB free）；
   - 27 个 run 全部 400 EP / 160k steps / 78,001 updates；
   - 主 checkpoint hash 与冻结记录一致；
   - 评估器重评主方法 10-scene 与原始 summary 逐位一致。

### 7.2 风险与缺口（按严重程度）

1. **外部 RL 基线只有 CDA（最严重）**
   - 旧论文工程 `uav_qos_paper` 计划 TD3 / PPO / MAPPO / Joint-SAC(PM) / Joint-SAC(0.90M) / CDA 六个学习基线。
   - 本包只有 CDA + PI。
   - 如果旧 TD3/PPO/MAPPO 是在 **不同 contract**（域随机化、动态 K、不同地图）下训的，不能与 fixed-500 主方法同表。
   - 解决：要么补训 TD3/PPO（同一 fixed-500 contract，3 seeds × 400 EP），要么把论文范围缩到“CDA + PI + 机制消融”，并在引言明确不声称覆盖所有 RL 基线。审稿人通常至少想看 TD3/PPO。

2. **调度器消融目前只是 frozen-policy，不是算法级**
   - 已完成 no-age / no-1-swap 的同场景反事实（§5.7），效应极大（no-age P95 69.15 s）。
   - 但策略是在 nominal 调度器下训练的；要做“算法级 scheduler ablation”claim，需补训 no-age（至少 3 seeds）与 no-1-swap（建议也补）。
   - 包内决策规则是“effect material → retrain the affected scheduler ablation”。按此规则应补训，成本约 6 runs × 400 EP（3 workers 约 5–6 h）。

3. **泛化未跑**
   - 目前只有 nominal 500 m、速度 0–6、初始位置固定。
   - “韧性”主张需要负载/速度/初始位置三组测试；否则只能叫“nominal 性能”。

4. **P95 尾部与主指标冲突**
   - 主方法 QSR/P5 更好，但 P95 比 LS020 差 1.52 s。
   - 如果摘要把“降低最坏中断”作为第一贡献，审稿人会抓住这一点。
   - 解决：把 P5 定义为“下尾韧性”主指标，P95 作为“极端尾部”次指标；同时给出 λ_s 的 Pareto，明确 0.1 是均值优先的可配置选择，而不是“全面最优”。

5. **CDA 是 adapted，且同时改了表示与信用**
   - 参数匹配做得很好（0.0564%），但审稿人可能要求官方 CDA 实现或引用其原始超参。
   - 更关键：CDA = flat encoder + unified n-step，主方法 = shared encoder + immediate；主 vs CDA 的差异是“表示 + 信用”的 bundle，不能单独归因。
   - 解决：补 **Flat-Relay + immediate**（只换表示、保留 immediate）完成 2×2 因子设计（Full / Recursive / Flat-Relay / CDA），见论文设计 E2；在方法/实验节明确“adapted to the same fixed-500 contract; not a verbatim reproduction”，并附参数匹配表。

6. **3 个训练种子的统计功效**
   - 90 个配对场景提升了场景级功效，但训练种子只有 3 个；不能声称“跨训练种子显著”。
   - 解决：分层 bootstrap（scene + seed），报 per-seed，避免只报 pooled p 值。

7. **最终 100 未跑**
   - 现在所有数字都是 dev/common-30；最终表必须等冻结后跑 10000–10099。
   - 不要在最终 100 之前再改 λ、scheduler、checkpoint 选择规则。

8. **checkpoint 选择协议**
   - 本包统一用最终 EP400 `agent.pt`；旧论文 README 说用 Dev3 选 best.pt。
   - 两者不能混。当前所有方法都是 final，内部一致；论文要明确写“final checkpoint, no test-based selection”，这其实比 best.pt 更干净。

9. **文档与实现不一致**
   - `experiment_matrix.json` 写 Phase IV 150 EP、OFAT；实际是 400 EP、十字网格。
   - 论文/附录必须按实际跑的描述，否则审稿人复现会对不上。

10. **主方法 provenance**
    - 已找回原始 run_config（λ=0.1, H128/H128, immediate），caveat 可以消掉。
    - 但原始 `run_config` 只有单一 `lambda_per_s`，需要在附录说明新旧代码的拆分等价性。

### 7.3 论文叙事建议

- **主指标**：Avg-QSR / Avg-SQA / P5-SQA；**次指标**：P95-Outage、Jain、Goodput、Energy、Runtime。
- **λ_s 写成可配置的 resilience knob**：
  - 0.1：均值/P5/公平性最优，主方法；
  - 0.2/0.4：用 1–3 pt 均值换 15–40% P95 尾部，适合“极端事件优先”场景；
  - 这样即使 P95 不是主方法最优，也是“设计选择”而不是“打不过”。
- **明确 CDA 是 adapted**，PI 是 real-time optimizer baseline；不要暗示它们是官方原版。
- **报 per-seed + 配对 CI**，不要只报 3-seed 平均；seed 7 的“均值打平、尾部更好”要如实写。
- **调度器消融和泛化**是审稿人最可能追问的两块；在投稿前补上，比再调 λ 更值。

---

## 8. 下一步清单（按优先级）

### P0：今天/明天必须做

- [x] 主方法 common-30 评估（已完成，90 episodes）
- [x] 主方法 vs LS020 配对统计（已完成）
- [x] 其余 4 方法 common-30（已完成，450 episodes）
- [x] 调度器消融 frozen-policy（已完成，§5.7）
- [ ] 补训版调度器消融（no-age 至少 3 seeds；no-1-swap 建议；约 5–6 h）
- [ ] 生成论文主表：5 方法 × 6 指标，mean ± 95% CI，配对差，per-seed
- [ ] 修正文档：λ 网格写“十字网格”，不是 OFAT；Phase IV 写 400 EP

### P1：本周

- [ ] 敏感度 common-30（S040/R005/R020）→ λ_s Pareto 图
- [ ] 推理时延（单进程 batch=1）
- [ ] 泛化三组（负载/速度/初始位置）
- [x] 补打包脚本：LS020 + sensitivity + analysis + common30 + scheduler
- [ ] 统计脚本：分层 bootstrap + Holm 校正 + 效应量

### P2：投稿前

- [ ] 决定外部基线范围：补 TD3/PPO，或缩窄论文 claim
- [ ] 冻结代码 hash / 配置 / 指标定义 / checkpoint 规则
- [ ] 最终 100 seeds（5 方法 + PI）
- [ ] 图表：收敛曲线、消融柱状图、Pareto、泛化、per-relay 负载
- [ ] 附录：CDA adapted 说明、参数量匹配、右删失、checkpoint 选择

---

## 9. 关键文件

| 文件 | 内容 |
|---|---|
| `analysis/run_registry.csv` | 27 个 seed-run 的合并登记表（GPU/λ/hash/状态） |
| `analysis/run_inventory_aggregate.csv` | 各条件最后 50 EP 训练指标 |
| `analysis/convergence_bins.csv` | 每 50 EP 收敛曲线 |
| `analysis/main_vs_ls020_30scenes.csv` | 主方法 vs LS020 配对统计 |
| `analysis/common30_method_summary.csv` | 5 方法 common-30 主表（mean/sd） |
| `analysis/common30_paired_vs_main.csv` | 主方法 vs 4 基线配对差/CI/胜率 |
| `analysis/scheduler_ablation_paired.csv` | nominal vs no-age / no-1-swap 配对统计 |
| `results/02_COMMON30_VALIDATION/` | 5 方法 450 episodes 评估原始文件 |
| `results/03_SCHEDULER_ABLATION/` | no-age / no-1-swap 反事实评估 |
| `results/02_PI_BCD_SCA/full_common30/` | PI 30-scene 评估与 runtime |
| `anchors/HQC_SAC_MAIN/seed_*/run_config_original.json` | 找回的原始主方法配置 |
| `docs/EXPERIMENT_MATRIX.md` | 四阶段矩阵（需按实际 λ 网格修正） |

---

## 10. 一句话回答“主方法用什么参数”

> **主方法用 (λ_r, λ_s) = (0.10, 0.10)**。这是原始主方法就采用的默认值，也是当前所有 Phase II/III 基线/消融的共同设置。30 个公共场景上，真正的 λ Pareto 是 **main (0.8096/10.19) → R005 (0.7966/8.33) → S040 (0.7884/6.26)**；LS020 (0.10,0.20) 被 R005 全面支配，不应作为“尾部代表”。除非论文把“最坏 5% 中断”设为唯一主指标并愿意重训全部基线，否则主方法不换；若要一个尾部优先的 deployable mode，选 S040，不是 LS020。
