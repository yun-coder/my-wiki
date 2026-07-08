"""Loop 编排器 — 基于 Loop Engineering 的迭代式 Agent 工作流。

基于 Loop Engineering 四大支柱（Prompt / Context / Loop / Harness）：
Loop 是核心执行引擎，负责将"问一个问题"升级为"完成任务"。

循环模型：
  Task Input → Agent Execution → Tool-based Verification → Feedback → Correction
  （任务输入 → 执行 → 工具验证 → 反馈 → 修正）

工作模式：
  1. 知识库分析 — 扫描已有 .md 文件，做 LLM 深度分析 + 质量验证
  2. 每日采集   — 从 AI资讯 固定链接定时抓取新内容（见 daily_task.py）

关键设计原则：
1. 明确的边界 — 每轮循环有确定的输入输出契约
2. 可靠的验证 — 使用确定性工具验证，而非让 LLM 自评
3. 终止条件 — 达到最大迭代次数或全部通过后停止，防止错误放大
4. 人在回路 — 关键节点可暂停等待人工确认
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 确保项目根目录在 path 中
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.core.config import Config
from agents.core.memory import Memory
from agents.knowledge.analyzer import KnowledgeAnalyzer, AnalysisResult
from agents.evaluator.evaluator import Evaluator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("loop")


# ============================================================================
# 数据类型
# ============================================================================


class CycleStatus:
    """单轮循环状态。"""
    PENDING = "pending"
    RUNNING = "running"
    PASSING = "passing"
    FAILING = "failing"
    CORRECTING = "correcting"
    SKIPPED = "skipped"
    MANUAL_REVIEW = "manual_review"


class LoopResult:
    """单次 Loop 迭代的完整结果。"""

    def __init__(self, task_id: str, phase: str):
        self.task_id = task_id
        self.phase = phase
        self.status = CycleStatus.PENDING
        self.input_data: Dict = {}
        self.output_data: Dict = {}
        self.feedback: Optional[str] = None
        self.error: Optional[str] = None
        self.duration_seconds: float = 0.0
        self.attempt: int = 1
        self.timestamp = datetime.utcnow().isoformat() + "Z"


# ============================================================================
# Harness — 基础设施管理
# ============================================================================


class Harness:
    """Harness Engineering: 提供 Agent 运行所需的基础设施。

    管理工具、目录结构和人在回路机制。
    """

    def __init__(self, config: Config):
        self.config = config
        self.state_dir = Path(config.workspace_path) / "state"
        self.loop_dir = self.state_dir / "loops"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保必要的目录结构存在。"""
        for d in [self.state_dir, self.loop_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def get_loop_run_dir(self, run_id: str) -> Path:
        """获取单次 Loop 运行的隔离目录。"""
        run_dir = self.loop_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def check_analyzer_available(self) -> bool:
        """检查 LLM 分析器是否可用。"""
        from agents.core.config import config
        return bool(
            config.agnes_api_key
            and config.agnes_api_key != "your_api_key_here"
        )

    def human_in_the_loop(
        self,
        question: str,
        context: str,
        auto_approve: bool = False,
    ) -> bool:
        """人在回路: 关键决策点暂停等待人工确认。"""
        if auto_approve:
            logger.info(f"[HITL] 自动批准: {question}")
            return True

        print(f"\n{'=' * 60}")
        print(f"需要人工确认")
        print(f"{'=' * 60}")
        print(f"\n问题: {question}")
        print(f"\n上下文:\n{context[:500]}")
        print(f"\n{'=' * 60}")
        print("请输入 'y' 继续, 'n' 跳过此项, 'q' 退出: ", end="")

        try:
            response = input().strip().lower()
            if response == "q":
                logger.info("[HITL] 用户选择退出")
                sys.exit(0)
            return response == "y"
        except (EOFError, KeyboardInterrupt):
            logger.info("[HITL] 默认跳过")
            return False


# ============================================================================
# 知识库扫描器
# ============================================================================


class KnowledgeBaseScanner:
    """扫描知识库目录，收集所有 .md 文件。"""

    KNOWN_CATEGORIES = [
        "00-overview", "01-模型", "02-工具",
        "03-项目", "04-视频",
    ]

    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)

    def scan(self) -> List[Dict[str, str]]:
        """扫描知识库，返回所有 .md 文件的信息。"""
        if not self.kb_path.exists():
            logger.error(f"知识库路径不存在: {self.kb_path}")
            return []

        files = []
        for category in self.KNOWN_CATEGORIES:
            cat_dir = self.kb_path / category
            if not cat_dir.exists():
                continue
            for md_file in sorted(cat_dir.glob("*.md")):
                files.append({
                    "path": str(md_file),
                    "title": md_file.stem,
                    "category": category,
                    "size": md_file.stat().st_size,
                })

        return files


# ============================================================================
# Loop Runner — 核心编排引擎
# ============================================================================


class LoopRunner:
    """Loop Engineering 编排引擎。

    基于本地知识库的迭代式分析流程：
    1. Scan    — 扫描知识库中的 .md 文件
    2. Analyze — LLM 对文件做深度分析（知识图谱、关联、摘要）
    3. Evaluate — 确定性规则验证文件质量
    4. Correct  — 验证失败时带反馈重试分析
    """

    def __init__(self, config: Config, harness: Harness):
        self.config = config
        self.harness = harness
        self.memory = Memory()
        self.run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.run_dir = harness.get_loop_run_dir(self.run_id)
        self.cycles: List[LoopResult] = []
        self.max_iterations = 3

    def run(self):
        """执行完整的 Loop 流程。"""
        logger.info("=" * 60)
        logger.info("Agentic AI Loop 启动 (知识库分析模式)")
        logger.info(f"Run ID: {self.run_id}")
        logger.info(f"知识库: {self.config.knowledge_base_path}")
        logger.info("=" * 60)

        start_time = time.time()

        # Phase 1: 扫描知识库
        kb_files = self._scan_knowledge_base()
        if not kb_files:
            logger.info("知识库中没有可处理的文件，Loop 结束")
            return

        # Phase 2: LLM 深度分析
        analysis_results = self._analyze_files(kb_files)

        # Phase 3: 验证 + 修正（迭代式）
        self._evaluate_and_correct(analysis_results)

        # 汇总
        elapsed = time.time() - start_time
        self._print_summary(elapsed)

    # ------------------------------------------------------------------
    # Phase 1: 扫描
    # ------------------------------------------------------------------

    def _scan_knowledge_base(self) -> List[Dict]:
        """Phase 1: 扫描知识库中的 .md 文件。"""
        logger.info("\n" + "=" * 60)
        logger.info("Phase 1: 扫描知识库")
        logger.info("=" * 60)

        cycle = LoopResult(task_id="scan", phase="scan")
        cycle.status = CycleStatus.RUNNING

        scanner = KnowledgeBaseScanner(self.config.knowledge_base_path)
        kb_files = scanner.scan()

        cycle.status = CycleStatus.PASSING if kb_files else CycleStatus.FAILING
        cycle.input_data = {"kb_path": str(self.config.knowledge_base_path)}
        cycle.output_data = {"total_files": len(kb_files)}

        # 按分类统计
        cat_counts = {}
        for f in kb_files:
            cat_counts[f["category"]] = cat_counts.get(f["category"], 0) + 1
        cycle.output_data["by_category"] = cat_counts

        logger.info(f"  发现 {len(kb_files)} 个 .md 文件")
        for cat, count in sorted(cat_counts.items()):
            logger.info(f"    {cat}: {count}")

        self.memory.append("scan", "pass" if kb_files else "fail",
                           f"扫描知识库: {len(kb_files)} 个文件")
        self._record_cycle(cycle)

        # 保存文件列表供后续 phase 使用
        self._save_kb_files(kb_files)

        return kb_files

    # ------------------------------------------------------------------
    # Phase 2: 分析
    # ------------------------------------------------------------------

    def _analyze_files(self, kb_files: List[Dict]) -> List[AnalysisResult]:
        """Phase 2: 对知识库文件做 LLM 深度分析。"""
        logger.info("\n" + "=" * 60)
        logger.info("Phase 2: LLM 深度分析")
        logger.info("=" * 60)

        cycle = LoopResult(task_id="analyze", phase="analyze")
        cycle.status = CycleStatus.RUNNING

        # 按分类分组，同批处理
        by_category: Dict[str, List[Dict]] = {}
        for f in kb_files:
            cat = f["category"]
            by_category.setdefault(cat, []).append(f)

        all_results = []
        analyzer = KnowledgeAnalyzer()

        for cat, files in sorted(by_category.items()):
            logger.info(f"\n  分析分类 [{cat}]: {len(files)} 个文件")

            # 读取文件内容
            pages = []
            for f in files:
                try:
                    content = self._read_file(Path(f["path"]))
                    pages.append({
                        "title": f["title"],
                        "content": content,
                        "category": cat,
                        "path": f["path"],
                    })
                except Exception as e:
                    logger.warning(f"  读取失败: {f['path']} — {e}")

            if not pages:
                continue

            # 批量分析
            results = analyzer.analyze_kb_batch(pages)
            all_results.extend(results)

            success = sum(1 for r in results if r.success)
            total_kp = sum(len(r.knowledge_points) for r in results)
            logger.info(f"  完成: {success}/{len(results)} 成功, "
                        f"提取 {total_kp} 个知识点")

        cycle.status = CycleStatus.PASSING if all_results else CycleStatus.SKIPPED
        cycle.output_data = {
            "total_files": len(kb_files),
            "analyzed": len(all_results),
            "total_knowledge_points": sum(len(r.knowledge_points) for r in all_results),
        }
        self.memory.append("analyze", "pass" if all_results else "fail",
                           f"分析 {len(all_results)} 个文件, "
                           f"提取 {sum(len(r.knowledge_points) for r in all_results)} 个知识点")
        self._record_cycle(cycle)

        self._save_analysis_results(all_results)
        return all_results

    # ------------------------------------------------------------------
    # Phase 3: 验证 + 修正
    # ------------------------------------------------------------------

    def _evaluate_and_correct(self, analysis_results: List[AnalysisResult]):
        """Phase 3: 验证 + 修正 — 迭代式质量门控。"""
        logger.info("\n" + "=" * 60)
        logger.info("Phase 3: 验证与修正 (Evaluate & Correct)")
        logger.info("=" * 60)

        if not analysis_results:
            logger.info("  没有分析结果可验证")
            return

        evaluator = Evaluator()
        iteration = 0
        all_pass = True

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"\n  【第 {iteration}/{self.max_iterations} 轮验证】")

            passing = 0
            failing = 0
            feedback_texts = []

            for result in analysis_results:
                if not result.success:
                    continue

                for kp in result.knowledge_points:
                    # 临时存档到 run_dir 做验证
                    temp_path = self.run_dir / f"temp_{kp.title[:30]}.md"
                    self._write_temp_file(temp_path, kp)

                    report = evaluator.evaluate(str(temp_path))
                    if report.passed:
                        passing += 1
                    else:
                        failing += 1
                        all_pass = False
                        if report.feedback_text:
                            feedback_texts.append(report.feedback_text)

                    # 清理临时文件
                    try:
                        temp_path.unlink(missing_ok=True)
                    except OSError:
                        pass

            logger.info(f"  结果: 通过 {passing}, 未通过 {failing}")

            if failing == 0:
                logger.info(f"  ✓ 全部验证通过！")
                break

            # 如果有反馈，注入 analyzer 重试
            if feedback_texts and iteration < self.max_iterations:
                logger.info(f"  生成 {len(feedback_texts)} 条修正反馈")
                combined_feedback = "\n".join(feedback_texts[:5])  # 限制反馈长度
                self._retry_with_feedback(analysis_results, combined_feedback)

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def _write_temp_file(self, path: Path, kp):
        """将知识点写入临时文件用于验证。"""
        path.write_text(
            f"# {kp.title}\n\n"
            f"**标签**: {' | '.join(kp.tags)}\n\n"
            f"> **摘要**: {kp.summary}\n\n"
            f"> 来源: [{kp.source_url}]({kp.source_url})\n"
            f"> 分类: {kp.category}\n\n"
            f"---\n\n"
            f"{kp.content}",
            encoding="utf-8",
        )

    def _read_file(self, path: Path) -> str:
        """读取文件，优先 UTF-8，回退 GBK（兼容 Windows 记事本保存的文件）。"""
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="gbk")

    def _retry_with_feedback(self, results: List[AnalysisResult], feedback: str):
        """带反馈重试分析。"""
        logger.info("  重新分析（带反馈）...")
        kb_files = self._load_kb_files()
        if not kb_files:
            return

        analyzer = KnowledgeAnalyzer()
        pages = []
        for f in kb_files:
            try:
                content = self._read_file(Path(f["path"]))
                pages.append({
                    "title": f["title"],
                    "content": content,
                    "category": f["category"],
                    "path": f["path"],
                })
            except Exception:
                pass

        if not pages:
            return

        new_results = analyzer.analyze_kb_batch_with_feedback(pages, feedback)
        for nr in new_results:
            if nr.success:
                for i, existing in enumerate(results):
                    if existing.scraped_title == nr.scraped_title:
                        results[i] = nr
                        break

    def _record_cycle(self, cycle: LoopResult):
        """记录一轮循环到 run_dir。"""
        cycle_file = self.run_dir / f"{cycle.task_id}.json"
        data = {
            "task_id": cycle.task_id,
            "phase": cycle.phase,
            "status": cycle.status,
            "attempt": cycle.attempt,
            "input_data": cycle.input_data,
            "output_data": cycle.output_data,
            "feedback": cycle.feedback,
            "error": cycle.error,
            "timestamp": cycle.timestamp,
        }
        cycle_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.cycles.append(cycle)

    def _save_kb_files(self, files: List[Dict]):
        """保存扫描到的文件列表。"""
        path = self.run_dir / "kb_files.json"
        path.write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_kb_files(self) -> List[Dict]:
        """加载文件列表。"""
        path = self.run_dir / "kb_files.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                try:
                    return json.loads(path.read_text(encoding="gbk"))
                except Exception:
                    return []
        return []

    def _save_analysis_results(self, results: List[AnalysisResult]):
        """保存分析结果。"""
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

    def _print_summary(self, elapsed: float):
        """打印 Loop 执行摘要。"""
        logger.info("\n" + "=" * 60)
        logger.info("Loop 执行摘要")
        logger.info("=" * 60)

        stats = {"passing": 0, "failing": 0, "skipped": 0}
        for c in self.cycles:
            if c.status in stats:
                stats[c.status] += 1

        logger.info(f"  总循环数: {len(self.cycles)}")
        for status, count in stats.items():
            if count > 0:
                logger.info(f"    {status}: {count}")
        logger.info(f"  总耗时: {elapsed:.1f} 秒")
        logger.info(f"  运行目录: {self.run_dir}")
        logger.info(f"  记忆日志: {self.memory.memory_path}")


# ============================================================================
# 入口
# ============================================================================


def run_loop(config: Config):
    """执行完整的迭代式 Loop 流程。"""
    harness = Harness(config)
    runner = LoopRunner(config, harness)
    runner.run()


if __name__ == "__main__":
    cfg = Config.from_env()
    run_loop(cfg)
