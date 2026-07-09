#!/usr/bin/env python3
"""
daily_collector.py — 每日 AI 资讯 + GitHub Trending 采集器

功能:
  1. HEX2077 日报抓取 + LLM 结构化 → 01_Daily/{today}-ai-digest.md
  2. GitHub Trending 抓取             → 01_Daily/{today}-github-trending.md
  3. 多信息源采集 + LLM 蒸馏          → AI知识库/{category}/*.md
  4. 重建 AI知识库总览

用法:
  python scripts/daily_collector.py            # 全量采集（所有源 + 归档）
  python scripts/daily_collector.py --quick    # 快速模式（仅日报 + GitHub）
  python scripts/daily_collector.py --help

依赖:
  pip install httpx openai python-dotenv
"""

from __future__ import annotations
import os, sys, re, json, time, textwrap

# Windows GBK 编码兼容：确保 stdout 使用 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "gb2312", "gb18030"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
from datetime import datetime, date
from typing import Optional

import httpx

# ── 路径 ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / "agentic-agent"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DAILY_DIR = PROJECT_ROOT / "01_Daily"
KB_DIR = PROJECT_ROOT / "AI知识库"
ENV_PATH = AGENT_DIR / ".env"

# ── 加载 .env ─────────────────────────────────────────────────────
_ENV_LOADED = False
def _ensure_env():
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
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
            self.client = OpenAI(
                api_key=os.environ.get("AGNES_API_KEY", ""),
                base_url=os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
            )
            self.model = os.environ.get("AGNES_MODEL", "agnes-2.0-flash")
        def complete(self, messages, **kwargs):
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=kwargs.get("temperature", 0.3),
                max_tokens=kwargs.get("max_tokens", 4096),
            )
            return {"content": resp.choices[0].message.content}
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
        content = result.get("content", "")
        print(f"  [hex2077] LLM 结构化完成 ({len(content)} 字符)")
        return {
            "title": latest_title,
            "date": _key if (_key := _date_key(entries[0])) else TODAY_STR,
            "source_url": full_url,
            "content": content,
        }
    except Exception as e:
        print(f"  [hex2077] LLM 异常: {e}，使用原始摘要")
        # 降级
        return {
            "title": latest_title,
            "date": _key if (_key := _date_key(entries[0])) else TODAY_STR,
            "source_url": full_url,
            "content": f"## {latest_title}\n\n{snippet}\n\n> 来源: [{full_url}]({full_url})",
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
        desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()[:200] if desc_m else ""

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

    if score_ai >= score_creative and score_ai >= score_dev:
        return "🤖 AI / 智能体"
    elif score_creative >= score_dev:
        return "🎨 创意 / 生成"
    else:
        return "🛠️ 开发工具"


def enrich_repos_with_zh_desc(repos: list[dict]) -> list[dict]:
    """用 LLM 批量生成中文简介"""
    if not repos:
        return repos
    items_text = "\n".join([
        f"[{i}] {r['title']}: {r['description'][:120]}"
        for i, r in enumerate(repos)
    ])
    prompt = f"你是一个技术翻译。为以下 GitHub 项目生成简洁的中文简介（15 字以内）。\n\n{items_text}\n\n直接输出 JSON: {{\"d\":[{{\"i\":0,\"z\":\"...\"}}]}} 不要其他文字。"
    try:
        resp = LLM_CLIENT.complete([
            {"role": "system", "content": "你是一个简洁的技术翻译。"},
            {"role": "user", "content": prompt},
        ], temperature=0.2, max_tokens=2048)
        text = resp.get("content", "")
        # 找第一个 { 到最后一个 }
        a, b = text.find('{'), text.rfind('}')
        if a == -1 or b <= a:
            return repos
        data = json.loads(text[a:b+1])
        for d in data.get("d", []):
            idx = d.get("i")
            if idx is not None and 0 <= idx < len(repos):
                repos[idx]["zh_desc"] = d.get("z", "")
    except Exception as e:
        print(f"  [zh-desc] 警告: {e}")
    return repos


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
        desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()[:200] if desc_m else ""
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
    """从知识库读取信息源列表"""
    source_path = KB_DIR / "00-overview" / "AI资讯_信息源列表.md"
    if not source_path.exists():
        print("  [sources] 信息源文件不存在")
        return []

    content = source_path.read_text(encoding="utf-8")
    sources = []
    for m in re.finditer(r'\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(https?://\S+)\s*\|\s*(.+?)\s*\|', content):
        title = m.group(1).strip()
        url = m.group(2).strip()
        desc = m.group(3).strip()
        if title == "站点":
            continue
        sources.append({"title": title, "url": url, "description": desc})

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
    }
    # 使用已知的文章入口
    if title in known_blog_feeds:
        url = known_blog_feeds[title]

    articles = []
    try:
        resp = _get_http().get(url)
        if resp.status_code != 200:
            return articles
        html = resp.text

        # 提取文章链接——干净版：只取看起来像文章/帖子的路径
        # 条件: href 中包含字母数字路径，没有常见文件扩展名
        all_links = re.findall(r'href="(https?://[^"#]+)"', html)

        seen = set()
        for link in all_links:
            # 硬过滤：非文章内容
            skip_patterns = [
                ".jpg", ".png", ".css", ".js", ".ico", ".svg", ".woff", ".ttf",
                ".eot", ".map", ".json", ".xml", ".webp", ".mp4", ".pdf",
                "fonts.googleapis.com", "fonts.gstatic.com",
                "google-analytics.com", "googletagmanager.com",
                "doubleclick.net", "facebook.com/plugins",
                "twitter.com/share", "x.com/share",
                "mailto:", "tel:", "javascript:",
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
            article_title = link.rstrip("/").split("/")[-1]
            article_title = article_title.replace("-", " ").replace("_", " ").replace(".html", "").replace(".md", "")
            # 不要太短或太长的标题
            if len(article_title) < 3 or len(article_title) > 100:
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
    """写入 AI 日报到 01_Daily/"""
    if not hex2077_result and not source_articles:
        print("  [日报] 无内容可写入")
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

    file_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [日报] 已写入: {file_path.name}")
    return file_path


def write_github_digest(repos: list[dict], weekly_ai: list[dict] = None) -> Optional[Path]:
    """写入 GitHub 热门项目到 01_Daily/"""
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

    file_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [GitHub] 已写入: {file_path.name}")
    return file_path


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="每日 AI 资讯 + GitHub Trending 采集器")
    parser.add_argument("--quick", action="store_true",
                        help="快速模式：仅采集 hex2077 日报 + GitHub Trending，不做蒸馏归档")
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

    # ── 3. 信息源采集 ──
    print("\n[3/5] 采集其他信息源...")
    source_articles = []
    if not args.quick:
        sources = load_info_sources()
        for src in sources:
            arts = fetch_source_articles(src)
            source_articles.extend(arts)
        print(f"  [sources] 共 {len(source_articles)} 条文章")
    else:
        print("  [sources] 快速模式，跳过")

    # ── 4. 已跳过 ──（知识库蒸馏归档功能已废弃）
    print("\n[4/5] 跳过（知识库归档已废弃）")

    # ── 5. 写入日报 ──
    print("\n[5/5] 写入日报文件...")
    digest_path = write_ai_digest(hex2077_result, source_articles)
    github_path = write_github_digest(github_repos, github_weekly_ai)

    print(f"\n{'='*50}")
    print("  ✅ 采集完成!")
    if digest_path:
        print(f"  📄 AI 日报: {digest_path.name}")
    if github_path:
        print(f"  📄 GitHub:  {github_path.name}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n  ❌ 脚本异常: {e}")
        _cleanup_and_exit(1)
    else:
        _cleanup_and_exit(0)
