# 论文修订稿写作计划（含图表制作规范）

- 日期：2026-11-05
- 上游定义：[PAPER_STRUCTURE_TABLES_MAP_20261105.md](PAPER_STRUCTURE_TABLES_MAP_20261105.md)（章节/表格/数字已冻结）
- 修订点来源：[PAPER_REVISION_CHECKLIST_20261105.md](PAPER_REVISION_CHECKLIST_20261105.md)
- 交付目录：`paper/`（修订稿 + LaTeX 表格片段 + 图 PDF/PNG）

## 工作流（5 阶段，含审核门）

| 阶段 | 内容 | 产出 | 审核门 |
|---|---|---|---|
| 0 | PDF 提取与素材调研 | 可读原文参考文本；现有图资产盘点 | — |
| 1 | 骨架 | `paper/manuscript.md`：全部章节标题 + 8 表 5 图占位 + 冻结数字声明块 | Gate 0：确认骨架 |
| 2 | 逐节撰写（7 个 gate） | 各节正文 + 引用的表格数字 | 每 gate 用户审阅 |
| 3 | IEEE 风格图表制作 | 表格 LaTeX 片段；图 PDF/PNG | Gate 8：图表审阅 |
| 4 | 一致性核对与打包 | 清单勾对表；paper/ 交付包 | Gate 9：终审 |

### 阶段 2 的 7 个审核门（每门通过才进下一门）

1. Title / Abstract / Introduction
2. System Model / Problem Formulation（奖励驱动 P1，无硬约束）
3. ROCS-0 Scheduler / Branch-Credit SAC（方法）
4. Experiment Setup + 主对比（Table I）
5. 调度器对比 + 消融 + 逐种子（Table II–IV）
6. 部署效率 + 能效 + λ 选择（Table V–VIII）
7. Discussion / Conclusion / Appendix

## 图表设计规范（IEEE 风格）

### 表格（LaTeX booktabs）
- 三线式：仅 `\toprule / \midrule / \bottomrule`，**无竖线**；表头下可加单位行。
- 数字右对齐、小数位统一（QSR 4 位、P95 2 位、能量整数）；每列**最佳值加粗**（obj 口径最佳=MAIN）。
- 脚注（`\tablenotemark` 或表下小字）：P95_Outage 注明"telemetry KPI, not a constraint"；bootstrap CI 行注明配对方法与 n；Table II 注明 dev 集 90 剧集、冻结控制器框架。
- 单栏表宽 ≤3.5in，双栏 ≤7.16in；表注 8pt。

### 图（matplotlib + IEEE 样式）
- 尺寸：单栏 3.5in / 双栏 7.16in；图内字体 **Helvetica 7–9pt**；正文 Times 兼容。
- 线宽 ≥0.75pt；数据线 1.2pt；网格仅主轴、淡灰虚线；无 chartjunk、无 3D。
- 配色（色盲安全 Okabe-Ito）：蓝 #0072B2、橙红 #D55E00、青绿 #009E73、紫 #CC79A7、黄 #E69F00、天蓝 #56B4E9；灰阶兼容（线型+标记双编码）。
- 坐标轴：单位入轴标（如 `P95 outage (s)`）；Pareto 图标注 "upper-left better" 方向箭头；CI 用阴影带。
- 输出：**PDF 矢量 + 600 dpi PNG**；图注 8pt、可独立理解（不依赖正文）。

### 图清单与数据/工具
| 图 | 内容 | 数据 | 工具 |
|---|---|---|---|
| Fig 1 | 两层 UAV 系统模型 + 会话动态（框图） | 系统参数 | matplotlib 矢量绘制 |
| Fig 2 | 框架：环境 / branch-credit 控制器 / ROCS-0 / 反馈 | 已有 `fig2_framework_publication.pdf` | 核对组件名=ROCS-0 |
| Fig 3 | 训练收敛曲线（3 种子奖励/服务） | `runs/` 训练日志 | matplotlib |
| Fig 4 | QSR–P95 Pareto 散点（λ 变体，标 main） | `analysis/lambda_pareto.csv` | matplotlib |
| Fig 5 | 逐种子 P95 分布（W6 佐证） | sealed 逐种子数据 | matplotlib（可选） |

## 执行约定
- 所有数字只从冻结的速查表取，不改动；措辞按速查表"易错措辞"备注执行。
- 每完成一个 gate 停下交你审阅；你说"继续"才进下一个。
