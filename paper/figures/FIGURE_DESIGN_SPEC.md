# 实验图设计规范（IEEE TVT 风格）

> 状态：2026-11-05 定稿，2026-11-06 增补 Fig. 7（VI-I 中继负载均衡）。
> 框架图（原 Fig. 2）按用户要求不绘制。
> 图编号已重排：Fig. 3 收敛 → Fig. 4 主结果 → Fig. 5 λ-Pareto → Fig. 6 逐种子 → Fig. 7 中继负载均衡。
> 所有数据取自密封 final-100（`results/09_FINAL_TEST100_SEALED`）与冻结 dev 集；
> 数字与 `paper/tables/*.tex`、`paper/tables/_chart_numbers.json` 一致，禁止手改。

## 通用规范

| 项目 | 规格 |
|---|---|
| 字体 | Arial，轴标签 7pt，刻度 6.5pt，图例 6.5pt，标注 6–6.5pt |
| 线宽 | 轴线/刻度 0.6pt，曲线 1.2–1.3pt，网格 0.4pt 虚线 alpha 0.35 |
| 配色 | Okabe-Ito 色盲安全：BLUE #0072B2、ORANGE #D55E00、GREEN #009E73、PURPLE #CC79A7、SKY #56B4E9、GRAY #808080 |
| 输出 | PDF（矢量，fonttype 42）+ PNG 600dpi，`bbox_inches=tight` |
| 尺寸 | 单列 3.5in（fig5/fig6），双列 7.16in（fig3/fig4） |
| 网格 | 仅坐标轴方向网格线，无上/右边框线（`ieee_style.apply_style()`） |

## Fig. 3 — 训练收敛曲线（双列，2 面板并排）

- **图表类型**：均值线 + min–max 阴影的时序曲线（每 50 episode 分箱，3 种子 × 400 episodes）。
- **面板**：(a) per-slot reward；(b) strict-QoS service ratio（严格服务比例）。
- **配色语义**：BLUE=Proposed、ORANGE=CDA-SAC (flat)、GREEN=Recursive-credit H128——与后文图保持一致。
- **设计细节**：
  - 阴影 = 同色 alpha 0.12，展示种子间离散度；
  - 右缘终值标注（同色加粗，如 "130.6"），xlim 0–400；
  - 图例位于 (a) 右下方，无边框。
- **叙事**：三法均 100 集内收敛；Proposed 奖励与严格服务率全程最高。

## Fig. 4 — 密封主结果分组柱状图（双列，核心证据图）

- **图表类型**：分组柱状图（每方法 2 根：QSR 浅色 + obj 深色），obj 柱带 95% bootstrap CI 须线。
- **数据**：Table I 密封集（7 方法 × 300 episodes）；obj CI 为配对 bootstrap（按训练种子+场景配对）。
- **排序**：按 obj 降序（Proposed → w/o 1-swap → TD3 → Recursive → CDA-SAC → PPO → w/o age）。
- **配色语义**：Proposed obj 柱 BLUE、QSR 柱 SKY；其余方法 obj 柱 GRAY、QSR 柱 #D9D9D9；须线黑色 0.9pt、capsize 2.2。
- **数值标注**：QSR 值灰色 6pt 标于柱顶；obj 值深色加粗 6.5pt 标于须线之上（避免与须线相交）。
- **图例**：左上角三色块（QSR / obj-proposed / obj-others）；右上角注 "whiskers: 95% bootstrap CI of obj"。
- **点睛注释**："QSR alone misleads: high ratio, lowest obj" 引线指向 w/o age 组。
- **叙事**：w/o age 的 QSR 最高（0.807）但 obj 最低（0.428）——单一 QSR 会得出错误结论；obj 才是论文指标。

## Fig. 5 — λ 权重 Pareto 前沿（单列，散点 + 阶梯线）

- **图表类型**：散点图（x=QSR 越高越好，y=P95 outage 越低越好）+ Pareto 前沿阶梯线。
- **数据**：dev 集 90 episodes，6 个 λ 配置（Table VIII 对应）。
- **标记编码**：前沿点实心（main 为 BLUE 星形，其余 GRAY 实心圆）；被支配点空心圆（白底灰边）；no-age 特例空心橙边圆。
- **前沿阶梯线**：steps-post 灰虚线穿过 S 形折线 (0.10,0.40)→(0.05,0.20)→main(0.10,0.10)。
- **标签**：手动偏移放置（下/上/左/右），配置名用 `(λ_age, λ_s)` 元组与 Table VIII 一致；main 两行标注。
- **方向箭头**：右下角 "better" 箭头指向右下（QSR 高 + P95 低），与轴标注一致。
- **xlim** (0.742, 0.818)，ylim (0, 75)，x 步长 0.01、y 步长 10。
- **叙事**：main 在 Pareto 前沿上（QSR 最优，P95 10.19s）；(0.10,0.40) 以 2.2pp QSR 换 6.26s 尾巴；no-age 完全塌方 (69.15s)。

## Fig. 6 — 逐种子稳定性（单列，双面板堆叠）

- **图表类型**：横向点图（Cleveland dot plot）。
- **面板 (a)**：P95 outage，x 对数轴 (6–100s)，7 方法 × 3 种子（Table IV 补充 CDA-SAC 行后 7 行）。
- **面板 (b)**：obj，x 线性轴 (0.35–0.85)，3 个调度器消融（Proposed / w/o 1-swap / w/o age），均值上方标数值（0.773 / 0.748 / 0.428）。
- **行排序**：(a) 按均值 P95 升序自顶向下（最好的在最上）；(b) Proposed 在最上。
- **种子配色**：Seed 7 SKY、Seed 17 ORANGE、Seed 27 PURPLE（与图 3 的方法色区分——本图内颜色只表种子）。
- **均值标记**：空心菱形（黑边、透明面、markeredgewidth 1.0）——透明面保证与种子点重合时下层点仍可见（w/o age 行 seed 7 与均值几乎重合，实心/白面都会遮挡）。
- **Proposed 行高亮**：BLUE alpha 0.07 行底纹 + 加粗行名。
- **图例**：面板 (a) 左下角，2×2（Seed 7/17/27 + Mean）。
- **叙事**：Proposed 三种子 obj 全部最高且 P95 全部 <12s；TD3/PPO 种子敏感（PPO seed17 P95 25.4s）。

## Fig. 7 — 中继负载均衡（单列，三面板堆叠）

- **图表类型**：分组箱线图（面板 a/b）+ 横向箱线图（面板 c）。
- **数据**：密封集 relay_slots.csv 每剧集每中继聚合（`analysis/relay_boxplot.csv`，8400 行 = 7 方法 × 300 剧集 × 4 中继）+ 剧集级 obj（`analysis/episode_obj_dist.csv`）。
- **面板 (a)**：per-relay QSR，Proposed（BLUE）vs TD3（ORANGE），ylim (0.60, 1.02)；Proposed 在 4 个中继上全面高于 TD3（0.76–0.85 vs 0.75–0.79），中继 3/4 有下侧离群点（低 QSR 剧集）。
- **面板 (b)**：C-UAV NOMA 回传功率分配，Proposed vs TD3 vs w/o age（GRAY），ylim (0.2, 3.7)；Proposed 把功率集中到回程受限的中继 1/2（中位 2.0/1.6 W vs 中继 3/4 的 0.7/0.6 W），TD3 近似均匀（1.1–1.3 W）；上侧长尾离群点 = 突发拥塞剧集（最高 3.07 W，故 ylim 留头部空间，图例置于右上 3.2–3.7 空区）。
- **面板 (c)**：剧集级 obj 分布，7 方法按均值升序自底向上（Proposed 顶部，BLUE 加粗），其余 GRAY alpha 0.45；右缘标均值（0.773 / 0.748 / 0.722 / 0.690 / 0.676 / 0.661 / 0.428）。
- **图例**：面板 (a) 右上 2 项（白底防压箱体），面板 (b) 右上 3 项（ylim 头部空区，无边框）；面板 (c) 无图例（蓝色 = Proposed 高亮，轴标签已列名）。
- **叙事**：挂载均衡（users Jain 全同 0.9992，ROCS-0 结构性质）→ 功率按需倾斜（power Jain 0.85 vs 基线 ≥0.93）→ 服务仍均衡（QSR Jain 0.9975）且每中继全面占优；对应 Table IX。

## 文件清单

```
paper/figures/ieee_style.py        # 共享样式（字体/线宽/配色/保存）
paper/figures/fig1_system.py       # 系统示意图（此前已定稿，未改动）
paper/figures/fig3_convergence.py  # 数据源 analysis/convergence_bins.csv
paper/figures/fig4_mainbars.py     # 数据源 paper/tables/_chart_numbers.json (obj_ci) + Table I
paper/figures/fig5_pareto.py       # 数据源 Table VIII（dev λ 变体）
paper/figures/fig6_perseed.py      # 数据源 paper/tables/_chart_numbers.json (per_seed, obj_ci)
paper/figures/fig7_relayload.py    # 数据源 analysis/relay_boxplot.csv + episode_obj_dist.csv
```

## 与表格的分工（避免重复感）

- Table I 给全指标精确数字；Fig. 4 给 QSR-vs-obj 的视觉对比 + CI 视觉化（表内无 CI 图）。
- Table IV 给逐种子数字；Fig. 6 给种子离散度的直观分布。
- Table VIII 给 λ 全指标；Fig. 5 给 Pareto 几何关系（表内无法表达的 trade-off 结构）。
- Table IX 给跨中继 Jain 指数精确值；Fig. 7 给 per-relay 分布形状与剧集级离散度（表内无法表达的分布与长尾）。
- Fig. 3 为训练动态，无对应表格。
