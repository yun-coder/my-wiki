# 嵌入模型（Embedding Models）

> 把文字变成数字向量，用于语义搜索和相似度计算
> 来源: LangChain 中文网集成目录
> 总数: 3 个集成

---

## 集成列表

- **Jina AI** (`pg_embedding
- **pg_embedding**`): [文档](https://www.langchain.com.cn/docs/integrations/providers/jina/)
- **Nomic** (`nomic`): [文档](https://www.langchain.com.cn/docs/integrations/providers/nomic/)
- **Voyage AI** (`voyageai`): [文档](https://www.langchain.com.cn/docs/integrations/providers/voyageai/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import jina
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

- `jina`
- `embedchain`