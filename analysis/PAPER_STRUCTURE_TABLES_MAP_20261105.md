# 论文结构与图表数据映射（修订稿冻结定义）

- 日期：2026-11-05（动笔写修订稿前的结构冻结版）
- 配套文档：[PAPER_REVISION_CHECKLIST_20261105.md](PAPER_REVISION_CHECKLIST_20261105.md)（修订点清单）
- 数据口径：主表=密封集官方（`results/09_FINAL_TEST100_SEALED`）；调度器对比/λ/能效=开发集（`results/02_COMMON30_VALIDATION` 等，90 剧集=3 种子×30 场景）。开发集与密封集范围在文中如实标注。

---

## 1. 实验完成状态（2026-11-05 磁盘核验，全部通过）

| # | 实验 | 规模 | 核验结果 | 数据位置 |
|---|---|---|---|---|
| 0 | 全部训练 | 42 任务 EP400×160k 步 | ✓ 完成；main 3 种子 anchors + SHA-256 存证 | `anchors/`、`runs/` |
| E1 | 经典调度器重跑（修复后） | 15 方法 × 3 种子 × 30 场景 | ✓ 45 个 episodes 文件全 30 行 | `results/02_COMMON30_VALIDATION/` |
| E2 | 调度器 per-slot 运行时 | 7 模式 × 1200 调用 | ✓ 汇总 + 逐槽 CSV | `results/05_SCHEDULER_RUNTIME/` |
| E3 | 控制器参数量/时延 | 9 方法 × CUDA/CPU | ✓ 参数表 + manifest | `results/04_CONTROLLER_LATENCY/` |
| E4 | 能耗重评 | 4 方法 × 3 种子 × 30 场景 | ✓ 12 个 episodes 文件全 30 行 | `results/06_ENERGY/` |
| L | λ 筛选 | 3 变体（+main/no-age 共用 dev） | ✓ 3×12 文件 | `results/04_LAMBDA_VARIANTS/` |
| G | 泛化（负载/移动/初始位置） | 8 条件 × 36 文件 | ✓ | `results/05_GENERALIZATION/` |
| A | 调度器消融诊断 | NO_AGE / NO_1SWAP × 12 文件 | ✓ | `results/03_SCHEDULER_ABLATION/` |
| F | **密封 final-100（官方）** | **7 方法 × 3 种子 × 100 场景 = 2100 剧集** | ✓ 21 个 episodes 文件全 100 行；freeze_manifest 在 | `results/09_FINAL_TEST100_SEALED/` |
| P | 08_PROVISIONAL | 存档 | ✓ 不引用；仅复现性声明用 bit-identical 事实 | `results/08_FINAL_TEST100_PROVISIONAL/` |

**已"修改好"的确认**：经典调度器为修复后真实实现（旧数据在 `results/_pre_fix_backup_E1/`，作废）；能耗模型含 C-UAV 旋翼推进+爬升功（已审计，保留）；15s 硬约束表述已在数据层重新映射为目标函数口径（见第 5 节速查表）。**唯一未完成的是论文正文本身**。

---

## 2. 论文结构（章节级定义，标注每节引用的图表与修订点）

| 节 | 内容要点 | 引用图表 | 落实的修订点 |
|---|---|---|---|
| Title | ROCS-0 + Branch-Credit SAC，vehicular/emergency 场景词 | — | A1 |
| Abstract | 目标函数口径结论（QSR−0.10·age），密封 2100 剧集、bootstrap、CPU 1.4ms | — | A1–A3 |
| I. Introduction | 贡献 3 条各 2–3 行 + 设计 insight；应急/车载 framing | 引用 Table I 数字 | A1–A3 |
| II. System Model | 两层 UAV、NOMA 回传、正交接入、动态 GU 会话 R_min∈{0.7,2.0,2.5}、200s 剧集 | Fig 1 | — |
| III. Problem Formulation | **奖励驱动目标**：QSR − 0.10×mean_age − 0.06×c_energy + 安全项；明确无硬约束，P95 为遥测 | — | A2、A3、W10 |
| IV. ROCS-0 Scheduler | age-weighted max-cost 完成 + 1-swap 改进 + 加权 refill；每 relay 独立、O(·) 复杂度 | 算法框 | A1、W2 |
| V. Branch-Credit SAC | relay set encoder + masked pooling；motion 递归信用、power 同槽效用 | Table V | A1 |
| VI. Experiments – Setup | 密封协议（100 场景×3 种子×7 方法）、配对 bootstrap、右删失、多重比较声明 | — | W4、W5、W10 |
| VI-A 主对比 | 密封 7 方法全指标 + obj + bootstrap 差值 | **Table I**、Fig 3、Fig 4 | W1 |
| VI-B 调度器对比 | 冻结主控制器框架下 ROCS-0 vs Equal/Max-CQI/PF/Max-QoS（dev 90 剧集） | **Table II** | W2、W8 |
| VI-C 消融 | 调度器：NO_AGE/NO_1SWAP（密封）；控制器：MOTION_ONLY/POWER_ONLY（dev） | **Table III** | W1、W2 |
| VI-D 逐种子稳定性 | 逐种子 obj 与 P95 | **Table IV**、Fig 6 | W1、W6 |
| VI-E 部署效率 | 参数量、CPU/GPU 时延、调度器运行时（部署数字引 CPU） | **Table V、VI** | W7 |
| VI-F 能效 | bits/J、C-UAV 航程；rotary-wing 模型引用+参数；解释总能耗相近 | **Table VII** | W9 |
| VI-G λ 选择 | (0.10,0.10) 冻结参数说明 + Pareto 表 | **Table VIII**、Fig 5 | A4、λ 决策 |
| VI-H 调度器运行时 | per-slot 运行时（部署引 CPU） | — | W7 |
| VI-I 中继负载均衡 | 跨中继 Jain（users/bh-load/power/QSR）+ per-relay 箱线 + 剧集 obj 分布（密封，零重跑） | **Table IX**、Fig 7 | 仿 TSC 参考论文 VI-D |
| VI-J 泛化 | C-UAV 位置/负载/移动速度扰动 + K=2/4/6 可扩展性（均 dev） | **Table X、Table XI** | 仿 TSC 参考论文 VI-B |
| VII. Discussion | limitations（启发式、K=4、仿真、SIC 理想化） | — | W5、W8、W10 |
| VIII. Conclusion | 目标函数口径总结 | — | A3 |
| Appendix | Joint-SAC 一句话披露；经典调度器细节；能耗参数表 | — | W3 |

---

## 3. 表格清单（Table I–X）

**Table I — 主对比（密封官方，7 方法 × 300 剧集）**
列：QSR / Avg_SQA / P5_SQA / P95_Outage_s（遥测）/ obj=QSR−0.10·age / Goodput_Mbps
来源：`results/09_FINAL_TEST100_SEALED/method_metric_summary.csv` + `analysis/sealed_final100_comparison_20261104.csv`

| 方法 | QSR | Avg_SQA | P5_SQA | P95_Outage_s | obj |
|---|---|---|---|---|---|
| **ROCS-0 + HQC-SAC (MAIN)** | **0.8043** | 0.7353 | **0.2387** | **10.10** | **0.7733** |
| NO_1SWAP | 0.8020 | 0.7122 | 0.1283 | 14.79 | 0.7478 |
| NO_AGE | 0.8073 | 0.7116 | 0.0326 | 66.24 | 0.4281 |
| TD3 | 0.7684 | 0.6884 | 0.1676 | 13.69 | 0.7221 |
| PPO | 0.7380 | 0.6502 | 0.1035 | 20.34 | 0.6613 |
| CDA | 0.7434 | 0.6714 | 0.1243 | 17.93 | 0.6757 |
| RECURSIVE_H128 | 0.7494 | 0.6758 | 0.1540 | 17.05 | 0.6900 |

配对 bootstrap（vs MAIN，n=20000，seed=0）：全部 win=1.000；NO_AGE +0.345 [0.331,0.359]；NO_1SWAP +0.025 [0.022,0.029]。

**Table II — 调度器对比（dev，冻结主控制器框架，90 剧集）**
来源：`results/02_COMMON30_VALIDATION/method_metric_summary.csv`
ROCS-0: QSR 0.8096 / P5 0.2369 / P95 10.19s / Goodput 50.75
Equal: 0.3548 / 0.0000 / 129.04s / 31.85；Max-CQI: 0.3970 / 0.0001 / 119.89s / 34.95
PF: 0.3985 / 0.0015 / 124.64s / 34.34；Max-QoS: 0.2776 / 0.0025 / 138.92s / 30.37
（Equal 的 P5=0.000 在正文解释：均分下总有份额≈0 的会话，W8）

**Table III — 消融**
调度器（密封）：NO_AGE / NO_1SWAP 行 + bootstrap 差值；控制器（dev）：MOTION_ONLY（QSR 0.7126, P95 24.69s）/ POWER_ONLY（0.5142, 48.54s）证明运动分支贡献。

**Table IV — 逐种子稳定性（W6）**
密封逐种子 obj：main / NO_1SWAP / NO_AGE = seed7 0.7643/0.7139/0.4518；seed17 0.7637/0.7503/0.3965；seed27 0.7917/0.7792/0.4361。
P95 逐种子：RECURSIVE 12.5–20.2s、TD3 seed17 16.9s、PPO seed17 25.4s。
来源：`analysis/sealed_final100_comparison_20261104.csv`（按 seed 分组）。

**Table V — 控制器复杂度（E3）**
在线（部署）参数：MAIN 123,271（motion+power）；MOTION_ONLY 61,062；POWER_ONLY 62,209；TD3 104,068；PPO 229,835；JOINT 113,763；离线 critics 另计（MAIN 242,180；总 365,451）。时延：部署引 CPU（MAIN 1.4ms）；GPU batch=1 3.9ms 注明 kernel 开销。
来源：`results/04_CONTROLLER_LATENCY/controller_latency_params.csv`。

**Table VI — 调度器运行时（E2）**
MAIN 均值 0.534ms / 最大 1.690ms per slot；经典模式 ~0.21ms。
来源：`results/05_SCHEDULER_RUNTIME/scheduler_runtime_summary.csv`。

**Table VII — 能效（E4，dev 90 剧集）**
MAIN: total 220,888J（c_phys 88,938J + m 131,950J）、bits/J 45,955、c_path 541m；TD3 41,715；CDA 40,127（465m）；PPO 38,530（796m）。
正文说明：总能耗相近=固定 200s 时长+低速 induced 主导+中继占大头；能效差异看 bits/J 与航程。
来源：`analysis/energy_summary_20261104.csv`。

**Table VIII — λ 变体（dev）**
main(0.10,0.10): QSR 0.8096 / P5 0.2369 / P95 10.19s；S040: 0.7884 / 0.2228 / **6.26s**；R005: 0.7966 / 8.33s；LS020: 0.7943 / 8.67s；R020: 0.7865 / 10.05s；no-age: 0.7527 / 69.15s。
正文：main 位于 Pareto 前沿（QSR、P5 双最优）；S040 以 −2.2pp QSR 换 P95 6.26s。
来源：`analysis/lambda_pareto.csv`。

**Table IX — 跨中继负载均衡（密封官方，7 方法，Jain 指数）**
Jain 口径：per-relay 300 剧集均值 → 跨 4 中继 Jain（`analysis/relay_load_analysis.py`）。
users Jain 全同 0.9992（挂载由 ROCS-0 加权 refill 决定，与控制器无关）；acc-load Jain 全同 0.9991（脚注提，表内略）。
bh-load Jain：MAIN 0.9632 / NO_1SWAP 0.9653 / NO_AGE 0.9813 / TD3 0.9941 / PPO 0.9780 / CDA 0.9970 / RECURSIVE 0.9640。
power Jain：**MAIN 0.8475** / 0.8809 / 0.9347 / 0.9932 / 0.9986 / 0.9963 / 0.9498——MAIN 最低=把 NOMA 回传功率集中到回程受限中继 1/2（1.95/1.57 W vs 0.76/0.71 W）。
QSR Jain：MAIN 0.9975（per-relay 0.762–0.854）；TD3 0.9997 但 per-relay 全部 ≤0.79（0.749–0.787，均匀地低）。
叙事：功率"有意失衡"换服务"保持均衡且全面占优"。
来源：`analysis/relay_boxplot.csv` + `_chart_numbers.json`（relay_load 键）。

**Table X — 泛化/鲁棒性（dev，9 条件 × 30 剧集/方法，2026-11-06 完成）**
协议：每条件 3 训练种子 × 10 评估种子 = 30 剧集/方法（冻结控制器，λ=(0.10,0.10)）。
MAIN 跨 9 条件：QSR ∈ [0.8016, 0.8538]（span 0.052）、P95 ≤ 11.19s；C-UAV 位置 3 档几乎平坦（0.833–0.835）、移动速度 3 档平坦（0.818–0.819）。
TD3：QSR ∈ [0.7543, 0.8096]（span 0.055，pos.3 掉到 0.7543/P95 18.5s）；CDA-SAC：QSR ∈ [0.6797, 0.7708]（span 0.091，pos.3 塌方 QSR 0.680/P95 26.7s）。
叙事：MAIN 对位置/负载/移动速度最鲁棒；CDA-SAC 对 C-UAV 初始位置敏感。
来源：`results/05_GENERALIZATION/generalization_all_episodes.csv` + `analysis/generalization_summary.py`（`_chart_numbers.json` "generalization" 键）。

**Table XI — 机队规模可扩展性（dev-only K 扫描，2026-11-06 完成）**
协议：MAIN 在 K=2/K=6 各从头训 1 种子（seed 7，400 EP，仅改中继数、其余冻结主配置），
与 K=4 dev 基线（seed 7）在同 30 个公共场景（9000-9029）评估。
K2: QSR 0.5466 / obj 0.1081 / P95 55.67s（欠供给塌方）；K4: 0.8056 / 0.7718 / 10.63s；
K6: 0.7959 / 0.7615 / 11.48s（+2 中继无增益，QSR −1.0pp，P95 +0.9s，goodput +0.6Mbps）。
叙事：K=4 是性价比最优点，支撑"固定 K=4"设计。
来源：`results/07_K_SCAN/*_summary.json` + `results/02_COMMON30_VALIDATION`（K=4 行）+ `_chart_numbers.json`（"k_scan" 键）。

---

## 4. 图清单

| 图 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| Fig 1 | 两层 UAV 系统模型 + 会话动态 | 系统参数 | 已定稿 `paper/figures/fig1_system.pdf` |
| Fig 2 | 不绘制（用户决定，2026-11-05） | — | — |
| Fig 3 | 训练收敛曲线（reward + 严格服务率，终值标注） | `analysis/convergence_bins.csv` | 已定稿 `paper/figures/fig3_convergence.pdf` |
| Fig 4 | 密封主结果 QSR vs obj 分组柱状图 + bootstrap CI | Table I + `_chart_numbers.json` | 已定稿 `paper/figures/fig4_mainbars.pdf` |
| Fig 5 | λ 变体 QSR–P95 Pareto 前沿阶梯线 | Table VIII（dev） | 已定稿 `paper/figures/fig5_pareto.pdf` |
| Fig 6 | 逐种子双面板点图（P95 对数 + obj 线性） | `_chart_numbers.json` | 已定稿 `paper/figures/fig6_perseed.pdf` |
| Fig 7 | 中继负载均衡三面板（per-relay QSR / 回传功率 / 剧集 obj） | `analysis/relay_boxplot.csv` + `episode_obj_dist.csv` | 已定稿 `paper/figures/fig7_relayload.pdf` |

---

## 5. 关键数字速查（写稿直接引用，不得更改）

- 密封目标代理：MAIN 0.7733；NO_1SWAP 0.7478（+0.025 [0.022,0.029]）；NO_AGE 0.4281（+0.345 [0.331,0.359]，年龄 3.79s）；TD3 0.7221；PPO 0.6613；CDA 0.6757；RECURSIVE 0.6900。
- 密封 P95 遥测：MAIN 10.10s；P5_SQA：MAIN 0.2387（NO_1SWAP 0.1283 → 1-swap 的增益在尾部）。
- 复现性：provisional vs 密封 main 逐位一致（max diff 0.000000）；工作负载 106.40 会话/场景一致；dev→sealed QSR 漂移 ≤0.006。
- 泛化（dev 90 剧集）：dev QSR 0.8096 vs 密封 0.8043。
- 能效：bits/J MAIN 45,955 > TD3 41,715 > CDA 40,127 > PPO 38,530；c_path：CDA 465m < MAIN 541m < TD3? < PPO 796m——正文措辞用"PPO 航程显著更长（796m）；CDA 航程略短但 bits/J 更低"，**勿写成"MAIN 航程最短"**（MAIN 的优势在 bits/J，不在航程）。
