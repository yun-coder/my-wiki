#!/usr/bin/env python3
"""
add_to_kb.py — 把你勾选的 AI 资讯卡片追加到 04_Knowledge/Notes/

Usage:
  python add_to_kb.py --date 2026-06-10 --ids 1 3 5
  python add_to_kb.py --date 2026-06-10 --ids all
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

CST = timezone(timedelta(hours=8))
SCRIPT_DIR = Path(__file__).parent
WIKI_ROOT = SCRIPT_DIR.parent
DAILY_DIR = WIKI_ROOT / "01_Daily"
NOTES_DIR = WIKI_ROOT / "04_Knowledge" / "Notes"


def parse_digest(date_str: str) -> list[dict]:
    p = DAILY_DIR / f"{date_str}-ai-digest.md"
    if not p.exists():
        print(f"[error] digest not found: {p}", file=sys.stderr)
        sys.exit(1)
    text = p.read_text(encoding="utf-8")

    items = []
    for m in re.finditer(
        r"## \[(\d+)\] (.+?)\n"
        r"- \*\*原文\*\*: (.+?)\n"
        r"- \*\*来源\*\*: (.+?)\n"
        r"- \*\*链接\*\*: <(.+?)>\n"
        r"- \*\*摘要\*\*: (.+?)\n",
        text,
    ):
        items.append({
            "id": int(m.group(1)),
            "title": m.group(2).strip(),
            "original_title": m.group(3).strip(),
            "source": m.group(4).strip(),
            "url": m.group(5).strip(),
            "summary": m.group(6).strip(),
        })
    return items


def slugify(text: str, max_len: int = 60) -> str:
    """生成文件名友好的 slug（中文保留 + 拼音？这里直接保中文 + 截断）。"""
    text = re.sub(r"[\s/\\:?*\"<>|]+", "-", text)
    return text[:max_len].rstrip("-")


def write_note(date_str: str, item: dict) -> Path:
    """把单条卡片写到 04_Knowledge/Notes/<slug>-<id>.md"""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    # 文件名带 ID 防止同日两条重名
    fname = f"{slugify(item['title'])}-{item['id']}.md"
    out = NOTES_DIR / fname
    today = datetime.now(CST).strftime("%Y-%m-%d")
    tags = f"#AI资讯 #AI #{item['source']}"
    content = (
        f"---\n"
        f"created: {today}\n"
        f"tags: {tags}\n"
        f"source: {item['url']}\n"
        f"source_title: \"{item['original_title']}\"\n"
        f"from_digest: {date_str}-ai-digest.md\n"
        f"---\n\n"
        f"# {item['title']}\n\n"
        f"> 摘自 [{date_str} AI 资讯简报](../01_Daily/{date_str}-ai-digest.md)，"
        f"原文：[{item['original_title']}]({item['url']})（{item['source']}）\n\n"
        f"## 摘要\n\n{item['summary']}\n\n"
        f"## 原文链接\n\n<{item['url']}>\n\n"
        f"---\n\n"
        f"*由 add_to_kb.py 自动写入 | 标签: {tags}*\n"
    )
    out.write_text(content, encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="日期 YYYY-MM-DD")
    p.add_argument("--ids", nargs="+", required=True, help="勾选编号，如 1 3 5 或 all")
    args = p.parse_args()

    items = parse_digest(args.date)
    by_id = {x["id"]: x for x in items}

    if args.ids == ["all"]:
        chosen = list(by_id.values())
    else:
        chosen = []
        for tok in args.ids:
            ids = [int(x) for x in re.findall(r"\d+", tok)]
            chosen.extend(by_id[i] for i in ids if i in by_id)
        # 去重保序
        seen, uniq = set(), []
        for c in chosen:
            if c["id"] not in seen:
                seen.add(c["id"]); uniq.append(c)
        chosen = uniq

    if not chosen:
        print("[warn] nothing selected (ids not in digest?)", file=sys.stderr)
        return 1

    print(f"📝 写入 {len(chosen)} 条到 04_Knowledge/Notes/：", file=sys.stderr)
    for c in chosen:
        path = write_note(args.date, c)
        rel = path.relative_to(WIKI_ROOT)
        print(f"  ✅ [{c['id']}] {c['title']}  →  {rel}")

    print(f"\n📚 共 {len(chosen)} 条已加入知识库", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
