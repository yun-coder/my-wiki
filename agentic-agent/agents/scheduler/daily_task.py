"""每日任务 — 从知识库读取信息源，定时抓取 AI资讯 并入库。

信息源链接存放在知识库 05-tools/ 目录下，通过扫描该目录获取采集目标。
"""

import os
import sys
import logging
import time
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 确保项目根目录在 path 中
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.core.config import Config
from agents.core.memory import Memory
from agents.crawler.scraper import ScrapingAgent
from agents.knowledge.analyzer import KnowledgeAnalyzer, AnalysisResult
from agents.knowledge.archiver import KnowledgeArchiver
from agents.evaluator.evaluator import Evaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("daily_task")


# ============================================================================
# 信息源文件 — 知识库中存放采集目标的 Markdown 文件
# ============================================================================

SOURCE_FILE = "AI资讯_信息源列表.md"
SOURCE_CATEGORY = "00-overview"


def extract_links_from_md(md_path: str) -> List[Dict[str, str]]:
    """从信息源 Markdown 文件中提取采集链接。

    解析表格行中的 URL 列，返回采集目标列表。
    格式: | 1 | X (Twitter) | https://x.com/home | AI 领域最新动态 |
    """
    content = Path(md_path).read_text(encoding="utf-8")
    links = []

    # 匹配表格行: | 数字 | 站点名 | URL | 说明 |
    row_pattern = re.compile(
        r'\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(https?://\S+)\s*\|\s*(.+?)\s*\|'
    )

    for match in row_pattern.finditer(content):
        title = match.group(1).strip()
        url = match.group(2).strip()
        desc = match.group(3).strip()

        # 跳过表头
        if title == "站点":
            continue

        links.append({
            "title": title,
            "url": url,
            "description": desc,
            "source": "AI资讯",
        })

    return links


# ============================================================================
# 每日任务 Runner
# ============================================================================


class DailyTaskRunner:
    """每日定时任务：读取信息源 → 抓取 → 分析 → 验证 → 存入知识库。"""

    def __init__(self, config: Config):
        self.config = config
        self.memory = Memory()
        self.run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.run_dir = Path(config.workspace_path) / "state" / "daily" / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """执行每日任务。"""
        logger.info("=" * 60)
        logger.info("📰 每日任务启动 — AI资讯采集")
        logger.info(f"Run ID: {self.run_id}")
        logger.info("=" * 60)

        start_time = time.time()

        # Step 0: 读取信息源
        source_links = self._load_source_links()
        if not source_links:
            logger.error("未找到信息源，请先将采集链接存入知识库")
            return

        logger.info(f"  信息源: {len(source_links)} 个链接")

        # Step 1: 爬取
        pages = self._crawl_links(source_links)
        if not pages:
            logger.warning("没有成功爬取的页面，任务结束")
            return

        logger.info(f"\n⏭️ Step 2-3 已跳过（知识库归档功能已禁用）")
        logger.info(f"  如需恢复，需重建 AI知识库 分类目录（01-模型/02-工具/03-项目/04-视频）")

        elapsed = time.time() - start_time
        logger.info(f"\n✅ 信息采集完成（仅抓取，未归档），耗时 {elapsed:.1f} 秒")

    def _load_source_links(self) -> List[Dict]:
        """从知识库读取信息源链接。"""
        source_path = os.path.join(
            self.config.knowledge_base_path, SOURCE_CATEGORY, SOURCE_FILE
        )

        if not os.path.exists(source_path):
            logger.error(f"信息源文件不存在: {source_path}")
            logger.info("请将采集链接存入知识库: {category}/{source_file}".format(
                category=SOURCE_CATEGORY, source_file=SOURCE_FILE
            ))
            return []

        links = extract_links_from_md(source_path)
        logger.info(f"  从 {source_path} 解析出 {len(links)} 个信息源")
        return links

    def _crawl_links(self, source_links: List[Dict]) -> List[Dict]:
        """Step 1: 爬取信息源链接。"""
        logger.info("\n📥 Step 1: 爬取信息源链接")
        logger.info("-" * 40)

        scraper = ScrapingAgent(workspace_path=self.config.workspace_path)

        # 构造 BookmarkEntry 对象
        from agents.crawler.bookmark_parser import BookmarkEntry
        entries = [
            BookmarkEntry(title=item["title"], url=item["url"], folder=item["source"])
            for item in source_links
        ]

        results = scraper.scrape_batch(entries, delay=1.0)

        success_pages = []
        for r in results:
            if r.success and r.content:
                success_pages.append({
                    "title": r.title or r.bookmark.title,
                    "content": r.content,
                    "folder": r.bookmark.folder,
                    "url": r.url,
                })

        logger.info(f"  爬取结果: 成功 {len(success_pages)}/{len(results)}")
        self.memory.append("daily_crawl", "pass" if success_pages else "fail",
                           f"AI资讯: 成功 {len(success_pages)}/{len(results)} 个页面")

        # 保存中间结果
        path = self.run_dir / "crawl_results.json"
        path.write_text(json.dumps(success_pages, ensure_ascii=False, indent=2), encoding="utf-8")

        return success_pages

    def _analyze_pages(self, pages: List[Dict]) -> List[AnalysisResult]:
        """Step 2: LLM 分析爬取内容。"""
        logger.info("\n🧠 Step 2: LLM 分析内容")
        logger.info("-" * 40)

        analyzer = KnowledgeAnalyzer()
        results = analyzer.analyze_batch(pages)

        total_kp = sum(len(r.knowledge_points) for r in results)
        successful = sum(1 for r in results if r.success)

        logger.info(f"  分析结果: 成功 {successful}/{len(results)}, "
                    f"共提取 {total_kp} 个知识点")
        self.memory.append("daily_analyze", "pass" if total_kp > 0 else "fail",
                           f"AI资讯分析: {total_kp} 个知识点")

        # 保存分析结果
        self._save_results(results)
        return results

    def _validate_and_archive(self, results: List[AnalysisResult]):
        """Step 3: 验证质量并存档。"""
        logger.info("\n✅ Step 3: 验证质量并存档")
        logger.info("-" * 40)

        archiver = KnowledgeArchiver()
        archiver.ensure_kb_exists()

        # 存档
        saved_paths = archiver.archive_batch(results)
        if not saved_paths:
            logger.warning("  没有文件可验证")
            return

        # 验证
        evaluator = Evaluator()
        passing = 0
        failing = 0
        for path in saved_paths:
            report = evaluator.evaluate(path)
            if report.passed:
                passing += 1
            else:
                failing += 1
                logger.warning(f"  ⚠ {os.path.basename(path)}: {report.summary}")

        logger.info(f"  验证结果: 通过 {passing}/{len(saved_paths)}")
        self.memory.append("daily_evaluate", "pass" if failing == 0 else "warn",
                           f"AI资讯验证: {passing}/{len(saved_paths)} 通过")

    def _save_results(self, results: List[AnalysisResult]):
        """保存分析结果到 run_dir。"""
        data = []
        for r in results:
            data.append({
                "scraped_title": r.scraped_title,
                "success": r.success,
                "error": r.error,
                "knowledge_points": [
                    {
                        "title": kp.title,
                        "category": kp.category,
                        "summary": kp.summary,
                        "content": kp.content,
                        "tags": kp.tags,
                        "source_url": kp.source_url,
                        "source_folder": kp.source_folder,
                    }
                    for kp in r.knowledge_points
                ],
            })
        path = self.run_dir / "analysis_results.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ============================================================================
# 入口
# ============================================================================


def run_daily_task(config: Config):
    """执行每日 AI资讯 采集任务。"""
    runner = DailyTaskRunner(config)
    runner.run()


if __name__ == "__main__":
    cfg = Config.from_env()
    run_daily_task(cfg)
