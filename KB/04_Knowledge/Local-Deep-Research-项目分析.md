# Local Deep Research 项目分析

> **项目信息**
> - 名称: Local Deep Research (LDR)
> - 仓库: https://github.com/LearningCircuit/local-deep-research
> - 许可: MIT
> - 定位: 本地部署的 AI 深度研究助手，支持多 LLM、多搜索引擎，注重隐私和安全
> - 核心作者: LearningCircuit 社区
> - Docker Pulls: 100K+ | PyPI Downloads: 10K+
> - 社区: Discord + Reddit (r/LocalDeepResearch)

---

## 📖 一、项目定位

**Local Deep Research** 是一个**可本地部署、支持任意 LLM、注重隐私安全的 AI 深度研究助手**。它能自动完成多轮搜索、信息综合、引用管理，生成带引用来源的研究报告。

### 核心价值主张
```
你的提问 → 多搜索引擎查询 → 内容提取与分析 → LLM 综合推理 → 带引用的研究报告
```

| 维度 | 特点 |
|------|------|
| **隐私** | 零遥测、零追踪、零分析 SDK。可全本地运行（Ollama + SearXNG） |
| **安全** | AES-256 SQLCipher 加密数据库、30+ CI 安全扫描器 |
| **灵活** | 支持 10 种 LLM 提供商、25+ 搜索引擎、30+ 研究策略 |
| **知识积累** | 每次研究结果可下载保存、索引，形成个人加密知识库 |
| **开放** | MIT 协议，pip/Docker/Unraid 多方式部署 |

---

## 🏗️ 二、技术架构

### 技术栈总览

```
┌──────────────────────────────────────────────────────┐
│                    前端 (Vanilla JS)                  │
│  Vite 构建 · 30+ CSS 主题 · WebSocket 实时更新       │
│  Flask Jinja2 模板渲染 · 模块化 JS 组件              │
├──────────────────────────────────────────────────────┤
│                    后端 (Python/Flask)                │
│  REST API · WebSocket · MCP Server · Benchmark CLI   │
├──────────┬──────────┬──────────┬────────────────────┤
│ 搜索层    │ LLM 层    │ 数据层    │ 安全层             │
│ 25+ 引擎  │ 10 提供商  │ SQLCipher │ 30+ CI 扫描器     │
│ 30+ 策略  │ 费用追踪  │ FAISS     │ SSRF/CSRF 防护    │
│ 自适应速率│ 自动发现  │ 用户隔离   │ 账户锁定           │
└──────────┴──────────┴──────────┴────────────────────┘
```

### 语言与框架
| 层 | 技术 | 说明 |
|----|------|------|
| **后端** | Python + Flask | 主业务逻辑，模块化设计 |
| **前端** | Vanilla JS + Vite | 零框架依赖，ESLint |
| **构建** | PDM (Python) + npm (JS) | 双包管理器 |
| **部署** | Docker Compose / pip / Unraid | 支持 GPU/CPU |
| **数据库** | SQLCipher (SQLite 加密) | 每用户独立加密库 |

---

## 🔍 三、搜索系统架构（核心亮点）

### 3.1 30+ 研究策略

LDR 最核心的差异化能力在于**可插拔的搜索策略系统**。不同策略适用于不同场景：

```
策略分类：
├── 基础策略
│   ├── standard_strategy         → 通用搜索+综合
│   ├── rapid_search_strategy     → 快速搜索（30s-3min）
│   └── direct_search_strategy    → 直接搜索不综合
│
├── 迭代推理
│   ├── focused_iteration_strategy    → 聚焦迭代（SimpleQA ~95%）
│   ├── iterative_reasoning_strategy  → 迭代推理
│   └── iterative_refinement_strategy → 迭代精炼
│
├── 并行搜索
│   ├── parallel_search_strategy      → 多引擎并行搜索
│   └── parallel_constrained_strategy → 并行+约束
│
├── 问题分解
│   ├── adaptive_decomposition_strategy  → 自适应问题分解
│   ├── recursive_decomposition_strategy → 递归分解
│   ├── smart_decomposition_strategy     → 智能分解
│   └── smart_query_strategy             → 智能查询构造
│
├── 证据驱动
│   ├── evidence_based_strategy      → 基于证据的搜索
│   ├── improved_evidence_based_strategy → 改进版证据搜索
│   └── constraint_*-strategy        → 约束引导搜索
│
├── 置信度系统
│   ├── dual_confidence_strategy     → 双重置信度验证
│   ├── concurrent_dual_confidence   → 并发双重置信度
│   └── dual_confidence_with_rejection → 置信度+拒绝机制
│
├── 专业领域
│   ├── browsecomp_*_strategy    → BrowseComp 基准优化
│   ├── news_strategy            → 新闻研究
│   └── source_based_strategy    → 基于来源的研究
│
├── AI 驱动
│   ├── langgraph_agent_strategy → LangGraph 自主 Agent ★新
│   └── llm_driven_modular_strategy → LLM 驱动模块化
│
└── 特殊
    ├── iterdrag_strategy        → ItermDrag 优化
    ├── mcp_strategy             → MCP 协议策略
    └── modular_strategy         → 模块化组合
```

### 3.2 约束检查系统（Constraint Checking）

这是 LDR 搜索质量的**核心机制**：

```
搜索结果 → 约束分析 → 证据评估 → 置信度计算 → 质量判定
                                              ├── 通过 → 输出
                                              └── 未通过 → 重新搜索/拒绝
```

| 检查器 | 功能 |
|--------|------|
| `threshold_checker` | 置信度阈值检查 |
| `strict_checker` | 严格约束检查 |
| `dual_confidence_checker` | 双重置信度验证 |
| `evidence_analyzer` | 证据质量分析 |
| `rejection_engine` | 拒绝低质量结果 |

### 3.3 候选探索器

```
约束引导探索器 → 根据问题约束引导搜索方向
多样性探索器   → 确保信息来源多样性
自适应探索器   → 根据中间结果动态调整搜索策略
并行探索器     → 多方向并行搜索
渐进探索器     → 逐步加深搜索深度
```

---

## 🌐 四、25+ 搜索引擎整合

### 免费学术引擎
| 引擎 | 数据源 | 特点 |
|------|--------|------|
| **arXiv** | 物理学/数学/CS 预印本 | 学术研究首选 |
| **PubMed** | 生物医学文献 | NIH 维护，公共领域 |
| **Semantic Scholar** | 跨学科学术搜索 | 含引用数据 |
| **NASA ADS** | 天体物理/物理/天文 | 专业天文文献 |
| **Zenodo** | 开放研究数据 | 数据集、软件 |
| **PubChem** | 化学/生物化学 | NIH 公共数据库 |
| **OpenAlex** | 学术元数据 280K+ 来源 | CC0 开放 |
| **OpenLibrary** | 开放图书 | 互联网档案馆 |

### 通用搜索
| 引擎 | 说明 |
|------|------|
| **SearXNG** | 元搜索引擎，隐私友好，推荐部署 |
| **Wikipedia** | 维基百科 |
| **DuckDuckGo** | 隐私搜索引擎 |
| **Mojeek** | 独立搜索引擎 |
| **Wayback Machine** | 历史网页档案 |
| **GitHub** | 代码仓库搜索 |
| **Stack Exchange** | 技术问答 |
| **The Guardian** | 新闻搜索 |
| **Wikinews** | 维基新闻 |
| **Gutenberg** | 免费电子书 |

### 商业/高级引擎
| 引擎 | 说明 |
|------|------|
| **Tavily** | AI 优化搜索 |
| **Brave Search** | 隐私优先网页搜索 |
| **Google (SerpAPI/PSE)** | 需 API Key |
| **Exa** | AI 原生搜索 |
| **ScaleSerp** | SERP API |
| **Serper** | Google 搜索 API |

### 自定义源
| 类型 | 说明 |
|------|------|
| **Local Documents** | 本地文档 AI 搜索 |
| **LangChain Retrievers** | 任意向量库/数据库集成 |
| **Elasticsearch** | ES 全文搜索 |
| **Paperless** | 文档管理系统集成 |
| **Meta Search** | 多引擎智能组合 |

### 搜索引擎架构设计

```python
# 工厂 + 注册表模式
SearchEngineFactory  →  EngineRegistry
                           ├── arXivEngine
                           ├── PubMedEngine
                           ├── WikipediaEngine
                           ├── BraveEngine
                           ├── SearXNEngine
                           └── ... (25+)

# 自适应速率限制
RateLimiter → LLM驱动的自适应等待
            → 跨引擎协调
            → 学习最佳请求间隔
```

---

## 🤖 五、LLM 集成（10 种提供商）

### 本地模型
| 提供商 | 接口 | 默认地址 |
|--------|------|----------|
| **Ollama** | 原生 API | `http://localhost:11434` |
| **LM Studio** | OpenAI 兼容 | `http://localhost:1234/v1` |
| **llama.cpp** | OpenAI 兼容 (llama-server) | `http://localhost:8080/v1` |

### 云端模型
| 提供商 | 说明 |
|--------|------|
| **OpenAI** | GPT-4, GPT-3.5 |
| **Anthropic** | Claude 3 |
| **Google** | Gemini |
| **OpenRouter** | 100+ 模型统一接口 |
| **xAI** | Grok |
| **IONOS** | 欧洲云提供商 |
| **Custom OpenAI Endpoint** | 任意 OpenAI 兼容 API |

### LLM 模块设计

```
LLM Registry
├── auto_discovery      → 自动发现本地运行的服务
├── provider_base       → 统一接口抽象
├── openai_base         → OpenAI 兼容层（复用）
└── implementations/
    ├── ollama.py       → Ollama 原生 API
    ├── openai.py       → OpenAI
    ├── anthropic.py    → Anthropic
    ├── google.py       → Google Gemini
    ├── openrouter.py   → OpenRouter
    ├── lmstudio.py     → LM Studio
    ├── llamacpp.py     → llama.cpp HTTP
    ├── xai.py          → xAI
    ├── ionos.py        → IONOS
    └── custom_openai_endpoint.py
```

---

## 🔒 六、安全体系（30+ 安全扫描器）

这是该项目的另一大亮点——**工业级安全实践**。

### 安全扫描矩阵
| 类别 | 工具 | 用途 |
|------|------|------|
| **代码分析** | CodeQL, Semgrep, DevSkim, Bearer | SAST 静态分析 |
| **密钥检测** | Gitleaks | 防止密钥泄露 |
| **依赖扫描** | OSV-Scanner, npm-audit, Retire.js | 已知漏洞检测 |
| **容器安全** | Trivy, Dockle, Hadolint, Checkov | 镜像/部署安全 |
| **运行时安全** | OWASP ZAP, Zizmor | Web 安全/CI 安全 |
| **供应链** | Cosign 签名, SLSA 溯源, SBOM | 镜像完整性验证 |

### 应用层安全
| 机制 | 实现 |
|------|------|
| **SQLCipher 加密** | AES-256 数据库加密，零知识架构 |
| **用户隔离** | 每用户独立加密数据库 |
| **CSRF 防护** | 全局 CSRF Token |
| **SSRF 防护** | URL 验证、网络请求过滤 |
| **账户锁定** | 登录失败锁定机制 |
| **密码策略** | 密码复杂度验证 |
| **会话管理** | 会话级凭据生命周期 |
| **文件验证** | 上传文件类型/内容校验 |
| **数据脱敏** | 日志敏感信息脱敏 |
| **路径验证** | 路径遍历防护 |
| **安全头** | HTTP Security Headers |

### 隐私承诺
- ❌ 无遥测
- ❌ 无分析
- ❌ 无追踪
- ❌ 无崩溃上报
- ❌ 无外部脚本
- ✅ robots.txt 尊重
- ✅ 诚实的 User-Agent

---

## 📡 七、MCP Server（Claude 集成）

### MCP 工具列表
| 工具                    | 描述                               | 耗时        | LLM 成本 |
| --------------------- | -------------------------------- | --------- | ------ |
| `search`              | 直接查询特定搜索引擎（arxiv/pubmed/wiki...） | 5-30s     | 无      |
| `quick_research`      | 快速研究摘要                           | 1-5 min   | 有      |
| `detailed_research`   | 详细分析                             | 5-15 min  | 有      |
| `generate_report`     | 完整报告                             | 10-30 min | 有      |
| `analyze_documents`   | 搜索本地文档                           | 30s-2min  | 有      |
| `list_search_engines` | 列出可用引擎                           | 即时        | 无      |
| `list_strategies`     | 列出研究策略                           | 即时        | 无      |
| `get_configuration`   | 获取当前配置                           | 即时        | 无      |

### 配置示例（Claude Code）
```json
{
  "mcpServers": {
    "local-deep-research": {
      "command": "ldr-mcp",
      "env": {
        "LDR_LLM_PROVIDER": "ollama",
        "LDR_LLM_OLLAMA_URL": "http://localhost:11434"
      }
    }
  }
}
```

---

## 📊 八、基准测试系统

### 内置 Benchmark
| 数据集 | 类型 | 说明 |
|--------|------|------|
| SimpleQA | 事实性问答 | OpenAI 发布，衡量事实准确度 |
| BrowseComp | Web 浏览能力 | 复杂 Web 搜索任务 |
| X-Bench DeepSearch | 综合深度搜索 | 多维度评估 |
| Custom Dataset | 自定义 | 用户自定义数据集模板 |

### Benchmark 架构
```
Benchmark Runner
├── Dataset Loader → SimpleQA / BrowseComp / Custom
├── Strategy Runner → 执行研究策略
├── Grader → 评估答案质量
├── Metrics Calculator → 准确率/效率/成本
└── Visualization → 结果可视化
```

### 已知性能数据
| 配置 | SimpleQA 准确率 |
|------|----------------|
| gpt-4.1-mini + SearXNG + focused_iteration | 90-95% |
| gpt-4.1-mini + Tavily + focused_iteration | 90-95% |
| gemini-2.0-flash-001 + SearXNG | 82% |

### Optuna 超参优化
LDR 集成了 Optuna 自动调优，可优化搜索参数以达到最佳准确率。

---

## 📚 九、知识库与文档管理

### 研究库（Research Library）
```
研究完成 → 下载来源 → 文本提取 → 索引嵌入 → 可搜索知识库
                                              ├── 跨文档搜索
                                              ├── 语义相似度
                                              └── 知识累积增长
```

### 文档下载器
| 下载器 | 源 |
|--------|-----|
| `arxiv_downloader` | arXiv PDF |
| `pubmed_downloader` | PubMed 文章 |
| `semantic_scholar_downloader` | Semantic Scholar |
| `biorxiv_downloader` | bioRxiv 预印本 |
| `openalex_downloader` | OpenAlex 元数据 |
| `direct_pdf_downloader` | 直接 PDF 链接 |
| `html_downloader` | 通用 HTML |
| `playwright_html_downloader` | JS 渲染页面 |
| `generic_downloader` | 通用下载 |

### 内容提取器
| 提取器 | 技术 |
|--------|------|
| `readability_extractor` | Mozilla Readability |
| `trafilatura_extractor` | trafilatura（最推荐） |
| `newspaper_extractor` | newspaper3k |
| `justext_extractor` | jusText 算法 |
| `metadata_extractor` | 元数据提取 |
| `pipeline` | 多提取器管道 |

---

## 📰 十、新闻订阅系统

```
订阅话题 → 定时搜索 → AI 过滤相关度 → 生成摘要 → 多格式推送
                                               ├── Markdown 报告
                                               ├── 结构化摘要
                                               └── Apprise 通知
```

| 特性 | 说明 |
|------|------|
| **频率** | 每日/每周/自定义 |
| **类型** | 话题订阅 + 搜索查询订阅 |
| **过滤** | AI 相关度评分 |
| **推荐** | 基于偏好的推荐算法 |
| **评分** | 用户评分反馈系统 |
| **存储** | 卡片式新闻存储 |

---

## 🎨 十一、前端设计

### 技术选型
- **Vanilla JS**（零框架依赖）
- **Vite** 构建打包
- **模块化组件**：components/services/utils 目录分离
- **Flask Jinja2** 模板渲染
- **WebSocket** 实时进度更新

### 30+ 主题系统
```
themes/
├── core/    → light, dark, midnight, sepia, high-contrast
├── dev/     → Catppuccin, Dracula, Gruvbox, Monokai, Nord, One Dark,
│              Solarized, Tokyo Night
├── nature/  → Forest, Lavender, Ocean, Rose, Sunset
└── research/→ Ayu Mirage, Everforest, Flexoki, Kanagawa, Night Owl,
               Palenight, Rosé Pine, Vesper
```

---

## 📦 十二、部署方式对比

| 方式 | 适用场景 | 命令 |
|------|----------|------|
| **Docker Compose** | 推荐，含 Ollama+SearXNG | `docker compose up -d` |
| **Docker GPU** | NVIDIA GPU 加速 | compose + gpu override |
| **pip install** | 开发者、Python 集成 | `pip install local-deep-research` |
| **Unraid** | Unraid NAS 服务器 | 社区模板 |
| **源码运行** | 二次开发 | git clone + PDM |

---

## 🔑 十三、核心架构模式

### 设计模式应用

| 模式 | 应用位置 |
|------|----------|
| **工厂模式** | SearchEngineFactory, RAGServiceFactory, StorageFactory |
| **注册表模式** | EngineRegistry, RetrieverRegistry, TextSplitterRegistry, LoaderRegistry |
| **策略模式** | 30+ SearchStrategy, 多种 ContentExtractor, 多种 CitationHandler |
| **模板方法** | BaseSearchEngine, BaseStrategy, BaseDownloader, BaseExtractor |
| **管道模式** | 内容提取管道 (ExtractionPipeline) |
| **观察者模式** | WebSocket 实时推送研究进度 |
| **中间件模式** | Flask 中间件链 (Auth/Cleanup/Queue/Database) |
| **代理模式** | SafeRequests 封装网络请求 |

### 模块化层次

```
入口层: web/app.py → Flask 应用工厂
路由层: web/routes/ → REST API + 页面路由
服务层: web/services/ → 业务逻辑编排
核心层: advanced_search_system/ → 搜索策略引擎
数据层: database/ → SQLCipher + SQLAlchemy + Alembic
工具层: web_search_engines/, llm/, embeddings/ → 搜索引擎/LLM/嵌入
安全层: security/ → 全栈安全防护
```

---

## 🎯 十四、与 OpenClaw 的联动价值

### MCP 集成路径
```
OpenClaw (Claude Desktop) 
  → MCP Protocol 
  → LDR MCP Server (ldr-mcp)
  → 本地 LLM + 搜索引擎 
  → 深度研究报告
```

### 潜在场景
1. **OpenClaw 中调用 LDR**：通过 MCP 在 Claude 对话中直接发起深度研究
2. **知识库互补**：LDR 的研究结果可导入 OpenClaw 的知识库（my-wiki）
3. **Benchmark 共享**：LDR 的 SimpleQA 测试可用于评估 OpenClaw 的 LLM 配置
4. **搜索能力增强**：LDR 的 25+ 搜索引擎可作为 OpenClaw 的外部搜索插件

---

## 📋 十五、总结

### 项目优势
| 维度 | 评价 |
|------|------|
| **架构设计** | ⭐⭐⭐⭐⭐ 高度模块化、可插拔、策略模式出色 |
| **安全实践** | ⭐⭐⭐⭐⭐ 30+ CI 扫描器、SQLCipher 加密、供应链签名 |
| **隐私保护** | ⭐⭐⭐⭐⭐ 零遥测、全本地可选、用户数据隔离 |
| **模型灵活性** | ⭐⭐⭐⭐⭐ 10 种 LLM 提供商、自动发现 |
| **搜索能力** | ⭐⭐⭐⭐⭐ 25+ 引擎、30+ 策略、自适应速率限制 |
| **代码质量** | ⭐⭐⭐⭐ 良好的分层抽象、工厂+注册表模式 |
| **文档完善** | ⭐⭐⭐⭐ README 详尽、docs 目录完整 |
| **前端现代化** | ⭐⭐⭐ Vanilla JS 可维护但有进步空间 |

### 技术债务/注意点
- 前端为 Vanilla JS，大型项目维护成本较高（可考虑渐进式引入框架）
- 策略数量（30+）较多，部分可能存在维护负担
- 社区 benchmarks 数据量尚在积累中

### 推荐学习点
1. **搜索策略模式**：如何设计可插拔的搜索策略系统
2. **安全最佳实践**：工业级 CI/CD 安全扫描配置
3. **LLM 抽象层**：多提供商统一接口设计
4. **SQLCipher 集成**：Python 中加密数据库的最佳实践
5. **MCP Server 实现**：如何为 Claude 构建工具服务

---

> 📌 本文档基于 2026-05-06 的 main 分支分析，代码约 3000+ 文件。项目活跃开发中，建议定期更新。
