# 论文修订清单（TVT 投稿版）

- 日期：2026-11-05
- 状态说明：所有支撑实验**已完成**（密封集官方统计 `results/09_FINAL_TEST100_SEALED`、E2/E3/E4），本清单只列**论文正文/图表修改项**，每项均标注"数据已就绪，待写入"。
- 依据：审稿意见 W1–W10（[PAPER_REVIEW_TVT_20261104.md](PAPER_REVIEW_TVT_20261104.md) 的后续逐条审核）+ 15s 过期指标纠正 + W3/W9 专项裁决。

---

## A. 全局口径修正（P0，优先处理）

- [ ] **A1 命名统一**：全文 HA-QCS → **ROCS-0**（age-weighted max-cost + 1-swap 实现是唯一事实来源）；旧 HA-QCS 表 IV/V 数字（QSR 82.10 等）一律不引用。
- [ ] **A2 删除 15s 硬约束表述**：当前代码无任何 T_out/15s 约束（RewardConfig 无此字段），P1 为纯奖励驱动 `age_penalized_v1`。删除"满足/违约 15s""P95 ≤ T_out"等所有硬约束措辞。
- [ ] **A3 结论改按目标函数映射**：所有方法对比结论改按奖励的服务项代理目标 **obj = QSR − 0.10×Mean_Under_Service_Age_s** 表述；P95_Outage_s 降级为尾部控制遥测 KPI（`session_longest_under_service_p95_s`），不再作为约束满足指标。
- [ ] **A4 数据口径**：主表只用 `results/09_FINAL_TEST100_SEALED` 官方数字；`08_FINAL_TEST100_PROVISIONAL` 不得引用（复现性声明中可提及 bit-identical 验证）。

---

## B. 审稿意见逐条落实（W1–W10）

- [ ] **W1（大修）种子方差被 bootstrap CI 掩盖** — 已用目标函数重新映射，无需降级结论。
  - 动作：正文所有"1-swap 增益 / 年龄项增益"结论改按 obj 表述（原 QSR 口径 main 仅 1/3 种子胜 NO_1SWAP，obj 口径 3/3 全胜）；补一张逐种子 obj 表。
  - 数据：obj 逐种子（main / NO_1SWAP / NO_AGE）= seed 7: 0.7643 / 0.7139 / 0.4518；seed 17: 0.7637 / 0.7503 / 0.3965；seed 27: 0.7917 / 0.7792 / 0.4361。NO_AGE 在真实目标下被年龄惩罚直接压垮（obj 0.4281，年龄 3.79s），其 QSR 与 main 持平是假象。
- [ ] **W2（大修）经典基线框架** — 重构为"冻结主控制器 + 经典调度器"。
  - 动作：方法节加一句"经典基线仅替换调度器，运动/功率控制与主方法完全一致，以隔离调度机制"；控制器贡献改由 **MOTION_ONLY / POWER_ONLY** 消融证明（E3 已有参数量，评估数据已就绪）。
- [ ] **W3 Joint-SAC 去留** — **决定：主文删除**（评审裁决）。
  - 理由：唯一无密封评估的方法；seed 27 发散（QSR 0.55、P95 52s）使均值掩盖双峰分布；CDA 已承担 flat-SAC 对照；密封集已按冻结协议一次性消耗，无法补入。
  - 动作：从主对比表/图例中删除 Joint-SAC 行；可选：附录一句话披露"Joint-SAC 于 seed 27 发散（QSR 0.55），未纳入密封评估；flat-SAC 控制效果由 CDA 提供"。
- [ ] **W4 密封协议披露** — 在可重现性声明中披露：密封场景在冻结前曾被 provisional 评估过一次；两次结果逐位一致（max scene diff 0.000000）；λ 选型与 Joint-SAC 去留决策只用开发场景，无选择污染。
- [ ] **W5 多重比较** — 保留 bootstrap CI，加一句声明："报告的是 per-comparison 95% bootstrap CI，未做 family-wise 校正"。
- [ ] **W6 逐种子表** — 附录补一张逐种子 P95 表预防质疑。
  - 数据：RECURSIVE P95 种子间 12.5–20.2s；TD3 seed 17 = 16.9s；PPO seed 17 = 25.4s。
- [ ] **W7 时延口径** — 部署数字引用 **CPU（1.4ms）**；GPU batch=1 的 3.9ms 在文中解释为 kernel 启动开销主导（单次小 batch 推理无并行收益），不引用为部署数字。
- [ ] **W8 Equal-share P5=0.000** — 正文解释：均分策略下总存在接入份额接近零的会话，P5 为 0 是策略属性而非 bug。
- [ ] **W9 能耗模型** — 已审计：**保留指标，不重新建模，不删除**。
  - 代码依据：`energy.py:10` rotary_wing_power（profile + 动量理论 induced + parasite 0.5·d₀·ρ·sA·v³ + 正向爬升功 m·g·Δz）；`presets.py:186` C-UAV drag_ratio=0.60（9kg 机型修复）+ 爬升功启用；`config.py:372` c_energy_weight=0.06 进入奖励（E4 用 physical_propulsion_j，不含数值正则项）——C-UAV 能耗是被优化的目标而非事后遥测。
  - 动作：正文补 rotary-wing 模型引用与参数表；解释总能耗相近的物理原因（固定 200s 时长、低速 induced 主导、K=4 中继占 ~60%）；能效差异改以 **bits/J + C-UAV 航程**呈现：main 45,955 bits/J、路径 541m vs PPO 38,530 bits/J、路径 796m（+19% 能效且飞行更少）。
- [ ] **W10 指标定义** — 方法/实验节写明：
  - P95_Outage_s = 场景内**会话级**最长连续欠服务时长的 P95 的**场景均值**；
  - 每场景约 22.2 个会话在剧集末**右删失**，写明删失处理方式（已完成会话按完成时刻统计，未完成按剧集末截断）。

---

## C. 表格更新清单

- [ ] **主对比表（密封，7 方法）**：列为 QSR / Mean_Under_Service_Age_s / obj / P95（遥测）/ 能效。密封 obj：MAIN **0.7733**（年龄 0.31s）、NO_1SWAP 0.7478、TD3 0.7221、RECURSIVE 0.6900、CDA 0.6757、PPO 0.6613、NO_AGE 0.4281（年龄 3.79s）。
- [ ] **消融表（密封 bootstrap，配对 n=20000, seed=0）**：vs main 全部 win=1.000；NO_AGE +0.345 [0.331, 0.359]；NO_1SWAP +0.025 [0.022, 0.029]。
- [ ] **逐种子表**（W6 数据，附录）。
- [ ] **E2 调度器运行时表**：main 均值 0.534ms / 最大 1.690ms per slot；经典调度器 ~0.21ms（`results/05_SCHEDULER_RUNTIME/`）。
- [ ] **E3 控制器复杂度表**：在线网络（部署）参数量：main 123,271（motion+power 分支）；离线 critics 242,180（总 365,451）；时延引 CPU 数字（`results/04_CONTROLLER_LATENCY/`）。
- [ ] **E4 能耗表**：4 方法 × bits/J / C-UAV 路径 / c_phys 占比（`analysis/energy_summary_20261104.csv`）。
- [ ] **λ 主配置选择段落**：声明 (0.10,0.10) 是此前全部对比实验所用的冻结参数，且位于 Pareto 前沿——QSR 0.810 与 P5 0.237 均为变体中最优；S040（λ_s=0.40）以 −2.2pp QSR 换取 P95 6.26s，属取舍而非支配。

---

## D. 统计与方法声明（实验节统一写入）

- [ ] 配对 bootstrap 细节：n=20,000、seed=0、按 (train_seed, eval_seed) 配对、CI=2.5/97.5 分位、win=重采样均值差 >0 的比例。
- [ ] 密封协议声明：100 场景（seeds 10000–10099）× 3 训练种子（7/17/27）× 7 方法 = 2100 剧集，方法冻结后**一次性**运行（`results/09_FINAL_TEST100_SEALED/freeze_manifest.json`）。
- [ ] 复现性声明：provisional vs 密封 main 逐位一致（max scene diff 0.000000）；工作负载跨方法一致（106.40 会话/场景）；dev→sealed 泛化 QSR 漂移 ≤0.006。
- [ ] 多重比较声明（W5）与右删失说明（W10）。

---

## E. 附录

- [ ] Joint-SAC 一句话披露（W3，可选）。
- [ ] 经典调度器实现细节（per-relay progressive_fill、需求截断、work-conserving；权重定义 Equal/Max-CQI/PF/Max-QoS）。
- [ ] 旋翼能耗模型参数表（W9）。
