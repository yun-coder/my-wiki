# 《Hands-On Large Language Models》分析笔记

> **书籍信息**
> - 书名: Hands-On Large Language Models（副标题: The Illustrated LLM Book）
> - 作者: Jay Alammar & Maarten Grootendorst
> - 出版社: O'Reilly (2024)
> - ISBN: 978-1098150969
> - 页数: ~400页，含近 300 张原创插图
> - 代码仓库: https://github.com/handsOnLLM/Hands-On-Large-Language-Models
> - 推荐序: Andrew Ng (DeepLearning.AI)、Nils Reimers (Cohere/sentence-transformers)、Leland McInnes (UMAP/HDBSCAN)

---

## 📖 书籍概览

本书是一本**图解式、可动手实践**的大语言模型（LLM）入门到进阶指南。全书以**视觉化教学**为核心特色（近 300 张原创插图），配合 Google Colab 可运行的 Jupyter Notebook，覆盖从 token 原理到模型微调的完整 LLM 技术栈。

### 书籍定位
- 🎯 **目标读者**: 有 Python 基础、想深入理解 LLM 原理和实践的开发者/数据科学家
- 📊 **难度曲线**: 由浅入深，前 3 章建立基础概念，中间章节展开应用，最后 3 章进入模型训练/微调
- 💻 **运行环境**: Google Colab (T4 GPU, 16GB VRAM 免费) 为主要推荐平台

### 章节结构总览

```
第一部分: 基础概念 (Ch1-3)
  Ch1  语言模型导论        → 加载运行 Phi-3、pipeline 使用
  Ch2  Token 与嵌入        → 分词器对比、词嵌入、文本嵌入、歌曲推荐
  Ch3  Transformer 内部    → 概率分布、采样解码、KV Cache

第二部分: 应用技术 (Ch4-8)
  Ch4  文本分类            → 表示模型/生成模型分类、零样本分类
  Ch5  文本聚类与主题建模   → 嵌入→降维→聚类流程、BERTopic
  Ch6  Prompt 工程         → In-Context Learning、Chain-of-Thought、Tree-of-Thought
  Ch7  高级文本生成技术     → LangChain Chains、Memory、Agents
  Ch8  语义搜索与 RAG      → 稠密检索、重排序、RAG 全流程

第三部分: 模型训练与微调 (Ch9-12)
  Ch9  多模态 LLM          → CLIP、BLIP-2、图像描述、视觉问答
  Ch10 创建文本嵌入模型     → 对比学习、Multiple Negatives Ranking Loss、TSDAE
  Ch11 微调表示模型         → BERT 微调、冻结层策略、NER、Few-shot
  Ch12 微调生成模型         → SFT + PPO/DPO 两步法、QLoRA、偏好对齐
```

---

## 📘 各章详细分析

### 第 1 章 · 语言模型导论

**核心内容**: 建立 LLM 第一印象，快速上手

| 知识点 | 说明 |
|--------|------|
| Phi-3 模型加载 | 使用 `transformers` 库加载 `AutoModelForCausalLM` + `AutoTokenizer` |
| Pipeline 封装 | 通过 `pipeline("text-generation")` 简化推理调用 |
| GPU 推理 | 模型加载到 GPU，使用 T4 (16GB) 运行 |
| 文本生成初体验 | 构造 prompt 并观察模型输出 |

**动手实践**: 在 Colab 上加载并运行微软 Phi-3 模型，体验 LLM 文本生成

---

### 第 2 章 · Token 与词嵌入

**核心内容**: 深入理解 LLM 的"语言单元"

| 知识点 | 说明 |
|--------|------|
| 分词器对比 | 比较不同 LLM 的分词器（GPT、BERT、LLaMA 等），理解 subword 分词（BPE/WordPiece） |
| 上下文词嵌入 | 加载 BERT 观察同一词在不同上下文中的动态嵌入变化 |
| 文本嵌入 | 使用 sentence-transformers 生成句子/文档级嵌入向量 |
| 嵌入空间探索 | Word Embeddings 之外——用嵌入做歌曲推荐（Spotify 场景） |

**关键洞察**: 
- Token ≠ 单词，一个单词可能被切分为多个 subword token
- 相同单词在不同上下文的嵌入向量差异巨大（如 "bank" 在金融 vs 河流语境）
- 文本嵌入（sentence embeddings）是后续分类、聚类、搜索的基础

---

### 第 3 章 · 深入 Transformer 内部

**核心内容**: 剖析生成式 LLM 的 Transformer 架构

| 知识点 | 说明 |
|--------|------|
| 模型输入输出 | 追踪 token 在模型中的流动：输入 → Embedding → Transformer Layers → LM Head → 概率分布 |
| 概率分布采样 | 从 logits 到 token 的选择策略：贪心、温度采样、Top-K、Top-P (nucleus) |
| KV Cache | 键值缓存加速生成的原理：缓存已计算的 Key/Value，避免重复计算 |
| 注意力机制可视化 | 观察 attention weights 理解模型"关注"什么 |

**关键洞察**:
- LLM 本质是"下一个 token 预测器"——每个位置输出下一个 token 的概率分布
- KV Cache 是推理加速的核心技术，将自回归生成的复杂度从 O(n²) 降至 O(n)
- 温度参数控制输出的随机性：低温更确定，高温更有创造性

---

### 第 4 章 · 文本分类

**核心内容**: 用表示模型和生成模型做文本分类

| 方法 | 技术栈 | 说明 |
|------|--------|------|
| 任务特定模型 | 微调 BERT 分类头 | 传统有监督分类，准确率高 |
| 嵌入 + 分类器 | Sentence Embedding + Logistic Regression | 轻量级方案，无需 GPU 微调 |
| 平均嵌入 + 余弦相似度 | 每类取平均向量 → 余弦匹配 | 最简单的分类器 |
| 零样本分类 | 自然语言描述标签 | 无需训练数据，用描述匹配类别 |
| 生成模型分类 | T5/FLAN-T5 (Encoder-Decoder) | 把分类转化为文本生成任务 |
| ChatGPT 分类 | OpenAI API | 调用 GPT 做分类（注意 token 成本） |

**关键对比**:
- 表示模型分类：快、省资源，适合固定类别
- 生成模型分类：灵活、可解释，但慢且贵
- 零样本分类：更换标签描述会影响结果——"A very negative movie review" vs "Negative"

---

### 第 5 章 · 文本聚类与主题建模

**核心内容**: 无监督文本分析的标准流程

**标准聚类 Pipeline**:
```
文档 → 嵌入（Sentence Transformer）→ 降维（UMAP）→ 聚类（HDBSCAN）→ 主题提取
```

| 步骤 | 工具/方法 | 作用 |
|------|-----------|------|
| 1. 嵌入文档 | `sentence-transformers` | 将文档转为高维向量 |
| 2. 降维 | UMAP | 从 384-768 维降至 5-50 维，保留局部结构 |
| 3. 聚类 | HDBSCAN | 密度聚类，自动识别离群点 |
| 4. 主题提取 | c-TF-IDF | 基于词频-逆文档频率提取主题关键词 |
| 5. 可视化 | 2D/3D 散点图、词云 | 直观展示聚类结果 |

**BERTopic 框架**:
- 模块化设计，可替换每个环节的模型
- 支持主题搜索（`find_topics()`）
- 高级表示模型：KeyBERTInspired（关键词增强）、Maximal Marginal Relevance（多样性优化）
- 文本生成增强：用 FLAN-T5 或 OpenAI API 生成主题描述

**应用场景**: arXiv 论文分类（计算语言学类别）、客服对话聚类、舆情分析

---

### 第 6 章 · Prompt 工程

**核心内容**: 系统化的提示词优化方法论

```
Prompt 基本要素:
├── 指令 (Instruction): 你要模型做什么
├── 上下文 (Context): 背景信息
├── 输入数据 (Input Data): 待处理的内容
└── 输出指示 (Output Indicator): 期望的输出格式
```

| 技术 | 说明 | 示例 |
|------|------|------|
| **In-Context Learning** | 在 prompt 中提供示例，无需微调 | Few-shot 分类、翻译 |
| **Chain Prompting** | 把复杂问题拆解为多步子问题 | 多轮对话式推理 |
| **Chain-of-Thought (CoT)** | 要求模型"先思考再回答" | 数学推理、逻辑判断 |
| **Zero-shot CoT** | 仅加 "Let's think step by step" | 无需示例的推理增强 |
| **Tree-of-Thought (ToT)** | 探索多条推理路径，选择最优 | 复杂规划、博弈决策 |
| **输出验证** | 提供示例约束输出格式 | JSON 结构化输出 |
| **受限采样** | 语法/格式约束 | 强制生成合法 JSON/代码 |

**关键洞察**:
- CoT 能将模型的推理能力提升 20-50%（取决于任务）
- In-Context Learning 的示例顺序和格式对效果有显著影响
- 复杂任务应拆解为 Chain Prompting，而非一次性大 prompt

---

### 第 7 章 · 高级文本生成技术

**核心内容**: 超越单一 prompt 的生成范式

| 技术 | 说明 |
|------|------|
| **Chains (链)** | 将多个 LLM 调用串联，形成处理管道 |
| **Multiple Chains** | 并行或条件分支的链组合 |
| **Memory 机制** | 让 LLM "记住"对话历史 |

**三种 Memory 类型**:
| 类型 | 机制 | 适用场景 |
|------|------|----------|
| ConversationBuffer | 保存完整对话历史 | 短对话 |
| ConversationBufferWindow | 仅保留最近 K 轮 | 长对话，控制 token 消耗 |
| ConversationSummary | 用 LLM 压缩历史为摘要 | 超长对话，信息保留 |

**LLM Agents**: 赋予 LLM 使用工具的能力（搜索、计算器、API 调用），实现自主决策和执行。

---

### 第 8 章 · 语义搜索与 RAG

**核心内容**: 现代搜索 + 检索增强生成全流程

#### 稠密检索 Pipeline
```
1. 文档分块 (Chunking) → 2. 嵌入 (Embedding) → 3. 构建索引 (Faiss/USearch) → 4. 查询搜索
```

| 步骤 | 技术 |
|------|------|
| 文本分块 | 按段落/固定 token 数切分，保持语义完整性 |
| 嵌入生成 | Sentence Transformer 生成向量 |
| 向量索引 | Faiss (Facebook AI Similarity Search) |
| 查询 | 用户查询 → 嵌入 → 向量相似度搜索 → Top-K 文档 |

#### 稠密检索的局限
- 对精确关键词匹配不敏感
- 可能返回语义相似但内容不相关的文档
- **解决方案**: 重排序 (Reranking)——用 Cross-Encoder 对初步检索结果精排

#### RAG (Retrieval-Augmented Generation)
```
用户查询 → 向量检索 → Top-K 文档 → 拼接 Prompt → LLM 生成 → 带来源引用的回答
```

**两种实现**:
1. **基于 API**: 嵌入用 Sentence Transformer + Faiss，生成用 OpenAI/Gemini
2. **全本地**: 嵌入模型 + 本地 LLM（如 Phi-3）+ Faiss 向量库

---

### 第 9 章 · 多模态大语言模型

**核心内容**: 让 LLM "看见"图像

| 模型/技术 | 功能 | 说明 |
|-----------|------|------|
| **CLIP** | 图文对齐 | 将图像和文本映射到同一嵌入空间，用余弦相似度衡量匹配度 |
| **SBERT + CLIP** | 跨模态检索 | 文本搜图、图搜文本 |
| **BLIP-2** | 图像理解 | 结合视觉编码器 + LLM，无需训练视觉-语言连接器 |

**BLIP-2 两大应用**:
1. **图像描述 (Image Captioning)**: 输入图片 → 输出自然语言描述
2. **视觉问答 (VQA)**: 输入图片+问题 → 输出答案

**关键架构**:
- CLIP 训练方式：对比学习，拉近匹配图文对、推远不匹配对
- BLIP-2 使用 Q-Former 作为视觉和语言之间的桥梁

---

### 第 10 章 · 创建文本嵌入模型

**核心内容**: 从零训练和微调嵌入模型

#### 训练嵌入模型的四大要素

| 要素 | 说明 |
|------|------|
| **数据** | 配对数据（如 query-document）、三元组数据（anchor-positive-negative） |
| **模型架构** | Bi-Encoder（双塔模型），常用 BERT/RoBERTa 作为基座 |
| **损失函数** | 核心：让相似样本靠近，不相似样本远离 |
| **评估** | MTEB (Massive Text Embedding Benchmark) |

#### 损失函数对比

| 损失函数 | 适用场景 | 说明 |
|----------|----------|------|
| Cosine Similarity Loss | 有正负标签 | 最大化正样本相似度，最小化负样本 |
| Multiple Negatives Ranking Loss | 仅有正样本对 | 批量内其他样本自动作为负样本（in-batch negatives） |

#### 微调策略

| 方法 | 类型 | 说明 |
|------|------|------|
| 有监督微调 | Supervised | 使用标注的正负样本对 |
| Augmented SBERT | 半监督 | Step1: 微调 Cross-Encoder → Step2: 生成银标数据 → Step3: 训练 Bi-Encoder |
| TSDAE | 无监督 | Transformer-based Denoising AutoEncoder，用加噪-去噪预训练 |

---

### 第 11 章 · 微调表示模型（BERT）

**核心内容**: 实战微调 BERT 做分类和序列标注

| 任务 | 方法 | 关键技术 |
|------|------|----------|
| **有监督分类** | HuggingFace Trainer | 数据 tokenization → 定义评估指标 → 训练 → 评估 |
| **冻结层策略** | Freeze Layers | 冻结 BERT 底层（1-5层），仅微调顶层+分类头，减少过拟合 |
| **Few-shot 分类** | SetFit 风格 | 少量样本微调（每类 8-50 个样本） |
| **MLM 预训练** | Masked Language Modeling | 领域自适应：用领域数据继续预训练 BERT |
| **命名实体识别 (NER)** | Token 分类 | 序列标注：每个 token 预测实体标签 (B-PER, I-LOC...) |

**NER 推荐数据集**:
- `tner/mit_movie_trivia` - 电影相关实体
- `tner/mit_restaurant` - 餐厅相关实体
- `wnut_17` - 社交媒体 NER
- `conll2003` - 经典新闻 NER 基准

**关键洞察**: 冻结底层是微调 BERT 的常用技巧——底层学到的是通用语言特征，顶层学到的是任务特定特征。

---

### 第 12 章 · 微调生成模型

**核心内容**: SFT → 偏好对齐两步微调法

#### 两步微调 Pipeline

```
Step 1: 监督微调 (SFT)
  ├── 数据预处理：指令-回答对
  ├── 模型量化 (Quantization): 4-bit/8-bit 减少显存
  ├── LoRA 配置: rank(r)、alpha、target_modules
  ├── 训练: QLoRA (量化+LoRA) 在消费级 GPU 上微调
  └── 合并 Adapter: 将 LoRA 权重合并回原模型

Step 2: 偏好对齐 (Preference Tuning)
  ├── 数据格式：chosen vs rejected 回答对
  ├── DPO (Direct Preference Optimization): 无需奖励模型，直接从偏好数据学习
  └── PPO (Proximal Policy Optimization): 需要奖励模型，强化学习对齐
```

| 技术 | 作用 | 特点 |
|------|------|------|
| **QLoRA** | 4-bit 量化 + LoRA 低秩适配 | 可在单张 24GB GPU 上微调 7B 模型 |
| **LoRA** | 仅训练低秩矩阵，冻结原模型 | 参数效率高，Adapter 仅几十 MB |
| **SFT** | 让模型学会遵循指令格式 | 基础能力获得 |
| **DPO** | 直接优化偏好，无需奖励模型 | 比 PPO 简单稳定 |
| **PPO** | 强化学习对齐人类偏好 | 经典 RLHF 方法，更灵活 |

---

## 🎁 Bonus 内容（额外进阶材料）

| # | 主题 | 说明 |
|---|------|------|
| 2 | **How Transformer LLMs Work** | DeepLearning.AI 合作课程，详细讲解 Transformer 内部机制 |
| 3 | **A Visual Guide to Quantization** | 图解量化技术：从 FP32 → INT8/INT4，模型压缩原理 |
| 4 | **A Visual Guide to Mamba** | 图解 Mamba 和状态空间模型 (SSM)——Transformer 的潜在替代架构 |
| 5 | **A Visual Guide to Mixture of Experts** | 图解 MoE：稀疏激活、专家路由、负载均衡 |
| 6 | **The Illustrated Stable Diffusion** | 图解 Stable Diffusion：扩散模型、U-Net、文本条件化 |
| 7 | **A Visual Guide to Reasoning LLMs** | 图解推理 LLM：CoT、Self-Consistency、Self-Refine 等推理策略 |
| 8 | **The Illustrated DeepSeek-R1** | 图解 DeepSeek-R1：纯强化学习推理训练、GRPO 算法 |
| 9 | **A Visual Guide to LLM Agents** | 图解 LLM Agent：工具使用、规划、记忆、多 Agent 协作 |

---

## 🔑 核心知识点总结

### 技术全景图

```
LLM 技术栈:
┌──────────────────────────────────────────────┐
│  应用层: 分类 · 聚类 · 搜索 · RAG · Agent    │
├──────────────────────────────────────────────┤
│  交互层: Prompt Engineering · CoT · ToT      │
├──────────────────────────────────────────────┤
│  模型层: Transformer · Tokenizer · Embedding │
├──────────────────────────────────────────────┤
│  训练层: SFT · LoRA · QLoRA · DPO · PPO     │
├──────────────────────────────────────────────┤
│  推理层: KV Cache · Quantization · Sampling  │
└──────────────────────────────────────────────┘
```

### 关键模型清单

| 模型 | 类型 | 用途 |
|------|------|------|
| Phi-3 | 生成式 LLM | 轻量级文本生成 |
| BERT/RoBERTa | 表示模型 | 分类、嵌入、NER |
| T5/FLAN-T5 | Encoder-Decoder | 分类、生成、翻译 |
| Sentence-BERT (SBERT) | 嵌入模型 | 语义相似度、搜索 |
| CLIP | 多模态 | 图文对齐 |
| BLIP-2 | 多模态 LLM | 图像描述、VQA |
| GPT-3.5/4 | 生成式 LLM API | 通用生成、分类 |

### 关键 Python 库

| 库 | 用途 |
|----|------|
| `transformers` | 模型加载、训练、推理 |
| `sentence-transformers` | 文本嵌入生成 |
| `datasets` | 数据集加载和处理 |
| `faiss` / `usearch` | 向量相似度搜索 |
| `bertopic` | 主题建模 |
| `langchain` | Chains、Memory、Agents |
| `peft` (LoRA) | 参数高效微调 |
| `bitsandbytes` | 模型量化 |
| `umap-learn` | 降维可视化 |
| `hdbscan` | 密度聚类 |

---

## 📚 推荐学习路径

```
入门 (1-2周)        进阶 (2-3周)        高级 (3-4周)
─────────          ──────────          ──────────
Ch1: LLM 初体验     Ch4: 文本分类        Ch10: 创建嵌入模型
Ch2: Token & 嵌入   Ch5: 聚类&主题建模   Ch11: 微调 BERT
Ch3: Transformer    Ch6: Prompt 工程     Ch12: 微调 LLM
                    Ch7: Chains/Agents   Bonus: 深入各专题
                    Ch8: RAG
                    Ch9: 多模态
```

---

> 📌 本文档基于原书代码仓库 v1.9.0 版本提取分析，记录了核心技术概念和实践方法。建议结合原书代码 Notebook 在 Google Colab 上动手实践。
