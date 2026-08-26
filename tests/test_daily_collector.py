import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

from scripts import daily_collector as collector


class EmptyLLM:
    def complete(self, *_args, **_kwargs):
        return {"content": ""}


class PartialLLM:
    def complete(self, *_args, **_kwargs):
        return {"content": '{"d":[{"i":0,"z":"浏览器自动化工具"}]}'}


class FailingLLM:
    def complete(self, *_args, **_kwargs):
        raise RuntimeError("temporary model outage")


class DailyCollectorTests(unittest.TestCase):
    def test_chinese_descriptions_are_complete_when_llm_is_empty(self):
        repos = [
            {
                "full_name": "demo/browser-agent",
                "title": "browser-agent",
                "description": "Web automation for AI agents",
                "language": "Python",
            },
            {
                "full_name": "demo/chat",
                "title": "chat",
                "description": "A mesh chat application",
                "language": "Rust",
            },
        ]
        with patch.object(collector, "LLM_CLIENT", EmptyLLM()):
            result = collector.enrich_repos_with_zh_desc(repos)
        self.assertTrue(all(collector._contains_chinese(r["zh_desc"]) for r in result))

    def test_partial_llm_result_is_filled_locally(self):
        repos = [
            {
                "full_name": f"demo/project-{i}",
                "title": f"project-{i}",
                "description": "A developer library",
                "language": "Go",
            }
            for i in range(3)
        ]
        with patch.object(collector, "LLM_CLIENT", PartialLLM()):
            result = collector.enrich_repos_with_zh_desc(repos)
        self.assertTrue(all(collector._contains_chinese(r["zh_desc"]) for r in result))

    def test_article_analysis_has_a_useful_fallback_when_llm_fails(self):
        articles = [{
            "source": "测试源",
            "title": "一个值得关注的 Agent 发布",
            "url": "https://example.com/agent",
            "snippet": "",
        }]
        with patch.object(collector, "LLM_CLIENT", FailingLLM()):
            result = collector.analyze_articles_with_llm(articles)
        self.assertIn("测试源", result[0]["summary"])
        self.assertIn("Agent", result[0]["summary"])

    def test_legacy_daily_outputs_are_disabled(self):
        with self.assertRaises(RuntimeError):
            collector.write_ai_digest(None, [])
        with self.assertRaises(RuntimeError):
            collector.write_github_digest([])

    def test_zero_keyword_project_is_not_misclassified_as_ai(self):
        repo = {"title": "bitchat", "description": "bluetooth mesh chat"}
        self.assertEqual(collector.categorize_repo(repo), "🛠️ 开发工具")

    def test_rss_uses_real_titles_instead_of_url_slugs(self):
        rss = """<?xml version="1.0"?>
        <rss><channel><item>
          <title>一个真实的 AI 新闻标题</title>
          <link>https://example.com/posts/123</link>
        </item></channel></rss>"""
        result = collector._extract_feed_articles(rss, "测试源", 5)
        self.assertEqual(result[0]["title"], "一个真实的 AI 新闻标题")
        self.assertEqual(result[0]["url"], "https://example.com/posts/123")

    def test_rss_excludes_sponsored_entries(self):
        rss = '''<rss><channel>
        <item><title>Editorial AI story</title><link>https://example.com/editorial</link><category>AI</category></item>
        <item><title>Paid AI story</title><link>https://example.com/paid</link><category>Sponsored Content</category></item>
        </channel></rss>'''
        result = collector._extract_feed_articles(rss, "Test", 5)
        self.assertEqual([item["title"] for item in result], ["Editorial AI story"])

    def test_root_env_is_a_supported_config_location(self):
        self.assertEqual(collector.ENV_PATHS[0], collector.PROJECT_ROOT / ".env")
        self.assertTrue(os.fspath(collector.ENV_PATHS[0]).endswith(".env"))

    def test_expanded_sources_are_loaded(self):
        sources = collector.load_info_sources()
        titles = {source["title"] for source in sources}
        self.assertGreaterEqual(len(sources), 20)
        self.assertTrue({"OpenAI News", "Google DeepMind", "arXiv cs.LG"} <= titles)

    def test_ai_news_source_is_loaded(self):
        sources = collector.load_info_sources()
        source = next(item for item in sources if item["title"] == "AI News")
        self.assertEqual(
            source["url"],
            "https://www.artificialintelligence-news.com/all-categories/",
        )

    def test_ai_news_parser_excludes_sponsored_cards(self):
        html = '''
        <div class="elementor e-loop-item post"><p>Artificial Intelligence</p>
          <h1><a href="https://www.artificialintelligence-news.com/news/useful-ai-story/">Useful AI story for teams</a></h1>
        </div>
        <div class="elementor e-loop-item post"><p>Sponsored Content</p>
          <h1><a href="https://www.artificialintelligence-news.com/news/paid-story/">Paid AI story for teams</a></h1>
        </div>'''
        result = collector._extract_ai_news_articles(html, "AI News", 5)
        self.assertEqual([item["title"] for item in result], ["Useful AI story for teams"])

    def test_article_deduplication_ignores_tracking_parameters(self):
        articles = [
            {"source": "A", "title": "Same AI launch", "url": "https://example.com/news/1?utm_source=a", "snippet": ""},
            {"source": "B", "title": "Same AI launch", "url": "https://example.com/news/1", "snippet": "More useful context"},
        ]
        result = collector.deduplicate_articles(articles)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["snippet"], "More useful context")


if __name__ == "__main__":
    unittest.main()
