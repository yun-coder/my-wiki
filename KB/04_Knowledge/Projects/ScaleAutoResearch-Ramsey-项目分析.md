---
created: 2026-05-11
tags: #项目分析 #AI科研 #数学 #Ramsey数 #自主研究 #Claude
source: "ScaleAutoResearch-Ramsey"
source_url: https://github.com/ypwang61/ScaleAutoResearch-Ramsey
author: Yiping Wang (Amazon AI PhD Fellow)
publish_date: 2026-05-07
---

# ScaleAutoResearch-Ramsey 项目分析

## 摘要
> 用 Claude Code 大规模并行自主研究，打破了保持 32 年的 Ramsey 数 R(3,17) 下界纪录。

## 项目概况

| 项 | 内容 |
|---|---|
| **仓库** | https://github.com/ypwang61/ScaleAutoResearch-Ramsey |
| **作者** | Yiping Wang（Amazon AI PhD Fellow） |
| **语言** | Jupyter Notebook + Python/Go |
| **协议** | Apache-2.0 |
| **创建** | 2026-05-07 |

## 核心成果

| 成果 | 内容 | 意义 |
|---|---|---|
| **R(3,17) ≥ 93** | 🏆 新世界纪录 | 打破 Wang-Wang-Yan 1994 的 R(3,17) ≥ 92，保持 32 年。AlphaEvolve (2026) 也只追平旧纪录 |
| **R(4,15) ≥ 160** | 改进 AlphaEvolve | 进一步推进 R(4,15) ≥ 159 |
| 非同构见证 | 发现第二个 n=91 的 α=16 无三角形图 | 不同于经典 Wang Z_91 循环图 |

### Ramsey 数背景

Ramsey 数 R(r,s)：至少 n 个人中，必然存在 r 人互相认识或 s 人互不认识。R(3,17) ≥ 93 意味着存在 92 个顶点的图，既无三角形也无 17-独立集。

## 方法论：ScaleAutoResearch

### 核心思路

```
传统数学研究：  人类数学家 → 思考 → 证明 → 论文（数月~数年）
AlphaEvolve：   演化搜索 + LLM 引导（需要定制算法设计）
本项目：         Claude Code/Codex × N 并行 + 简单实验脚手架
```

### 关键要素

1. **大量并行 Agent** — 同时运行多个 Claude Code / Codex 自主研究 session
2. **统一实验脚手架** — 每个 Agent 共享：
   - 只读验证器（verify.py，黄金标准）
   - 初始程序 + 参考材料
   - program.md（指令文件：让 Agent 无限迭代）
   - results.tsv（机器可读结果）+ record.md（人类可读进展）
3. **按宽度+深度缩放** — 更多并行 Agent（宽度）+ 更长运行时间（深度）
4. **进展共享** — 更强的 Agent 通过 GitHub branches 共享中间结果
5. **人类介入极简** — 启动 Agent、监控进展、偶尔调整方向

### 灵感来源

- autoresearch: [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- Google DeepMind [AlphaEvolve](https://arxiv.org/abs/2603.09172)
- [ThetaEvolve](https://github.com/ypwang61/ThetaEvolve)

## 搜索过程：R(3,17) 的 12 级突破

### Phase 1-4：Cayley 图 + SA 搜索（~4天，全部卡住）

尝试了 18 种算法变体（SA、Cayley 图、GA 交叉、Ghost Vertex 等），全部卡在 α=18 的"地板"。

### Phase 5：范式转换

**关键翻转：** 从"消灭三角形"翻转为"消灭独立集"
- 起点：一个满足 α ≤ 16（无独立集冲突）但有 12 个三角形的图
- 新策略：compound_drop_repair — 删三角形边 → 修复新产生的独立集

### Phase 6-9：连续突破（约 9 小时）

```
冲突数    关键突破
12  →    compound_drop_repair 新范式首次生效
11  →    并行搜索继续推进
10  →    同日突破
 9  →    结构分析发现 hub 顶点聚集
 8  →    关键洞察：多步 compound 链穿越高冲突瞬态
 7  →    同一 "magic formula" 再次生效
 6  →    off-hub 新三角形出现 → 真正逃出局部最优
 5  →    加速突破
4-3 →    短窗口内连续突破
 2  →    短窗口内
 1  →    短窗口内
 0  →    🏆 R(3,17) ≥ 93 SOTA!
```

### "Magic Formula"

核心算法是 `compound_drop_repair` 的一组调优超参数 `(keep_uphill, beam, random_keep, repair_top, drop_sample)`：
- `keep_uphill` 允许 LONG compound 链（5 步，瞬态冲突数百）
- 与 h_walk 的绝对 bound 不同，cdr 的 `keep_uphill` 是相对于当前状态的加性值
- 同一组参数打破了从 12 到 0 的所有层级

### SOTA 见证属性

- n = 92 顶点，727 条边
- α = 16（无 17-独立集）
- 0 个三角形（triangle-free）
- 度数 min/max/avg = 15/16/15.80（接近 16-正则）

## 与其他 AI 数学研究的对比

| 方法 | 代表 | R(3,17) 结果 | 方法复杂度 |
|---|---|---|---|
| 人类数学家 | Wang-Wang-Yan 1994 | ≥ 92（保持 32 年） | 人工构造 |
| AlphaEvolve | Google DeepMind 2026 | ≥ 92（追平） | 定制演化框架 |
| **ScaleAutoResearch** | **Yiping Wang 2026** | **≥ 93（突破！）** | **Claude Code + 简单脚手架** |

## 技术评价

### 亮点
- 32 年数学纪录被打破，硬核科学成就
- 方法论极简：Claude Code + 简单脚手架 + 大量并行
- 实验记录极其透明：完整记录每次失败和突破
- AlphaEvolve 对比：更简单的方法达到更好结果
- 一个人 + AI 完成的工作

### 局限
- "magic formula" 超参数是经验性的，不同问题可能需要不同调参
- 搜索成本高：需要大量 Claude Code API 调用（数天并行运行）
- 问题特殊性：Ramsey 数有明确验证器（多项式可验证），最适合 AI 自主研究
- 泛化性未验证：目前只在 Ramsey 数上验证

## 更广泛的意义

> **ScaleAutoResearch** 展示了一种新的科学研究范式：用大量 AI Agent 并行执行自主研究，用可验证的 oracle 作为进度度量，通过宽度（更多 Agent）和深度（更长运行）来缩放，最终突破人类长期未能解决的开放问题。

这不是第一个也不是最后一个，但可能是最"极简"的一次——没有定制演化框架，没有复杂的基础设施，就是 Claude Code + 并行。

## 相关资源
- [[Intentional Updates for Streaming RL]] — 同为 2026 年的新工作，展示了 AI 在优化理论中的进展
- [AlphaEvolve 论文](https://arxiv.org/abs/2603.09172) — DeepMind 的相关工作
- [Karpathy autoresearch](https://github.com/karpathy/autoresearch) — 灵感来源

## 引用

```bibtex
@software{scaleautoresearch_ramsey_2026,
  title  = {ScaleAutoResearch-Ramsey},
  author = {Wang, Yiping},
  year   = {2026},
  url    = {https://github.com/ypwang61/ScaleAutoResearch-Ramsey},
  note   = {Verified graph witnesses for new lower bounds on classical Ramsey numbers}
}
```

---
*捕获自: https://github.com/ypwang61/ScaleAutoResearch-Ramsey*
