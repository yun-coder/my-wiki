#!/usr/bin/env python3
"""
digest_ai_news.py — 每天 12:00 由 cron 调用

流程：
  1. 调 collect_ai_sources.py 拿原始 items
  2. 调用 LLM 蒸馏：30-50 条 → 5-10 条精华
  3. 写 my-wiki/KB/01_Daily/<YYYY-MM-DD>-ai-digest.md（含 [1]...[N] 编号）
  4. 推送当前聊天：精简单报 + 提示「回复 1 3 5 加入知识库」

LLM 调用通过 my-agents 的 OpenAI 兼容 API（dev.json 配置）。
推送通道：写入 inbox 文件 + 调用 hermes notify（可选）。

Usage:
  python digest_ai_news.py           # 完整流程
  python digest_ai_news.py --dry-run # 只蒸馏不写文件
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

CST = timezone(timedelta(hours=8))
SCRIPT_DIR = Path(__file__).parent
WIKI_ROOT = SCRIPT_DIR.parent
DAILY_DIR = WIKI_ROOT / "01_Daily"
NOTES_DIR = WIKI_ROOT / "04_Knowledge" / "Notes"
INBOX_FILE = WIKI_ROOT / ".._inbox.md"   # 放在 KB 同级，根目录显眼位置

# 蒸馏 prompt
DISTILL_PROMPT = """你是 AI 行业新闻编辑。给我一个**今日 AI 资讯精选**简报。

输入是从多个 AI 资讯源抓来的 {total} 条原始材料（含标题、URL、来源）：

```json
{raw_items}
```

要求：
1. 选 5-10 条**最有信息量、最值得个人知识库收藏**的（去重 + 过滤低质水稿 / 软文 / 页面导航）
2. 每条给：
   - **标题**（简明中文概括，不超过 25 字）
   - **原文标题**（原标题）
   - **来源**（保留原始来源名）
   - **URL**（保留）
   - **2-3 句摘要**（中文，说明这条为什么值得收藏）
3. 严格按 JSON 输出，不要 Markdown 代码块包装

输出格式（**纯 JSON 数组**）：
[
  {{
    "id": 1,
    "title": "中文标题",
    "original_title": "原文标题",
    "source": "来源",
    "url": "https://...",
    "summary": "摘要"
  }},
  ...
]
"""


def call_llm(items: list[dict], model_config: dict) -> list[dict]:
    """调 OpenAI 兼容 API 蒸馏。model_config 来自 dev.json。"""
    import urllib.request
    prompt = DISTILL_PROMPT.format(
        total=len(items),
        raw_items=json.dumps(items, ensure_ascii=False, indent=2)[:15000],
    )

    req_body = {
        "model": model_config.get("model", "gpt-4.1-mini"),
        "messages": [
            {"role": "system", "content": "你是 AI 资讯蒸馏助手，输出严格 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

    req = urllib.request.Request(
        f"{model_config['base_url'].rstrip('/')}/chat/completions",
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {model_config['api_key']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode("utf-8"))
    content = resp["choices"][0]["message"]["content"]

    # 尝试解析 JSON
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.M)
    return json.loads(content)


def render_digest_md(date_str: str, items: list[dict], raw_count: int) -> str:
    """渲染每日 digest markdown。"""
    lines = [
        f"# {date_str} AI 资讯精选",
        "",
        f"> 来源：Chrome「AI资讯」书签 + 量子位/AIBase/HuggingFace 抓取（原始 {raw_count} 条，蒸馏后 {len(items)} 条）",
        f"> 推送：cron 12:00 自动 | LLM 蒸馏 | 回复 `1 3 5` 把卡片加入 [[04_Knowledge/Notes/]]",
        "",
    ]
    for it in items:
        lines.extend([
            f"## [{it['id']}] {it['title']}",
            f"- **原文**: {it.get('original_title','')}",
            f"- **来源**: {it['source']}",
            f"- **链接**: <{it['url']}>",
            f"- **摘要**: {it['summary']}",
            "",
            f"**是否加入知识库**: [ ] 1  复制命令：`1`",
            "",
        ])
    lines.extend([
        "---",
        "",
        "## 勾选指令",
        "",
        "在本对话回复（空格或逗号分隔数字）：",
        "",
        "```",
        "1 3 5        # 加入第 1、3、5 条",
        "all          # 全部加入",
        "none         # 都不加入",
        "```",
        "",
        "*由 cron + LLM 自动生成*",
        "",
    ])
    return "\n".join(lines)


def heuristic_filter(items: list[dict], limit: int = 8) -> list[dict]:
    """启发式过滤：去导航链接、URL 形态判别、按来源均衡取。

    判定为「导航/凑数」的规则：
      - 标题 < 8 字（基本是入口站名）
      - 标题含 '首页'、'登录'、'注册'、'API'、'定价' 等营销词
      - 标题纯英文且与 chrome-bookmarks 来源里的入口站名一致
    """
    nav_keywords = [
        "首页", "登录", "注册", "定价", "文档", "API", "Console",
        "开发平台", "工作台", "Dashboard", "Sign in", "Sign up",
        "Pricing", "Docs",
    ]
    # chrome-bookmarks 入口站名（黑名单，避免把这些当文章）
    chrome_entry_names = {"X (Twitter)", "Reddit", "机器之心", "量子位", "AIBase基地",
                          "何夕2077个人站", "Hugging Face 博客", "Zread"}

    out: list[dict] = []
    seen_urls: set[str] = set()
    by_source: dict[str, int] = {}

    for it in items:
        title = it.get("title", "").strip()
        url = it.get("url", "")
        src = it.get("source", "")

        if not title or not url or url in seen_urls:
            continue
        if title in chrome_entry_names:  # 入口站本身跳过
            continue
        if len(title) < 8:
            continue
        if any(k.lower() in title.lower() for k in nav_keywords):
            continue

        # 按来源均衡（每源最多 limit 条）
        if by_source.get(src, 0) >= max(3, limit // 2):
            continue

        seen_urls.add(url)
        by_source[src] = by_source.get(src, 0) + 1
        out.append({
            "id": len(out) + 1,
            "title": title[:50],
            "original_title": title,
            "source": src,
            "url": url,
            "summary": f"来自 {src}，标题: {title[:80]}",
        })
        if len(out) >= limit:
            break

    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--date", help="覆盖日期（默认今天）", default=None)
    args = p.parse_args()

    date_str = args.date or datetime.now(CST).strftime("%Y-%m-%d")

    # 1. 调采集脚本
    print(f"[1/4] 采集原始数据...", file=sys.stderr)
    raw_proc = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "collect_ai_sources.py")],
        capture_output=True, text=True, timeout=60
    )
    if raw_proc.returncode != 0:
        print(f"[error] collect failed: {raw_proc.stderr}", file=sys.stderr)
        return 1
    try:
        raw = json.loads(raw_proc.stdout)
    except json.JSONDecodeError as e:
        print(f"[error] collect output not JSON: {e}", file=sys.stderr)
        return 1
    raw_items = raw.get("items", [])
    print(f"     拿到 {len(raw_items)} 条原始", file=sys.stderr)

    if not raw_items:
        print("[warn] no items, skip distillation", file=sys.stderr)
        return 0

    # 2. 调 LLM 蒸馏（如可用）
    print(f"[2/4] 调 LLM 蒸馏...", file=sys.stderr)
    digest = None
    if os.environ.get("HERMES_LLM_DISABLED") != "1":
        dev_json = Path(r"D:/学习院/my-agents/dev.json")
        if dev_json.exists():
            cfg = json.loads(dev_json.read_text(encoding="utf-8"))
            model_cfg = cfg.get("openai", {})
            if model_cfg.get("api_key"):
                try:
                    digest = call_llm(raw_items, model_cfg)
                except Exception as e:
                    print(f"     LLM 失败 ({e})，回退启发式过滤", file=sys.stderr)

    if digest is None:
        # 启发式过滤
        digest = heuristic_filter(raw_items, limit=8)
        print(f"     启发式过滤: {len(digest)} 条", file=sys.stderr)
    else:
        print(f"     LLM 蒸馏: {len(digest)} 条", file=sys.stderr)

    # 3. 渲染 + 写文件
    md = render_digest_md(date_str, digest, len(raw_items))
    out_path = DAILY_DIR / f"{date_str}-ai-digest.md"
    if args.dry_run:
        print("=" * 60, file=sys.stderr)
        print(md, file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        return 0
    out_path.write_text(md, encoding="utf-8")
    print(f"     写入: {out_path}", file=sys.stderr)

    # 4. 推送到当前聊天（inbox 文件 + 简短 stdout）
    print(f"[4/4] 推送摘要...", file=sys.stderr)
    summary = "\n".join([
        f"📰 **{date_str} AI 资讯精选** ({len(digest)} 条)",
        "",
        *[f"**[{d['id']}]** {d['title']} — {d['source']}\n> {d['summary'][:80]}..." for d in digest],
        "",
        f"📄 完整简报：`{out_path.relative_to(WIKI_ROOT.parent)}`",
        "✅ 回复 `1 3 5` 把卡片加入 [[04_Knowledge/Notes/]]",
    ])
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
