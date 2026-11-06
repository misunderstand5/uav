# [TITLE] — 修订稿骨架（Gate 0 待确认）

> 状态：骨架。正文逐节撰写中，数字已冻结（见文末冻结数字块）。
> 目标期刊：IEEE Transactions on Vehicular Technology。全文 ROCS-0 命名（A1）；无 15s 硬约束表述（A2）；结论按 obj 口径（A3）；主表只用 09 密封数据（A4）。

## Title（待定稿，Gate 1）
Resilient Minimum-QoS Scheduling and Branch-Credit Learning for Two-Tier UAV Networks

## Abstract（占位，Gate 1）
- 场景：应急/车载临时覆盖，两层 UAV，动态高负载，最小速率保障。
- 问题：连续欠服务尾部；奖励驱动目标 QSR − λ·age − 能耗 + 安全。
- 方法：ROCS-0 调度器 + branch-credit SAC 控制器。
- 数字（冻结）：密封 2100 剧集；obj 0.7733；P95 遥测 10.10s；CPU 1.4ms；调度器 0.534ms/slot；bits/J 45,955。

## I. Introduction（Gate 1）
- 背景/动机（应急 framing）、3 条贡献（每条 2–3 行 + 一个数字）、设计 insight。
- 数字引用：Table I、Table V、Table VI。

## II. System Model（Gate 2）
- 两层 UAV：C-UAV（NOMA 回传 20MHz/5W）→ K=4 M-UAV（正交接入 5MHz/1W）→ 动态 GU 会话。
- R_min ∈ {0.7, 2.0, 2.5} Mbit/s；200s 剧集；到达/离开/移动模型。
- Fig 1（系统模型图，阶段 3 制作）。

## III. Problem Formulation（Gate 2）
- **奖励驱动目标（无硬约束）**：per-slot r_n = QSR_n − 0.10·mean_age_n − 0.06·c_energy_n + 安全项（加速度/高度）；M-UAV 能耗为 KPI（V20.52R R1）。
- P95_Outage_s 定位：遥测 KPI，非约束（A2/A3/W10）。
- 指标定义（W10）：P95 = 场景内会话级 P95 的场景均值；右删失处理。

## IV. ROCS-0 Scheduler（Gate 3）
- age-weighted max-cost 完成（w_i = 1 + λ(O_i + Δt)）+ best-improvement 1-swap + 加权 refill；每 relay 独立 2-D 资源约束。
- 算法框 + 复杂度（引用 Table VI：0.534ms/slot）。

## V. Branch-Credit SAC Controller（Gate 3）
- relay set encoder + masked pooling；motion 分支递归信用（长时程）、power 分支同槽效用（短时程）。
- 参数量/时延引用 Table V（CPU 1.4ms；W7）。
- 框架图不单独绘制（用户决定）；系统示意仅 Fig 1。

## VI. Experiments（Gate 4–6）
### VI-A Setup（Gate 4）
- 密封协议：100 场景 × 3 种子 × 7 方法 = 2100 剧集，冻结后一次性运行（W4）；配对 bootstrap（n=20000, seed=0）；多重比较声明（W5）；右删失（W10）；复现性（bit-identical）。
### VI-B 主对比（Gate 4）— Table I + Fig 3（收敛）+ Fig 4（QSR vs obj 主柱图）
### VI-C 调度器对比（Gate 5）— Table II（冻结控制器框架，W2/W8）
### VI-D 消融（Gate 5）— Table III（NO_AGE/NO_1SWAP 密封 + MOTION_ONLY/POWER_ONLY dev）
### VI-E 逐种子稳定性（Gate 5）— Table IV + Fig 6（逐种子点图，W6）
### VI-F 部署效率（Gate 6）— Table V + Table VI（W7 CPU 口径）
### VI-G 能效（Gate 6）— Table VII（W9：rotary-wing 引用 + bits/J/航程）
### VI-H λ 选择（Gate 6）— Table VIII + Fig 5（Pareto）
### VI-I 中继负载均衡（Gate 6）— Table IX（跨中继 Jain）+ Fig 7（per-relay QSR/功率 + 剧集 obj 分布，密封零重跑，仿 TSC 参考论文 VI-D）
### VI-J 泛化/鲁棒性（Gate 6）— Table X（C-UAV 位置/负载/移动速度扰动，dev 标注）+ Table XI（K=2/4/6 可扩展性，dev-only 扫描）

## VII. Discussion / Limitations（Gate 7）
- 启发式无最优性保证、固定 K=4、仿真无实测、SIC 理想化；W5/W8/W10 解释句。

## VIII. Conclusion（Gate 7）

## Appendix（Gate 7）
- A：Joint-SAC 一句话披露（W3，可选）。
- B：经典调度器实现细节。
- C：旋翼能耗模型参数表（W9）。

---

## 表格占位（冻结数字，阶段 3 转 LaTeX）

### Table I — 主对比（密封官方，7 方法 × 300 剧集）
来源：`results/09_FINAL_TEST100_SEALED/method_metric_summary.csv` + `analysis/sealed_final100_comparison_20261104.csv`

| 方法 | QSR | Avg_SQA | P5_SQA | P95_Outage_s（遥测） | obj | Goodput_Mbps |
|---|---|---|---|---|---|---|
| **ROCS-0 + HQC-SAC (MAIN)** | **0.8043** | 0.7353 | **0.2387** | **10.10** | **0.7733** | 50.93 |
| NO_1SWAP | 0.8020 | 0.7122 | 0.1283 | 14.79 | 0.7478 | 49.96 |
| NO_AGE | 0.8073 | 0.7116 | 0.0326 | 66.24 | 0.4281 | 50.53 |
| TD3 | 0.7684 | 0.6884 | 0.1676 | 13.69 | 0.7221 | 47.01 |
| PPO | 0.7380 | 0.6502 | 0.1035 | 20.34 | 0.6613 | 43.53 |
| CDA | 0.7434 | 0.6714 | 0.1243 | 17.93 | 0.6757 | 45.17 |
| RECURSIVE_H128 | 0.7494 | 0.6758 | 0.1540 | 17.05 | 0.6900 | 45.64 |

Bootstrap vs MAIN（配对 n=20000, seed=0）：全部 win=1.000；NO_AGE +0.345 [0.331,0.359]；NO_1SWAP +0.025 [0.022,0.029]。

### Table II — 调度器对比（dev 90 剧集，冻结主控制器）
ROCS-0: QSR 0.8096 / P5 0.2369 / P95 10.19s / Goodput 50.75
Equal: 0.3548 / 0.0000 / 129.04s / 31.85；Max-CQI: 0.3970 / 0.0001 / 119.89s / 34.95
PF: 0.3985 / 0.0015 / 124.64s / 34.34；Max-QoS: 0.2776 / 0.0025 / 138.92s / 30.37

### Table III — 消融
调度器（密封）：NO_AGE / NO_1SWAP 行（同 Table I）+ bootstrap 差值。
控制器（dev）：MOTION_ONLY（QSR 0.7126 / P95 24.69s）；POWER_ONLY（0.5142 / 48.54s）。

### Table IV — 逐种子（密封）
obj：main / NO_1SWAP / NO_AGE = seed7 0.7643/0.7139/0.4518；seed17 0.7637/0.7503/0.3965；seed27 0.7917/0.7792/0.4361。
P95：RECURSIVE 12.5–20.2s；TD3 seed17 16.9s；PPO seed17 25.4s。

### Table V — 控制器复杂度（E3）
在线（部署）：MAIN 123,271；MOTION_ONLY 61,062；POWER_ONLY 62,209；TD3 104,068；PPO 229,835；JOINT 113,763。
离线 critics：MAIN 242,180（总 365,451）。时延：CPU 1.4ms（部署口径）；GPU batch=1 3.9ms（kernel 开销）。

### Table VI — 调度器运行时（E2）
MAIN 均值 0.534ms / 最大 1.690ms per slot；经典模式 ~0.21ms。

### Table VII — 能效（E4，dev 90 剧集）
MAIN: total 220,888J（c_phys 88,938J + m 131,950J）/ bits/J 45,955 / c_path 541m
TD3 41,715；CDA 40,127（465m）；PPO 38,530（796m）。

### Table VIII — λ 变体（dev）
main: QSR 0.8096 / P5 0.2369 / P95 10.19s；S040: 0.7884 / 0.2228 / **6.26s**；R005: 0.7966 / 8.33s；LS020: 0.7943 / 8.67s；R020: 0.7865 / 10.05s；no-age: 0.7527 / 69.15s。

## 图占位（均已制作，见 `paper/figures/FIGURE_DESIGN_SPEC.md`）
- Fig 1：系统模型（`paper/figures/fig1_system.pdf`）
- Fig 2：不绘制（用户决定）
- Fig 3：收敛曲线（`paper/figures/fig3_convergence.pdf`，数据 `analysis/convergence_bins.csv`）
- Fig 4：主结果 QSR vs obj 分组柱状图 + bootstrap CI（`paper/figures/fig4_mainbars.pdf`）
- Fig 5：λ 变体 QSR–P95 Pareto 前沿（`paper/figures/fig5_pareto.pdf`）
- Fig 6：逐种子双面板点图（`paper/figures/fig6_perseed.pdf`）
- Fig 7：中继负载均衡三面板箱线图（`paper/figures/fig7_relayload.pdf`，数据 `analysis/relay_boxplot.csv` + `episode_obj_dist.csv`）

---

## 冻结数字块（起草专用，禁止改动）

- obj 密封：MAIN 0.7733 / NO_1SWAP 0.7478 / NO_AGE 0.4281 / TD3 0.7221 / PPO 0.6613 / CDA 0.6757 / RECURSIVE 0.6900
- NO_AGE 年龄 3.79s；bootstrap：NO_AGE +0.345 [0.331,0.359]，NO_1SWAP +0.025 [0.022,0.029]，win=1.000
- 复现性：provisional vs 密封 main max diff 0.000000；工作负载 106.40 会话/场景；dev→sealed QSR 漂移 ≤0.006（0.8096→0.8043）
- 措辞红线：CDA 航程 465m 短于 MAIN 541m → 不写"MAIN 航程最短"；不出现"15s 预算/违约/满足约束"；P95 一律标注"telemetry"
