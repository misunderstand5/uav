# 参考论文实验设计拆解与我们的实验重设计提案

> 参考论文：Zhang et al., "Asynchronous Task Scheduling and Resource Allocation for
> UAV-Enabled Mobile Edge Computing Networks," IEEE TSC, vol. 19, no. 1, 2026（AL-MAPPO）。
> 本文档目的：学习其实验设计的可取之处，逐项对照我们现有实验，给出补齐方案。
> 状态：2026-11-06 汇总稿 + 执行记录。用户已拍板：①VI-I 做（全部密封数据）②VI-J 做
> ③FCFS/NDF 不补 ④K 可扩展性做 dev-only 小规模扫描（MAIN 在 K=2/6 各训 1 种子）。
> 红线：密封 final-100 数据只做分析、绝不重跑；一切新实验走 dev 集并显式标注。

---

## 一、参考论文实验设计拆解

### 1.1 实验配置要点

| 维度 | 参考论文做法 |
|---|---|
| 数据来源 | **真实 trace 驱动**（Alibaba Cluster Data V2017，过滤 3629 条任务，任务生成建模为 Poisson 过程）|
| 场景生成 | ED 位置每个 episode 随机生成（训练+测试都是）→ 测试未见场景 |
| 环境接口 | 标准 gym 接口；每 UAV 独立异步时钟 |
| 测试规模 | 100 个测试 episode（训练后策略） |
| 种子 | 训练曲线 2 个随机种子 |
| 统计 | **无 CI、无 bootstrap、无逐种子表**（这是它的弱点） |

### 1.2 指标体系

| 指标 | 含义 | 我们对应 |
|---|---|---|
| Energy utility | 计算能耗/(计算+移动能耗) | 我们有 bits/J、c_phys_energy_share（类似） |
| Task missing ratio | 超时任务占比 | 我们：1−QSR（QSR 即按时服务率）|
| Avg. task completion time | 生成→完成平均时长 | 我们：Mean_Under_Service_Age_s / 会话生命周期 |
| Pending requests 时序 | 积压队列随时间变化 | **缺失**（可算）|
| Throughput / completed computation | 完成量 | 我们：Goodput_Mbps、completed_sessions |
| **Per-UAV 负载均衡** | 每个 UAV 的能耗/吞吐分布（箱线图） | **缺失**（可算）|
| **Jain 公平性（跨 UAV）** | 式 (24)，跨 UAV 负载公平 | **部分缺失**：我们只有跨用户 Jain_SQA |
| 训练动态 | reward/utility/missing ratio/completion time 曲线 | 我们有 reward + strict service ratio |

### 1.3 基线体系

| 参考论文基线 | 作用 | 我们对应 |
|---|---|---|
| A-MAPPO（去分层动作） | 机制消融 | NO_1SWAP / NO_AGE / MOTION_ONLY / POWER_ONLY ✓ |
| IPPO（独立 PPO，DTDE） | 无协调对照 | PPO ✓（且另有 TD3）|
| Random（贪心候选集随机选） | 下界 | **缺失**（可选，dev 零训练成本）|
| FCFS（先到先服务） | 经典启发式 | **缺失**（可选，dev 零训练成本）|
| NDF（最近截止期优先） | 经典启发式 | Max-QoS 近似（最差 0.2776）；**可补正式 NDF** |

### 1.4 实验节结构（A–D）及叙事功能

| 节 | 内容 | 叙事功能 | 我们现状 |
|---|---|---|---|
| VI-A | α 权重灵敏度（α∈{1,10,20,30}，归一化技巧 α*） | 论证权衡系数选择 | 我们升级为 **2D λ Pareto**（Table VIII + Fig 5），更强 ✓ |
| VI-B | 收敛 + 可扩展性（4 种设置：固定/随机初始位置、Rician/PL/无时延信道、4–7 架 UAV） | 鲁棒性+可扩展性 | 部分：收敛图 Fig 3 ✓；泛化数据在 `results/05_GENERALIZATION`（C-UAV 初始位置×3、负载×0.8/1.0/1.2、移动速度×3）**但论文结构里没有对应小节** |
| VI-C | 主对比（UAV 数 2–7 扫描 × 5 基线 × 4 指标） | 主结果 | Table I + Fig 4 ✓（固定 K=4） |
| VI-D | **负载均衡 + 吞吐**（per-UAV 箱线图 + Jain 表 + 积压时序） | 证明"多智能体协作没有偏载" | **缺失**——这是最大差距 |

---

## 二、差距清单（按"成本/收益"排序）

### G1 ★ 中继负载均衡分析（零成本，密封数据现成）

参考论文用整个 VI-D 节证明多 UAV 间负载均衡（箱线图 Fig 9–12 + Jain 表 Table V）。
我们密封目录里已有 `nominal__{method}__trainseed_{s}__relay_slots.csv`：
每槽每中继的 `relay_assigned_user_count`、`relay_access_load_ratio`、`relay_backhaul_load_ratio`、
`relay_power_w`、`relay_qsr`、`relay_goodput_mbps`（relay_id ∈ {1,2,3,4}）。

**可新增（全部用现有密封数据，零重跑）：**
1. **Table（新）跨中继负载均衡**：4 个中继的 mean/P5/P95 负载、能耗、QSR + **跨中继 Jain 指数**（仿其 Table V）——注意与我们现有"跨用户 Jain_SQA"区分开（现有的是用户公平，新的是中继负载公平）。
2. **Fig（新）per-relay 分布**：MAIN 各中继 300 episodes 的负载/QSR 箱线图（仿其 Fig 9/10/11）。
3. 叙事：ROCS-0 的 max-cost + 1-swap 是否造成偏载？与 Equal 等启发式对比负载失衡度。

### G2 ★ 积压/服务队列时序（零成本）

参考论文 Fig 8(d)：pending requests 随 slot 演变。
我们的 `relay_slots.csv` 有每槽 `relay_assigned_user_count` / `relay_access_load_ratio` → 可画
4 中继合计积压会话数随时间的均值曲线（MAIN vs NO_AGE vs Max-CQI），一眼看出 NO_AGE
的积压失控（对应 P95 66s 的机制解释）。可作为 Fig 6 或新面板。

### G3 ★ 剧集级分布（零成本）

参考论文大量用箱线图展示 100 测试 episode 的分布（Fig 9/11/12）。
我们 `episodes.csv` 每方法 300 行（100 场景 × 3 种子）含 QSR/obj/P95/Goodput → 可画
7 方法 × obj/QSR 箱线图，直观展示稳定性（比 Table I 单点更可信，回应 W6 逐种子关切）。
可作为 Fig 6 的替代/补充或新图。

### G4 泛化套件进入正文（数据已跑完，只需统计+写）

`results/05_GENERALIZATION/` 已有：C-UAV 初始位置 c_init_1/2/3、负载 load_x0.8/1.0/1.2、
移动速度 mobility_1/2/3 mps —— 对应参考论文 VI-B 的"不同设置鲁棒性"。
当前论文结构（VI-A..VI-H）**没有泛化小节**，数据躺在磁盘上没用上。
**建议**：新增 VI 小节"泛化/鲁棒性"，3 张 mini 表或 1 张表（各扰动下 QSR/obj/P95），
叙事先于 Limitations（"训练集外扰动下仍保持优势"）。

### G5 补齐 deadline 启发式基线 FCFS/NDF（低成本，dev 零训练）

参考论文基线含 FCFS + NDF。我们经典调度器有 Equal/Max-CQI/PF/Max-QoS，
缺"先到先服务"与"最近截止期优先"两个标准启发式。它们是确定性调度器，
在冻结主控制器 + dev 90 剧集上跑即可（无训练，几十分钟级）。**必须标注 dev 数据**。
收益：补全经典基线谱系，审稿人不会问"为什么没有 FCFS/NDF"。

### G6 K 可扩展性（高成本，暂缓）

参考论文 VI-C 扫 UAV 数 2–7。我们 K=4 固定。做 K∈{2,4,6} 需要**重新训练**
所有 RL 方法 × 多种子（4060Ti 8GB 上数天级），与密封协议冲突风险高。
**建议：暂缓**；在 Limitations 中写明"K=4 固定，扩展性留作未来工作"，
或用 05_GENERALIZATION 的负载扫描（load×0.8/1.2）部分替代"规模变化"叙事。

### G7 信道模型对比（超出范围，写入 Limitations）

参考论文对比 Rician/PL/无时延三种信道。我们 NOMA 回传 + 正交接入信道固定。
不改模型；在 Limitations 中一句带过（仿其叙事："信道建模的理想化"）。

---

## 三、重设计后的实验节结构提案

```
VI-A 实验设置（密封协议、bootstrap、右删失）        [不变]
VI-B 主对比        Table I + Fig 3 + Fig 4          [不变]
VI-C 调度器对比    Table II                         [不变]
VI-D 消融          Table III                        [不变]
VI-E 逐种子稳定性  Table IV + Fig 6                 [不变]
VI-F 部署效率      Table V + VI                     [不变]
VI-G 能效          Table VII                        [不变]
VI-H λ 选择        Table VIII + Fig 5               [不变]
VI-I 中继负载均衡  ★新增 Table IX + 新 Fig（G1/G2/G3 合并） 
VI-J 泛化/鲁棒性   ★新增 Table X（G4，05_GENERALIZATION 数据）
```

- G1/G2/G3 合并为 **VI-I**：一张跨中继 Jain 表 + 一个 2–3 面板图
  （(a) per-relay 负载箱线 (b) 积压时序 (c) 剧集级 obj 分布），全部密封数据。
- G4 为 **VI-J**：扰动扫描表，dev 数据。
- G5 若批准：在 VI-C 表后加 FCFS/NDF 两行（dev 标注）。

新增图表数据源汇总：

| 新增 | 数据源 | 需重跑? |
|---|---|---|
| Table IX 跨中继 Jain/负载 | `09_FINAL_TEST100_SEALED/*relay_slots.csv` | 否 |
| Fig 7 负载均衡三面板 | 同上 + `*episodes.csv` | 否 |
| Table X 泛化扰动 | `05_GENERALIZATION/generalization_all_episodes.csv` | 否（已存在）|
| Table II 增补 FCFS/NDF 行 | 新 dev 评估（冻结控制器） | 是（dev，低成本）|

---

## 四、参考论文的弱点（不要学）

1. **无置信区间/显著性检验**：只有 2 种子均值曲线，100 episodes 无误差棒 → 我们密封
   +配对 bootstrap + CI + 逐种子披露是更强资产，保持并强调。
2. **α 一维扫描**：我们用 2D λ Pareto + 前沿阶梯线，表达力更强，保持。
3. **无逐种子表**：我们 Table IV/Fig 6 已覆盖，保持。
4. **无运行时/复杂度实验**：我们 Table V/VI 是差异化优势，保持。

## 五、决策点（已拍板）与执行记录（2026-11-06）

| # | 决策点 | 拍板 | 执行状态 |
|---|---|---|---|
| 1 | VI-I 中继负载均衡（G1+G2+G3） | 做，全部密封数据 | ✅ 完成：Table IX（`paper/tables/table9_relay.tex`，跨中继 Jain：users 全同 0.9992 / bh-load / power / QSR）+ Fig 7（`paper/figures/fig7_relayload.pdf`，三面板：per-relay QSR、per-relay 回传功率、剧集 obj 分布） |
| 2 | VI-J 泛化节（G4） | 做 | ✅ 完成：Table X（`paper/tables/table10_generalization.tex`，9 条件 × 3 方法；MAIN QSR span 0.052 / P95 ≤11.2s；CDA-SAC 在 c_init_3 塌方 0.680/26.7s） |
| 3 | FCFS/NDF 基线（G5） | 不补 | — |
| 4 | K 可扩展性（G6） | 做 dev-only 小规模扫描 | ✅ 完成：Table XI（`paper/tables/table11_kscan.tex`）。MAIN 在 K=2/K=6 各训 1 种子（seed 7，400 EP，`runs/K_SCAN/`），与 K=4 dev 基线同 30 场景评估（`results/07_K_SCAN/`）。K2 欠供给塌方（QSR 0.5466 / P95 55.7s）；K6 无增益（0.7959 / 11.5s vs K4 0.8056 / 10.6s）→ K=4 是性价比最优点，支撑固定 K=4 设计 |

**VI-I 关键叙事**（密封数据，零重跑）：挂载均衡是 ROCS-0 加权 refill 的结构性质（users Jain 全同 0.9992，与控制器无关）→ MAIN 把 NOMA 回传功率**有意**集中到回程受限的中继 1/2（1.95/1.57 W vs 0.76/0.71 W，power Jain 0.8475 全方法最低）→ 服务仍均衡且全面占优（QSR Jain 0.9975，per-relay 0.762–0.854；TD3 均匀功率但四个中继全部拥塞、per-relay QSR 均匀地低 0.749–0.787）。

**VI-J 关键叙事**（dev）：MAIN 跨 9 扰动条件 QSR ∈ [0.8016, 0.8538]、P95 ≤ 11.19s；对 C-UAV 初始位置（0.833–0.835）与移动速度（0.818–0.819）几乎不敏感；CDA-SAC 对位置敏感（span 0.091，pos.3 塌方）。
