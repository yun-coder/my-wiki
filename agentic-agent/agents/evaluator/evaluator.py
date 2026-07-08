"""评判器 — 确定性规则验证 + 反馈驱动的质量门控。

借鉴 loop-engineering 的 Gate 理念：
写代码/产出的 LLM 绝不能自己评判自己，评判必须是确定性的。

新增能力：
- 确定性 Gate 检查（5 条硬规则）
- 反馈生成：验证失败时输出可操作的修正建议
- 失败模式分类：帮助定位系统性问题
"""

import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举类型
# ============================================================================


class FailureCategory(Enum):
    """失败模式分类 — 帮助定位系统性问题。"""
    EMPTY_CONTENT = "empty_content"
    MISSING_SOURCE = "missing_source"
    SECRET_LEAK = "secret_leak"
    POOR_FORMAT = "poor_format"
    LOW_QUALITY = "low_quality"
    UNKNOWN = "unknown"


@dataclass
class GateResult:
    """单个 gate 的评判结果。"""
    name: str
    passed: bool
    reason: str
    suggestion: str = ""  # 修正建议（验证失败时）


@dataclass
class FailurePattern:
    """失败模式统计。"""
    category: FailureCategory
    count: int
    affected_files: List[str] = field(default_factory=list)


@dataclass
class EvaluationReport:
    """整体评判报告。"""
    gates: List[GateResult]
    passed: bool
    summary: str
    failure_patterns: List[FailurePattern] = field(default_factory=list)
    feedback_text: str = ""  # 综合修正建议


# ============================================================================
# 评判器
# ============================================================================


class Evaluator:
    """确定性评判器 + 反馈生成器。

    对存档的知识文件运行硬规则检查，并在失败时生成可操作的修正建议。
    """

    def __init__(self):
        self.gates = [
            self._gate_non_empty,
            self._gate_has_content,
            self._gate_has_source,
            self._gate_no_secrets,
            self._gate_valid_markdown,
        ]

    def evaluate(self, file_path: str) -> EvaluationReport:
        """对单个文件运行所有 gate 检查 + 反馈生成。"""
        results = []
        content = ""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return EvaluationReport(
                gates=[],
                passed=False,
                summary=f"读取文件失败: {e}",
                feedback_text=f"无法读取文件: {e}",
            )

        failed_categories = []

        for gate in self.gates:
            result = gate(file_path, content)
            results.append(result)
            if not result.passed:
                logger.warning(f"  ✗ Gate 失败: {result.name} — {result.reason}")
                # 分类失败模式
                cat = self._classify_failure(result.name)
                if cat:
                    failed_categories.append((cat, os.path.basename(file_path)))
            else:
                logger.debug(f"  ✓ Gate 通过: {result.name}")

        all_passed = all(r.passed for r in results)
        passed_count = sum(1 for r in results if r.passed)
        total = len(results)

        # 生成反馈
        feedback = self._generate_feedback(results, content, file_path)

        report = EvaluationReport(
            gates=results,
            passed=all_passed,
            summary=f"{passed_count}/{total} gates passed",
            feedback_text=feedback,
        )

        # 统计失败模式
        if failed_categories:
            patterns = self._aggregate_patterns(failed_categories)
            report.failure_patterns = patterns

        if all_passed:
            logger.info(f"  ✓ 评判通过: {os.path.basename(file_path)}")
        else:
            logger.warning(f"  ✗ 评判未通过: {os.path.basename(file_path)}")

        return report

    def _classify_failure(self, gate_name: str) -> Optional[FailureCategory]:
        """将 gate 名称映射到失败模式分类。"""
        mapping = {
            "G1_non_empty": FailureCategory.EMPTY_CONTENT,
            "G2_has_content": FailureCategory.LOW_QUALITY,
            "G3_has_source": FailureCategory.MISSING_SOURCE,
            "G4_no_secrets": FailureCategory.SECRET_LEAK,
            "G5_valid_markdown": FailureCategory.POOR_FORMAT,
        }
        return mapping.get(gate_name)

    def _aggregate_patterns(
        self, failed_categories: List[tuple]
    ) -> List[FailurePattern]:
        """聚合失败模式统计。"""
        pattern_map: Dict[FailureCategory, FailurePattern] = {}

        for cat, filename in failed_categories:
            if cat not in pattern_map:
                pattern_map[cat] = FailurePattern(category=cat, count=0)
            pattern_map[cat].count += 1
            pattern_map[cat].affected_files.append(filename)

        return list(pattern_map.values())

    def _generate_feedback(
        self, gates: List[GateResult], content: str, file_path: str
    ) -> str:
        """生成可操作的修正反馈。

        这是 Loop Engineering 中 "feedback" 环节的关键：
        验证失败时不仅要告诉用户"挂了"，还要说明"怎么修"。
        """
        failed_gates = [g for g in gates if not g.passed]
        if not failed_gates:
            return ""

        lines = [f"文件 {os.path.basename(file_path)} 验证未通过，建议修正:\n"]

        suggestions = {
            "G1_non_empty": "  → 知识点内容过少，建议重新分析原页面或跳过此条目",
            "G2_has_content": "  → 实质内容不足，可能需要更详细的原始页面或调整分析 prompt",
            "G3_has_source": "  → 缺少来源链接，请在分析时保留原始 URL 信息",
            "G4_no_secrets": "  → 可能包含敏感信息（API Key/密码等），请移除后再存档",
            "G5_valid_markdown": "  → Markdown 格式不完整，确保包含标题（#）和正文",
        }

        for gate in failed_gates:
            suggestion = suggestions.get(gate.name, f"  → {gate.reason}")
            lines.append(suggestion)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Gate 定义（确定性规则）
    # ------------------------------------------------------------------

    def _gate_non_empty(self, path: str, content: str) -> GateResult:
        """G1: 内容非空。"""
        if not content or len(content.strip()) < 10:
            return GateResult(
                "G1_non_empty", False, "内容过少 (<10字符)",
                suggestion="知识点内容过少，建议跳过或重新爬取原页面",
            )
        return GateResult("G1_non_empty", True, "内容充足")

    def _gate_has_content(self, path: str, content: str) -> GateResult:
        """G2: 包含实质性内容（不只是标题和引用）。"""
        cleaned = re.sub(r'[#>*_`\n\r]', ' ', content)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if len(cleaned) < 50:
            return GateResult(
                "G2_has_content", False, "实质内容不足 (<50字符)",
                suggestion="知识点缺乏实质内容，建议调整分析 prompt 以提取更多信息",
            )
        return GateResult("G2_has_content", True, "实质内容充足")

    def _gate_has_source(self, path: str, content: str) -> GateResult:
        """G3: 包含来源链接。"""
        if re.search(r'https?://', content):
            return GateResult("G3_has_source", True, "包含来源链接")
        return GateResult(
            "G3_has_source", False, "缺少来源链接",
            suggestion="请在分析时保留原始 URL，确保每个知识点都有来源追溯",
        )

    def _gate_no_secrets(self, path: str, content: str) -> GateResult:
        """G4: 不包含敏感信息。"""
        secret_patterns = [
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
            (r'Bearer\s+[a-zA-Z0-9\-._~+/]+', "Bearer Token"),
            (r'api[_-]?key\s*[:=]\s*\S+', "API Key 赋值"),
            (r'password\s*[:=]\s*\S+', "Password 赋值"),
            (r'sk-[a-zA-Z0-9]{20,}', "Secret Key"),
        ]
        for pattern, label in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return GateResult(
                    "G4_no_secrets", False, f"可能包含敏感信息: {label}",
                    suggestion=f"检测到可能的 {label}，请从知识点中移除后再存档",
                )
        return GateResult("G4_no_secrets", True, "未发现敏感信息")

    def _gate_valid_markdown(self, path: str, content: str) -> GateResult:
        """G5: 有效的 Markdown 格式。"""
        if not re.search(r'^#\s+', content, re.MULTILINE):
            return GateResult(
                "G5_valid_markdown", False, "缺少标题",
                suggestion="知识点缺少 Markdown 标题（#），请在存档时补充",
            )
        # 额外检查：是否有分隔线（前后结构完整性）
        if "---" not in content:
            return GateResult(
                "G5_valid_markdown", False, "缺少段落分隔",
                suggestion="建议在标题和正文之间添加 --- 分隔线",
            )
        return GateResult("G5_valid_markdown", True, "Markdown 格式有效")
