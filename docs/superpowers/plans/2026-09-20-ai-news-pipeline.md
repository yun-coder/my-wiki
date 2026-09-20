# AI资讯统一采集实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Chrome `AI资讯` 书签接入主采集器，修复定时任务入口，并建立后续知识库渐进治理的质量边界。

**Architecture:** 在 `daily_collector.py` 内增加纯函数式书签读取、URL 规范化和四类分类；主流程把公开书签源与 Markdown 信息源合并后统一去重。旧 `digest_ai_news.py` 转为兼容调用，Windows 任务改调用仓库 wrapper。

**Tech Stack:** Python 3.11、标准库 `json/pathlib/urllib`、现有 `httpx`、`unittest`、Windows Task Scheduler XML。

**Spec:** `docs/superpowers/specs/2026-09-20-ai-news-pipeline-design.md`

## Global Constraints

- 不修改用户原工作区已有的未提交知识库文件。
- 不删除历史知识库内容；本次只增加采集质量边界和可审阅入口。
- Chrome 书签读取失败时必须可诊断，不能静默写入空结果。
- URL 去重必须移除跟踪参数但保留业务参数。

### Task 1: Chrome 书签读取与分类

**Files:**
- Modify: `tests/test_daily_collector.py`
- Modify: `scripts/daily_collector.py`

**Interfaces:**
- Produces `load_chrome_ai_bookmarks(path: Path | None = None) -> list[dict]`。
- Produces `classify_bookmark(bookmark: dict) -> str`。
- Produces `normalize_bookmark_url(url: str) -> str`。

- [ ] **Step 1: Write failing tests**

  覆盖只读取 `AI资讯` 文件夹、保留业务查询参数、移除 `utm_*`/`gclid`、重复 URL 合并，以及四类分类。

- [ ] **Step 2: Run the focused tests and verify failure**

  Run: `python -m unittest tests.test_daily_collector.DailyCollectorTests.test_chrome_ai_bookmarks_are_loaded_and_classified -v`
  Expected: FAIL because the new loader is not defined.

- [ ] **Step 3: Implement the minimal loader and classifier**

  从 `%LOCALAPPDATA%/Google/Chrome/User Data/Default/Bookmarks` 读取 JSON，递归定位 `AI资讯`，输出 `title/url/folder/category/observe_only`。

- [ ] **Step 4: Run focused and full tests**

  Run: `python -m unittest tests.test_daily_collector.DailyCollectorTests.test_chrome_ai_bookmarks_are_loaded_and_classified -v` and `python -m unittest discover -s tests -v`。

- [ ] **Step 5: Commit**

  `git add tests/test_daily_collector.py scripts/daily_collector.py && git commit -m "feat: load and classify Chrome AI bookmarks"`

### Task 2: 接入主采集流程与质量边界

**Files:**
- Modify: `tests/test_daily_collector.py`
- Modify: `scripts/daily_collector.py`
- Modify: `scripts/knowledge_curator.py`
- Modify: `AI知识库/13-AI资讯信息源.md`

**Interfaces:**
- Produces `load_all_info_sources() -> list[dict]`，合并 Markdown 配置和 Chrome 书签。
- `fetch_source_articles` 对 `observe_only` 源返回空列表，不制造登录页伪资讯。

- [ ] **Step 1: Write failing tests**

  覆盖公开源参与采集、观察源不写入文章、合并后按规范化 URL 去重，以及“待补充正文分析”不进入当日精选。

- [ ] **Step 2: Run focused tests and verify failure**

  Run: `python -m unittest tests.test_daily_collector.DailyCollectorTests.test_bookmark_sources_are_merged_into_daily_collection -v`
  Expected: FAIL because the merged source function and quality predicate do not exist.

- [ ] **Step 3: Implement integration**

  主流程在非 `--quick` 模式加载 20 条书签，打印四类计数；观察源保留在来源统计但跳过正文抓取；在 curator 的当日摘要过滤导航和空泛降级摘要。

- [ ] **Step 4: Run full tests**

  Run: `python -m unittest discover -s tests -v`。

- [ ] **Step 5: Commit**

  `git add tests/test_daily_collector.py scripts/daily_collector.py scripts/knowledge_curator.py AI知识库/13-AI资讯信息源.md && git commit -m "feat: merge Chrome bookmarks into daily collector"`

### Task 3: 收敛旧入口并修复定时任务

**Files:**
- Modify: `scripts/digest_ai_news.py`
- Modify: `MyWikiDailyTask.xml`
- Modify: `run_daily_collector.bat`
- Modify: `tests/test_daily_collector.py`

- [ ] **Step 1: Write failing regression tests**

  验证兼容脚本指向主入口，任务 XML 不再出现 `D:\\local-projects\\my-wiki`，并使用当前仓库 wrapper。

- [ ] **Step 2: Run focused tests and verify failure**

  Run: `python -m unittest tests.test_daily_collector.DailyCollectorTests.test_scheduler_points_to_current_project -v`
  Expected: FAIL because XML still contains the old path.

- [ ] **Step 3: Implement the minimal configuration changes**

  用 `cmd.exe /d /c` 调用当前目录的 `run_daily_collector.bat`；兼容脚本仅转调 `daily_collector.main`。

- [ ] **Step 4: Run full tests and a quick collection smoke test**

  Run: `python -m unittest discover -s tests -v` and `python scripts/daily_collector.py --quick`。

- [ ] **Step 5: Commit**

  `git add scripts/digest_ai_news.py MyWikiDailyTask.xml run_daily_collector.bat tests/test_daily_collector.py && git commit -m "fix: restore daily collector task entrypoint"`

### Task 4: 验证与交付说明

**Files:**
- Review: `git diff --check`
- Review: `git status --short`

- [ ] **Step 1:** Run the full test suite and record the exact pass count.
- [ ] **Step 2:** Run `python scripts/daily_collector.py --quick` and record bookmark/source diagnostics.
- [ ] **Step 3:** Confirm no user-owned files in the original worktree were touched.
- [ ] **Step 4:** Report the first knowledge-base cleanup batch as a follow-up list; do not bulk-delete historical entries.
