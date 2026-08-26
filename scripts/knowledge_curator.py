#!/usr/bin/env python3
"""把抓取结果去重、分析并持续合并到 AI 知识库。"""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_ROOT / "AI知识库"
NAVIGATION_PATH = KB_DIR / "00-overview" / "知识库导航.md"
PROJECT_INDEX = KB_DIR / "09-项目分类索引.md"
INSIGHT_INDEX = KB_DIR / "10-资讯洞察库.md"
TODAY = date.today().isoformat()

PROJECT_CATEGORIES = [
    "AI 智能体与技能",
    "RAG 与知识管理",
    "AI 视频与音频",
    "AI 图像、视觉与 3D",
    "大模型与 AI 基础设施",
    "开发工具与工程效率",
    "前端、设计与内容创作",
    "数据分析、金融与商业",
    "学习资源与教程",
    "其他开源项目",
]

NEWS_CATEGORIES = [
    "模型与前沿研究",
    "智能体与 AI 应用",
    "开源项目与开发工具",
    "多模态与内容生成",
    "商业产品与行业动态",
    "政策、治理与安全",
]


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[*_`|>#\[\]]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=path.parent,
        prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as handle:
        handle.write(content.rstrip() + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def update_navigation() -> Path:
    """同步导航更新时间；自动运行只维护一条状态，避免日志无限增长。"""
    if not NAVIGATION_PATH.exists():
        raise FileNotFoundError(f"知识库导航不存在: {NAVIGATION_PATH}")

    content = NAVIGATION_PATH.read_text(encoding="utf-8")
    update_line = f"> 个人 AI 知识体系总览 | 更新: {TODAY}"
    content, replaced = re.subn(
        r"^> 个人(?: AI )?知识体系总览 \| 更新: \d{4}-\d{2}-\d{2}$",
        update_line,
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if not replaced:
        raise ValueError("知识库导航缺少标准更新时间行")

    record = f"- **最近自动整理**: {TODAY}（项目索引与资讯洞察库）"
    content, count = re.subn(
        r"^- \*\*最近自动整理\*\*: .*?$",
        record,
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if not count:
        marker = "## 维护说明"
        if marker not in content:
            content = content.rstrip() + f"\n\n---\n\n{marker}\n"
        content = content.replace(marker, f"{marker}\n\n{record}", 1)

    atomic_write(NAVIGATION_PATH, content)
    print(f"  [导航] 已同步: {NAVIGATION_PATH.name} ({TODAY})")
    return NAVIGATION_PATH


def normalize_repo_url(url: str) -> Optional[str]:
    match = re.match(
        r"https?://github\.com/([^/\s?#]+)/([^/\s?#)]+)", url.strip(),
        re.IGNORECASE,
    )
    if not match:
        return None
    owner, name = match.groups()
    name = name.rstrip(".,;:")
    if name.lower().endswith(".git"):
        name = name[:-4]
    if name.lower() in {"stargazers", "issues", "pulls"}:
        return None
    if owner.lower() in {
        "features", "topics", "marketplace", "settings", "login",
        "sponsors", "collections", "events",
    }:
        return None
    return f"https://github.com/{owner}/{name}"


def _description_near_link(line: str, label: str) -> str:
    # 表格第二列通常是说明；Trending 的中文简介通常在链接后。
    cells = [clean_text(cell) for cell in line.strip().strip("|").split("|")]
    useful = [
        cell for cell in cells
        if cell and label.lower() not in cell.lower()
        and "github.com/" not in cell.lower()
        and cell not in {"项目", "说明", "技术栈", "仓库", "链接"}
    ]
    if useful:
        return max(useful, key=len)[:180]
    suffix = line.split(")", 1)[-1] if ")" in line else ""
    return clean_text(suffix.lstrip(" —-:"))[:180]


def scan_existing_projects() -> dict[str, dict]:
    """扫描个人收藏、知识库和历史日报，形成首次迁移基线。"""
    projects: dict[str, dict] = {}
    paths = [PROJECT_ROOT / "09-GitHub项目个人收集.md"]
    paths.extend(KB_DIR.rglob("*.md"))
    paths.extend((PROJECT_ROOT / "01_Daily").glob("*github-trending.md"))

    link_pattern = re.compile(
        r"\[([^\]]+)\]\((https?://github\.com/[^)\s]+)\)", re.IGNORECASE
    )
    for path in paths:
        if not path.exists() or path == PROJECT_INDEX:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines):
            for label, raw_url in link_pattern.findall(line):
                url = normalize_repo_url(raw_url)
                if not url:
                    continue
                full_name = url.removeprefix("https://github.com/")
                name = full_name.split("/", 1)[-1]
                description = _description_near_link(line, label)
                if not description and index + 1 < len(lines):
                    next_line = clean_text(lines[index + 1])
                    if (next_line and "github.com/" not in next_line
                            and not re.match(r"^\d+\.", next_line)
                            and not next_line.startswith(("⭐", "总"))):
                        description = next_line[:180]
                key = full_name.lower()
                existing = projects.setdefault(key, {
                    "full_name": full_name,
                    "name": name,
                    "url": url,
                    "description": "",
                    "language": "",
                    "first_seen": TODAY,
                    "last_seen": TODAY,
                    "sources": set(),
                })
                if len(description) > len(existing["description"]):
                    existing["description"] = description
                existing["sources"].add(path.name)
    return projects


def parse_project_index() -> dict[str, dict]:
    if not PROJECT_INDEX.exists():
        return {}
    projects = {}
    row_pattern = re.compile(
        r"^\|\s*\[([^\]]+)\]\((https?://github\.com/[^)]+)\)\s*"
        r"\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
    )
    for line in PROJECT_INDEX.read_text(encoding="utf-8").splitlines():
        match = row_pattern.match(line)
        if not match:
            continue
        label, url, description, features, language, first_seen, last_seen = match.groups()
        normalized = normalize_repo_url(url)
        if not normalized:
            continue
        full_name = normalized.removeprefix("https://github.com/")
        projects[full_name.lower()] = {
            "full_name": full_name,
            "name": label,
            "url": normalized,
            "description": clean_text(description),
            "features": [tag.strip() for tag in features.split("、") if tag.strip()],
            "language": clean_text(language).replace("—", ""),
            "first_seen": first_seen.strip() or TODAY,
            "last_seen": last_seen.strip() or TODAY,
            "sources": {"项目分类索引"},
        }
    return projects


def _matched(text: str, *keywords: str) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_project(project: dict) -> tuple[str, list[str]]:
    text = " ".join([
        project.get("full_name", ""), project.get("name", ""),
        project.get("description", ""),
    ]).lower()

    feature_rules = [
        ("Agent", ("agent", "multi-agent", "multiagent", "claude-code")),
        ("技能系统", ("skill", "prompt", "workflow")),
        ("RAG", ("rag", "retrieval", "embedding", "vector")),
        ("知识库", ("knowledge", "memory", "mem0", "graph")),
        ("视频生成", ("video", "movie", "drama", "reel", "caption")),
        ("图像生成", ("image", "diffusion", "comfyui", "visual")),
        ("语音音频", ("voice", "audio", "tts", "speech", "music")),
        ("3D", ("3d", "threejs", "world model")),
        ("模型训练推理", ("model", "llm", "inference", "transformer", "pytorch")),
        ("AI 网关", ("gateway", "router", "api", "provider")),
        ("网页抓取", ("crawl", "scrap", "browser", "playwright", "firecrawl")),
        ("代码开发", ("code", "developer", "review", "debug", "cli", "sdk")),
        ("前端 UI", ("vue", "react", "frontend", "ui", "design", "css")),
        ("文档处理", ("document", "pdf", "ocr", "office", "markdown")),
        ("数据分析", ("data", "analytics", "database", "sql")),
        ("金融交易", ("finance", "stock", "trading", "market")),
        ("教程资源", ("awesome", "learn", "book", "course", "tutorial", "cookbook")),
        ("自动化", ("automation", "workflow", "pipeline")),
    ]
    features = [label for label, keywords in feature_rules if _matched(text, *keywords)]
    features = list(dict.fromkeys(features))[:4] or ["通用工具"]

    if _matched(text, "rag", "retrieval", "embedding", "vector", "knowledge", "memory", "mem0"):
        category = "RAG 与知识管理"
    elif _matched(text, "video", "voice", "audio", "tts", "speech", "music", "reel", "drama"):
        category = "AI 视频与音频"
    elif _matched(text, "image", "diffusion", "comfyui", "vision", "visual", "3d", "ocr"):
        category = "AI 图像、视觉与 3D"
    elif _matched(text, "agent", "skill", "claude-code", "multiagent", "multi-agent"):
        category = "AI 智能体与技能"
    elif _matched(text, "llm", "model", "inference", "transformer", "gateway", "router", "pytorch"):
        category = "大模型与 AI 基础设施"
    elif _matched(text, "finance", "stock", "trading", "market", "business", "crm"):
        category = "数据分析、金融与商业"
    elif _matched(text, "awesome", "learn", "book", "course", "tutorial", "cookbook", "exercise"):
        category = "学习资源与教程"
    elif _matched(text, "vue", "react", "frontend", "ui", "ux", "design", "css", "editor"):
        category = "前端、设计与内容创作"
    elif _matched(text, "code", "developer", "cli", "sdk", "framework", "library",
                  "terminal", "browser", "crawl", "scrap", "database", "sql", "tool"):
        category = "开发工具与工程效率"
    else:
        category = "其他开源项目"
    return category, features


def fallback_description(project: dict, category: str, features: list[str]) -> str:
    description = clean_text(project.get("description", ""))
    invalid = (
        "github.com/" in description.lower()
        or bool(re.match(r"^\d+\.", description))
        or len(description) < 4
    )
    if description and not invalid and re.search(r"[\u4e00-\u9fff]", description):
        return description[:180]
    feature_text = "、".join(features[:2])
    return f"面向{feature_text}场景的{category}项目"


def merge_projects(new_repos: Iterable[dict]) -> dict[str, dict]:
    projects = parse_project_index() or scan_existing_projects()
    for repo in new_repos:
        full_name = repo.get("full_name", "").strip("/")
        url = normalize_repo_url(repo.get("url", "") or f"https://github.com/{full_name}")
        if not url:
            continue
        full_name = url.removeprefix("https://github.com/")
        key = full_name.lower()
        item = projects.setdefault(key, {
            "full_name": full_name,
            "name": repo.get("title") or full_name.split("/", 1)[-1],
            "url": url,
            "description": "",
            "language": "",
            "first_seen": TODAY,
            "last_seen": TODAY,
            "sources": set(),
        })
        incoming_desc = clean_text(repo.get("zh_desc") or repo.get("description", ""))
        if len(incoming_desc) > len(item.get("description", "")):
            item["description"] = incoming_desc
        item["language"] = repo.get("language") or item.get("language", "")
        item["last_seen"] = TODAY
        item.setdefault("sources", set()).add("GitHub Trending")
    return projects


def build_github_summary(daily_repos: Iterable[dict],
                         weekly_repos: Iterable[dict]) -> dict:
    """保留本次 GitHub 日榜、周榜和新增项目，避免只剩总索引。"""
    daily = list(daily_repos)
    weekly = list(weekly_repos)
    existing = parse_project_index() or scan_existing_projects()
    all_repos = {}
    for repo in [*daily, *weekly]:
        url = normalize_repo_url(repo.get("url", "") or f"https://github.com/{repo.get('full_name', '')}")
        if url:
            all_repos.setdefault(url.removeprefix("https://github.com/").lower(), repo)

    new_projects = [
        repo for key, repo in all_repos.items()
        if key not in existing
    ]
    return {
        "daily_count": len(daily),
        "weekly_count": len(weekly),
        "new_projects": new_projects,
        "daily_top": daily[:10],
        "weekly_top": sorted(
            weekly, key=lambda repo: repo.get("stars_weekly", 0), reverse=True
        )[:10],
    }


def write_project_index(projects: dict[str, dict],
                        github_summary: Optional[dict] = None) -> Path:
    grouped = defaultdict(list)
    for project in projects.values():
        category, features = classify_project(project)
        project["category"] = category
        project["features"] = features
        project["description"] = fallback_description(project, category, features)
        grouped[category].append(project)

    lines = [
        "# 项目分类索引",
        "",
        f"> 自动维护的项目主索引｜按类型与功能点去重归类｜更新：{TODAY}",
        f"> 当前收录：**{len(projects)}** 个唯一 GitHub 项目",
        "",
        "## 分类统计",
        "",
        "| 类型 | 项目数 |",
        "|---|---:|",
    ]
    counts = Counter({category: len(grouped[category]) for category in PROJECT_CATEGORIES})
    for category in PROJECT_CATEGORIES:
        lines.append(f"| {category} | {counts[category]} |")

    if github_summary is not None:
        new_projects = github_summary.get("new_projects", [])
        lines.extend([
            "", "---", "", "## 今日 GitHub 变动摘要", "",
            f"- 日榜抓取：{github_summary.get('daily_count', 0)} 个项目",
            f"- AI 周增长榜：{github_summary.get('weekly_count', 0)} 个项目",
            f"- 本次新增：**{len(new_projects)}** 个项目（按首次进入索引计算）",
            "",
            "### 本次新增项目",
            "",
            "| 项目 | 来源榜单 | 今日/周增长 | 总 Star |",
            "|---|---|---:|---:|",
        ])
        if new_projects:
            daily_keys = {
                repo.get("full_name", "").lower() for repo in github_summary.get("daily_top", [])
            }
            for repo in new_projects:
                full_name = repo.get("full_name", "")
                board = "日榜 + 周榜" if full_name.lower() in daily_keys else "周榜 AI"
                growth = repo.get("stars_today", repo.get("stars_weekly", 0))
                total = repo.get("total_stars", 0)
                lines.append(
                    f"| [{full_name}]({repo.get('url', '')}) | {board} | "
                    f"+{growth} | {total:,} |"
                )
        else:
            lines.append("| — | 本次没有新项目 | — | — |")

    for category in PROJECT_CATEGORIES:
        lines.extend([
            "",
            "---",
            "",
            f"## {category}",
            "",
            "| 项目 | 中文说明 | 功能点 | 技术栈 | 首次收录 | 最近更新 |",
            "|---|---|---|---|---|---|",
        ])
        for project in sorted(grouped[category], key=lambda item: item["full_name"].lower()):
            description = project["description"].replace("|", "／")
            features = "、".join(project["features"])
            language = clean_text(project.get("language", "")) or "—"
            lines.append(
                f"| [{project['full_name']}]({project['url']}) | {description} | "
                f"{features} | {language} | {project.get('first_seen', TODAY)} | "
                f"{project.get('last_seen', TODAY)} |"
            )
    atomic_write(PROJECT_INDEX, "\n".join(lines))
    return PROJECT_INDEX


def classify_news(title: str, summary: str = "") -> tuple[str, list[str]]:
    text = f"{title} {summary}".lower()
    if _matched(text, "监管", "政策", "安全", "版权", "治理", "隐私", "security"):
        category = "政策、治理与安全"
    elif _matched(text, "视频", "图像", "语音", "多模态", "video", "image", "audio"):
        category = "多模态与内容生成"
    elif _matched(text, "agent", "智能体", "copilot", "助手", "应用"):
        category = "智能体与 AI 应用"
    elif _matched(text, "开源", "github", "框架", "工具", "开发", "sdk", "open source"):
        category = "开源项目与开发工具"
    elif _matched(text, "模型", "研究", "论文", "推理", "训练", "llm", "benchmark"):
        category = "模型与前沿研究"
    else:
        category = "商业产品与行业动态"
    tags = [
        label for label, keys in [
            ("模型", ("模型", "llm", "推理", "训练")),
            ("Agent", ("agent", "智能体")),
            ("开源", ("开源", "github", "open source")),
            ("多模态", ("视频", "图像", "语音", "多模态")),
            ("产品", ("产品", "发布", "上线", "应用")),
            ("行业", ("行业", "公司", "市场", "商业")),
        ] if _matched(text, *keys)
    ]
    return category, tags[:3] or ["行业动态"]


def _parse_existing_insights() -> dict[str, dict]:
    if not INSIGHT_INDEX.exists():
        return {}
    entries = {}
    row = re.compile(
        r"^\|\s*\[([^\]]+)\]\((https?://[^)]+)\)\s*\|\s*([^|]*)\|\s*"
        r"([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|"
    )
    current_category = NEWS_CATEGORIES[-1]
    for line in INSIGHT_INDEX.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading in NEWS_CATEGORIES:
                current_category = heading
        match = row.match(line)
        if match:
            title, url, summary, tags, first_seen, last_seen = match.groups()
            entries[url] = {
                "title": title, "url": url, "summary": clean_text(summary),
                "tags": [tag.strip() for tag in tags.split("、")],
                "category": current_category, "first_seen": first_seen.strip(),
                "last_seen": last_seen.strip(),
            }
    return entries


def scan_historical_insights() -> dict[str, dict]:
    """把历史日报中有效链接迁入长期洞察库，之后不再依赖日报。"""
    entries = {}
    pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
    blocked_titles = {
        "inbox", "news", "tools", "blog", "github", "huggingface",
        "favicon", "copilot", "github app", "mcp", "actions",
    }
    for path in (PROJECT_ROOT / "01_Daily").glob("*ai-digest.md"):
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
        seen_date = date_match.group(1) if date_match else TODAY
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            for title, url in pattern.findall(line):
                title = clean_text(title)
                meaningful_title = (
                    len(re.findall(r"[\u4e00-\u9fff]", title)) >= 4
                    or (len(title.split()) >= 4 and len(title) >= 18)
                )
                compact_title = re.sub(r"[\s-]", "", title)
                if (not meaningful_title or title.lower() in blocked_titles
                        or title.startswith(("http://", "https://"))
                        or re.fullmatch(r"\d+", title)
                        or re.fullmatch(r"[0-9a-f]{24,}", compact_title, re.IGNORECASE)
                        or re.fullmatch(r"[\da-f-]{12,}", title, re.IGNORECASE)
                        or "githubassets.com" in url or "workable.com" in url):
                    continue
                category, tags = classify_news(title)
                existing = entries.setdefault(url, {
                    "title": title,
                    "url": url,
                    "summary": f"{title}；待后续抓取补充详细分析",
                    "tags": tags,
                    "category": category,
                    "first_seen": seen_date,
                    "last_seen": seen_date,
                })
                existing["first_seen"] = min(existing["first_seen"], seen_date)
                existing["last_seen"] = max(existing["last_seen"], seen_date)
    return entries


def merge_insights(items: Iterable[dict]) -> dict[str, dict]:
    entries = _parse_existing_insights()
    if not entries:
        entries = scan_historical_insights()
    for item in items:
        url = item.get("url", "").strip()
        title = clean_text(item.get("title", ""))
        if not url.startswith(("http://", "https://")) or len(title) < 5:
            continue
        summary = clean_text(item.get("summary") or item.get("snippet") or title)[:160]
        fallback_category, fallback_tags = classify_news(title, summary)
        category = item.get("category")
        if category not in NEWS_CATEGORIES:
            category = fallback_category
        tags = item.get("tags") or fallback_tags
        existing = entries.setdefault(url, {
            "title": title, "url": url, "summary": summary,
            "tags": tags, "category": category,
            "first_seen": TODAY, "last_seen": TODAY,
        })
        existing["title"] = title
        if len(summary) > len(existing.get("summary", "")):
            existing["summary"] = summary
        existing["category"] = category
        existing["tags"] = tags
        existing["last_seen"] = TODAY
    return entries


def build_daily_summary(articles: Iterable[dict]) -> dict:
    """从本次运行结果生成可读的“今天抓到了什么”摘要。"""
    items = list(articles)
    valid = [
        item for item in items
        if item.get("url", "").startswith(("http://", "https://"))
        and len(clean_text(item.get("title", ""))) >= 5
    ]
    featured = []
    seen_urls = set()
    for item in valid:
        url = item["url"].strip()
        title = clean_text(item.get("title", ""))
        summary = clean_text(item.get("summary") or item.get("snippet", ""))
        source = clean_text(item.get("source", "未知来源"))
        if url in seen_urls:
            continue
        if len(summary) < 20 or summary == title:
            summary = f"{source} 抓取到主题“{title}”，待补充正文分析。"
        seen_urls.add(url)
        featured.append({
            "title": title[:100],
            "url": url,
            "summary": summary[:180],
            "category": item.get("category") or classify_news(title, summary)[0],
            "source": source,
        })
        if len(featured) >= 5:
            break

    return {
        "source_count": len({clean_text(item.get("source", "")) for item in items if item.get("source")}),
        "sources": sorted({clean_text(item.get("source", "")) for item in items if item.get("source")}),
        "candidate_count": len(items),
        "valid_count": len(valid),
        "featured": featured,
    }


def write_insight_index(entries: dict[str, dict], daily_summary: Optional[dict] = None) -> Path:
    grouped = defaultdict(list)
    for entry in entries.values():
        grouped[entry.get("category", NEWS_CATEGORIES[-1])].append(entry)
    lines = [
        "# 资讯洞察库",
        "",
        f"> 每日抓取结果经分析、去重后持续更新｜更新：{TODAY}",
        f"> 当前收录：**{len(entries)}** 条有效洞察；不再生成逐日文件",
    ]
    if daily_summary is not None:
        sources = "、".join(daily_summary.get("sources", [])) or "无"
        lines.extend([
            "", "---", "", "## 今日抓取摘要", "",
            f"- 采集来源：{daily_summary.get('source_count', 0)} 个",
            f"- 候选条目：{daily_summary.get('candidate_count', 0)} 条；通过有效性检查：{daily_summary.get('valid_count', 0)} 条",
            f"- 来源清单：{sources}",
            "- 今日值得关注的信息：",
        ])
        featured = daily_summary.get("featured", [])
        if featured:
            for item in featured:
                title = item["title"].replace("|", "／")
                summary = item["summary"].replace("|", "／")
                lines.append(
                    f"  - [{title}]({item['url']})（{item['source']}，{item['category']}）：{summary}"
                )
        else:
            lines.append("  - 本次没有足够正文可提炼的条目，保留原始链接待下次补抓。")
    for category in NEWS_CATEGORIES:
        lines.extend([
            "", "---", "", f"## {category}", "",
            "| 主题 | 分析结论 | 标签 | 首次收录 | 最近更新 |",
            "|---|---|---|---|---|",
        ])
        values = sorted(
            grouped[category],
            key=lambda item: (item.get("last_seen", ""), item["title"]),
            reverse=True,
        )
        for entry in values:
            title = entry["title"].replace("|", "／")
            summary = entry["summary"].replace("|", "／")
            tags = "、".join(entry["tags"])
            lines.append(
                f"| [{title}]({entry['url']}) | {summary} | {tags} | "
                f"{entry['first_seen']} | {entry['last_seen']} |"
            )
    atomic_write(INSIGHT_INDEX, "\n".join(lines))
    return INSIGHT_INDEX


def curate_knowledge_base(repos: Iterable[dict],
                          articles: Iterable[dict],
                          github_summary: Optional[dict] = None) -> tuple[Path, Path]:
    articles = list(articles)
    projects = merge_projects(repos)
    project_path = write_project_index(projects, github_summary)
    insights = merge_insights(articles)
    insight_path = write_insight_index(insights, build_daily_summary(articles))
    update_navigation()
    return project_path, insight_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="离线整理 AI 知识库")
    parser.add_argument("--rebuild", action="store_true",
                        help="忽略已有自动索引，从原始收藏和历史记录重建")
    args = parser.parse_args()
    projects = scan_existing_projects() if args.rebuild else merge_projects([])
    project_path = write_project_index(projects)
    insights = scan_historical_insights() if args.rebuild else merge_insights([])
    insight_path = write_insight_index(insights)
    print(f"项目索引：{project_path}")
    print(f"资讯洞察：{insight_path}")
