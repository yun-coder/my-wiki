import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts import knowledge_curator as curator


class KnowledgeCuratorTests(unittest.TestCase):
    def test_github_summary_finds_new_projects(self):
        existing = {"old/project": {"full_name": "old/project"}}
        daily = [{
            "full_name": "new/daily-project",
            "url": "https://github.com/new/daily-project",
            "stars_today": 120,
            "total_stars": 1000,
        }]
        weekly = [{
            "full_name": "new/weekly-project",
            "url": "https://github.com/new/weekly-project",
            "stars_weekly": 300,
            "total_stars": 2000,
        }]
        with patch.object(curator, "parse_project_index", return_value=existing):
            summary = curator.build_github_summary(daily, weekly)
        self.assertEqual(summary["daily_count"], 1)
        self.assertEqual(summary["weekly_count"], 1)
        self.assertEqual(
            {repo["full_name"] for repo in summary["new_projects"]},
            {"new/daily-project", "new/weekly-project"},
        )

    def test_navigation_date_and_record_are_updated_idempotently(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            navigation = Path(temp_dir) / "知识库导航.md"
            navigation.write_text(
                "# 知识库导航\n\n"
                "> 个人知识体系总览 | 更新: 2026-07-27\n\n"
                "## 维护说明\n\n"
                "- **最近自动整理**: 2026-07-27（项目索引与资讯洞察库）\n",
                encoding="utf-8",
            )
            with patch.object(curator, "NAVIGATION_PATH", navigation):
                curator.update_navigation()
                curator.update_navigation()

            result = navigation.read_text(encoding="utf-8")
            self.assertIn(f"更新: {curator.TODAY}", result)
            record = f"- **最近自动整理**: {curator.TODAY}（项目索引与资讯洞察库）"
            self.assertEqual(result.count(record), 1)

    def test_daily_summary_identifies_useful_items(self):
        summary = curator.build_daily_summary([
            {
                "source": "测试源",
                "title": "Agent 工程实践",
                "url": "https://example.com/agent",
                "summary": "介绍如何为 Agent 增加可观测性、预算控制和失败重试。",
                "category": "智能体与 AI 应用",
            },
            {
                "source": "测试源",
                "title": "导航",
                "url": "https://example.com/nav",
                "summary": "导航",
            },
        ])
        self.assertEqual(summary["candidate_count"], 2)
        self.assertEqual(summary["valid_count"], 1)
        self.assertEqual(len(summary["featured"]), 1)
        self.assertIn("可观测性", summary["featured"][0]["summary"])

    def test_repo_url_is_canonicalized(self):
        self.assertEqual(
            curator.normalize_repo_url("https://github.com/OpenAI/openai-agents-python.git"),
            "https://github.com/OpenAI/openai-agents-python",
        )

    def test_agent_project_has_type_and_features(self):
        category, features = curator.classify_project({
            "full_name": "openai/openai-agents-python",
            "name": "openai-agents-python",
            "description": "Agent framework and tools",
        })
        self.assertEqual(category, "AI 智能体与技能")
        self.assertIn("Agent", features)

    def test_video_project_is_classified_by_function(self):
        category, features = curator.classify_project({
            "full_name": "demo/video-captioner",
            "name": "video-captioner",
            "description": "AI video caption generator",
        })
        self.assertEqual(category, "AI 视频与音频")
        self.assertIn("视频生成", features)

    def test_news_is_grouped_by_topic(self):
        category, tags = curator.classify_news(
            "开源多智能体框架发布", "支持 Agent 协作与工具调用"
        )
        self.assertEqual(category, "智能体与 AI 应用")
        self.assertIn("Agent", tags)

    def test_english_only_description_gets_chinese_fallback(self):
        project = {"description": "A fast command line tool"}
        result = curator.fallback_description(
            project, "开发工具与工程效率", ["代码开发", "自动化"]
        )
        self.assertRegex(result, r"[\u4e00-\u9fff]")

    def test_github_navigation_url_is_not_a_repository(self):
        self.assertIsNone(
            curator.normalize_repo_url("https://github.com/features/copilot")
        )


if __name__ == "__main__":
    unittest.main()
