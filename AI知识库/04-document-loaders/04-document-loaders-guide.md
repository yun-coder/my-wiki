# 文档加载器（Document Loaders）

> 把各种格式的文档转成 AI 能理解的纯文本
> 来源: LangChain 中文网集成目录
> 总数: 31 个集成

---

## 集成列表

- **ArXiv** (`arxiv`): [文档](https://www.langchain.com.cn/docs/integrations/providers/arxiv/)
- **AZLyrics** (`azlyrics`): [文档](https://www.langchain.com.cn/docs/integrations/providers/azlyrics/)
- **BeautifulSoup** (`beautiful_soup`): [文档](https://www.langchain.com.cn/docs/integrations/providers/beautiful_soup/)
- **Bookend AI** (`bookendai`): [文档](https://www.langchain.com.cn/docs/integrations/providers/bookendai/)
- **Browserbase** (`doctran
- **doctran**`): [文档](https://www.langchain.com.cn/docs/integrations/providers/browserbase/)
- **College Confidential** (`college_confidential`): [文档](https://www.langchain.com.cn/docs/integrations/providers/college_confidential/)
- **Confluence** (`confluence`): [文档](https://www.langchain.com.cn/docs/integrations/providers/confluence/)
- **Dedoc** (`dedoc`): [文档](https://www.langchain.com.cn/docs/integrations/providers/dedoc/)
- **Discord** (`discord`): [文档](https://www.langchain.com.cn/docs/integrations/providers/discord/)
- **Docugami** (`docugami`): [文档](https://www.langchain.com.cn/docs/integrations/providers/docugami/)
- **Evernote** (`evernote`): [文档](https://www.langchain.com.cn/docs/integrations/providers/evernote/)
- **Firecrawl** (`firecrawl`): [文档](https://www.langchain.com.cn/docs/integrations/providers/firecrawl/)
- **GitBook** (`gitbook`): [文档](https://www.langchain.com.cn/docs/integrations/providers/gitbook/)
- **GitHub** (`box`): [文档](https://www.langchain.com.cn/docs/integrations/providers/github/)
- **GitLab** (`gitlab`): [文档](https://www.langchain.com.cn/docs/integrations/providers/gitlab/)
- **Project Gutenberg** (`gutenberg`): [文档](https://www.langchain.com.cn/docs/integrations/providers/gutenberg/)
- **Hacker News** (`hacker_news`): [文档](https://www.langchain.com.cn/docs/integrations/providers/hacker_news/)
- **iFixit** (`ifixit`): [文档](https://www.langchain.com.cn/docs/integrations/providers/ifixit/)
- **IMSDB** (`imsdb`): [文档](https://www.langchain.com.cn/docs/integrations/providers/imsdb/)
- **MediaWiki Dump** (`mediawikidump`): [文档](https://www.langchain.com.cn/docs/integrations/providers/mediawikidump/)
- **Notion** (`notion`): [文档](https://www.langchain.com.cn/docs/integrations/providers/notion/)
- **Obsidian** (`obsidian`): [文档](https://www.langchain.com.cn/docs/integrations/providers/obsidian/)
- **Pandas** (`pandas`): [文档](https://www.langchain.com.cn/docs/integrations/providers/pandas/)
- **PubMed** (`pubmed`): [文档](https://www.langchain.com.cn/docs/integrations/providers/pubmed/)
- **Reddit** (`reddit`): [文档](https://www.langchain.com.cn/docs/integrations/providers/reddit/)
- **Slack** (`slack`): [文档](https://www.langchain.com.cn/docs/integrations/providers/slack/)
- **Stack Exchange** (`stackexchange`): [文档](https://www.langchain.com.cn/docs/integrations/providers/stackexchange/)
- **Telegram** (`telegram`): [文档](https://www.langchain.com.cn/docs/integrations/providers/telegram/)
- **Unstructured** (`unstructured`): [文档](https://www.langchain.com.cn/docs/integrations/providers/unstructured/)
- **Wikipedia** (`wikipedia`): [文档](https://www.langchain.com.cn/docs/integrations/providers/wikipedia/)
- **YouTube** (`youtube`): [文档](https://www.langchain.com.cn/docs/integrations/providers/youtube/)

---

## 使用说明

### 如何在 LangChain 中使用

```python
from langchain_community import arxiv
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
- `html2text`
- `rank_bm25`

- `browserless`
- `doctran`
- `docusaurus`
- `dropbox`
- `duckdb`
- `html2text`
- `joplin`
- `roam`
- `tomarkdown`
- `assemblyai`
- `github`
- `outline`
- `geopandas`
- `spacy`
- `tensorflow_datasets`
- `brave_search`
- `browserbase`
- `browserless`
- `datadog_logs`
- `diffbot`
- `dropbox`
- `duckdb`
- `etherscan`
- `facebook`
- `figma`
- `geopandas`
- `github`
- `html2text`
- `iugu`
- `joplin`
- `lakefs`
- `modern_treasury`
- `nuclia`
- `oracleai`
- `psychic`
- `roam`
- `rockset`
- `spreedly`
- `stripe`
- `tensorflow_datasets`
- `tomarkdown`
- `trello`
- `twitter`
- `weather`
- `whatsapp`
- `xata`

## 补充集成（来自 LangChain 中文网）
- `html2text`
- `rank_bm25`

- `airtable`
- `bibtex`
- `bilibili`
- `blackboard`
- `html2text`
- `rank_bm25`
- `acreom`