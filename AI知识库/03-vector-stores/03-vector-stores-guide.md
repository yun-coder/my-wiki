# 向量存储（Vector Stores）

> 专门存储向量数据的数据库，支持语义搜索
> 来源: LangChain 中文网集成目录
> 总数: 23 个集成

---

## 集成列表

- **阿里云** (`marqo`
- **marqo**): [文档](https://www.langchain.com.cn/docs/integrations/providers/alibaba_cloud/)
- **AnalyticDB** (`kdbai`
- **kdbai**): [文档](https://www.langchain.com.cn/docs/integrations/providers/analyticdb/)
- **百度** (`dashvector`
- **dashvector**): [文档](https://www.langchain.com.cn/docs/integrations/providers/baidu/)
- **Apache Cassandra** (`infinispanvs`
- **infinispanvs**): [文档](https://www.langchain.com.cn/docs/integrations/providers/cassandra/)
- **Chroma** (`opensearch`
- **opensearch**): [文档](https://www.langchain.com.cn/docs/integrations/providers/chroma/)
- **ClickHouse** (`epsilla`
- **epsilla**): [文档](https://www.langchain.com.cn/docs/integrations/providers/clickhouse/)
- **Databricks** (`infino`
- **infino**): [文档](https://www.langchain.com.cn/docs/integrations/providers/databricks/)
- **Elasticsearch** (`infinity`
- **infinity**): [文档](https://www.langchain.com.cn/docs/integrations/providers/elasticsearch/)
- **FaunaDB** (`myscale`
- **myscale**): [文档](https://www.langchain.com.cn/docs/integrations/providers/fauna/)
- **LanceDB** (`apache_doris`
- **apache_doris**): [文档](https://www.langchain.com.cn/docs/integrations/providers/lancedb/)
- **Meilisearch** (`kinetica`
- **kinetica**): [文档](https://www.langchain.com.cn/docs/integrations/providers/meilisearch/)
- **Milvus** (`arangodb
- **arangodb**`
- **lantern**): [文档](https://www.langchain.com.cn/docs/integrations/providers/milvus/)
- **MongoDB Atlas** (`astradb`
- **astradb**): [文档](https://www.langchain.com.cn/docs/integrations/providers/mongodb_atlas/)
- **PGVector** (`motherduck`
- **motherduck**): [文档](https://www.langchain.com.cn/docs/integrations/providers/pgvector/)
- **Pinecone** (`awadb`
- **awadb**): [文档](https://www.langchain.com.cn/docs/integrations/providers/pinecone/)
- **Qdrant** (`hologres`
- **hologres**): [文档](https://www.langchain.com.cn/docs/integrations/providers/qdrant/)
- **Redis** (`neo4j`
- **neo4j**): [文档](https://www.langchain.com.cn/docs/integrations/providers/redis/)
- **Supabase** (`annoy`
- **annoy**): [文档](https://www.langchain.com.cn/docs/integrations/providers/supabase/)
- **Typesense** (`dingo`
- **dingo**): [文档](https://www.langchain.com.cn/docs/integrations/providers/typesense/)
- **Vearch** (`falkordb`
- **falkordb**): [文档](https://www.langchain.com.cn/docs/integrations/providers/vearch/)
- **Vespa** (`ontotext_graphdb`
- **ontotext_graphdb**): [文档](https://www.langchain.com.cn/docs/integrations/providers/vespa/)
- **Weaviate** (`jaguar`
- **jaguar**): [文档](https://www.langchain.com.cn/docs/integrations/providers/weaviate/)
- **Zilliz** (`bageldb`
- **bageldb**): [文档](https://www.langchain.com.cn/docs/integrations/providers/zilliz/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import alibaba_cloud
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
- `neo4j`

- `cassandra`
- `clickhouse`
- `lantern`
- `meilisearch`
- `milvus`
- `neo4j`
- `pg_embedding`
- `pinecone`
- `qdrant`
- `redis`
- `rockset`
- `singlestoredb`
- `starrocks`
- `tidb`
- `tigergraph`
- `tigris`
- `transwarp`
- `usearch`
- `vdms`
- `vearch`
- `vespa`
- `weaviate`
- `zilliz`
- `analyticdb`
- `databricks`
- `fauna`
- `lancedb`
- `mongodb_atlas`
- `pgvector`
- `supabase`
- `typesense`
- `bagel`
- `cube`
- `snowflake`
- `tair`
- `xata`
- `yellowbrick`
- `yeagerai`
- `vlite`
- `upstash`
- `ragatouille`
- `momento`
- `tigris`

## 补充集成（来自 LangChain 中文网）
- `neo4j`

- `arangodb`
- `atlas`
- `elasticsearch`
- `neo4j`
- `semadb`