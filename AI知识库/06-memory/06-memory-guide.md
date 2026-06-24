# 记忆系统（Memory）

> 让 AI 记住之前的对话内容，跨会话持久化
> 来源: LangChain 中文网集成目录
> 总数: 3 个集成

---

## 集成列表

- **Motorhead** (`motorhead`): [文档](https://www.langchain.com.cn/docs/integrations/providers/motorhead/)
- **Remembrall** (`remembrall`): [文档](https://www.langchain.com.cn/docs/integrations/providers/remembrall/)
- **Zep** (`zep`): [文档](https://www.langchain.com.cn/docs/integrations/providers/zep/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import motorhead
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
