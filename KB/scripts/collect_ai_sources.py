#!/usr/bin/env python3
"""
collect_ai_sources.py — 采集 AI 资讯原始数据

数据源：
  1. Chrome 书签「AI 资讯」文件夹（Default Profile, 跳过 synced）
  2. last30days public RSS (https://www.last30days.com/rss)
  3. newsnow.busiyi.world 热搜 API
  4. sopilot.net hot tweets

输出：
  - 原始 JSON 写到 stdout（被 cron 接收）
  - 同时落地到 cache/last_run.json（去重用）

Usage:
  python collect_ai_sources.py > today.json
  python collect_ai_sources.py --print-cache   # 打印上次结果
"""
from __future__ import annotations
import json
import os
import sys
import re
import argparse
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / "last_run.json"
SEEN_FILE = CACHE_DIR / "seen_urls.json"

CHROME_BOOKMARKS = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Google" / "Chrome" / "User Data" / "Default" / "Bookmarks"
)
AI_NEWS_FOLDER = "AI资讯"

# 公开数据源 —— 全部为入口站首页热帖抓取（之前的 API 都 404/SSL 失败）
# 每个站点配一个 article_link 提取器（CSS 选择器粗略匹配）
HOMEPAGE_SCRAPERS = [
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/",
        "title_sel": "h2 a, .article-title a, .post-title a",
        "link_sel": "h2 a, .article-title a, .post-title a",
        "host": "jiqizhixin.com",
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "title_sel": "h3 a, .entry-title a, .article-title a",
        "link_sel": "h3 a, .entry-title a, .article-title a",
        "host": "qbitai.com",
    },
    {
        "name": "AIBase基地",
        "url": "https://www.aibase.com/zh",
        "title_sel": "h2 a, h3 a, .title a",
        "link_sel": "h2 a, h3 a, .title a",
        "host": "aibase.com",
    },
    {
        "name": "Hugging Face 博客",
        "url": "https://huggingface.co/blog/zh",
        "title_sel": "h2 a, h3 a, .blog-title a",
        "link_sel": "h2 a, h3 a, .blog-title a",
        "host": "huggingface.co",
    },
]


def fetch(url: str, timeout: int = 15) -> str | None:
    """HTTP GET with User-Agent."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Hermes-Wiki-Bot)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(f"[warn] fetch failed {url}: {e}", file=sys.stderr)
        return None


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return set()


def save_seen(seen: set[str]) -> None:
    SEEN_FILE.write_text(
        json.dumps(sorted(seen)[-2000:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------- Chrome 书签 ----------------
def collect_chrome_bookmarks() -> list[dict]:
    """递归 Chrome 书签 JSON，定位「AI 资讯」文件夹下的所有 url。
    明确跳过 'synced' 根（防移动设备内容污染）。"""
    if not CHROME_BOOKMARKS.exists():
        print(f"[warn] Chrome bookmarks not found: {CHROME_BOOKMARKS}", file=sys.stderr)
        return []

    try:
        data = json.loads(CHROME_BOOKMARKS.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[warn] read Chrome bookmarks failed: {e}", file=sys.stderr)
        return []

    out: list[dict] = []
    # 限定在 bookmark_bar 和 other 两个根，synced 跳过
    roots = data.get("roots", {})
    for root_key in ("bookmark_bar", "other"):
        root = roots.get(root_key, {})
        _walk_bookmarks(root, AI_NEWS_FOLDER, out, path_parts=[])

    return out


def _walk_bookmarks(node: dict, target_folder: str, out: list[dict], path_parts: list[str]) -> None:
    """递归找 target_folder 命中的文件夹，收集其下所有 url。"""
    if node.get("type") != "folder":
        return
    name = node.get("name", "")
    new_path = path_parts + [name]
    if name == target_folder:
        # 命中，收集这个文件夹下所有 url
        _collect_urls(node, out, new_path)
        # 不 return —— 允许同一棵子树有多个同名文件夹
    for child in node.get("children", []):
        if child.get("type") == "folder":
            _walk_bookmarks(child, target_folder, out, new_path)


def _collect_urls(node: dict, out: list[dict], path: list[str]) -> None:
    for child in node.get("children", []):
        if child.get("type") == "url":
            url = child.get("url", "").strip()
            if url and url.startswith(("http://", "https://")):
                out.append({
                    "title": child.get("name", url),
                    "url": url,
                    "source": "chrome-bookmarks",
                    "folder": " / ".join(path),
                })
        elif child.get("type") == "folder":
            _collect_urls(child, out, path + [child.get("name", "")])


# ---------------- 公开 RSS ----------------
def parse_rss(xml_text: str, source_name: str) -> list[dict]:
    """极简 RSS 解析：title/link/pubDate。"""
    items = []
    for m in re.finditer(
        r"<item[^>]*>(.*?)</item>", xml_text, re.DOTALL | re.IGNORECASE
    ):
        block = m.group(1)
        title = _tag(block, "title")
        link = _tag(block, "link") or _tag(block, "guid")
        pub = _tag(block, "pubDate") or _tag(block, "dc:date")
        if link:
            items.append({
                "title": _strip_html(title or link),
                "url": link.strip(),
                "source": source_name,
                "published": pub or "",
            })
    return items


# ---------------- 首页热帖（极简） ----------------
def scrape_homepage(scraper: dict, limit: int = 10) -> list[dict]:
    """极简 HTML 解析：用 title_sel 取每条 <a> 文本 + href。"""
    from html.parser import HTMLParser

    text = fetch(scraper["url"])
    if not text:
        return []

    # 简化：用 CSS 选择器名字匹配的标签扫描
    target_tags = re.findall(
        rf'<(h2|h3)\s*[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not target_tags:
        # 兜底：任意 a[href] 抓取前 limit
        target_tags = re.findall(
            r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            text,
            re.DOTALL | re.IGNORECASE,
        )
        target_tags = [(t[0], t[0], t[1]) for t in target_tags]

    out: list[dict] = []
    seen: set[str] = set()
    host = scraper["host"]
    for tag, href, raw in target_tags:
        # 绝对化
        if href.startswith("/"):
            url = f"https://{host}{href}"
        elif href.startswith("http"):
            url = href
        else:
            continue
        if host not in url or url in seen:
            continue
        title = _strip_html(raw).strip()
        if not title or len(title) < 6 or len(title) > 200:
            continue
        seen.add(url)
        out.append({
            "title": title,
            "url": url,
            "source": scraper["name"],
            "published": "",
        })
        if len(out) >= limit:
            break
    return out


def _tag(block: str, name: str) -> str | None:
    m = re.search(
        rf"<{name}[^>]*>(.*?)</{name}>", block, re.DOTALL | re.IGNORECASE
    )
    return m.group(1).strip() if m else None


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


# ---------------- 公开 JSON API ----------------
def parse_newsnow_api(text: str) -> list[dict]:
    """newsnow 格式: {status, items: [{id, title, url, ...}, ...]}"""
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        return []
    out = []
    for it in d.get("data", {}).get("items", []) or d.get("items", []):
        title = it.get("title") or it.get("text") or ""
        url = it.get("url") or it.get("mobileUrl") or ""
        if title and url:
            out.append({
                "title": title,
                "url": url,
                "source": "newsnow",
                "published": str(it.get("createdAt", "")),
            })
    return out


def parse_sopilot(text: str) -> list[dict]:
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        return []
    items = d.get("data", []) if isinstance(d, dict) else d
    out = []
    for it in items if isinstance(items, list) else []:
        title = it.get("title") or it.get("text") or ""
        url = it.get("url") or it.get("link") or ""
        if title and url:
            out.append({
                "title": title,
                "url": url,
                "source": "sopilot",
                "published": str(it.get("timestamp", "")),
            })
    return out


# ---------------- 主流程 ----------------
def collect_all() -> dict:
    seen = load_seen()
    items: list[dict] = []
    sources_summary = {}

    # 1. Chrome 书签
    chrome_items = collect_chrome_bookmarks()
    sources_summary["chrome-bookmarks"] = len(chrome_items)
    items.extend(chrome_items)

    # 2. 公开源（首页热帖抓取）
    for scraper in HOMEPAGE_SCRAPERS:
        parsed = scrape_homepage(scraper, limit=10)
        sources_summary[scraper["name"]] = len(parsed)
        items.extend(parsed)

    # 去重（按 url），丢弃已 seen 的
    unique = []
    for it in items:
        url = it.get("url", "")
        if not url or url in seen:
            continue
        unique.append(it)
        seen.add(url)

    save_seen(seen)

    result = {
        "collected_at": datetime.now(CST).isoformat(),
        "sources": sources_summary,
        "total_unique": len(unique),
        "items": unique,
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--print-cache", action="store_true", help="打印上次缓存")
    p.add_argument("--out", help="写到指定文件，默认 stdout")
    args = p.parse_args()

    if args.print_cache:
        if CACHE_FILE.exists():
            sys.stdout.write(CACHE_FILE.read_text(encoding="utf-8"))
            return 0
        print("[error] no cache yet", file=sys.stderr)
        return 1

    result = collect_all()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    CACHE_FILE.write_text(text, encoding="utf-8")
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
