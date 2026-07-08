"""知识存档器 — 将分析结果写入本地知识库。"""

import os
import logging
from pathlib import Path
from typing import List, Optional

from agents.knowledge.analyzer import KnowledgePoint, AnalysisResult

logger = logging.getLogger(__name__)


class KnowledgeArchiver:
    """知识存档器。

    将分析得到的知识点写入知识库对应的子目录。
    每个知识点保存为一个 Markdown 文件。
    """

    def __init__(self, kb_path: str = ""):
        if not kb_path:
            from agents.core.config import config
            kb_path = config.knowledge_base_path
        self.kb_path = kb_path
        logger.info(f"知识库路径: {self.kb_path}")

    def archive(self, result: AnalysisResult) -> Optional[str]:
        """存档单个分析结果。

        Returns:
            保存的文件路径，失败返回 None
        """
        if not result.success or not result.knowledge_points:
            return None

        saved_paths = []
        for kp in result.knowledge_points:
            path = self._save_knowledge_point(kp)
            if path:
                saved_paths.append(path)

        if saved_paths:
            logger.info(f"  已存档 {len(saved_paths)} 个知识点: {result.scraped_title}")
        return saved_paths[0] if saved_paths else None

    def archive_batch(self, results: List[AnalysisResult]) -> List[str]:
        """批量存档。"""
        saved = []
        for result in results:
            path = self.archive(result)
            if path:
                saved.append(path)

        logger.info(f"\n存档完成: {len(saved)}/{len(results)} 个结果已保存")
        return saved

    def _save_knowledge_point(self, kp: KnowledgePoint) -> Optional[str]:
        """保存单个知识点到知识库。"""
        target_dir = os.path.join(self.kb_path, kp.category)
        os.makedirs(target_dir, exist_ok=True)

        safe_name = "".join(
            c if c.isalnum() or c in " _-." else "_" for c in kp.title
        )
        safe_name = safe_name.replace(" ", "_")[:80]

        md_path = os.path.join(target_dir, f"{safe_name}.md")
        if os.path.exists(md_path):
            import time
            ts = time.strftime("%Y%m%d_%H%M%S")
            md_path = os.path.join(target_dir, f"{safe_name}_{ts}.md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {kp.title}\n\n")

            if kp.tags:
                tags_str = " | ".join(kp.tags)
                f.write(f"**标签**: {tags_str}\n\n")

            f.write(f"> **摘要**: {kp.summary}\n\n")
            f.write(f"> 来源: [{kp.source_url}]({kp.source_url})\n")
            f.write(f"> 原始分类: {kp.source_folder}\n\n")
            f.write("---\n\n")
            f.write(kp.content)

        logger.info(f"    存档: {md_path}")
        return md_path

    def ensure_kb_exists(self):
        """确保知识库目录存在。"""
        os.makedirs(self.kb_path, exist_ok=True)
