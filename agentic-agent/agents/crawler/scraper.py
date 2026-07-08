"""Scrapling 爬虫封装 — 使用 Scrapling 抓取网页内容并提取结构化信息。"""

import os
import re
import time
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from agents.crawler.bookmark_parser import BookmarkEntry

logger = logging.getLogger(__name__)


@dataclass
class ScrapedPage:
    """爬取到的单个页面。"""
    bookmark: BookmarkEntry
    url: str
    title: str
    content: str  # 清理后的纯文本内容
    md_path: str = ""  # 保存的 markdown 文件路径
    success: bool = False
    error: str = ""
    scraped_at: str = ""


class ScrapingAgent:
    """基于 Scrapling 的爬取 Agent。

    工作流程：
    1. 接收书签条目列表
    2. 使用 Scrapling 逐个爬取
    3. 提取标题和正文内容
    4. 保存为 Markdown 文件
    """

    def __init__(self, workspace_path: str = ""):
        if not workspace_path:
            workspace_path = str(Path(__file__).parent.parent.parent)
        self.workspace_path = workspace_path
        self.cache_dir = os.path.join(workspace_path, "state", "scraper_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.results: List[ScrapedPage] = []
        self._fetcher_class = None
        self._import_scrapling()

    def _import_scrapling(self):
        """导入 Scrapling，失败时给出友好提示。"""
        try:
            from scrapling import Fetcher
            self._fetcher_class = Fetcher
            logger.info("Scrapling Fetcher 已加载")
        except ImportError:
            logger.warning(
                "Scrapling 未安装！运行: pip install \"scrapling[fetchers]\""
            )
            self._fetcher_class = None

    def _extract_text_from_response(self, resp) -> str:
        """从 scrapling Response 对象中提取纯文本内容。"""
        try:
            html = resp.html_content if hasattr(resp, 'html_content') else ""
            if not html:
                return ""

            # 移除 script 和 style 标签
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

            # 用 HTMLParser 提取文本
            from html.parser import HTMLParser
            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text_parts = []
                    self._in_pre = False
                def handle_starttag(self, tag, attrs):
                    if tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                               'article', 'section', 'li', 'blockquote', 'pre'):
                        self.text_parts.append('\n')
                    if tag == 'pre':
                        self._in_pre = True
                def handle_endtag(self, tag):
                    if tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                               'article', 'section', 'li', 'blockquote', 'pre'):
                        self.text_parts.append('\n')
                    if tag == 'br':
                        self.text_parts.append('\n')
                def handle_data(self, data):
                    self.text_parts.append(data)

            extractor = TextExtractor()
            extractor.feed(html)
            text = ''.join(extractor.text_parts)

            # 清理：去除多余空白
            text = re.sub(r'[ \t]+', ' ', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()

            return text
        except Exception as e:
            logger.debug(f"文本提取失败: {e}")
            return ""

    def scrape(self, bookmark: BookmarkEntry, delay: float = 1.0) -> ScrapedPage:
        """爬取单个书签页面。"""
        page = ScrapedPage(
            bookmark=bookmark,
            url=bookmark.url,
            title="",
            content="",
            success=False,
        )

        if not self._fetcher_class:
            page.error = "Scrapling 未安装，跳过爬取"
            return page

        try:
            logger.info(f"正在爬取: {bookmark.title} ({bookmark.folder})")

            fetcher = self._fetcher_class(
                configure_headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }
            )

            resp = fetcher.get(bookmark.url)
            time.sleep(delay)

            if resp.status != 200:
                page.error = f"HTTP {resp.status}"
                logger.warning(f"  爬取失败: {bookmark.title} — HTTP {resp.status}")
                return page

            # 提取标题
            title_elem = resp.xpath("//title")
            if title_elem:
                page.title = title_elem[0].text.strip() if title_elem[0].text else bookmark.title
            else:
                page.title = bookmark.title

            # 提取正文内容
            page.content = self._extract_text_from_response(resp)

            if not page.content:
                page.content = f"页面标题: {page.title}\nURL: {bookmark.url}\n分类: {bookmark.folder}"

            if len(page.content) > 50000:
                page.content = page.content[:50000] + "\n\n...(内容过长已截断)"

            page.success = True
            page.scraped_at = time.strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"  爬取成功: {page.title} ({len(page.content)} 字符)")

        except Exception as e:
            page.error = str(e)
            logger.warning(f"  爬取失败: {bookmark.title} — {e}")

        return page

    def scrape_batch(self, bookmarks: List[BookmarkEntry], delay: float = 1.5) -> List[ScrapedPage]:
        """批量爬取书签。"""
        self.results = []
        total = len(bookmarks)
        logger.info(f"开始批量爬取: {total} 个链接")

        for i, bm in enumerate(bookmarks, 1):
            logger.info(f"[{i}/{total}] ")
            result = self.scrape(bm, delay=delay)
            self.results.append(result)

        success = sum(1 for r in self.results if r.success)
        failed = total - success
        logger.info(f"\n爬取完成: {success} 成功, {failed} 失败")

        return self.results

    def save_to_markdown(self, page: ScrapedPage) -> str:
        """将爬取内容保存为 Markdown 文件。"""
        if not page.success or not page.content:
            return ""

        safe_title = "".join(c if c.isalnum() or c in " _-." else "_" for c in page.bookmark.title)
        safe_title = safe_title.replace(" ", "_")[:60]
        folder_safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in page.bookmark.folder)

        md_dir = os.path.join(self.cache_dir, folder_safe)
        os.makedirs(md_dir, exist_ok=True)

        md_path = os.path.join(md_dir, f"{safe_title}.md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {page.title}\n\n")
            f.write(f"> 来源: [{page.bookmark.url}]({page.bookmark.url})\n")
            f.write(f"> 分类: {page.bookmark.folder}\n")
            f.write(f"> 爬取时间: {page.scraped_at}\n\n")
            f.write("---\n\n")
            f.write(page.content)

        page.md_path = md_path
        return md_path

    def save_all(self):
        """保存所有爬取结果为 Markdown 文件。"""
        saved = 0
        for page in self.results:
            if page.success:
                path = self.save_to_markdown(page)
                if path:
                    saved += 1
        logger.info(f"已保存 {saved}/{len(self.results)} 个页面到 {self.cache_dir}")
        return saved
