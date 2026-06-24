# 部署与推理（Deployment & Inference）

> 本地部署、云端推理、模型服务化
> 来源: LangChain 中文网集成目录
> 总数: 24 个集成

---

## 集成列表

- **百川** (`baichuan`): [文档](https://www.langchain.com.cn/docs/integrations/providers/baichuan/)
- **Banana.dev** (`bananadev`): [文档](https://www.langchain.com.cn/docs/integrations/providers/bananadev/)
- **Baseten** (`baseten`): [文档](https://www.langchain.com.cn/docs/integrations/providers/baseten/)
- **字节跳动** (`byte_dance`): [文档](https://www.langchain.com.cn/docs/integrations/providers/byte_dance/)
- **Coze** (`coze`): [文档](https://www.langchain.com.cn/docs/integrations/providers/coze/)
- **C Transformers** (`ctransformers`): [文档](https://www.langchain.com.cn/docs/integrations/providers/ctransformers/)
- **CTranslate2** (`ctranslate2`): [文档](https://www.langchain.com.cn/docs/integrations/providers/ctranslate2/)
- **华为** (`huawei`): [文档](https://www.langchain.com.cn/docs/integrations/providers/huawei/)
- **科大讯飞** (`acreom
- **acreom**`): [文档](https://www.langchain.com.cn/docs/integrations/providers/iflytek/)
- **LittleLLM** (`littlellm`): [文档](https://www.langchain.com.cn/docs/integrations/providers/littlellm/)
- **llama.cpp** (`llamacpp`): [文档](https://www.langchain.com.cn/docs/integrations/providers/llamacpp/)
- **MiniMax** (`minimax`): [文档](https://www.langchain.com.cn/docs/integrations/providers/minimax/)
- **MLX** (`mlx`): [文档](https://www.langchain.com.cn/docs/integrations/providers/mlx/)
- **Modal** (`modal`): [文档](https://www.langchain.com.cn/docs/integrations/providers/modal/)
- **ModelScope** (`modelscope`): [文档](https://www.langchain.com.cn/docs/integrations/providers/modelscope/)
- **Oracle Cloud** (`oci`): [文档](https://www.langchain.com.cn/docs/integrations/providers/oci/)
- **Ollama** (`ollama`): [文档](https://www.langchain.com.cn/docs/integrations/providers/ollama/)
- **OpenLLM** (`openllm`): [文档](https://www.langchain.com.cn/docs/integrations/providers/openllm/)
- **Oracle AI** (`oracleai`): [文档](https://www.langchain.com.cn/docs/integrations/providers/oracleai/)
- **Replicate** (`replicate`): [文档](https://www.langchain.com.cn/docs/integrations/providers/replicate/)
- **RWKV** (`rwkv`): [文档](https://www.langchain.com.cn/docs/integrations/providers/rwkv/)
- **腾讯** (`tencent`): [文档](https://www.langchain.com.cn/docs/integrations/providers/tencent/)
- **Xinference** (`xinference`): [文档](https://www.langchain.com.cn/docs/integrations/providers/xinference/)
- **智谱AI** (`zhipuai`): [文档](https://www.langchain.com.cn/docs/integrations/providers/zhipuai/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import baichuan
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

- `apache`
- `beam`
- `breebs`
- `cerebriumai`
- `chaindesk`
- `chroma`
- `clarifai`
- `cnosdb`
- `cogniswitch`
- `connery`
- `couchbase`
- `ctranslate2`
- `deepsparse`
- `flyte`
- `forefrontai`
- `friendly`
- `gpt4all`
- `html2text`
- `konko`
- `lakefs`
- `labelstudio`
- `maritalk`
- `nlpcloud`
- `octoai`
- `petals`
- `pipelineai`
- `predictionguard`
- `premai`
- `pygmalionai`
- `spark`
- `sparkllm`
- `streamlit`
- `together`
- `writer`
- `mlflow`
- `mlflow_tracking`
- `nlpcloud`
- `octoai`
- `petals`
- `pipelineai`
- `predictionguard`
- `premai`
- `pygmalionai`
- `spark`
- `sparkllm`
- `streamlit`
- `together`
- `writer`
- `cerebriumai`
- `chaindesk`
- `cnosdb`
- `cogniswitch`
- `connery`
- `couchbase`
- `ctranslate2`
- `deepsparse`
- `flyte`
- `forefrontai`
- `friendly`
- `gpt4all`
- `konko`
- `lakefs`
- `labelstudio`
- `maritalk`
- `nlpcloud`
- `octoai`
- `petals`
- `pipelineai`
- `predictionguard`
- `premai`
- `pygmalionai`
- `spark`
- `sparkllm`
- `streamlit`
- `together`
- `writer`

## 补充集成（来自 LangChain 中文网）

- `ainetwork`
- `alchemy`
- `arcee`
- `arcgis`
- `baidu`
- `bittensor`
- `clova`
- `iflytek`
- `ray_serve`
- `yandex`
- `alibaba_cloud`