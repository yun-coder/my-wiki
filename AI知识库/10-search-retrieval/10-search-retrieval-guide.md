# 搜索与检索（Search & Retrieval）

> 增强搜索能力，支持 RAG 系统中的文档检索
> 来源: LangChain 中文网集成目录
> 总数: 11 个集成

---

## 集成列表

- **AskNews** (`asknews`): [文档](https://www.langchain.com.cn/docs/integrations/providers/asknews/)
- **Breebs** (`breebs`): [文档](https://www.langchain.com.cn/docs/integrations/providers/breebs/)
- **Context** (`context`): [文档](https://www.langchain.com.cn/docs/integrations/providers/context/)
- **DocArray** (`docarray`): [文档](https://www.langchain.com.cn/docs/integrations/providers/docarray/)
- **Dria** (`dria`): [文档](https://www.langchain.com.cn/docs/integrations/providers/dria/)
- **Embedchain** (`embedchain`): [文档](https://www.langchain.com.cn/docs/integrations/providers/embedchain/)
- **Metal** (`metal`): [文档](https://www.langchain.com.cn/docs/integrations/providers/metal/)
- **RAGatouille** (`ragatouille`): [文档](https://www.langchain.com.cn/docs/integrations/providers/ragatouille/)
- **BM25** (`rank_bm25`): [文档](https://www.langchain.com.cn/docs/integrations/providers/rank_bm25/)
- **Rebuff** (`rebuff`): [文档](https://www.langchain.com.cn/docs/integrations/providers/rebuff/)
- **Vectara** (`vectara`): [文档](https://www.langchain.com.cn/docs/integrations/providers/vectara/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import asknews
# 具体用法请参考各集成文档
```

### 选型建议

| 需求 | 推荐 |
|------|------|
| 快速原型 | Chroma（向量存储）、Unstructured（文档加载） |
| 生产环境 | Qdrant/Pinecone（向量存储） |
| 中文优化 | 阿里云、百度、智谱AI |
| 低成本 | Chroma（本地免费）、Ollama（本地免费） |

---

## 参考

- [LangChain 中文网](https://www.langchain.com.cn/docs/integrations/providers/)


## 补充集成（来自 LangChain 中文网）

- `activeloop_deeplake`
- `arize`
- `searchapi`
- `searx`
- `you`
- `brave_search`
- `duckduckgo_search`
- `exa_search`
- `serpapi`
- `serpapi`
- `you`
- `brave_search`
- `duckduckgo_search`
- `exa_search`