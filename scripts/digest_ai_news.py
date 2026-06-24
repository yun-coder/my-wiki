#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
digest_ai_news.py — 每日 AI 资讯采集 + LLM 蒸馏

流程:
1. 读 Chrome 书签「AI资讯」分类
2. 抓取量子位/AIBase/HuggingFace 首页热帖
3. 调 Agnes LLM 蒸馏成 5-10 条精华
4. 写 D:\学习院\my-wiki\01_Daily\<今天>-ai-digest.md
5. 在 stdout 输出推送摘要

用法:
  python digest_ai_news.py
  
注意:
- 需要 .env 文件 (AGNES_API_KEY)
- 首次运行会自动安装依赖
"""
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

import httpx

# 自动加载 .env
_ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
if _ENV_PATH.exists():
    for line in _ENV_PATH.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def fetch_chrome_ai_bookmarks() -> list[dict]:
    """读 Chrome 书签里「AI资讯」分类"""
    bm_path = Path(os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data/Default/Bookmarks')
    if not bm_path.exists():
        return []
    
    data = json.loads(bm_path.read_text(encoding='utf-8'))
    results = []
    
    def walk_folder(folder, path=""):
        if not isinstance(folder, dict):
            return
        name = folder.get("name", "")
        folder_path = f"{path}/{name}"
        
        if folder.get("type") == "url":
            # 这是一个 URL
            # 只要父路径包含 AI 就收集
            if "AI" in path.upper() or "AI" in name.upper() or "资讯" in name or "News" in name:
                # 只收集 AI资讯 下的 URL
                if "/AI资讯/" in folder_path:
                    results.append({
                        "source": "chrome-bookmarks",
                        "title": name,
                        "url": folder.get("url", ""),
                    })
        elif "children" in folder:
            for child in folder["children"]:
                walk_folder(child, folder_path)
    
    try:
        root = data.get("roots", {})
        for key in ["bookmark_bar", "other", "synced"]:
            if key in root:
                bar = root[key]
                for child in bar.get("children", []):
                    walk_folder(child)
    except Exception:
        pass
    
    return results


def fetch_blog_topics(url: str, title: str) -> list[dict]:
    """抓取博客首页热帖"""
    results = []
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=15, follow_redirects=True)
        if r.status_code != 200:
            return results
        
        # 提取文章链接 (针对量子位等站点)
        links = re.findall(r'href="([^"]+\.html[^\"]*)"', r.text)
        
        for link in links[:10]:  # 最多 10 篇
            if link.startswith('/'):
                link = url.rstrip('/') + link
            elif not link.startswith('http'):
                link = url.rstrip('/') + '/' + link
            
            # 去重
            if link in [item['url'] for item in results]:
                continue
            
            # 抓取文章标题
            article_title = link.split('/')[-1].replace('-', ' ').replace('_', ' ')
            try:
                article_r = httpx.get(link, headers={"User-Agent": UA}, timeout=10, follow_redirects=True)
                if article_r.status_code == 200:
                    article_titles = re.findall(r'<title[^>]*>([^<]+)</title>', article_r.text, re.IGNORECASE)
                    if article_titles:
                        article_title = article_titles[0].split(' – ')[0].split(' - ')[0].strip()
            except Exception:
                pass
            
            results.append({
                "source": title,
                "title": article_title,
                "url": link,
            })
    except Exception:
        pass
    
    return results


def fetch_qbit_topics() -> list[dict]:
    """抓取量子位热帖"""
    return fetch_blog_topics("https://www.qbitai.com/", "量子位")


def fetch_aibase_topics() -> list[dict]:
    """抓取 AIBase 热帖"""
    return fetch_blog_topics("https://aibase.com/", "AIBase基地")


def fetch_hf_topics() -> list[dict]:
    """抓取 HuggingFace 热帖"""
    return fetch_blog_topics("https://huggingface.co/blog", "HuggingFace")


def distill_with_llm(items: list[dict]) -> str:
    """调 LLM 蒸馏成 5-10 条精华"""
    api_key = os.environ.get("AGNES_API_KEY", "")
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
    model = os.environ.get("AGNES_MODEL", "agnes-2.0-flash")
    
    if not api_key:
        return None
    
    # 构造 prompt
    prompt = f"""你是 AI 资讯编辑。从以下 {len(items)} 条候选中选出 5-10 条最有价值的，按热度排序。

每条候选:
{chr(10).join([f"- [{i}] {item['title']} ({item['source']}) {item['url']}" for i, item in enumerate(items)])}

要求:
1. 按热度/影响力排序
2. 每条包含: 标题、一句话摘要、来源
3. 格式:
[1] 标题
> 摘要...
来源: xxx

4. 排除重复/低价值内容"""
    
    try:
        r = httpx.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是专业的 AI 资讯编辑，擅长从大量候选中精选最有价值的资讯。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"LLM 失败 (HTTP Error {r.status_code})", file=sys.stderr)
            return None
    except Exception as e:
        print(f"LLM 异常: {e}", file=sys.stderr)
        return None


def heuristic_filter(items: list[dict]) -> list[dict]:
    """LLM 失败时的启发式过滤"""
    # 简单按标题长度和关键词排序
    keywords = ["AI", "模型", "开源", "发布", "突破", "论文", "工具", "平台"]
    
    scored = []
    for item in items:
        score = 0
        title = item["title"].upper()
        for kw in keywords:
            if kw in title:
                score += 1
        score += len(item["title"])  # 标题越长越详细
        scored.append((score, item))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:10]]


def main() -> int:
    print("[1/4] 采集原始数据...")
    
    # 1. 采集
    all_items = []
    
    # Chrome 书签
    bm_items = fetch_chrome_ai_bookmarks()
    print(f"     拿到 {len(bm_items)} 条书签")
    all_items.extend(bm_items)
    
    # 博客热帖
    qbit = fetch_qbit_topics()
    print(f"     量子位: {len(qbit)} 条")
    all_items.extend(qbit)
    
    aibase = fetch_aibase_topics()
    print(f"     AIBase: {len(aibase)} 条")
    all_items.extend(aibase)
    
    hf = fetch_hf_topics()
    print(f"     HuggingFace: {len(hf)} 条")
    all_items.extend(hf)
    
    if not all_items:
        print("     无数据，退出")
        return 0
    
    print(f"     共 {len(all_items)} 条候选")
    
    # 2. 蒸馏
    print("[2/4] 调 LLM 蒸馏...")
    distilled = distill_with_llm(all_items)
    
    if distilled:
        print(f"     LLM 蒸馏成功")
    else:
        print(f"     LLM 失败，回退启发式过滤")
        distilled_items = heuristic_filter(all_items)
        distilled = f"📰 **{datetime.now().strftime('%Y-%m-%d')} AI 资讯精选** ({len(distilled_items)} 条)\n\n"
        for i, item in enumerate(distilled_items[:10], 1):
            distilled += f"**[{i}]** {item['title']} — {item['source']}\n> {item['url']}\n\n"
    
    # 3. 写入
    print("[3/4] 写入日报...")
    daily_dir = Path(r'D:\学习院\my-wiki\01_Daily')
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    file_path = daily_dir / f'{today}-ai-digest.md'
    
    header = f"""# 📰 AI 资讯日报 - {today}

> 自动采集 + LLM 蒸馏
> 来源: Chrome 书签 + 量子位 + AIBase + HuggingFace
"""
    
    file_path.write_text(header + distilled, encoding='utf-8')
    print(f"     写入: {file_path}")
    
    # 4. 推送摘要
    print("[4/4] 推送摘要...")
    print()
    print(distilled)
    print(f"📄 完整简报: `KB\\01_Daily\\{today}-ai-digest.md`")
    print("✅ 回复 `1 3 5` 把卡片加入 [[04_Knowledge/Notes/]]")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
