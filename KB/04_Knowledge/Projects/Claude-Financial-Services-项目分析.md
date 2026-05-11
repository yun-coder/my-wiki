---
created: 2026-05-08
tags: #开源项目 #Claude #金融AI #Agent #MCP #Anthropic
source: "Claude for Financial Services"
source_url: https://github.com/anthropics/financial-services
author: Anthropic
publish_date: 2026
---

# Claude for Financial Services — Anthropic 官方金融服务 Agent 工具集

> **项目信息**
> - 仓库: [github.com/anthropics/financial-services](https://github.com/anthropics/financial-services)
> - 组织: Anthropic
> - 许可: Apache License 2.0
> - 性质: 官方开源，参考模板
> - 定位: 金融服务工作流 Agent、技能和数据连接器

---

## 摘要
> Anthropic 官方出品的金融服务 Agent 工具集，覆盖投行、股票研究、私募股权、财富管理、基金运营五大垂直领域，提供端到端工作流 Agent + 领域技能 + MCP 数据连接器，支持 Claude Cowork 插件和 Managed Agents API 双模式部署。

---

## 📖 一、项目定位

### 一句话定位
**Claude 在金融服务业的"官方技能包"** — 不是产品，而是参考模板和最佳实践。

### 核心理念
```
传统方式: 金融分析师手动建模 → 写备忘录 → 做PPT → 反复修改
Claude 方式: Agent 自动执行工作流 → 生成初稿 → 人工审核签批
```

### 关键声明
> ⚠️ 不构成投资、法律、税务建议。Agent 产出的是待审分析师工作产品，所有输出均需合格专业人士审核签批。

---

## 🏗️ 二、架构设计

### 双模式部署
| 模式 | 适用场景 | 部署方式 |
|------|---------|---------|
| **Claude Cowork 插件** | 交互式使用 | Settings → Plugins → Add plugin |
| **Managed Agents API** | 后端集成，无头部署 | `/v1/agents` API + 子 Agent 编排 |

> 同一套系统提示词和技能，两种运行方式。

### 仓库结构
```
plugins/
  agent-plugins/          # 命名 Agent（端到端工作流）
  vertical-plugins/       # 按垂直领域分组的技能 + 命令 + 连接器
  partner-built/          # 合作伙伴插件（LSEG, S&P Global）
managed-agent-cookbooks/  # Managed Agent 部署模板
claude-for-msft-365-install/  # Microsoft 365 插件部署工具
scripts/                  # 部署/校验/编排脚本
```

### 核心概念关系
```
┌─────────────────────────────────────────────────┐
│                  整体架构                         │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Agents   │ ←  │  Skills  │ ←  │ Connectors│  │
│  │ (工作流)  │    │ (领域知识)│    │  (MCP)   │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │         │
│       └───────┬───────┘               │         │
│               ↓                       │         │
│  ┌────────────────────┐              │         │
│  │  Claude Cowork     │              │         │
│  │  或 Managed Agents │              │         │
│  └────────────────────┘              │         │
│               ↑                       ↑         │
│       人工审核签批              数据提供商 API   │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 🤖 三、Agent 清单（10 个）

### 投行 & 咨询
| Agent | 功能 |
|-------|------|
| **Pitch Agent** | Comps、先例、LBO → 品牌化 Pitch Deck，端到端 |
| **Meeting Prep Agent** | 客户会议前的简报包准备 |

### 研究与建模
| Agent | 功能 |
|-------|------|
| **Market Researcher** | 行业/主题 → 行业概览、竞争格局、同业对比、投资标的清单 |
| **Earnings Reviewer** | 财报电话会 + 文件 → 模型更新 → 研究报告初稿 |
| **Model Builder** | DCF、LBO、三表模型、Comps — 在 Excel 中实时建模 |

### 基金运营 & 财务
| Agent | 功能 |
|-------|------|
| **Valuation Reviewer** | 接收 GP 包 → 运行估值模板 → 生成 LP 报告 |
| **GL Reconciler** | 发现差异 → 追溯根因 → 路由签批 |
| **Month-End Closer** | 应计、滚动、差异分析 |
| **Statement Auditor** | LP 报表分发前审计 |

### 运营 & 合规
| Agent | 功能 |
|-------|------|
| **KYC Screener** | 解析入驻文件 → 运行规则引擎 → 标记缺失项 |

---

## 📦 四、垂直领域插件（9 个）

| 插件 | 覆盖技能 |
|------|---------|
| **financial-analysis** *(核心)* | Comps、DCF、LBO、三表模型、Deck QC、Excel 审计、11 个数据连接器 |
| **investment-banking** | CIM、Teaser、流程函、买方清单、并购模型、交易跟踪 |
| **equity-research** | 财报笔记、首次覆盖、模型更新、论点跟踪、催化剂日历 |
| **private-equity** | 寻源、筛选、尽调清单、IC 备忘录、组合监控 |
| **wealth-management** | 客户回顾、财务规划、再平衡、TLH |
| **fund-admin** | GL 对账、差异追溯、应计、滚动、差异分析 |
| **operations** | KYC 文件解析和规则评估 |
| **lseg** *(合作方)* | 债券 RV、掉期曲线、FX carry、期权波动率 |
| **sp-global** *(合作方)* | 公司简介、财报预览、融资摘要 |

---

## 🔌 五、MCP 数据连接器（11 个）

所有连接器集中在 financial-analysis 核心插件中共享：

| 提供商 | 数据类型 |
|--------|---------|
| **Daloopa** | 财务数据提取 |
| **Morningstar** | 基金/股票数据 |
| **S&P Global** (Kensho) | 资本市场数据 |
| **FactSet** | 金融数据终端 |
| **Moody's** | 信用数据 |
| **MT Newswires** | 实时新闻 |
| **Aiera** | 财报电话会 AI 分析 |
| **LSEG** | 伦敦证交所数据 |
| **PitchBook** | PE/VC 交易数据 |
| **Chronograph** | PE 组合监控 |
| **Egnyte** | 文档管理 |

---

## 💡 六、核心价值与启示

### 技术价值
1. **Agent 模板化** — 每个 Agent 自包含（系统提示 + 技能），开箱即用
2. **技能与 Agent 分离** — 技能按垂直领域组织，Agent 按需组合
3. **MCP 连接器集中管理** — 一次接入，所有 Agent 共享
4. **双部署模式** — 交互式（Cowork）+ 无头（API），灵活适配

### 架构启示
```
值得借鉴的设计模式:

1. Agent = System Prompt + Skills Bundle
   → 每个 Agent 自包含，安装即用

2. Skills 按 Vertical 组织，Agent 按需 Bundle
   → 源在 vertical-plugins，通过 sync 脚本同步到 agent-plugins
   → 避免重复，保持一致性

3. MCP Connectors 集中在 Core Plugin
   → 一个地方管理所有数据源连接

4. 全文件化（Markdown + YAML）
   → 无构建步骤，人类可读可编辑
```

### 对我们的参考意义
- **Agent 技能分层架构**：核心技能 → 垂直领域技能 → 具体工作流 Agent
- **MCP 作为统一数据层**：所有外部数据通过 MCP 接入
- **人机协作模式**：Agent 产出初稿，人类审核签批，而非完全自动化
- **"参考模板"定位**：官方明确说这是起点，鼓励用户定制

---

## 🔍 七、局限性与思考

### 局限
1. **依赖 Anthropic 生态** — Cowork 插件和 Managed Agents API 都是 Claude 专属
2. **需要付费数据源** — MCP 连接器大多需要订阅或 API Key
3. **仅英文** — 目前所有技能和模板都是英文
4. **参考模板而非产品** — 需要大量定制才能投入实际使用

### 延伸思考
- **Agent 工程的最佳实践样本** — Anthropic 官方的 Agent 架构设计值得深入参考
- **金融 AI 的边界** — 明确声明"不构成投资建议"，所有输出需人工审核
- **技能组合模式** 可迁移到其他垂直领域（法律、医疗、工程等）
- **MCP 连接器的集中管理思路** — 如果我们做多 Agent 系统，值得借鉴

---

## 📎 相关资源
- [GitHub 仓库](https://github.com/anthropics/financial-services)
- [Claude Cowork](https://claude.com/product/cowork)
- [Claude Managed Agents API](https://docs.claude.com/en/api/managed-agents)
- [MCP 协议](https://modelcontextprotocol.io/)

## 标签
#开源项目 #Claude #金融AI #Agent #MCP #Anthropic #技能架构 #工作流自动化

---
*分析时间: 2026-05-08*
