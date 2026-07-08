"""书签解析器 — 从 Chrome/Edge 导出的 HTML 书签中提取指定文件夹的链接。"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class BookmarkEntry:
    """单个书签条目。"""
    title: str
    url: str
    folder: str  # 所属文件夹名
    add_date: Optional[str] = None


def parse_bookmarks(bookmarks_path: str, folders: Optional[List[str]] = None) -> List[BookmarkEntry]:
    """解析书签 HTML 文件，返回指定文件夹的所有书签。

    使用正则表达式解析 Netscape-format 书签 HTML，避免 HTMLParser
    嵌套层级追踪的复杂性。

    Args:
        bookmarks_path: 书签 HTML 文件路径
        folders: 要提取的文件夹名列表，None 则提取全部

    Returns:
        BookmarkEntry 列表
    """
    with open(bookmarks_path, "r", encoding="UTF-8") as f:
        html_content = f.read()

    # 提取所有 H3 文件夹标题及其层级深度
    folder_pattern = re.compile(
        r'<DT>\s*<H3(?:\s[^>]*)?>(.*?)</H3>',
        re.DOTALL
    )

    # 提取所有 <A> 书签链接
    link_pattern = re.compile(
        r'<DT>\s*<A\s+([^>]*?)>(.*?)</A>',
        re.DOTALL
    )

    entries: List[BookmarkEntry] = []
    current_folder = ""

    # 按顺序扫描所有 H3 和 A 标签
    all_tags = []
    for m in folder_pattern.finditer(html_content):
        all_tags.append(('folder', m.group(1).strip(), m.start()))
    for m in link_pattern.finditer(html_content):
        href_match = re.search(r'href\s*=\s*"([^"]*)"', m.group(1), re.IGNORECASE)
        add_date_match = re.search(r'add_date\s*=\s*"([^"]*)"', m.group(1), re.IGNORECASE)
        href = href_match.group(1) if href_match else ""
        add_date = add_date_match.group(1) if add_date_match else ""
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        all_tags.append(('link', (href, title, add_date), m.start()))

    # 按出现顺序排序
    all_tags.sort(key=lambda x: x[2])

    for tag_type, data, _ in all_tags:
        if tag_type == 'folder':
            current_folder = data
        elif tag_type == 'link':
            href, title, add_date = data
            if href:
                entries.append(BookmarkEntry(
                    title=title,
                    url=href,
                    folder=current_folder,
                    add_date=add_date or None,
                ))

    # 如果指定了文件夹过滤
    if folders:
        entries = [e for e in entries if e.folder.strip() in folders]

    return entries


def get_folder_names(bookmarks_path: str) -> List[str]:
    """获取书签中所有文件夹名称。"""
    with open(bookmarks_path, "r", encoding="UTF-8") as f:
        html_content = f.read()
    h3_pattern = re.compile(r"<H3(?:\s[^>]*)?>(.*?)</H3>", re.DOTALL)
    folders = []
    for match in h3_pattern.finditer(html_content):
        text = match.group(1).strip()
        if text and text not in folders:
            folders.append(text)
    return folders


def print_bookmark_summary(entries: List[BookmarkEntry]):
    """打印书签摘要统计。"""
    from collections import Counter
    folder_counts = Counter(e.folder for e in entries)

    print(f"\n{'='*60}")
    print(f"书签解析完成 — 共 {len(entries)} 条链接")
    print(f"{'='*60}\n")

    for folder, count in sorted(folder_counts.items()):
        print(f"  [{folder}]: {count} 条")

    print()
