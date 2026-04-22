# LangChain / LangGraph / DeepAgents 学习路径

## 框架关系

```
Deep Agents
    ↑ 基于
LangGraph
    ↑ 基于
LangChain
```

| 框架 | 定位 | 复杂度 |
|------|------|--------|
| **LangChain** | LLM 应用开发框架，提供模型 I/O、工具、检索等基础组件 | ⭐ 入门 |
| **LangGraph** | 基于图的运行时，用于构建有状态、多步骤的 Agent 工作流 | ⭐⭐ 进阶 |
| **DeepAgents** | 基于 LangGraph 的 Agent 工具箱，提供开箱即用的深度 Agent 能力 | ⭐⭐⭐ 高级 |

> 参考：[LangChain vs LangGraph vs Deep Agents](https://docs.langchain.com/oss/python/concepts/products)

---

## 学习前置知识

### 1. Python 基础
- **必须**：熟练使用 Python（版本 3.10+）
- 理解协程/异步编程（`async/await`）
- 理解上下文管理器（`with` 语句）
- 理解生成器（`yield`）

### 2. LLM 基础概念
- **Prompt Engineering**：了解如何写好提示词
- **Function Calling / Tool Use**：大模型调用外部工具的机制
- **Chain of Thought**：让模型逐步思考
- **Temperature / Top-p**：了解生成参数对输出的影响
- **Token / Context Window**：理解上下文长度限制

### 3. AI Agent 核心概念
- **ReAct**（Reasoning + Acting）：推理-行动模式
- **Tool**：Agent 调用外部工具的能力
- **Memory**：短期记忆（对话历史）与长期记忆（向量存储）
- **Planning / Task Decomposition**：任务分解与规划
- **Human-in-the-Loop (HITL)**：人机协作模式

### 4. LangChain 概念（入门必须）

| 概念 | 说明 |
|------|------|
| **Model I/O** | 封装好的 LLM 调用接口（ChatModel, PromptTemplate, OutputParser） |
| **Chains** | 将多个组件串联执行（LLMChain, SimpleSequentialChain） |
| **Tools & Toolkits** | 工具定义（Wikipedia, Google Search, Calculator 等） |
| **Memory** | 对话记忆（ConversationBufferMemory, VectorStoreRetrieverMemory） |
| **Retrievers** | RAG 检索器（VectorStoreRetriever, BM25Retriever） |
| **Callbacks** | 事件回调（用于流式输出、日志记录） |

### 5. LangGraph 概念（进阶必须）

| 概念 | 说明 |
|------|------|
| **StateGraph** | 核心——用图来管理 Agent 状态 |
| **State** | 状态对象（整个图共享的数据结构） |
| **Node** | 图中的节点（可以是函数、Agent 或 Tool） |
| **Edge** | 图中的边（决定下一步流向） |
| **Conditional Edge** | 条件边（根据状态决定分支） |
| **Middleware** | 中间件（拦截器，用于人类介入、限流等） |
| **Interrupt** | 中断点（暂停执行等待人类确认） |
| **Streaming** | 流式输出（实时看到 Agent 执行过程） |

### 6. Deep Agents 概念（高级必须）

| 概念 | 说明 |
|------|------|
| **AGENTS.md** | Agent 的身份定义和指令文件 |
| **Skills** | 按需加载的能力模块（类似 OpenClaw 的 Skill） |
| **Backends** | 后端服务集成（搜索、代码执行等） |
| **Long-term Memory** | 基于文件系统的长期记忆 |
| **Subagent Orchestration** | 子 Agent 编排（主 Agent 派发任务给子 Agent） |
| **Deep Research Pattern** | 深度研究模式（多次搜索、整合、输出） |

---

## 学习路径

### 阶段 1：LangChain 入门（101）

**目标**：理解 LangChain 基本抽象，会写简单的 Chain

**必须掌握**：
```
1. Model I/O
   - ChatOpenAI / ChatAnthropic 调用
   - PromptTemplate 定义
   - OutputParser 解析输出

2. 简单 Chains
   - LLMChain 用法
   - SequentialChain 串联

3. Memory
   - ConversationBufferMemory 对话记忆

4. Tools
   - 定义自定义 Tool
   - 组合使用多个 Tool

5. Streaming
   - 使用 Callback 实现流式输出
```

**教程资源**：
- [LangChain Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
- `notebooks/101/101_langchain_langgraph.ipynb`

**练手项目**：
- 制作一个带记忆的聊天机器人
- 制作一个调用 Wikipedia 搜索的工具

---

### 阶段 2：LangGraph 进阶（201）

**目标**：能用 StateGraph 构建有状态的 Agent 工作流

**必须掌握**：
```
1. StateGraph 基础
   - 定义 State（使用 TypedDict/Pydantic）
   - 添加 Node（普通函数）
   - 添加 Edge（普通边 + 条件边）
   - compile() 编译图

2. 状态管理
   - 状态更新逻辑
   - 条件分支（函数返回值决定走向）

3. Human-in-the-Loop
   - interrupt() 中断执行
   - 人类确认后继续
   - Middleware 中间件

4. 调试与流式
   - Streaming 输出每个节点
   - LangGraph Studio 可视化调试
```

**教程资源**：
- [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph/overview)
- `notebooks/101/102_middleware.ipynb`
- [DeepLearning.ai: AI Agents in LangGraph](https://learn.deeplearning.ai/courses/ai-agents-in-langgraph/information)

**练手项目**：
- 制作一个邮件分类 + 回复 Agent
- 制作一个多步骤研究 Agent

---

### 阶段 3：Deep Agents 高级

**目标**：掌握生产级 Deep Agent 架构

**必须掌握**：
```
1. Deep Agent 架构
   - create_deep_agent() 创建深度 Agent
   - 内置的 planning, memory, skills 机制

2. Multi-Agent 系统
   - Supervisor 模式（一个主 Agent 调度子 Agent）
   - 平行子研究 Agent（类似 Manus 的架构）

3. AGENTS.md 设计
   - Agent 身份定义
   - 指令编写最佳实践

4. Skills 系统
   - Skill 定义（SKILL.md）
   - 按需动态加载

5. 长期记忆
   - 基于文件系统的记忆存储
   - 跨会话记忆保持
```

**教程资源**：
- `notebooks/201/deepagents.ipynb`
- [Deep Agents 文档](https://docs.langchain.com/oss/python/deepagents/)
- [Deep Agents from Scratch - Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/11/langchains-deep-agent-guide/)

**练手项目**：
- 制作一个深度研究 Agent（搜索 → 整理 → 输出报告）
- 制作一个多 Agent 音乐商店（订单 Agent + 推荐 Agent）

---

## 推荐学习顺序

```
1. Python 基础（必须先会）
        ↓
2. LLM 基础概念（Prompt, Tool, Memory）
        ↓
3. LangChain 入门（Model I/O, Chains, Memory）
        ↓
4. LangGraph 进阶（StateGraph, Conditional Edge, HITL）
        ↓
5. Multi-Agent 模式（Supervisor, 并行子 Agent）
        ↓
6. Deep Agents（生产级架构，AGENTS.md, Skills）
```

---

## 官方学习资源

| 资源 | 链接 |
|------|------|
| LangGraph 101 仓库 | https://github.com/langchain-ai/langgraph-101 |
| LangChain 官方文档 | https://docs.langchain.com/ |
| LangGraph 官方文档 | https://docs.langchain.com/langgraph/ |
| Deep Agents 文档 | https://docs.langchain.com/deepagents/ |
| LangChain Academy（免费课程）| https://academy.langchain.com/ |
| DeepLearning.ai 课程 | https://learn.deeplearning.ai/courses/ai-agents-in-langgraph |

---

## 环境搭建

```bash
# 1. 克隆 langgraph-101
git clone https://github.com/langchain-ai/langgraph-101.git
cd langgraph-101

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
cp .env.example .env  # 配置 API Key
uv sync

# 4. 本地运行 Agent
langgraph dev
```

---

## 与 OpenClaw 的类比

| LangChain/LangGraph 概念 | OpenClaw 类比 |
|-------------------------|---------------|
| StateGraph | 工作流/流程编排 |
| Tool | Skill（技能） |
| AGENTS.md | SOUL.md + IDENTITY.md |
| Memory | MEMORY.md |
| Deep Agent | 团队 Leader Agent |
| Subagent | 团队成员 Agent |
| Interrupt / HITL | 人工确认环节 |
| Streaming | 实时进度输出 |

---

## 总结

学习这三者需要储备的知识：

1. **Python 基础**（必须）
2. **LLM 核心概念**（必须）
3. **Agent 设计模式**（必须）
4. **LangChain 基础**（入门）
5. **LangGraph 状态机**（进阶）
6. **Multi-Agent 编排**（高阶）
7. **Deep Agents 生产架构**（高级）

建议时间分配：
- LangChain：1-2 周
- LangGraph：2-3 周
- Deep Agents：2-4 周
