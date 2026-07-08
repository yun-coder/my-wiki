# Agentic AI 系统

基于 Loop Engineering 四大支柱（Prompt / Context / Loop / Harness）的本地知识库管理 Agent 系统。

> 核心理念：从"问一个问题"升级为"完成任务"——通过结构化迭代循环，让 Agent 自主执行、验证、修正，直到目标达成。

## 架构

```
agni-agent/
├── agents/
│   ├── core/              # Agent 核心 + Harness 基础设施
│   │   ├── config.py          # .env 配置加载
│   │   ├── agnes_client.py    # Agnes AI API 客户端
│   │   └── memory.py          # 三层记忆管理（事件日志 + 上下文窗口 + 长期摘要）
│   ├── crawler/           # 爬虫模块
│   │   ├── bookmark_parser.py   # 书签 HTML 解析
│   │   └── scraper.py           # Scrapling 封装
│   ├── knowledge/         # 知识处理
│   │   ├── analyzer.py          # LLM 内容分析（支持反馈驱动重试）
│   │   └── archiver.py          # 知识库存档
│   └── scheduler/         # 编排引擎
│       ├── loop.py              # Loop Engineering 迭代式编排（知识库分析）
│       └── daily_task.py        # 每日定时采集（AI资讯链接抓取入库）
├── state/                 # 运行时：记忆日志 + 上下文 + 循环轨迹
│   ├── memory.md              # Layer 1: Append-only 事件日志
│   ├── memory_context.json    # Layer 2: 短期上下文窗口
│   ├── memory_summary.json    # Layer 3: 长期趋势统计
│   ├── scraper_cache/         # 爬取缓存
│   ├── loops/                 # Loop 分析模式运行轨迹
│   └── daily/                 # 每日采集模式运行轨迹
├── .env                   # 配置
├── .gitignore
├── requirements.txt
└── main.py                # 入口
```

## 两种工作模式

### 模式 1: 知识库分析（默认）

扫描 `KNOWLEDGE_BASE_PATH` 下的所有 `.md` 文件，用 LLM 做深度分析 + 质量验证：

```
扫描知识库 → LLM 深度分析 → 验证 + 修正（最多 3 轮迭代）
```

### 模式 2: 每日采集（`--daily`）

从知识库中读取 "AI资讯 信息源" 文件，定时抓取新内容存入知识库：

```
读取信息源文件 → 爬取 → LLM 分析 → 验证 → 存档到知识库
```

> 信息源链接存放在 `05-tools/AI资讯_信息源列表.md`，修改该文件即可增减采集目标。

## Loop Engineering 四大支柱

### 1. Prompt Engineering — 如何问问题
[analyzer.py](agents/knowledge/analyzer.py) 中的 SYSTEM_PROMPT 定义了知识提取的结构化指令。

### 2. Context Engineering — 给模型什么信息
[memory.py](agents/core/memory.py) 的 `build_context_prompt()` 将运行历史和失败模式整合为上下文。

### 3. Loop Engineering — 结构化迭代循环
[loop.py](agents/scheduler/loop.py) 和 [daily_task.py](agents/scheduler/daily_task.py) 是核心编排引擎：

```
Task Input → Agent Execution → Tool-based Verification → Feedback → Correction
```

### 4. Harness Engineering — 基础设施
提供工具可用性检查、人在回路（HITL）、运行隔离目录、循环轨迹 JSON 记录。

## 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置

编辑 `.env` 文件：

```
AGNES_API_KEY=你的实际Key
KNOWLEDGE_BASE_PATH=D:/学习院/my-wiki/AI知识库
```

### 3. 运行

```powershell
# 知识库分析模式（默认）
python main.py

# 每日 AI资讯 采集模式
python main.py --daily
```

## 工作流程

### 知识库分析模式

1. **扫描** — 读取知识库下的所有 `.md` 文件（11 个分类目录）
2. **分析** — Agnes AI 对文件做深度分析：提取核心概念、关键实体、关联关系
3. **验证** — 5 条确定性规则检查分析质量（非 LLM 自评）
4. **修正** — 验证失败时，将反馈注入 LLM 重新分析（最多 3 轮迭代）

### 每日采集模式

1. **读取信息源** — 从知识库 `05-tools/AI资讯_信息源列表.md` 提取采集链接
2. **爬取** — Scrapling 逐个抓取网页内容（反检测 + 隐身模式）
3. **分析** — Agnes AI 分析内容，提取结构化知识点
4. **验证** — 5 条确定性规则检查存档质量
5. **存档** — 写入知识库对应分类目录

> 增减采集目标只需编辑 `05-tools/AI资讯_信息源列表.md` 中的表格。

## 记忆系统

三层架构设计：

| 层级 | 文件 | 用途 | 生命周期 |
|------|------|------|----------|
| Layer 1 | `memory.md` | Append-only 事件日志 | 永久 |
| Layer 2 | `memory_context.json` | 最近 N 条事件（滑动窗口） | 短期 |
| Layer 3 | `memory_summary.json` | 跨周期趋势统计 | 长期 |

每次运行的完整轨迹保存在 `state/loops/{run_id}/` 或 `state/daily/{run_id}/` 下。

## 技术栈

- **OpenAI SDK** — LLM API 客户端（Agnes AI 兼容接口）
- **Scrapling** — 网页抓取，支持反检测和隐身模式
- **python-dotenv** — 环境变量管理
