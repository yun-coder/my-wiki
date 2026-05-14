---
created: 2026-05-14
updated: 2026-05-14
tags:
  - AI
  - Agent
  - 学习计划
  - RAG
  - MCP
  - 工程化
---

# AI Agent 技术栈学习计划（2026 优化版）

> 目标：用最高效率掌握能真实交付 AI Agent 产品的技术栈。路线从“会调用模型”升级为“能做可靠、可观测、可部署、可维护的 Agent 系统”。

## 结论先行

原计划覆盖面很全，但不够高效：37 项技术并列学习会造成战线过长，且部分优先级已需要更新。2026 年更优路线应围绕 5 条主线推进：

1. **模型接口与工具调用**：优先掌握 OpenAI Responses API / Claude Messages API / Gemini API，而不是把旧 Chat Completions 当主线。
2. **Agent 编排**：LangGraph 作为生产级状态机主线；CrewAI/AutoGen 作为场景型补充，不建议平均投入。
3. **RAG 与知识工程**：从“向量库 + Embedding”升级到“文档解析、混合检索、重排、评估、权限隔离”的完整链路。
4. **MCP 与上下文工程**：MCP 已成为工具接入标准之一，但必须同时学习权限、审计、工具投毒和提示注入防护。
5. **生产工程化**：可观测、评测、异步任务、容器化、成本治理，应提前进入学习路线，而不是最后再补。

## 当前计划的问题

### 1. 时间估算偏长，学习颗粒度偏散

原计划 6-9 个月覆盖 37 项技术，适合团队全景培训，不适合个人高效率突破。个人路线应该先做一条端到端主线，再按项目需要补分支。

推荐压缩为：

| 阶段 | 时间 | 目标 |
|---|---:|---|
| 0. 快速对齐 | 3 天 | 建立最新 Agent 技术地图，选主框架 |
| 1. MVP 闭环 | 2 周 | 做出可运行 RAG + 工具调用 Agent |
| 2. 生产雏形 | 4 周 | 加入评测、日志、权限、部署 |
| 3. 复杂 Agent | 4 周 | LangGraph 状态机、人工审核、长期任务 |
| 4. 专项深化 | 持续 | MCP 安全、多模态、私有化、微调 |

### 2. OpenAI 主线需要更新

原计划把 OpenAI API 写成 GPT-4o / o3 + Chat Completions。2026 年新项目应优先学习：

- Responses API：统一文本、图像、工具、状态、多轮和内置工具。
- Agents SDK：工具、handoff、trace、guardrail 的开发体验。
- Structured Outputs：优先用严格 schema，而不是只依赖 JSON mode。
- 最新模型选择：复杂编码和专业任务优先 `gpt-5.5`；成本/延迟敏感任务选择 mini/nano 变体。

参考：
- [OpenAI Models](https://developers.openai.com/api/docs/models)
- [Migrate to the Responses API](https://platform.openai.com/docs/guides/migrate-to-responses)
- [OpenAI Responses API Reference](https://platform.openai.com/docs/api-reference/responses/retrieve)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [OpenAI Tools](https://platform.openai.com/docs/guides/tools)

### 3. Prompt Engineering 应降级为基础能力，Context Engineering 应升级

Prompt 仍重要，但它不再是 Agent 能力的天花板。2026 年更关键的是：

- 上下文选择：哪些数据进入模型，哪些不进入。
- 工具描述：工具边界、参数 schema、错误语义。
- 状态管理：短期上下文、长期记忆、任务状态。
- 评测闭环：prompt 改动必须有 eval，不靠感觉。
- 权限边界：模型不能因为上下文里出现指令就拥有额外权限。

### 4. LangGraph 应提前，LangChain 基础应压缩

LangChain 可学，但不建议花 3-4 周深挖全部组件。更高效的顺序是：

1. 直接掌握模型调用、工具调用、结构化输出。
2. 用 LangChain 只学必要集成。
3. 尽早进入 LangGraph：状态、节点、边、checkpoint、human-in-the-loop、streaming。

参考：
- [LangGraph.js Reference](https://langchain-ai.github.io/langgraphjs/reference/modules/langgraph.html)
- [LangGraph Pregel Runtime](https://langchain-ai.github.io/langgraphjs/reference/classes/langgraph.Pregel.html)

### 5. MCP 必学，但必须和安全一起学

MCP 已经不只是“工具服务器开发”，而是 Agent 接入外部世界的协议层。学习时不能只写 hello world server，应覆盖：

- Tools：动作能力，必须有权限、审计、超时、幂等。
- Resources：上下文数据，必须标注来源、权限、更新时间。
- Prompts：模板能力，必须防止被工具/资源污染。
- Security：工具投毒、提示注入、密钥泄露、权限膨胀、供应链风险。

参考：
- [MCP Architecture Overview](https://modelcontextprotocol.io/docs/concepts)
- [MCP Resources](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/)

## 推荐学习路线

## 阶段 0：技术地图校准（3 天）

目标：知道 2026 年 Agent 技术栈的主线，不被框架名牵着跑。

必做：

- 阅读 OpenAI Responses API、Structured Outputs、Tools 文档。
- 阅读 MCP 概念：Tools / Resources / Prompts。
- 阅读 LangGraph 核心概念。
- 建立自己的“技术选型表”。

产出物：

- `Agent 技术选型表`
- `常用模型与适用场景表`
- `个人 Agent 项目 idea 列表`

## 阶段 1：Agent MVP 闭环（2 周）

目标：做出一个真实可用的“个人知识库问答 + 工具调用 Agent”。

### 学习重点

| 模块 | 必学内容 | 推荐深度 |
|---|---|---|
| OpenAI / Claude / Gemini API | 多轮、流式、视觉、工具调用 | 熟练 |
| Structured Outputs | JSON Schema / Pydantic / Zod | 熟练 |
| Function Calling / Tool Use | 参数 schema、错误处理、重试 | 熟练 |
| RAG 基础 | 文档解析、chunk、embedding、向量检索 | 熟练 |
| FastAPI | API 封装、流式返回、错误码 | 熟练 |

### 推荐技术选择

| 场景 | 首选 |
|---|---|
| 模型 API 主线 | OpenAI Responses API |
| Python 后端 | FastAPI |
| 结构化输出 | Pydantic + Structured Outputs |
| 本地向量库 | Chroma / FAISS |
| 生产向量库 | Qdrant / Milvus |
| 文档解析 | PyMuPDF + Docling / LlamaParse |
| UI 验证 | 简单 Web UI 或 CLI |

### 实战项目

做一个“个人知识库 Agent”：

- 输入：`D:\gitCode\my-wiki\KB` 中的 Markdown 笔记。
- 能力：搜索笔记、总结主题、生成学习计划、更新待办。
- 工具：文件读取、关键词搜索、笔记链接建议。
- 输出：严格 JSON + 可读 Markdown 双格式。

验收标准：

- 能回答“某个主题我有哪些笔记”。
- 能输出引用来源路径。
- 能识别不知道的内容，而不是编造。
- 能稳定调用至少 3 个工具。

## 阶段 2：RAG 与评测生产化（4 周）

目标：从 demo 变成可靠系统。

### 学习重点

| 模块 | 必学内容 | 推荐深度 |
|---|---|---|
| 文档解析 | PDF/Word/HTML/Markdown 清洗 | 熟练 |
| 混合检索 | BM25 + 向量检索 | 熟练 |
| Reranker | BGE / Cohere / CrossEncoder | 熟练 |
| RAG 评估 | Faithfulness、Context Precision、Recall | 熟练 |
| Observability | trace、token、latency、error、cost | 熟练 |
| 权限隔离 | 用户、租户、文档 ACL | 熟练 |

### 工具建议

| 能力 | 推荐 |
|---|---|
| RAG 框架 | LlamaIndex 或轻量自研 pipeline |
| 评测 | RAGAS / DeepEval |
| 可观测 | Langfuse / Phoenix / LangSmith |
| 检索服务 | Qdrant / Milvus |
| 任务队列 | Celery + Redis，后续再学 Kafka |

参考：
- [LlamaIndex RAG](https://docs.llamaindex.ai/en/stable/understanding/rag/)
- [LlamaIndex Agents](https://docs.llamaindex.ai/en/stable/use_cases/agents/)
- [LlamaIndex Workflows](https://docs.llamaindex.ai/en/stable/workflows/)

### 实战项目

升级“个人知识库 Agent”为“可评测知识库系统”：

- 每个答案必须带来源。
- 每周跑一次固定评测集。
- 对比不同 chunk 策略和 reranker。
- 记录 token 成本和响应时延。

验收标准：

- 有 30 条固定测试问题。
- 每次改 prompt / 检索策略都能比较前后效果。
- 答案可追溯到具体文件。

## 阶段 3：复杂 Agent 编排（4 周）

目标：掌握真实业务里的多步骤、可中断、可审核 Agent。

### 学习重点

| 模块 | 必学内容 | 推荐深度 |
|---|---|---|
| LangGraph | StateGraph、conditional edge、checkpoint | 精通 |
| Human-in-the-loop | 人工审核、暂停、恢复、拒绝 | 熟练 |
| 长任务 | 状态持久化、重试、超时、补偿 | 熟练 |
| 多 Agent | 角色分工、handoff、结果裁决 | 了解到熟练 |
| CrewAI / AutoGen | 用于业务编排和快速 PoC | 了解 |

CrewAI 可以作为“角色型协作”的补充，重点看 Crews 和 Flows，而不是把它作为唯一主架构。

参考：
- [CrewAI Documentation](https://docs.crewai.com/en)
- [CrewAI Flows](https://docs.crewai.com/en/concepts/flows)
- [CrewAI Crews](https://docs.crewai.com/en/concepts/crews)

### 实战项目

做一个“学习计划执行 Agent”：

- 输入：学习目标和当前笔记。
- 自动拆解周计划。
- 每天生成任务。
- 根据完成情况调整计划。
- 遇到高成本/高风险动作需要人工确认。

验收标准：

- 支持中断后恢复。
- 每个节点有 trace。
- 每个工具调用有参数、结果、错误记录。
- 人工审核节点可修改下一步计划。

## 阶段 4：MCP 与工具生态（2-4 周）

目标：把 Agent 从单应用升级为可扩展工具生态。

### 学习重点

| 模块 | 必学内容 | 推荐深度 |
|---|---|---|
| MCP Server | tools/resources/prompts | 熟练 |
| MCP Client | 工具发现、权限确认、错误处理 | 熟练 |
| 工具安全 | allowlist、scoped token、审计日志 | 熟练 |
| 工具质量 | schema、超时、幂等、重试 | 熟练 |
| 工具市场风险 | 工具投毒、名称仿冒、供应链 | 了解到熟练 |

### 实战项目

为个人知识库做一个 MCP Server：

- `search_notes(query)`
- `read_note(path)`
- `list_recent_notes(days)`
- `suggest_links(note_path)`
- `create_note(title, folder, content)`，需要人工确认

验收标准：

- 读操作和写操作权限分离。
- 写操作必须确认。
- 所有工具调用记录审计日志。
- 工具描述不包含可被用户内容覆盖的安全承诺。

## 阶段 5：专项深化（持续）

按业务需要选择，不要全都同时学。

| 方向 | 什么时候学 | 推荐深度 |
|---|---|---|
| 多模态 Agent | 有图像/语音/视频业务时 | 熟练 |
| Browser / Computer Use | 需要操作网页或桌面软件时 | 熟练 |
| 私有化模型 | 有数据合规或成本压力时 | 熟练 |
| 微调 / DPO / RLHF | RAG 和 prompt 已无法满足时 | 了解到熟练 |
| Kubernetes | 需要多服务生产部署时 | 熟练 |
| Kafka | 高吞吐事件流场景 | 了解到熟练 |
| DSPy | 有稳定评测集且要自动优化 prompt 时 | 了解 |

Gemini 的长上下文和多模态能力值得关注，适合长文档、视频/音频、多文件分析场景。

参考：
- [Gemini Long Context](https://ai.google.dev/gemini-api/docs/long-context)

## 新版优先级表

| 优先级 | 技术 | 判断 |
|---|---|---|
| P0 | Responses API / Claude API / Gemini API | Agent 基础入口 |
| P0 | Tool Calling / Structured Outputs | 稳定性核心 |
| P0 | RAG 基础 + 文档解析 | 企业落地核心 |
| P0 | FastAPI + 流式输出 | 产品化入口 |
| P0 | Eval + Observability | 从 demo 到生产的分水岭 |
| P1 | LangGraph | 复杂 Agent 主线 |
| P1 | MCP | 工具生态主线 |
| P1 | Reranker / Hybrid Search | RAG 质量核心 |
| P1 | 权限 / 安全 / Prompt Injection 防御 | 上线必备 |
| P2 | CrewAI / AutoGen | 多 Agent PoC 和业务编排补充 |
| P2 | 私有化模型 / vLLM / Ollama | 成本和合规场景 |
| P2 | Browser / Computer Use | 自动化场景 |
| P3 | Fine-tuning / RLHF / DSPy | 有数据和评测后再深入 |

## 不建议的学习方式

- 不要先把 37 项技术全看一遍再动手。
- 不要从框架教程开始堆 demo，而忽略评测和数据质量。
- 不要把 Prompt Engineering 当成主要护城河。
- 不要在没有评测集前做 DSPy 或微调。
- 不要让 Agent 直接拥有写文件、发请求、删数据等高风险权限。
- 不要把 MCP Server 当普通脚本暴露，必须做权限和审计。

## 每周执行模板

```markdown
## 本周目标
- 

## 本周必做项目
- 

## 本周只学这 3 个概念
1. 
2. 
3. 

## 验收标准
- [ ] 有可运行代码
- [ ] 有测试/评测样例
- [ ] 有失败案例记录
- [ ] 有复盘笔记

## 复盘
- 本周最有价值的收获：
- 最大卡点：
- 下周要删掉/推迟的内容：
```

## 12 周高效版本

| 周次 | 主题 | 产出 |
|---:|---|---|
| 1 | Responses API / Claude / Gemini 基础 | 多模型调用 demo |
| 2 | Tool Calling + Structured Outputs | 3 工具 Agent |
| 3 | 文档解析 + Markdown 知识库读取 | 笔记读取 pipeline |
| 4 | Embedding + 向量检索 + BM25 | 本地 RAG |
| 5 | Reranker + 引用来源 | 高质量 RAG |
| 6 | FastAPI + Streaming | Agent API 服务 |
| 7 | RAGAS / DeepEval | 固定评测集 |
| 8 | Langfuse / LangSmith / Phoenix | 观测 dashboard |
| 9 | LangGraph 基础 | 状态机 Agent |
| 10 | Checkpoint + Human-in-the-loop | 可中断审批流 |
| 11 | MCP Server | 知识库工具服务 |
| 12 | 安全与权限 | 可演示生产雏形 |

## 适合放入个人知识库的位置

推荐保存到：

`KB/04_Knowledge/Notes/AI-Agent-技术栈学习计划-2026优化版.md`

同时建议新增或更新：

- `KB/04_Knowledge/Notes/Agent-技术选型表.md`
- `KB/04_Knowledge/Notes/RAG-评测实践.md`
- `KB/04_Knowledge/Notes/MCP-安全清单.md`
- `KB/04_Knowledge/Projects/个人知识库-Agent-项目规划.md`

## 总结

最高效路线不是“学完所有 Agent 框架”，而是围绕一个真实项目持续迭代：

**个人知识库 Agent → 可评测 RAG → LangGraph 编排 → MCP 工具体系 → 安全与部署。**

这条线最贴合你的知识库现状，也最容易产出可复用资产。
