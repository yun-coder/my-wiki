"""知识分析器 — 使用 Agnes AI 分析爬取内容，提取知识点并归档。"""

import os
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from agents.core.agnes_client import AgnesClient
from agents.core.config import config as app_config

logger = logging.getLogger(__name__)


@dataclass
class KnowledgePoint:
    """单个知识点。"""
    title: str
    category: str  # 分类目录名
    summary: str
    content: str  # 结构化内容
    tags: List[str] = field(default_factory=list)
    source_url: str = ""
    source_folder: str = ""


@dataclass
class AnalysisResult:
    """单次分析结果。"""
    scraped_title: str
    knowledge_points: List[KnowledgePoint] = field(default_factory=list)
    error: str = ""
    success: bool = False


class KnowledgeAnalyzer:
    """知识分析器 — 调用 LLM 分析爬取内容，提取知识点。"""

    # 知识库目录映射：书签文件夹 -> 知识库子目录
    CATEGORY_MAP = {
        "AI资讯": "02-工具",
        "AI大模型平台": "01-模型",
        "AI工具": "02-工具",
        "AI项目收藏": "03-项目",
        "AI学习": "02-工具",
        "AI-prompts": "02-工具",
        "视频生成": "04-视频",
    }

    SYSTEM_PROMPT = """你是一个 AI 知识整理专家。你的任务是将网页内容整理成结构化的知识条目。

请严格按照以下 JSON 格式输出，不要输出任何其他内容：
{
  "knowledge_points": [
    {
      "title": "知识点标题",
      "category": "分类目录名（从以下选择: 01-模型, 02-工具, 03-项目, 04-视频）",
      "summary": "一句话总结（50字以内）",
      "content": "结构化内容（Markdown格式，包含关键信息、工具名、API地址等）",
      "tags": ["标签1", "标签2"],
      "source_url": "来源URL",
      "source_folder": "原始文件夹名"
    }
  ]
}

要求：
1. 从网页内容中提取有价值的 AI 知识
2. 每个页面至少提取 1-3 个知识点
3. content 部分要结构化，包含：工具/项目简介、核心功能、使用方式、相关链接
4. tags 要准确描述知识点主题
5. 如果页面内容很少或无法提取有效知识，返回空数组
6. 只输出 JSON，不要有其他文字"""

    def __init__(self, client: Optional[AgnesClient] = None):
        self.client = client or AgnesClient(
            api_key=app_config.agnes_api_key,
            base_url=app_config.agnes_base_url,
            model=app_config.agnes_model,
        )

    def analyze_page(self, title: str, content: str, folder: str, url: str) -> AnalysisResult:
        """分析单个页面内容，提取知识点。

        Args:
            title: 页面标题
            content: 页面正文内容
            folder: 书签所属文件夹
            url: 来源 URL

        Returns:
            AnalysisResult
        """
        if not content or len(content.strip()) < 50:
            logger.info(f"  内容过少，跳过分析: {title}")
            return AnalysisResult(scraped_title=title, success=False, error="内容过少")

        # 截断内容以适应 token 限制
        max_content_len = 20000
        if len(content) > max_content_len:
            content = content[:max_content_len] + "\n\n...(内容过长已截断)"

        prompt = f"""请分析以下网页内容，提取 AI 知识点。

页面标题: {title}
所属分类: {folder}
来源URL: {url}

网页内容:
{content}

请按照系统指令的 JSON 格式输出。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.complete(messages, max_tokens=4096, temperature=0.3)
            text = response.get("content", "")

            # 解析 JSON
            knowledge_points = self._parse_response(text, folder, url)

            return AnalysisResult(
                scraped_title=title,
                knowledge_points=knowledge_points,
                success=len(knowledge_points) > 0,
            )

        except Exception as e:
            logger.error(f"  分析失败: {title} — {e}")
            return AnalysisResult(
                scraped_title=title,
                knowledge_points=[],
                success=False,
                error=str(e),
            )

    def analyze_page_with_feedback(
        self,
        title: str,
        content: str,
        folder: str,
        url: str,
        feedback: str,
    ) -> AnalysisResult:
        """带反馈的页面分析 — Loop Engineering 的修正环节。

        将验证阶段的失败反馈注入到 LLM 分析 prompt 中，
        让分析器在下次提取时规避已知问题。

        Args:
            feedback: 来自 Evaluator 的修正建议文本

        Returns:
            AnalysisResult
        """
        if not content or len(content.strip()) < 50:
            logger.info(f"  内容过少，跳过分析: {title}")
            return AnalysisResult(scraped_title=title, success=False, error="内容过少")

        max_content_len = 20000
        if len(content) > max_content_len:
            content = content[:max_content_len] + "\n\n...(内容过长已截断)"

        prompt = f"""请分析以下网页内容，提取 AI 知识点。

⚠️ 修正反馈（来自上一轮验证）:
{feedback}

请特别注意以上反馈，避免同样的质量问题。

页面标题: {title}
所属分类: {folder}
来源URL: {url}

网页内容:
{content}

请按照系统指令的 JSON 格式输出。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.complete(messages, max_tokens=4096, temperature=0.3)
            text = response.get("content", "")

            knowledge_points = self._parse_response(text, folder, url)

            return AnalysisResult(
                scraped_title=title,
                knowledge_points=knowledge_points,
                success=len(knowledge_points) > 0,
            )

        except Exception as e:
            logger.error(f"  分析失败: {title} — {e}")
            return AnalysisResult(
                scraped_title=title,
                knowledge_points=[],
                success=False,
                error=str(e),
            )

    def _parse_response(self, text: str, folder: str, url: str) -> List[KnowledgePoint]:
        """从 LLM 响应中解析 JSON。"""
        # 尝试提取 JSON 块
        import re
        json_match = re.search(r'\{[\s\S]*"knowledge_points"[\s\S]*\}', text)
        if not json_match:
            # 尝试找到第一个 { 到最后一个 }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start:end + 1]
            else:
                logger.warning(f"  无法解析 JSON 响应: {text[:200]}")
                return []
        else:
            json_str = json_match.group()

        try:
            data = json.loads(json_str)
            points = []
            for item in data.get("knowledge_points", []):
                points.append(KnowledgePoint(
                    title=item.get("title", "未命名"),
                    category=item.get("category", self._resolve_category(folder)),
                    summary=item.get("summary", ""),
                    content=item.get("content", ""),
                    tags=item.get("tags", []),
                    source_url=item.get("source_url", url),
                    source_folder=item.get("source_folder", folder),
                ))
            return points
        except json.JSONDecodeError as e:
            logger.warning(f"  JSON 解析失败: {e}")
            logger.debug(f"  原始响应: {text[:500]}")
            return []

    def _resolve_category(self, folder: str) -> str:
        """将书签文件夹映射到知识库子目录。"""
        return self.CATEGORY_MAP.get(folder, "05-tools")

    def analyze_kb_batch(self, pages: List[Dict[str, str]]) -> List[AnalysisResult]:
        """批量分析知识库文件，提取知识图谱和关联关系。

        针对已有 .md 文件的内容，做深度分析：
        - 提取核心概念和关键实体
        - 识别文件间的关联关系
        - 生成结构化摘要
        """
        results = []
        total = len(pages)
        logger.info(f"开始批量分析知识库文件: {total} 个")

        for i, page in enumerate(pages, 1):
            logger.info(f"[{i}/{total}] 分析: {page['title']}")
            result = self._analyze_kb_file(
                title=page["title"],
                content=page["content"],
                category=page["category"],
                path=page.get("path", ""),
            )
            results.append(result)
            if result.success:
                logger.info(f"  ✓ 提取 {len(result.knowledge_points)} 个知识点: {result.scraped_title}")
            else:
                logger.info(f"  ✗ 分析失败: {result.scraped_title} — {result.error}")

        total_kp = sum(len(r.knowledge_points) for r in results)
        logger.info(f"\n分析完成: {sum(1 for r in results if r.success)} 成功, "
                     f"共提取 {total_kp} 个知识点")

        return results

    def analyze_kb_batch_with_feedback(
        self, pages: List[Dict[str, str]], feedback: str
    ) -> List[AnalysisResult]:
        """带反馈的知识库文件批量分析。"""
        results = []
        total = len(pages)
        logger.info(f"开始带反馈批量分析: {total} 个文件")

        for i, page in enumerate(pages, 1):
            logger.info(f"[{i}/{total}] 重新分析（带反馈）: {page['title']}")
            result = self._analyze_kb_file_with_feedback(
                title=page["title"],
                content=page["content"],
                category=page["category"],
                path=page.get("path", ""),
                feedback=feedback,
            )
            results.append(result)

        return results

    def _analyze_kb_file(
        self, title: str, content: str, category: str, path: str
    ) -> AnalysisResult:
        """分析单个知识库文件，提取深层知识。"""
        if not content or len(content.strip()) < 20:
            return AnalysisResult(scraped_title=title, success=False, error="内容过少")

        # 截断内容以适应 token 限制
        max_content_len = 20000
        if len(content) > max_content_len:
            content = content[:max_content_len] + "\n\n...(内容过长已截断)"

        system_prompt = """你是一个 AI 知识图谱分析师。你的任务是对已有的知识文件做深度分析，提取结构化信息。

请严格按照以下 JSON 格式输出，不要输出任何其他内容：
{
  "knowledge_points": [
    {
      "title": "分析主题",
      "category": "分类目录名",
      "summary": "一句话总结（50字以内）",
      "content": "结构化内容（包含：核心概念、关键实体、工具/框架名称、关联关系、适用场景）",
      "tags": ["标签1", "标签2"],
      "source_url": "",
      "source_folder": "分类目录名"
    }
  ]
}

要求：
1. 从文件中提取核心概念和关键实体（工具名、框架名、API、方法论等）
2. 识别文件间的潜在关联关系
3. content 部分要结构化，包含：核心概念、关键实体、适用场景、注意事项
4. tags 要准确描述知识主题
5. 如果文件内容很少或无法提取有效知识，返回空数组
6. 只输出 JSON，不要有其他文字"""

        prompt = f"""请对以下知识库文件做深度分析。

文件标题: {title}
分类目录: {category}
文件路径: {path}

文件内容:
{content}

请按照系统指令的 JSON 格式输出。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.complete(messages, max_tokens=4096, temperature=0.3)
            text = response.get("content", "")

            knowledge_points = self._parse_response(text, category, path)

            return AnalysisResult(
                scraped_title=title,
                knowledge_points=knowledge_points,
                success=len(knowledge_points) > 0,
            )

        except Exception as e:
            logger.error(f"  分析失败: {title} — {e}")
            return AnalysisResult(
                scraped_title=title,
                knowledge_points=[],
                success=False,
                error=str(e),
            )

    def _analyze_kb_file_with_feedback(
        self, title: str, content: str, category: str, path: str, feedback: str
    ) -> AnalysisResult:
        """带反馈的知识库文件分析。"""
        if not content or len(content.strip()) < 20:
            return AnalysisResult(scraped_title=title, success=False, error="内容过少")

        max_content_len = 20000
        if len(content) > max_content_len:
            content = content[:max_content_len] + "\n\n...(内容过长已截断)"

        system_prompt = """你是一个 AI 知识图谱分析师。你对已有知识文件做深度分析。

请严格按照以下 JSON 格式输出，不要输出任何其他内容：
{
  "knowledge_points": [
    {
      "title": "分析主题",
      "category": "分类目录名",
      "summary": "一句话总结（50字以内）",
      "content": "结构化内容（包含：核心概念、关键实体、工具/框架名称、关联关系、适用场景）",
      "tags": ["标签1", "标签2"],
      "source_url": "",
      "source_folder": "分类目录名"
    }
  ]
}

要求：
1. 从文件中提取核心概念和关键实体
2. 识别文件间的潜在关联关系
3. content 部分要结构化
4. tags 要准确描述知识主题
5. 只输出 JSON"""

        prompt = f"""请对以下知识库文件做深度分析。

⚠️ 修正反馈（来自验证阶段）:
{feedback}

请特别注意以上反馈，避免同样的质量问题。

文件标题: {title}
分类目录: {category}
文件路径: {path}

文件内容:
{content}

请按照系统指令的 JSON 格式输出。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.complete(messages, max_tokens=4096, temperature=0.3)
            text = response.get("content", "")

            knowledge_points = self._parse_response(text, category, path)

            return AnalysisResult(
                scraped_title=title,
                knowledge_points=knowledge_points,
                success=len(knowledge_points) > 0,
            )

        except Exception as e:
            logger.error(f"  分析失败: {title} — {e}")
            return AnalysisResult(
                scraped_title=title,
                knowledge_points=[],
                success=False,
                error=str(e),
            )

    def analyze_batch(self, pages: List[Dict[str, str]]) -> List[AnalysisResult]:
        """批量分析多个页面。

        Args:
            pages: [{"title": ..., "content": ..., "folder": ..., "url": ...}]

        Returns:
            AnalysisResult 列表
        """
        results = []
        total = len(pages)
        logger.info(f"开始批量分析: {total} 个页面")

        for i, page in enumerate(pages, 1):
            logger.info(f"[{i}/{total}] ")
            result = self.analyze_page(
                title=page["title"],
                content=page["content"],
                folder=page["folder"],
                url=page["url"],
            )
            results.append(result)
            if result.success:
                logger.info(f"  ✓ 提取 {len(result.knowledge_points)} 个知识点: {result.scraped_title}")
            else:
                logger.info(f"  ✗ 分析失败: {result.scraped_title} — {result.error}")

        total_kp = sum(len(r.knowledge_points) for r in results)
        logger.info(f"\n分析完成: {sum(1 for r in results if r.success)} 成功, "
                     f"共提取 {total_kp} 个知识点")

        return results
