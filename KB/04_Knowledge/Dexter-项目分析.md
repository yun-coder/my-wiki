# Dexter 项目分析

> **项目信息**
> - 名称: Dexter
> - 仓库: https://github.com/virattt/dexter
> - 作者: @virattt
> - 版本: 2026.5.2 (CalVer)
> - 许可: MIT
> - 定位: "Think Claude Code, but built specifically for financial research"
> - 社区: Twitter @virattt + Discord

---

## 📖 一、项目定位

**Dexter** 是一个**终端内运行的自主金融研究 Agent**。它接收复杂金融问题，自动分解为研究步骤，调用实时市场数据工具，自我验证，迭代优化，最终输出数据支撑的结论。

> "I don't make small talk about volatility. I'm a researcher who thinks." — Dexter's SOUL

### 核心理念
- 巴菲特 + 芒格投资哲学为根基
- 先收集数据，再形成观点（而非相反）
- DCF 估值给出的是**范围**而非单点数字
- 智力诚实：不懂就说不懂

---

## 🏗️ 二、技术架构

### 技术栈
```
┌─────────────────────────────────────────────────┐
│               CLI 界面 (Ink/React)               │
│  Ink TUI 组件 · 多模型切换 · 实时事件流          │
├─────────────────────────────────────────────────┤
│               Agent 核心引擎                     │
│  迭代工具调用循环 · 上下文压缩 · Scratchpad      │
├──────────┬──────────┬──────────┬────────────────┤
│ LLM 层    │ 工具层    │ 技能层    │ 数据层         │
│ 6 提供商  │ 金融+搜索 │ SKILL.md │ 内存/嵌入/搜索  │
└──────────┴──────────┴──────────┴────────────────┘
```

| 层 | 技术 | 说明 |
|----|------|------|
| **运行时** | Bun | 核心运行时，替代 Node.js |
| **CLI 界面** | Ink (React for CLI) | 终端内 React 组件渲染 |
| **AI 框架** | LangChain | LLM 抽象、工具绑定 |
| **语言** | TypeScript (strict) | 全量类型安全 |
| **测试** | Bun test + Jest | 双测试框架 |
| **评估** | LangSmith | LLM-as-Judge 评估 |
| **浏览器** | Playwright | 网页抓取 |

---

## 🤖 三、LLM 集成（6 种提供商）

```typescript
// 默认模型: gpt-5.4
// 提供商检测基于前缀:
//   claude-*    → Anthropic
//   gemini-*    → Google
//   gpt-*       → OpenAI
//   grok-*      → xAI
//   openrouter/*→ OpenRouter
//   ollama/*    → 本地 Ollama
```

| 提供商 | 说明 |
|--------|------|
| **OpenAI** | 默认，gpt-5.4 |
| **Anthropic** | Claude，支持 cache_control 提示缓存 |
| **Google** | Gemini |
| **xAI** | Grok |
| **OpenRouter** | 100+ 模型统一网关 |
| **Ollama** | 本地运行（`OLLAMA_BASE_URL` 配置） |

---

## 🔧 四、工具系统

### 金融工具
| 工具 | 功能 | 数据源 |
|------|------|--------|
| `get_financials` | 综合财务数据查询 | financialdatasets.ai |
| `get_market_data` | 实时行情 | financialdatasets.ai |
| `read_filings` | SEC 文件阅读（10-K/10-Q/8-K） | SEC EDGAR |
| `screen_stocks` | 股票筛选 | financialdatasets.ai |
| `get_income_statements` | 利润表 | financialdatasets.ai |
| `get_balance_sheets` | 资产负债表 | financialdatasets.ai |
| `get_cash_flow_statements` | 现金流量表 | financialdatasets.ai |
| `get_key_ratios` | 关键比率 | financialdatasets.ai |
| `get_analyst_estimates` | 分析师预测 | financialdatasets.ai |
| `get_insider_trades` | 内部交易 | financialdatasets.ai |
| `get_earnings` | 财报数据 | financialdatasets.ai |
| `get_segments` | 业务分部 | financialdatasets.ai |
| `get_stock_price` | 股价 | financialdatasets.ai |
| `get_crypto_price` | 加密货币价格 | financialdatasets.ai |

### 搜索工具
| 工具 | 说明 |
|------|------|
| `web_search` | Exa（优先）/ Tavily（fallback） |
| `x_search` | X/Twitter 搜索 |
| `browser` | Playwright 网页抓取 |

### 文件系统工具
| 工具 | 说明 |
|------|------|
| `read_file` | 读取文件 |
| `write_file` | 写入文件 |
| `edit_file` | 编辑文件（基于 diff） |

### 内存工具
| 工具 | 说明 |
|------|------|
| `memory_search` | 语义搜索记忆 |
| `memory_get` | 精确读取记忆 |
| `memory_update` | 更新记忆 |

---

## 🧠 五、Agent 核心架构

### Agent 循环
```
用户问题 → 系统提示构建 → LLM 推理（流式）
  → 工具调用检测 → 并发执行只读工具 → 结果回注
  → 微压缩（每轮）→ Token 超阈值？→ 全量压缩
  → 继续迭代 → 达到最大轮次或结束信号 → 最终答案生成
```

### 关键设计

| 机制 | 说明 |
|------|------|
| **Scratchpad** | 单一致信源，所有工具结果持久化，每个查询一个 `.jsonl` |
| **微压缩 (Microcompact)** | 每轮压缩工具结果，保留关键数据 |
| **全量压缩 (Compact)** | Token 超阈值时按重要性清理上下文 |
| **并发执行** | 只读工具并发调用，提升速度 |
| **最终答案** | 独立 LLM 调用（不绑定工具），用完整 scratchpad 生成 |
| **安全限制** | 最大 10 轮迭代 + 循环检测 + 溢出重试 |

### 上下文管理
```
Anthropic 风格上下文管理：
├── 完整工具结果保留在上下文
├── 超过阈值时清理最旧结果
├── 保留最近 K 轮的工具结果
└── 最终答案阶段使用单独 LLM 调用
```

---

## 📚 六、技能系统（Skills）

Dexter 有内置的 **SKILL.md 技能系统**——和 OpenClaw 的 skills 概念一致：

### 内置技能

#### DCF 估值 (`dcf-valuation`)
8 步完整 DCF 估值流程：
```
1. 收集财务数据（FCF、资产负债表、分析师预测、当前价格）
2. 计算 FCF 增长率（CAGR，交叉验证，上限 15%）
3. 估算 WACC（根据行业选择基准范围）
4. 预测未来现金流（5年 + 终值）
5. 折现计算公允价值
6. 敏感性分析（3×3 矩阵）
7. 验证合理性（EV 偏差<30%、终值占比 50-80%）
8. 结构化输出
```

#### X 研究 (`x-research`)
X/Twitter 情绪研究 Workflow：
```
1. 分解问题为 3-5 个目标查询（含 $TICKER、from:、情绪关键词）
2. 执行搜索（sort by likes, min_likes 过滤）
3. 可选：检查关键账户资料
4. 可选：追踪推文线程
5. 按主题合成（看涨/看跌/中性/新闻）
```

### 技能架构
```
src/skills/
├── registry.ts       → 启动时扫描 SKILL.md
├── loader.ts         → 解析 YAML frontmatter
├── types.ts          → 类型定义
└── dcf/
│   ├── SKILL.md      → 技能定义
│   └── sector-wacc.md→ 行业 WACC 参考数据
└── x-research/
    └── SKILL.md      → X 研究流程
```

---

## 💾 七、内存系统

```
对话历史 → 分块 → 嵌入 → SQLite 存储 → 语义搜索
                                       ├── MMR 多样性排序
                                       ├── 时间衰减权重
                                       └── Session 文件管理
```

| 组件 | 说明 |
|------|------|
| `chunker` | 文本分块 |
| `embeddings` | 嵌入生成 |
| `indexer` | 向量索引 |
| `search` | 语义搜索 |
| `mmr` | Maximal Marginal Relevance 去重 |
| `temporal-decay` | 时间衰减 |

---

## 📊 八、评估系统

### LangSmith 评估
```bash
bun run src/evals/run.ts           # 全部金融问题
bun run src/evals/run.ts --sample 10  # 随机抽样
```

- **数据集**: `src/evals/dataset/finance_agent.csv`
- **评估方式**: LLM-as-Judge（用 LLM 评判答案正确性）
- **实时 UI**: Ink 界面显示进度、当前问题、准确率统计
- **追踪**: 结果记录到 LangSmith

---

## 📱 九、WhatsApp 网关

通过 WhatsApp 与 Dexter 对话：

```bash
bun run gateway:login    # 扫码登录 WhatsApp
bun run gateway          # 启动网关
```

### 网关架构
```
WhatsApp (Baileys) → 消息路由 → Agent 处理 → 回复发送
                    ├── 会话管理
                    ├── 群聊支持（@提及检测）
                    ├── 心跳机制
                    └── 访问控制
```

---

## 🔑 十、核心设计亮点

| 亮点 | 说明 |
|------|------|
| **Ink + React CLI** | 终端内 React 组件渲染，UI 体验远超传统 CLI |
| **SKILL.md 系统** | 与 OpenClaw 完全同构的技能定义方式 |
| **SOUL.md 人格** | 巴菲特+芒格投资哲学驱动的 agent 人格 |
| **Scratchpad 透明** | 所有工具调用记录为 `.jsonl`，完全可审计 |
| **6 种 LLM 自适应** | 前缀自动检测，一条命令切换 |
| **上下文压缩** | 微压缩 + 全量压缩双重机制 |
| **内存系统** | SQLite + 嵌入 + MMR + 时间衰减 |
| **WhatsApp 集成** | 通过 Baileys 实现 WhatsApp 交互 |

---

## ⚠️ 十一、依赖要求

| 依赖 | 说明 |
|------|------|
| **Bun** | 运行时必须（v1.0+） |
| **OpenAI API Key** | 默认 LLM 提供商 |
| **Financial Datasets API Key** | 金融数据（financialdatasets.ai） |
| **Exa API Key** | Web 搜索（可选，无则用 Tavily） |
| **Playwright** | 浏览器工具（`postinstall` 自动安装 Chromium） |

---

## 📋 十二、总结

| 维度 | 评价 |
|------|------|
| **领域专注度** | ⭐⭐⭐⭐⭐ 金融研究垂直领域，巴菲特/芒格哲学驱动 |
| **架构设计** | ⭐⭐⭐⭐⭐ Agent 循环 + Scratchpad + 压缩，设计精良 |
| **代码质量** | ⭐⭐⭐⭐⭐ TypeScript strict + ink React + 测试覆盖 |
| **可扩展性** | ⭐⭐⭐⭐⭐ SKILL.md 技能系统 + 6 种 LLM 可插拔 |
| **用户体验** | ⭐⭐⭐⭐ Ink TUI 出色，但终端门槛较高 |
| **创新性** | ⭐⭐⭐⭐⭐ CLI Agent + 金融研究 + 人格化 SOUL 独树一帜 |

### 与 OpenClaw 的相似性
- 同样使用 **SKILL.md** 技能系统（YAML frontmatter + Markdown body）
- 同样有 **SOUL.md** 文件定义 agent 人格
- 同样的 Agent 循环设计（工具调用 → 结果回注 → 迭代）
- 同样的多 LLM 提供商抽象
- 同样的内存/嵌入/搜索系统

> 📌 Dexter 本质上是"垂直领域的 OpenClaw"——专注金融研究，用 Ink 做终端 UI。其 SOUL.md 和 SKILL.md 设计思路可直接借鉴到 OpenClaw 自定义 agent 中。
