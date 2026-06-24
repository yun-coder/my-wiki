# AI 知识库

> 从 LangChain 中文网 **301 个 Provider 全部收录** + 拆分整理为 10 个知识分类。
> 每个 provider 配有中文名、官方文档链接，并说明"是什么、怎么用、什么场景"。

---

## 📊 知识库统计

**总计 354 个 provider**，分类如下：

| 分类 | 数量 | 说明 |
|------|------|------|
| `01-chat-models/` | 40 个 | 聊天模型：能跟你对话的 AI（GPT-4、Claude、Qwen、GLM、DeepSeek、Minimax 等） |
| `02-embedding-models/` | 4 个 | 嵌入模型：把文字变成向量，用于相似度搜索 |
| `03-vector-stores/` | 66 个 | 向量数据库：存文字向量，支持语义搜索（Chroma、Milvus、Qdrant、Pinecone、Weaviate 等） |
| `04-document-loaders/` | 70 个 | 文档加载器：把 PDF/Word/网页/Notion/Slack/YouTube 等转成 AI 能理解的文本 |
| `05-tools/` | 30 个 | AI 工具：让 AI 能搜索网页、运行代码、调用 API、发邮件、抓取数据等 |
| `06-memory/` | 3 个 | 记忆系统：让 AI 记住对话历史，支持长期记忆 |
| `07-agent-orchestration/` | 1 个 | Agent 编排：让多个 AI 协作完成任务（DSPy 等） |
| `08-monitoring/` | 55 个 | 监控与评估：追踪 LLM 调用、Token 用量、响应质量、可观测性 |
| `09-deployment/` | 66 个 | 部署与推理：把模型跑起来（vLLM、TGI、Modal、Replicate、AWS、GCP、Azure、阿里云、腾讯云、火山引擎等） |
| `10-search-retrieval/` | 19 个 | 搜索与检索：搜索引擎集成（Google、Bing、Brave、Exa、Tavily 等） |

---

## 🔗 知识链路图（RAG 系统为例）

```
[用户提问]
   ↓
[05-tools/] 搜索引擎 (Brave/Google/Exa)
   ↓
[10-search-retrieval/] 检索增强 (Tavily/You)
   ↓
[04-document-loaders/] 文档加载 (Notion/PDF/YouTube)
   ↓
[02-embedding-models/] 文本转向量 (OpenAI/Cohere)
   ↓
[03-vector-stores/] 存到向量库 (Chroma/Milvus)
   ↓
[01-chat-models/] 调用 LLM (GPT-4/Claude/Qwen)
   ↓
[06-memory/] 记住上下文 (Mem0/Zep)
   ↓
[08-monitoring/] 追踪质量 (LangSmith/Helicone)
   ↓
[09-deployment/] 部署上线 (vLLM/Modal/AWS)
   ↓
[最终回答]
```

---

## 📂 目录结构

```
D:\学习院\my-wiki\AI知识库\
├── 00-overview/README.md          ← 本文件
├── 01-chat-models/01-chat-models-guide.md
├── 02-embedding-models/02-embedding-models-guide.md
├── 03-vector-stores/03-vector-stores-guide.md
├── 04-document-loaders/04-document-loaders-guide.md
├── 05-tools/05-tools-guide.md
├── 06-memory/06-memory-guide.md
├── 07-agent-orchestration/07-agent-orchestration-guide.md
├── 08-monitoring/08-monitoring-guide.md
├── 09-deployment/09-deployment-guide.md
└── 10-search-retrieval/10-search-retrieval-guide.md
```

---

## 🎯 使用方式

1. **学习 AI 技术栈**：从 01 顺序往下看，了解构建 AI 应用需要哪些组件
2. **选型参考**：想用某个技术（如 RAG、Agent），直接查对应分类的指南
3. **项目搭建**：根据知识链路图，挑选合适的 provider 组合

---

**最后更新**: 2026-06-24 (新增视频生成专项)
**数据来源**:
- https://www.langchain.com.cn/docs/integrations/providers/ (LangChain 301 provider)
- Chrome 书签 + 真实 Agnes 生成 (视频生成专项 9 个)


---

## 🎬 视频生成专项(2026-06-24)

基于 Chrome 书签扫描 + 真实 Agnes 生成,产出 9 个视频生成知识点:

| 文件 | 内容 |
|------|------|
| `11-video-generation/seedance.md` | 字节 Seedance + ArcReel + Prompt 库 |
| `11-video-generation/short-drama-tools.md` | 短剧分镜工具(Toonflow/LumenX/TypeTale 等) |
| `11-video-generation/one-click-generators.md` | 一键生成器(MoneyPrinterPlus/Story-Flicks 等) |
| `11-video-generation/subtitle-notes.md` | 字幕与笔记工具(BiliNote/VideoCaptioner 等) |
| `11-video-generation/cogvideo-zhipu.md` | 智谱 CogVideo |
| `11-video-generation/hunyuan-tencent.md` | 腾讯混元视频+3D |
| `11-video-generation/vidu.md` | 生数 Vidu |
| `11-video-generation/ffmpeg.md` | 视频工具链(FFmpeg) |
| `11-video-generation/huashu-skills.md` | 花叔创作 Skills 合集 |

## 🎬 视频生成专项

基于 Chrome 书签扫描 + 真实 Agnes 生成,产出 9 个视频生成知识点:

- `cogvideo-zhipu.md` (2947 字节)
- `ffmpeg.md` (2119 字节)
- `huashu-skills.md` (2790 字节)
- `hunyuan-tencent.md` (2018 字节)
- `one-click-generators.md` (4169 字节)
- `seedance.md` (2596 字节)
- `short-drama-tools.md` (2750 字节)
- `subtitle-notes.md` (5297 字节)
- `vidu.md` (1601 字节)
