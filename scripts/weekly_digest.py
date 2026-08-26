#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weekly_digest.py — 周度精华提取脚本

流程:
1. 扫描项目目录下 01_Daily\ 目录中的所有日报
2. 读取前 N 天的日报内容
3. 调 LLM 提取精华知识点，分类归档到 AI知识库/01-04/
4. 质量验证（5 Gates）

用法:
  python weekly_digest.py [--days 7]
"""
from __future__ import annotations
import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from openai import OpenAI

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


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = PROJECT_ROOT / '01_Daily'
KB_DIR = PROJECT_ROOT / 'AI知识库'

CATEGORY_MAP = {
    '模型': '01-模型',
    '工具': '02-工具',
    '项目': '03-项目',
    '视频': '04-视频',
}


def load_weekly_digests(days: int = 7) -> list[str]:
    """加载最近 N 天的日报内容"""
    cutoff = datetime.now() - timedelta(days=days)
    digests = []
    
    if not DAILY_DIR.exists():
        return digests
    
    for md_file in sorted(DAILY_DIR.glob('*.md')):
        try:
            # 文件名格式: 2026-06-30-ai-digest.md
            stem = md_file.stem
            parts = stem.split('-')
            if len(parts) >= 3:
                date_str = '-'.join(parts[:3])  # 2026-06-30
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if file_date >= cutoff:
                    content = md_file.read_text(encoding='utf-8')
                    digests.append(content)
        except Exception:
            continue
    
    return digests


def extract_with_llm(digests: list[str]) -> list[dict]:
    """调 LLM 提取精华知识点"""
    api_key = os.environ.get("AGNES_API_KEY", "")
    base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
    model = os.environ.get("AGNES_MODEL", "agnes-1.5-flash")
    
    if not api_key:
        print("ERROR: 缺少 AGNES_API_KEY", file=sys.stderr)
        return []
    
    combined = "\n\n=== 分割线 ===\n\n".join(digests)
    
    prompt = f"""你是 AI 知识整理专家。从以下日报中提取有价值的知识点。

{combined}

要求:
1. 按分类提取: 模型(01-模型)、工具(02-工具)、项目(03-项目)、视频(04-视频)
2. 每个知识点包含:
   - title: 简洁标题
   - category: 分类目录名
   - summary: 一句话摘要
   - content: 结构化内容（关键信息、工具名、API、使用方式等）
   - tags: 标签列表
   - source_url: 来源链接（必须从日报中提取，格式如 https://www.qbitai.com/...）
3. 只提取真正有价值的内容，排除低质量条目
4. 输出 JSON 格式:
{{
  "knowledge_points": [
    {{
      "title": "...",
      "category": "01-模型",
      "summary": "...",
      "content": "...",
      "tags": ["..."],
      "source_url": "https://www.qbitai.com/..."
    }}
  ]
}}

重要: source_url 必须填写真实的来源链接，不能为空字符串。
"""
    
    try:
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=180.0)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是专业的 AI 知识整理专家，擅长从资讯中提取结构化知识点。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        
        text = response.choices[0].message.content
        
        # 解析 JSON
        json_match = re.search(r'\{[\s\S]*"knowledge_points"[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            return data.get('knowledge_points', [])
        else:
            print(f"ERROR: 无法解析 LLM 响应", file=sys.stderr)
            return []
    except Exception as e:
        print(f"LLM 异常: {e}", file=sys.stderr)
        return []


def archive_knowledge_points(points: list[dict]) -> list[str]:
    """归档知识点到知识库"""
    saved = []
    
    for kp in points:
        category = kp.get('category', '02-工具')
        title = kp.get('title', '未命名')
        tags = kp.get('tags', [])
        summary = kp.get('summary', '')
        content = kp.get('content', '')
        source_url = kp.get('source_url', '')
        
        target_dir = KB_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 安全文件名
        safe_name = re.sub(r'[^\w\-_.]', '_', title)[:80]
        md_path = target_dir / f"{safe_name}.md"
        
        # 如果文件已存在，加时间戳
        if md_path.exists():
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            md_path = target_dir / f"{safe_name}_{ts}.md"
        
        # 写入 Markdown
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            if tags:
                f.write(f"**标签**: {' | '.join(tags)}\n\n")
            f.write(f"> **摘要**: {summary}\n\n")
            if source_url:
                f.write(f"> 来源: [{source_url}]({source_url})\n")
            f.write(f"> 分类: {category}\n\n")
            f.write("---\n\n")
            f.write(content)
        
        saved.append(str(md_path))
        print(f"  ✓ 归档: {md_path.name}")
    
    return saved


def validate_files(paths: list[str]) -> dict:
    """质量验证（5 Gates）"""
    passing = 0
    failing = 0
    failures = []
    
    for path in paths:
        try:
            content = Path(path).read_text(encoding='utf-8')
            
            # G1: 内容非空
            if len(content.strip()) < 10:
                failures.append(f"{path}: 内容过少")
                failing += 1
                continue
            
            # G2: 包含实质性内容
            cleaned = re.sub(r'[#>*_`\n\r]', ' ', content)
            if len(cleaned.strip()) < 50:
                failures.append(f"{path}: 实质内容不足")
                failing += 1
                continue
            
            # G3: 包含来源链接
            if not re.search(r'https?://', content):
                failures.append(f"{path}: 缺少来源链接")
                failing += 1
                continue
            
            # G4: 不包含敏感信息
            if re.search(r'sk-[a-zA-Z0-9]{20,}', content):
                failures.append(f"{path}: 可能包含敏感信息")
                failing += 1
                continue
            
            # G5: 有效 Markdown
            if not re.search(r'^#\s+', content, re.MULTILINE):
                failures.append(f"{path}: 缺少标题")
                failing += 1
                continue
            
            passing += 1
            
        except Exception as e:
            failures.append(f"{path}: 读取失败 - {e}")
            failing += 1
    
    return {
        'passing': passing,
        'failing': failing,
        'failures': failures,
    }


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    print(f"[1/4] 加载最近 {days} 天的日报...")
    digests = load_weekly_digests(days)
    print(f"     找到 {len(digests)} 篇日报")
    
    if not digests:
        print("     无数据，退出")
        return 0
    
    print("\n[2/4] 调 LLM 提取精华知识点...")
    points = extract_with_llm(digests)
    print(f"     提取到 {len(points)} 个知识点")
    
    if not points:
        print("     无知识点，退出")
        return 0
    
    print("\n[3/4] 归档到知识库...")
    saved = archive_knowledge_points(points)
    print(f"     已保存 {len(saved)} 个文件")
    
    print("\n[4/4] 质量验证...")
    report = validate_files(saved)
    print(f"     通过: {report['passing']}, 失败: {report['failing']}")
    
    if report['failures']:
        print("\n失败详情:")
        for f in report['failures']:
            print(f"  ⚠ {f}")
    
    print(f"\n✅ 周度精华提取完成!")
    print(f"📄 归档文件: {len(saved)} 个")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
