---
created: 2025-01-15
updated: 2026-05-11
tags:
  - AI
  - 学习路线
  - LLM
  - 深度学习
---

# AI 学习路线图（2026 版）

> 从零基础到 AI 工程师，按层次递进的学习路径。每个阶段建议 2-4 周，根据基础可灵活调整。

---

## 第一层：基础层

### 1. Python + 数学基础

打好编程和数学底子，是所有后续内容的根基。

**学习要点：**
- Python 核心语法、面向对象编程
- NumPy / Pandas 数据处理
- 线性代数（矩阵运算、特征值分解）
- 概率论与统计（贝叶斯、分布、假设检验）
- 微积分基础（梯度、链式法则）

**推荐资源：**
- [3Blue1Brown 线性代数的本质](https://www.bilibili.com/video/BV1ys4y1a7oA/)（视频，强烈推荐）
- [CS231n 数学基础笔记](https://cs231n.github.io/python-numpy-tutorial/)
- 《Python 机器学习基础教程》（O'Reilly）

**优先级：⭐⭐⭐⭐⭐ 必学**

---

## 第二层：框架层

### 2. PyTorch / TensorFlow

掌握深度学习框架，实现从理论到代码的跨越。

**学习要点：**
- 张量操作、自动求导机制
- 搭建全连接网络、CNN、RNN
- 训练循环：损失函数、优化器、学习率调度
- GPU 训练加速

**推荐资源：**
- [PyTorch 官方 60 分钟入门](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html)
- [动手学深度学习（d2l.ai）](https://zh.d2l.ai/)（中文，PyTorch 版本）
- [PyTorch 实战教程](https://github.com/yunjey/pytorch-tutorial)

**优先级：⭐⭐⭐⭐⭐ 必学**

### 3. Transformer 理论基础

理解现代 AI 的核心架构，几乎所有大模型都基于此。

**学习要点：**
- Self-Attention 机制
- Multi-Head Attention
- Position Encoding（位置编码）
- Encoder-Decoder 架构
- KV Cache 与推理优化

**推荐资源：**
- [The Illustrated Transformer（图解 Transformer）](https://jalammar.github.io/illustrated-transformer/)（经典必读）
- [Transformer 原始论文](https://arxiv.org/abs/1706.03762)
- [哈佛 Transformer 注解版](https://nlp.seas.harvard.edu/annotated-transformer/)

**优先级：⭐⭐⭐⭐⭐ 必学**

---

## 第三层：应用层

### 4. Prompt Engineering 基础

学会与 AI 高效沟通，是当下最实用的技能之一。

**学习要点：**
- Prompt 设计模式（零样本、少样本、思维链 CoT）
- 结构化 Prompt（System / User / Assistant 分离）
- Prompt 变量化与模板管理
- 评估 Prompt 效果的方法

**推荐资源：**
- [Prompt Engineering Guide](https://www.promptingguide.ai/zh)（中文版，全面且持续更新）
- [OpenAI Prompt 最佳实践](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering 文档](https://docs.anthropic.com/zh-CN/docs/build-with-claude/prompt-engineering/overview)

**优先级：⭐⭐⭐⭐⭐ 必学**

### 5. LangChain / LlamaIndex 框架

构建 LLM 应用的主流开发框架。

**学习要点：**
- Chain 与 Agent 基本概念
- Tool Calling / Function Calling
- Memory 管理（对话记忆）
- LlamaIndex 的数据索引与查询管道
- LangGraph 工作流编排

**推荐资源：**
- [LangChain 官方文档](https://python.langchain.com/docs/)
- [LangGraph 入门教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [LlamaIndex 官方文档](https://docs.llamaindex.ai/)

**优先级：⭐⭐⭐⭐ 高优**

### 6. 向量数据库（FAISS / Milvus）

RAG 系统的核心存储组件。

**学习要点：**
- Embedding 原理与常用模型（BGE / OpenAI Embedding）
- 向量相似度搜索（余弦相似度、HNSW）
- FAISS 本地部署与使用
- Milvus / Qdrant 分布式向量数据库
- 混合检索（向量 + 关键词）

**推荐资源：**
- [FAISS 官方指南](https://github.com/facebookresearch/faiss/wiki)
- [Milvus 官方文档](https://milvus.io/docs)
- [向量数据库对比指南](https://zilliz.com/learn/introduction-to-vector-databases)

**优先级：⭐⭐⭐⭐ 高优**

### 7. RAG 系统搭建

检索增强生成，是当前企业落地 AI 最主流的方式。

**学习要点：**
- 文档切分策略（Chunking）
- Embedding + 向量检索流程
- Reranker 重排序
- RAG 评估（RAGAS 框架）
- Advanced RAG（多跳检索、自适应检索）

**推荐资源：**
- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)
- [RAGAS 评估框架](https://docs.ragas.io/)
- [LlamaIndex RAG 最佳实践](https://docs.llamaindex.ai/en/stable/use_cases/rag.html)

**优先级：⭐⭐⭐⭐ 高优**

---

## 第四层：进阶层

### 8. 微调技术（LoRA / QLoRA）

让通用模型适配特定领域的关键技术。

**学习要点：**
- 全参数微调 vs 参数高效微调（PEFT）
- LoRA 原理（低秩适配）
- QLoRA 量化微调（4-bit 训练）
- SFT（监督微调）数据准备
- DPO / RLHF 对齐技术

**推荐资源：**
- [LoRA 原始论文](https://arxiv.org/abs/2106.09685)
- [Hugging Face PEFT 库](https://huggingface.co/docs/peft/)
- [LLaMA-Factory 微调框架](https://github.com/hiyouga/LLaMA-Factory)（中文友好）

**优先级：⭐⭐⭐ 中高**

### 9. 多模态模型应用

处理文本、图像、音频、视频的综合能力。

**学习要点：**
- Vision-Language Model（VLM）原理
- 图像理解（GPT-4V / Gemini / Qwen-VL）
- 多模态 Embedding
- 视频分析与音频处理
- 多模态 Agent（如 Computer Use）

**推荐资源：**
- [OpenAI Vision 指南](https://platform.openai.com/docs/guides/vision)
- [Qwen-VL 系列文档](https://qwenlm.github.io/blog/qwen-vl/)
- [多模态学习综述](https://arxiv.org/abs/2301.06623)

**优先级：⭐⭐⭐ 中高**

### 10. Agent 架构开发

从单次对话到自主决策的 AI 系统。

**学习要点：**
- ReAct（推理 + 行动）模式
- Tool Calling 与 Function Calling 深入
- Multi-Agent 协作（CrewAI / AutoGen）
- Agent 评估与安全约束
- MCP 协议（Model Context Protocol）

**推荐资源：**
- [LangGraph Agent 教程](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [CrewAI 官方文档](https://docs.crewai.com/)
- [Anthropic MCP 协议规范](https://modelcontextprotocol.io/)

**优先级：⭐⭐⭐⭐ 高优**

---

## 第五层：工程层

### 11. 模型部署优化（Docker / Kubernetes）& MLOps

将模型从开发环境推到生产环境。

**学习要点：**
- 模型推理优化（vLLM / TensorRT-LLM）
- Docker 容器化部署
- Kubernetes 集群管理与自动扩缩容
- GPU 调度与资源管理
- CI/CD 流水线（模型版本管理、自动化测试）
- 监控与可观测性（Prometheus + Grafana）
- LLM Gateway（限流、负载均衡、多模型路由）

**推荐资源：**
- [vLLM 官方文档](https://docs.vllm.ai/)
- [NVIDIA TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- [MLOps 实战指南](https://neptune.ai/blog/mlops)
- [Kubernetes 生产实践](https://kubernetes.io/docs/home/)

**优先级：⭐⭐⭐ 中高**

---

## 学习建议

| 阶段 | 预计时间 | 目标 |
|------|---------|------|
| 基础层 | 4-8 周 | 能独立完成数据处理和简单模型训练 |
| 框架层 | 4-6 周 | 理解 Transformer，能跑通训练流程 |
| 应用层 | 6-8 周 | 能搭建完整的 RAG / Agent 应用 |
| 进阶层 | 4-6 周 | 能进行微调和多模态开发 |
| 工程层 | 4-6 周 | 能将模型部署到生产环境 |

> 💡 **核心建议：** 不要试图一次学完所有内容。建议先打通「基础层 → 应用层」的路径，在实际项目中积累经验后，再根据需要深入进阶层和工程层。做项目 > 看教程。
