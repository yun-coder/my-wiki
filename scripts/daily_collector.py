#!/usr/bin/env python3
"""
daily_collector.py — 每日 AI 资讯 + GitHub Trending 采集器

功能:
  1. 抓取 HEX2077 与多个 AI 信息源
  2. 抓取 GitHub Trending
  3. 分析、去重，并按类型与功能点归类
  4. 持续更新 AI知识库/09-项目分类索引.md 与 10-资讯洞察库.md

用法:
  python scripts/daily_collector.py            # 全量采集并更新知识库
  python scripts/daily_collector.py --quick    # 快速模式（核心源 + GitHub）
  python scripts/daily_collector.py --help

依赖:
  pip install httpx openai python-dotenv
"""

from __future__ import annotations
import os, sys, re, json, time, textwrap
import html as html_lib
import xml.etree.ElementTree as ET
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin, urlparse

# Windows GBK 编码兼容：确保 stdout 使用 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "gb2312", "gb18030"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
from datetime import datetime, date
from typing import Optional

import httpx
try:
    from .knowledge_curator import (
        curate_knowledge_base, build_github_summary, NEWS_CATEGORIES
    )
except ImportError:  # 直接运行 scripts/daily_collector.py
    from knowledge_curator import (
        curate_knowledge_base, build_github_summary, NEWS_CATEGORIES
    )

# ── 路径 ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / "agentic-agent"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DAILY_DIR = PROJECT_ROOT / "01_Daily"
KB_DIR = PROJECT_ROOT / "AI知识库"
ENV_PATHS = (
    PROJECT_ROOT / ".env",  # 当前知识库的实际配置位置
    AGENT_DIR / ".env",     # 兼容旧目录结构
)

# ── 加载 .env ─────────────────────────────────────────────────────
_ENV_LOADED = False
def _ensure_env():
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    for env_path in ENV_PATHS:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    _ENV_LOADED = True

_ensure_env()

# ── LLM Client（复用 agentic-agent 的 AgnesClient）────────────────
try:
    sys.path.insert(0, str(AGENT_DIR))
    from agents.core.agnes_client import AgnesClient
    from agents.core.config import Config as AgentConfig
    _agent_cfg = AgentConfig.from_env()
    LLM_CLIENT = AgnesClient(
        api_key=_agent_cfg.agnes_api_key,
        base_url=_agent_cfg.agnes_base_url,
        model=_agent_cfg.agnes_model,
    )
except ImportError:
    # 降级：内联实现
    from openai import OpenAI
    class _FallbackClient:
        def __init__(self):
            # OpenAI 1.20 passes the removed ``proxies`` argument when it
            # creates its own httpx client. Supplying one explicitly keeps
            # the collector compatible with httpx 0.28+.
            http_client = httpx.Client(
                timeout=180.0, follow_redirects=True, verify=False
            )
            self.client = OpenAI(
                api_key=os.environ.get("AGNES_API_KEY", ""),
                base_url=os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
                http_client=http_client,
            )
            self.model = os.environ.get("AGNES_MODEL", "agnes-2.0-flash")
        def complete(self, messages, **kwargs):
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=kwargs.get("temperature", 0.3),
                max_tokens=kwargs.get("max_tokens", 4096),
            )
            content = resp.choices[0].message.content or ""
            return {"content": content}
    LLM_CLIENT = _FallbackClient()

def _make_http() -> httpx.Client:
    """创建带超时和 UA 的 httpx 客户端（每次调用时新建，用完关闭）"""
    return httpx.Client(timeout=30.0, follow_redirects=True, verify=False,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"})

_HTTP: httpx.Client | None = None
def _get_http() -> httpx.Client:
    global _HTTP
    if _HTTP is None:
        _HTTP = _make_http()
    return _HTTP

def _close_http():
    global _HTTP
    if _HTTP is not None:
        try:
            _HTTP.close()
        except Exception:
            pass
        _HTTP = None

import sys
def _cleanup_and_exit(code=0):
    _close_http()
    sys.exit(code)

TODAY = date.today()
TODAY_STR = TODAY.isoformat()  # 2026-07-07


def _clean_text(value: str) -> str:
    """清理从 HTML/LLM 返回的单行文本。"""
    value = html_lib.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _contains_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value or ""))


def _atomic_write_text(path: Path, content: str) -> None:
    """先写临时文件再替换，避免任务中断留下半个日报。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n",
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as tmp:
        tmp.write(content.rstrip() + "\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _extract_feed_articles(content: str, source_title: str,
                           max_articles: int) -> list[dict]:
    """从 RSS/Atom 中提取真实标题和链接。解析失败时交给 HTML 逻辑。"""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    articles = []
    entries = root.findall(".//item")
    if not entries:
        entries = [
            element for element in root.iter()
            if element.tag.rsplit("}", 1)[-1] == "entry"
        ]
    for entry in entries:
        children = {child.tag.rsplit("}", 1)[-1]: child for child in entry}
        title_node = children.get("title")
        link_node = children.get("link")
        categories = [
            _clean_text(child.text or "").casefold()
            for child in entry
            if child.tag.rsplit("}", 1)[-1] == "category"
        ]
        if any("sponsored" in category for category in categories):
            continue
        title = _clean_text(title_node.text if title_node is not None else "")
        link = ""
        if link_node is not None:
            link = (link_node.get("href") or link_node.text or "").strip()
        if len(title) >= 5 and link.startswith(("http://", "https://")):
            articles.append({
                "source": source_title,
                "title": title[:120],
                "url": link,
                "snippet": "",
            })
        if len(articles) >= max_articles:
            break
    return articles


def _extract_ai_news_articles(content: str, source_title: str,
                              max_articles: int) -> list[dict]:
    """解析 AI News 栏目页，并排除赞助内容与栏目导航。"""
    articles = []
    seen = set()
    cards = re.findall(
        r'<div[^>]+class="[^"]*\be-loop-item\b[^"]*"[^>]*>(.*?)(?='
        r'<div[^>]+class="[^"]*\be-loop-item\b|\Z)',
        content,
        re.DOTALL | re.IGNORECASE,
    )
    for card in cards:
        if re.search(r'>\s*Sponsored Content\s*<', card, re.IGNORECASE):
            continue
        match = re.search(
            r'<a[^>]+href=["\'](https?://www\.artificialintelligence-news\.com/news/[^"\']+)["\'][^>]*>'
            r'(.*?)</a>',
            card,
            re.DOTALL | re.IGNORECASE,
        )
        if not match:
            continue
        url = match.group(1).rstrip("/")
        title = _clean_text(match.group(2))
        if url in seen or len(title) < 10:
            continue
        seen.add(url)
        articles.append({
            "source": source_title,
            "title": title[:120],
            "url": url,
            "snippet": "",
        })
        if len(articles) >= max_articles:
            break
    return articles


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """按规范化 URL 和标题跨来源去重，保留信息更完整的条目。"""
    unique = []
    positions = {}
    for article in articles:
        url = (article.get("url") or "").strip()
        parsed = urlparse(url)
        canonical_url = parsed._replace(query="", fragment="").geturl().rstrip("/")
        title = _clean_text(article.get("title", ""))
        title_key = re.sub(r"[^\w\u4e00-\u9fff]+", "", title).casefold()
        if not canonical_url.startswith(("http://", "https://")) or len(title_key) < 5:
            continue
        key = (parsed.netloc.lower().removeprefix("www."), title_key)
        url_key = ("url", canonical_url.casefold())
        existing_index = positions.get(url_key, positions.get(key))
        candidate = {**article, "title": title, "url": canonical_url}
        if existing_index is None:
            positions[url_key] = positions[key] = len(unique)
            unique.append(candidate)
            continue
        existing = unique[existing_index]
        existing_detail = len(_clean_text(existing.get("summary") or existing.get("snippet", "")))
        candidate_detail = len(_clean_text(candidate.get("summary") or candidate.get("snippet", "")))
        if candidate_detail > existing_detail:
            unique[existing_index] = candidate
    return unique


def _get_with_retry(url: str, attempts: int = 2) -> httpx.Response:
    """对资讯源的瞬时 TLS/限流错误做一次短重试。"""
    last_error = None
    for attempt in range(attempts):
        try:
            response = _get_http().get(url)
            if response.status_code < 500:
                return response
            last_error = RuntimeError(f"HTTP {response.status_code}")
        except Exception as error:
            last_error = error
        if attempt + 1 < attempts:
            time.sleep(0.5)
    if last_error:
        raise last_error
    raise RuntimeError(f"请求失败: {url}")


# ══════════════════════════════════════════════════════════════════
# Part 1: HEX2077 日报抓取
# ══════════════════════════════════════════════════════════════════

def fetch_hex2077_daily() -> Optional[str]:
    """抓取 hex2077.dev/docs 的最新日报并结构化整理"""
    print("  [hex2077] 正在获取最新日报...")
    try:
        resp = _get_http().get("https://hex2077.dev/docs")
        if resp.status_code != 200:
            print(f"  [hex2077] HTTP {resp.status_code}, 跳过")
            return None
        html = resp.text
    except Exception as e:
        print(f"  [hex2077] 请求失败: {e}")
        return None

    # 1. 找最新日报的链接和摘要
    # 链接格式: /docs/2026-07/2026-07-07/
    entries = re.findall(
        r'<a[^>]*href="(/docs/\d{4}-\d{2}/\d{4}-\d{2}-\d{4}/)"[^>]*>'
        r'\s*<h3[^>]*>(.*?)</h3>\s*'
        r'(.*?)</a>',
        html, re.DOTALL
    )
    if not entries:
        # 宽松匹配
        entries = re.findall(
            r'href="(/docs/\d{4}-\d{2}/\d{4}-\d{2}-\d{2}/)"[^>]*>.*?<h3[^>]*>(.*?)</h3>',
            html, re.DOTALL
        )
        entries = [(p, t, "") for p, t in entries]

    if not entries:
        print("  [hex2077] 未找到日报条目")
        return None

    # 按日期排序，取最新
    def _date_key(e):
        m = re.search(r'/(\d{4}-\d{2}-\d{2})/', e[0])
        return m.group(1) if m else ""
    entries.sort(key=_date_key, reverse=True)
    latest_path, latest_title, snippet = entries[0]

    # 清洗标题
    latest_title = re.sub(r'<[^>]+>', '', latest_title).strip()
    # 清洗摘要
    snippet = re.sub(r'<[^>]+>', '', snippet).strip()
    snippet = re.sub(r'\s+', ' ', snippet)[:500]

    full_url = f"https://hex2077.dev{latest_path}"
    print(f"  [hex2077] 最新: {latest_title} → {full_url}")

    # 2. 同时尝试获取详情页
    detail_text = ""
    try:
        detail_resp = _get_http().get(full_url)
        if detail_resp.status_code == 200:
            dt = detail_resp.text
            # 尝试提取正文
            for tag in ["article", "main", ".prose", ".content", "body"]:
                m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', dt, re.DOTALL | re.IGNORECASE)
                if m:
                    detail_text = m.group(1)
                    break
            if not detail_text:
                detail_text = dt
            detail_text = re.sub(r'<[^>]+>', ' ', detail_text)
            detail_text = re.sub(r'\s+', ' ', detail_text)[:8000]
    except Exception:
        pass

    # 3. 用 LLM 结构化输出（I_01 风格）
    feed = f"标题: {latest_title}\n摘要: {snippet}"
    if detail_text:
        feed += f"\n\n详情:\n{detail_text[:6000]}"

    prompt = f"""你是一个专业的 AI 资讯编辑。以下是从 HEX2077 获取的最新 AI 日报原始内容。

{feed}

请严格按照以下要求输出：

## 输出格式（Markdown）

### 📰 今日核心资讯
按以下分类逐一列出，每条资讯包含：
- **标题**: 保留原文标题
- **核心逻辑**: 20-30 字提炼核心
- **链接**: 如果原文有链接保留

分类包括：模型发布 / 开源项目 / 商业动态 / 政策监管 / 前沿研究 / 行业趋势 / 社媒热议

### 💡 今日洞察
2-3 条趋势判断或行业启示

要求：
1. 保持原始资讯的完整性，不遗漏任何要点
2. 每条资讯必须有实质内容"""


    try:
        result = LLM_CLIENT.complete([
            {"role": "system", "content": "你是专业的 AI 资讯编辑，擅长从原始资讯中提取结构化信息。"},
            {"role": "user", "content": prompt},
        ], temperature=0.3, max_tokens=4096)
        content = (result.get("content", "") or "").strip()
        print(f"  [hex2077] LLM 结构化完成 ({len(content)} 字符)")
        # 只有标题、模板或极短响应都不能算一份日报。
        content_without_headings = re.sub(r"(?m)^#{1,6}\s+.*$", "", content)
        if len(_clean_text(content_without_headings)) < 80:
            print("  [hex2077] LLM 正文不足，尝试使用原始内容")
            raise ValueError("LLM returned insufficient content")
        return {
            "title": latest_title,
            "date": _key if (_key := _date_key(entries[0])) else TODAY_STR,
            "source_url": full_url,
            "content": content,
        }
    except Exception as e:
        print(f"  [hex2077] LLM 异常: {e}，使用原始摘要")
        # 原始页面也没有正文时返回 None，防止落盘空日报。
        fallback_text = _clean_text(detail_text or snippet)
        if len(fallback_text) < 80:
            print("  [hex2077] 原始正文不足，本次跳过该来源")
            return None
        # 有足够原文时才降级写入。
        return {
            "title": latest_title,
            "date": _key if (_key := _date_key(entries[0])) else TODAY_STR,
            "source_url": full_url,
            "content": f"## {latest_title}\n\n{fallback_text[:3000]}\n\n> 来源: [{full_url}]({full_url})",
        }


# ══════════════════════════════════════════════════════════════════
# Part 2: GitHub Trending 抓取
# ══════════════════════════════════════════════════════════════════

def fetch_github_trending() -> list[dict]:
    """抓取 GitHub Trending 每日热门项目"""
    print("  [github] 正在获取 GitHub Trending...")
    try:
        resp = _get_http().get("https://github.com/trending?since=daily")
        html = resp.text if resp.status_code == 200 else ""
    except Exception as e:
        print(f"  [github] httpx 失败: {e}")
        # curl fallback with binary output
        import subprocess
        try:
            result = subprocess.run(
                ["curl", "-s", "--connect-timeout", "15", "--max-time", "25",
                 "-H", "User-Agent: Mozilla/5.0",
                 "https://github.com/trending?since=daily"],
                capture_output=True, timeout=30
            )
            html = result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""
        except Exception as e2:
            print(f"  [github] curl 也失败: {e2}")
            return []

    if not html or len(html) < 10000:
        print(f"  [github] 无法获取数据")
        return []

    repos = []
    articles_raw = re.split(r'<article\s+class="Box-row"[^>]*>', html)[1:]

    for art in articles_raw:
        # 1. owner/repo: href="/owner/repo" inside h2/h3 heading
        m = re.search(r'<h[23][^>]*>.*?<a[^>]*href="/([^"/]+/[^"/]+)"', art, re.DOTALL)
        if not m:
            continue
        full_name = m.group(1)
        if "/" not in full_name or "sponsor" in full_name:
            continue
        owner, repo_name = full_name.split("/", 1)

        # 2. title — <em> text (the repo name)
        title_m = re.search(r'<em[^>]*>\s*(.*?)\s*</em>', art)
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else repo_name

        # 3. description
        desc_m = re.search(r'<p\s+class="col-9[^"]*"[^>]*>\s*(.*?)\s*</p>', art, re.DOTALL)
        desc = _clean_text(desc_m.group(1))[:300] if desc_m else ""

        # 4. language
        lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>\s*(.*?)\s*</span>', art)
        lang = lang_m.group(1).strip() if lang_m else ""

        # 5. total stars from stargazers link
        total_m = re.search(r'href="/[^"]*/stargazers"[^>]*>.*?octicon-star.*?</svg>\s*([\d,]+)', art, re.DOTALL | re.IGNORECASE)
        total_stars = total_m.group(1).replace(",", "") if total_m else "0"

        # 6. today stars
        stars_m = re.search(r'float-sm-right[^>]*>.*?octicon-star.*?</svg>\s*([\d,]+)\s*star', art, re.DOTALL | re.IGNORECASE)
        stars_today = stars_m.group(1).replace(",", "") if stars_m else "0"

        repos.append({
            "owner": owner, "name": repo_name, "full_name": full_name,
            "title": title, "description": desc, "language": lang,
            "stars_today": int(stars_today) if stars_today.isdigit() else 0,
            "total_stars": int(total_stars) if total_stars.isdigit() else 0,
            "url": f"https://github.com/{full_name}",
        })

    print(f"  [github] 解析到 {len(repos)} 个项目")
    return repos


def categorize_repo(repo: dict) -> str:
    """按关键词对 repo 分类"""
    t = (repo["title"] + " " + repo["description"]).lower()
    ai_keywords = ["agent", "llm", "ai", "gpt", "claude", "rag", "embedding",
                   "model", "inference", "transformer", "token", "prompt"]
    creative_keywords = ["video", "image", "music", "audio", "generate",
                         "diffusion", "art", "design", "creative", "3d"]
    dev_keywords = ["cli", "tool", "sdk", "api", "framework", "library",
                    "plugin", "extension", "ide", "editor", "terminal"]

    score_ai = sum(1 for k in ai_keywords if k in t)
    score_creative = sum(1 for k in creative_keywords if k in t)
    score_dev = sum(1 for k in dev_keywords if k in t)

    if score_ai == score_creative == score_dev == 0:
        return "🛠️ 开发工具"
    if score_ai >= score_creative and score_ai >= score_dev:
        return "🤖 AI / 智能体"
    elif score_creative >= score_dev:
        return "🎨 创意 / 生成"
    else:
        return "🛠️ 开发工具"


def enrich_repos_with_zh_desc(repos: list[dict]) -> list[dict]:
    """用 LLM 批量生成中文简介；缺项时使用本地中文降级说明。"""
    if not repos:
        return repos

    # 分批可避免项目较多时 JSON 被模型截断；每一批使用局部索引。
    for start in range(0, len(repos), 10):
        batch = repos[start:start + 10]
        items_text = "\n".join(
            f"[{i}] {r['full_name']}: {r.get('description', '')[:180]}"
            for i, r in enumerate(batch)
        )
        prompt = (
            "你是技术编辑。为以下 GitHub 项目各写一句准确、自然的中文简介"
            "（12—35 个汉字），不得只翻译项目名，也不得漏项。\n\n"
            f"{items_text}\n\n"
            '仅输出 JSON：{"d":[{"i":0,"z":"中文简介"}]}'
        )
        try:
            resp = LLM_CLIENT.complete([
                {"role": "system", "content": "你只输出合法 JSON，不使用 Markdown。"},
                {"role": "user", "content": prompt},
            ], temperature=0.2, max_tokens=2048)
            text = resp.get("content", "") or ""
            a, b = text.find("{"), text.rfind("}")
            if a == -1 or b <= a:
                raise ValueError("LLM 未返回 JSON")
            data = json.loads(text[a:b + 1])
            for item in data.get("d", []):
                idx = item.get("i")
                zh_desc = _clean_text(str(item.get("z", "")))
                if isinstance(idx, int) and 0 <= idx < len(batch) and _contains_chinese(zh_desc):
                    batch[idx]["zh_desc"] = zh_desc[:80]
        except Exception as e:
            print(f"  [zh-desc] 第 {start + 1}-{start + len(batch)} 项生成失败: {e}")

    missing = 0
    for repo in repos:
        if not _contains_chinese(repo.get("zh_desc", "")):
            repo["zh_desc"] = _fallback_zh_desc(repo)
            missing += 1
    if missing:
        print(f"  [zh-desc] {missing} 个项目使用本地中文降级说明")
    return repos


def _fallback_zh_desc(repo: dict) -> str:
    """LLM 不可用时仍给出有信息量的中文项目说明。"""
    text = f"{repo.get('title', '')} {repo.get('description', '')}".lower()
    rules = [
        (("agent", "agentic"), "AI 智能体工具与工作流"),
        (("llm", "gpt", "claude", "model"), "大模型应用与开发项目"),
        (("chat", "irc", "message"), "开源通信与聊天工具"),
        (("browser", "web automation"), "浏览器与网页自动化工具"),
        (("code review", "review"), "自动化代码审查工具"),
        (("design", "webflow", "framer", "cms"), "设计与内容管理工具"),
        (("database", "sql"), "数据库管理与 SQL 工具"),
        (("terminal", "cli"), "命令行与终端效率工具"),
        (("video", "image", "audio", "music"), "多媒体创作与处理工具"),
        (("server", "deploy", "self-hosted"), "开源服务与自托管工具"),
        (("framework", "library", "sdk", "api"), "开发框架与工具库"),
        (("learn", "book", "course", "cookbook"), "技术学习资料与实践示例"),
    ]
    for keywords, description in rules:
        if any(keyword in text for keyword in keywords):
            return description
    language = _clean_text(repo.get("language", ""))
    return f"{language} 开源项目" if language else "值得关注的开源项目"


def analyze_articles_with_llm(articles: list[dict]) -> list[dict]:
    """对消息做摘要、主题分类和功能/影响标签，失败时保留原始信息。"""
    if not articles:
        return articles
    for start in range(0, len(articles), 10):
        batch = articles[start:start + 10]
        payload = "\n".join(
            f"[{i}] 标题：{item.get('title', '')}\n"
            f"内容：{_clean_text(item.get('summary') or item.get('snippet', ''))[:500]}"
            for i, item in enumerate(batch)
        )
        prompt = (
            "分析以下 AI/技术消息。每条输出：一句中文结论（不是标题复述）、"
            "一个分类、1-3 个功能或影响标签。分类必须取自："
            f"{'、'.join(NEWS_CATEGORIES)}。\n\n{payload}\n\n"
            '仅输出 JSON：{"d":[{"i":0,"s":"结论","c":"分类","t":["标签"]}]}'
        )
        try:
            response = LLM_CLIENT.complete([
                {"role": "system", "content": "你是知识库编辑，只输出合法 JSON，不能漏项。"},
                {"role": "user", "content": prompt},
            ], temperature=0.2, max_tokens=4096)
            text = response.get("content", "") or ""
            left, right = text.find("{"), text.rfind("}")
            if left < 0 or right <= left:
                raise ValueError("LLM 未返回 JSON")
            data = json.loads(text[left:right + 1])
            for result in data.get("d", []):
                index = result.get("i")
                if not isinstance(index, int) or not 0 <= index < len(batch):
                    continue
                summary = _clean_text(str(result.get("s", "")))
                category = _clean_text(str(result.get("c", "")))
                tags = [
                    _clean_text(str(tag)) for tag in result.get("t", [])
                    if _clean_text(str(tag))
                ]
                if _contains_chinese(summary) and len(summary) >= 12:
                    batch[index]["summary"] = summary[:180]
                if category in NEWS_CATEGORIES:
                    batch[index]["category"] = category
                if tags:
                    batch[index]["tags"] = tags[:3]
        except Exception as error:
            print(f"  [消息分析] 第 {start + 1}-{start + len(batch)} 条分析失败: {error}")
            for item in batch:
                if len(_clean_text(item.get("summary") or item.get("snippet", ""))) < 20:
                    title = _clean_text(item.get("title", ""))
                    source = _clean_text(item.get("source", "信息源"))
                    item["summary"] = f"{source} 抓取到“{title}”，待补充正文分析。"
    return articles


def fetch_github_weekly_ai() -> list[dict]:
    """抓取 GitHub 按周维度增长的 AI 相关热门项目"""
    print("  [github-weekly] 正在获取 AI 快速增长项目...")
    try:
        resp = _get_http().get("https://github.com/trending?since=weekly")
        html = resp.text if resp.status_code == 200 else ""
    except Exception:
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-s", "--connect-timeout", "15", "--max-time", "25",
                 "-H", "User-Agent: Mozilla/5.0",
                 "https://github.com/trending?since=weekly"],
                capture_output=True, timeout=30
            )
            html = result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""
        except Exception:
            return []

    if not html or len(html) < 10000:
        return []

    articles_raw = re.split(r'<article\s+class="Box-row"[^>]*>', html)[1:]
    repos = []
    for art in articles_raw:
        m = re.search(r'<h[23][^>]*>.*?<a[^>]*href="/([^"/]+/[^"/]+)"', art, re.DOTALL)
        if not m:
            continue
        full_name = m.group(1)
        if "/" not in full_name or "sponsor" in full_name:
            continue
        title_m = re.search(r'<em[^>]*>\s*(.*?)\s*</em>', art)
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else full_name.split("/")[1]
        desc_m = re.search(r'<p\s+class="col-9[^"]*"[^>]*>\s*(.*?)\s*</p>', art, re.DOTALL)
        desc = _clean_text(desc_m.group(1))[:300] if desc_m else ""
        lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>\s*(.*?)\s*</span>', art)
        lang = lang_m.group(1).strip() if lang_m else ""
        total_m = re.search(r'href="/[^"]*/stargazers"[^>]*>.*?octicon-star.*?</svg>\s*([\d,]+)', art, re.DOTALL | re.IGNORECASE)
        total_stars = total_m.group(1).replace(",", "") if total_m else "0"
        stars_m = re.search(r'float-sm-right[^>]*>.*?octicon-star.*?</svg>\s*([\d,]+)\s*star', art, re.DOTALL | re.IGNORECASE)
        stars_weekly = stars_m.group(1).replace(",", "") if stars_m else "0"

        # 只保留 AI 相关项目
        t = (title + " " + desc).lower()
        ai_kw = ["ai", "llm", "agent", "gpt", "claude", "model", "embedding",
                 "rag", "transformer", "neural", "machine learning", "deep learning",
                 "pytorch", "tensorflow", "diffusion", "token", "prompt"]
        if not any(k in t for k in ai_kw):
            continue

        repos.append({
            "owner": full_name.split("/")[0], "name": full_name.split("/")[1],
            "full_name": full_name, "title": title, "description": desc,
            "language": lang,
            "stars_weekly": int(stars_weekly) if stars_weekly.isdigit() else 0,
            "total_stars": int(total_stars) if total_stars.isdigit() else 0,
            "url": f"https://github.com/{full_name}",
        })

    print(f"  [github-weekly] 筛选出 {len(repos)} 个 AI 相关项目")
    return repos


# ══════════════════════════════════════════════════════════════════
# Part 3: 多信息源采集
# ══════════════════════════════════════════════════════════════════

def load_info_sources() -> list[dict]:
    """从知识库读取信息源配置表。"""
    source_path = KB_DIR / "13-AI资讯信息源.md"
    if not source_path.exists():
        print("  [sources] 信息源文件不存在")
        return []

    content = source_path.read_text(encoding="utf-8")
    section = content.split("## 信息源列表", 1)[-1].split("\n## ", 1)[0]
    sources = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7 or not cells[0].isdigit() or not cells[2].startswith("http"):
            continue
        try:
            max_articles = max(1, min(int(cells[4]), 10))
        except ValueError:
            max_articles = 2
        sources.append({
            "title": cells[1],
            "url": cells[2],
            "source_type": cells[3],
            "max_articles": max_articles,
            "enabled": cells[5] == "启用",
            "description": cells[6],
        })

    print(f"  [sources] 读取到 {len(sources)} 个信息源")
    return sources


def fetch_source_articles(source: dict, max_articles: int = 5) -> list[dict]:
    """抓取单个信息源的热门文章列表"""
    url = source["url"]
    title = source["title"]
    # 跳过需要登录或无法直接抓取的源
    skip_domains = ["x.com", "twitter.com", "reddit.com"]
    if any(d in url for d in skip_domains):
        return [{"source": title, "title": f"[需要登录] {title}", "url": url, "snippet": ""}]

    # 已知有文章结构的源，直接返回其首页作为入口
    known_blog_feeds = {
        "机器之心": "https://www.jiqizhixin.com/rss",
        "量子位": "https://www.qbitai.com/feed",
        "Hugging Face 博客": "https://huggingface.co/blog/zh",
        "AIBase基地": "https://www.aibase.com/zh",
        "何夕2077": "https://hex2077.dev/blog",
        "Zread": "https://zread.ai/",
        "观猹": "https://watcha.cn/",
        "Vibe Coding 雷达": "https://radar.lyihub.com/",
        "last30days-skill": "https://github.com/mvanhorn/last30days-skill",
        "OpenAI News": "https://openai.com/news/rss.xml",
        "Anthropic News": "https://www.anthropic.com/news",
        "Google DeepMind": "https://deepmind.google/blog/rss.xml",
        "Google Research": "https://research.google/blog/",
        "BAIR Blog": "https://bair.berkeley.edu/blog/feed.xml",
        "Microsoft Research": "https://www.microsoft.com/en-us/research/blog/",
        "NVIDIA Developer Blog": "https://developer.nvidia.com/blog/feed/",
        "Mozilla.ai": "https://blog.mozilla.ai/rss/",
        "Linux Foundation AI/ML": "https://www.linuxfoundation.org/blog/tag/ai-ml",
        "arXiv cs.LG": "https://export.arxiv.org/rss/cs.LG",
        "arXiv cs.AI": "https://export.arxiv.org/rss/cs.AI",
        "AI News": "https://www.artificialintelligence-news.com/feed/",
    }
    # 使用已知的文章入口
    if title in known_blog_feeds:
        url = known_blog_feeds[title]

    articles = []
    try:
        try:
            resp = _get_with_retry(url)
        except Exception:
            if title != "AI News" or url == source["url"]:
                raise
            url = source["url"]
            resp = _get_with_retry(url)
        if (resp.status_code != 200 and title == "AI News"):
            url = source["url"]
            resp = _get_with_retry(url)
        if resp.status_code != 200:
            return articles
        html = resp.text

        feed_articles = _extract_feed_articles(html, title, max_articles)
        if feed_articles:
            return feed_articles

        if title == "AI News":
            return _extract_ai_news_articles(html, title, max_articles)

        # 提取文章链接——干净版：只取看起来像文章/帖子的路径
        # 条件: href 中包含字母数字路径，没有常见文件扩展名
        all_links = re.findall(
            r'<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>',
            html, re.DOTALL | re.IGNORECASE
        )

        seen = set()
        for link, anchor_html in all_links:
            link = urljoin(url, html_lib.unescape(link.strip()))
            if not link.startswith(("http://", "https://")):
                continue
            # 一般资讯页只收本站文章，防止把页脚外链当新闻。
            source_host = urlparse(url).netloc.removeprefix("www.")
            link_host = urlparse(link).netloc.removeprefix("www.")
            if source_host and link_host and not (
                link_host == source_host or link_host.endswith("." + source_host)
            ):
                continue
            # 硬过滤：非文章内容
            skip_patterns = [
                ".jpg", ".png", ".css", ".js", ".ico", ".svg", ".woff", ".ttf",
                ".eot", ".map", ".json", ".xml", ".webp", ".mp4", ".pdf",
                "fonts.googleapis.com", "fonts.gstatic.com",
                "google-analytics.com", "googletagmanager.com",
                "doubleclick.net", "facebook.com/plugins",
                "twitter.com/share", "x.com/share",
                "mailto:", "tel:", "javascript:",
                "/login", "/signin", "/signup", "/register", "/inbox",
                "/about", "/contact", "/privacy", "/terms", "/tools",
                "githubassets.com", "workable.com",
            ]
            if any(s in link.lower() for s in skip_patterns):
                continue

            # 主页/导航类短链接过滤
            path = link.replace(f"https://", "").replace(f"http://", "")
            path_segments = [p for p in path.split("/") if p and not p.startswith("www.")]
            if len(path_segments) < 2:
                continue  # 只有域名，不是文章

            if link in seen:
                continue
            seen.add(link)

            # 使用域名前缀区分不同源
            article_title = _clean_text(anchor_html)
            if not article_title:
                article_title = link.rstrip("/").split("/")[-1]
                article_title = article_title.replace("-", " ").replace("_", " ")
                article_title = re.sub(r"\.(html?|md)$", "", article_title, flags=re.IGNORECASE)
            # 不要太短或太长的标题
            nav_titles = {
                "home", "blog", "news", "docs", "github", "huggingface",
                "首页", "博客", "资讯", "新闻", "更多", "关于我们",
            }
            if (len(article_title) < 5 or len(article_title) > 120
                    or article_title.strip().lower() in nav_titles
                    or re.fullmatch(r"[\da-f-]{16,}", article_title.strip(), re.IGNORECASE)):
                continue

            articles.append({
                "source": title,
                "title": article_title[:80],
                "url": link,
                "snippet": "",
            })
            if len(articles) >= max_articles:
                break
    except Exception as e:
        print(f"    [sources] {title} 抓取失败: {e}")

    return articles


# ══════════════════════════════════════════════════════════════════
# Part 4: 写入日报文件
# ══════════════════════════════════════════════════════════════════

def write_ai_digest(hex2077_result: Optional[dict],
                     source_articles: list[dict]) -> Optional[Path]:
    """旧接口已停用；采集结果必须进入长期知识库。"""
    raise RuntimeError("01_Daily 日报输出已停用，请使用 curate_knowledge_base")
    source_articles = [
        article for article in source_articles
        if len(_clean_text(article.get("title", ""))) >= 5
        and article.get("url", "").startswith(("http://", "https://"))
        and not article.get("title", "").startswith("[需要登录]")
    ]
    if hex2077_result:
        body = _clean_text(hex2077_result.get("content", ""))
        if len(body) < 80:
            print("  [日报] HEX2077 正文不足，已从日报中剔除")
            hex2077_result = None
    if not hex2077_result and not source_articles:
        print("  [日报] 没有通过质量检查的内容，不创建或覆盖文件")
        return None

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DAILY_DIR / f"{TODAY_STR}-ai-digest.md"

    lines = [f"# 📰 AI 资讯日报 - {TODAY_STR}",
             "",
             f"> 采集时间: {datetime.now():%Y-%m-%d %H:%M:%S}",
             f"> 来源: hex2077 + 信息源采集 | LLM 蒸馏",
             ""]

    # HEX2077 部分
    if hex2077_result:
        lines.append("---")
        lines.append("")
        lines.append(f"## 📡 HEX2077 AI 日报")
        lines.append("")
        lines.append(f"> 来源: [{hex2077_result['source_url']}]({hex2077_result['source_url']})")
        lines.append("")
        lines.append(hex2077_result["content"])
        lines.append("")

    # 信息源精选
    if source_articles:
        lines.append("---")
        lines.append("")
        lines.append("## 🔍 信息源精选")
        lines.append("")
        for art in source_articles:
            lines.append(f"- [{art['title']}]({art['url']}) — *{art['source']}*")
            if art.get("snippet"):
                lines.append(f"  > {art['snippet'][:100]}")
        lines.append("")

    _atomic_write_text(file_path, "\n".join(lines))
    print(f"  [日报] 已写入: {file_path.name}")
    return file_path


def write_github_digest(repos: list[dict], weekly_ai: list[dict] = None) -> Optional[Path]:
    """旧接口已停用；项目必须进入分类索引。"""
    raise RuntimeError("01_Daily GitHub 输出已停用，请使用 curate_knowledge_base")
    if not repos and not weekly_ai:
        print("  [GitHub] 无内容可写入")
        return None

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DAILY_DIR / f"{TODAY_STR}-github-trending.md"

    # 预先生成中文简介
    repos = enrich_repos_with_zh_desc(repos)
    if weekly_ai:
        weekly_ai = enrich_repos_with_zh_desc(weekly_ai)

    # 按分类聚合
    categorized = {}
    for repo in repos:
        cat = categorize_repo(repo)
        categorized.setdefault(cat, []).append(repo)

    lines = [
        f"# ⭐ GitHub 热门项目 - {TODAY_STR}",
        "",
        f"> 数据来源: GitHub Trending (daily + weekly) | 采集时间: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
    ]

    # ── 每日热门 ──
    for cat in ["🤖 AI / 智能体", "🎨 创意 / 生成", "🛠️ 开发工具"]:
        cat_repos = categorized.get(cat, [])
        if not cat_repos:
            continue
        lines.append(f"---")
        lines.append("")
        lines.append(f"## {cat}")
        lines.append("")
        cat_repos.sort(key=lambda r: r["stars_today"], reverse=True)
        for r in cat_repos:
            lang_tag = f" | 📝 {r['language']}" if r.get("language") else ""
            zh_tag = f" — {r['zh_desc']}" if r.get("zh_desc") else ""
            lines.append(f"**[{r['title']}]({r['url']})**{zh_tag}")
            lines.append(f"> {r['description']}")
            lines.append(f"> ⭐ +{r['stars_today']}/日 | 总 ⭐ {r['total_stars']:,}{lang_tag}")
            lines.append("")

    # ── 周度 AI 快速增长板块 ──
    if weekly_ai:
        weekly_ai.sort(key=lambda r: r.get("stars_weekly", 0), reverse=True)
        lines.append("---")
        lines.append("")
        lines.append("## 📈 AI 快速增长（本周）")
        lines.append("")
        lines.append("> 来自 GitHub Trending weekly 维度，AI 相关项目按周增长排序")
        lines.append("")
        for r in weekly_ai[:10]:
            zh_tag = f" — {r['zh_desc']}" if r.get("zh_desc") else ""
            lang_tag = f" | 📝 {r['language']}" if r.get("language") else ""
            lines.append(f"**[{r['title']}]({r['url']})**{zh_tag}")
            lines.append(f"> {r['description']}")
            lines.append(f"> ⭐ +{r['stars_weekly']}/周 | 总 ⭐ {r['total_stars']:,}{lang_tag}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*报告自动生成，数据源: GitHub Trending*")

    _atomic_write_text(file_path, "\n".join(lines))
    print(f"  [GitHub] 已写入: {file_path.name}")
    return file_path


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="每日 AI 资讯 + GitHub Trending 采集器")
    parser.add_argument("--quick", action="store_true",
                        help="快速模式：仅采集 HEX2077 + GitHub Trending")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  📡 AI 资讯采集器 — {TODAY_STR}")
    print(f"{'='*50}\n")

    # ── 1. HEX2077 日报 ──
    print("[1/5] 采集 HEX2077 AI 日报...")
    hex2077_result = fetch_hex2077_daily()

    # ── 2. GitHub Trending ──
    print("\n[2/5] 采集 GitHub Trending...")
    github_repos = fetch_github_trending()
    github_weekly_ai = fetch_github_weekly_ai()
    github_summary = build_github_summary(github_repos, github_weekly_ai)

    # ── 3. 信息源采集 ──
    print("\n[3/5] 采集其他信息源...")
    source_articles = []
    if not args.quick:
        sources = load_info_sources()
        for src in sources:
            if not src.get("enabled", True):
                continue
            arts = fetch_source_articles(src, src.get("max_articles", 2))
            source_articles.extend(arts)
        before_dedup = len(source_articles)
        source_articles = deduplicate_articles(source_articles)
        print(f"  [sources] 共 {len(source_articles)} 条文章（去重前 {before_dedup} 条）")
    else:
        print("  [sources] 快速模式，跳过")

    # ── 4. 分析、去重、归类 ──
    print("\n[4/5] 分析消息并整理知识...")
    all_repos_by_name = {}
    for repo in [*github_repos, *github_weekly_ai]:
        all_repos_by_name[repo["full_name"].lower()] = repo
    curated_repos = enrich_repos_with_zh_desc(list(all_repos_by_name.values()))

    knowledge_articles = list(source_articles)
    if hex2077_result:
        knowledge_articles.append({
            "source": "HEX2077",
            "title": hex2077_result["title"],
            "url": hex2077_result["source_url"],
            "summary": hex2077_result["content"],
        })
    knowledge_articles = deduplicate_articles(knowledge_articles)
    knowledge_articles = analyze_articles_with_llm(knowledge_articles)

    # ── 5. 直接更新长期知识库，不再生成 01_Daily 记录 ──
    print("\n[5/5] 更新 AI 知识库...")
    project_path, insight_path = curate_knowledge_base(
        curated_repos, knowledge_articles, github_summary
    )

    print(f"\n{'='*50}")
    print("  ✅ 采集完成!")
    print(f"  📚 项目索引: {project_path.name}")
    print(f"  🧠 资讯洞察: {insight_path.name}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ❌ 脚本异常: {e}")
        _cleanup_and_exit(1)
    else:
        _cleanup_and_exit(0)
