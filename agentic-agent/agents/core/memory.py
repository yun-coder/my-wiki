"""Memory — 有状态记忆管理系统，Context Engineering 的核心。

从简单的 append-only 日志升级为真正的记忆管理层：
1. Append-only 事件日志 — 不可变的运行轨迹
2. 短期上下文窗口 — 最近 N 条记录，用于当前决策
3. 长期摘要 — 跨多次运行的趋势统计
4. 知识索引 — 已存档知识点的快速查找

这对应 Loop Engineering 中的 Context Engineering：
决定"模型/Agent 看到什么信息"来做出更好的决策。
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


# ============================================================================
# 数据类型
# ============================================================================


@dataclass
class MemoryEvent:
    """单条记忆事件 — append-only 不可变记录。"""
    timestamp: str
    phase: str          # discover / crawl / analyze / archive / evaluate / correct
    status: str         # pass / fail / warn / skipped
    summary: str
    metadata: Dict[str, Any] = None  # 附加上下文数据

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CycleSummary:
    """单次完整循环的摘要。"""
    run_id: str
    started_at: str
    ended_at: str
    total_cycles: int
    passing_cycles: int
    failing_cycles: int
    skipped_cycles: int
    knowledge_points_added: int
    files_archived: int
    evaluation_rounds: int


# ============================================================================
# 记忆管理器
# ============================================================================


class Memory:
    """有状态记忆管理器。

    三层架构：
    ┌─────────────────────────────────────────────────┐
    │ Layer 1: Event Log (append-only, 永久)           │
    │   state/memory.md — 人类可读的运行轨迹            │
    ├─────────────────────────────────────────────────┤
    │ Layer 2: Context Window (滑动窗口, 短期)          │
    │   state/memory_context.json — 最近 N 条事件       │
    │   用于当前决策的上下文注入                         │
    ├─────────────────────────────────────────────────┤
    │ Layer 3: Long-term Summary (聚合, 长期)          │
    │   state/memory_summary.json — 趋势统计            │
    │   用于跨周期分析和改进                             │
    └─────────────────────────────────────────────────┘
    """

    def __init__(self, memory_path: str = ""):
        if not memory_path:
            project_root = Path(__file__).parent.parent.parent
            memory_path = str(project_root / "state" / "memory.md")
        self.memory_path = memory_path
        memory_dir = os.path.dirname(memory_path)
        self.context_path = os.path.join(memory_dir, "memory_context.json")
        self.summary_path = os.path.join(memory_dir, "memory_summary.json")
        os.makedirs(memory_dir, exist_ok=True)
        self._init_files()

    def _init_files(self):
        """初始化记忆文件。"""
        if not os.path.exists(self.memory_path):
            Path(self.memory_path).write_text(
                "# Agent Memory Log\n\n"
                "Append-only log of all loop cycles.\n"
                "Each line: <timestamp> | <phase> | <status> | <summary>\n\n"
            )
        if not os.path.exists(self.context_path):
            Path(self.context_path).write_text("{}")
        if not os.path.exists(self.summary_path):
            Path(self.summary_path).write_text("{}")

    # ------------------------------------------------------------------
    # Layer 1: Append-only 事件日志
    # ------------------------------------------------------------------

    def append(self, phase: str, status: str, summary: str, metadata: Dict = None) -> str:
        """追加一条记忆事件。

        Args:
            phase: 阶段名 (discover/crawl/analyze/archive/evaluate/correct)
            status: 状态 (pass/fail/warn/skipped)
            summary: 摘要
            metadata: 附加上下文数据

        Returns:
            生成的时间戳字符串
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        line = f"{timestamp} | {phase} | {status} | {summary}\n"

        with open(self.memory_path, "a", encoding="utf-8") as f:
            f.write(line)

        # 同时存入结构化事件
        event = MemoryEvent(
            timestamp=timestamp,
            phase=phase,
            status=status,
            summary=summary,
            metadata=metadata or {},
        )
        self._store_event(event)

        return line

    # ------------------------------------------------------------------
    # Layer 2: 短期上下文窗口
    # ------------------------------------------------------------------

    def get_context_window(self, n: int = 20) -> List[MemoryEvent]:
        """获取最近 N 条事件作为上下文窗口。

        用于当前决策时注入相关历史背景。
        """
        events = self._load_events()
        return events[-n:] if len(events) > n else events

    def get_phase_history(self, phase: str, n: int = 10) -> List[MemoryEvent]:
        """获取指定阶段的历史记录。"""
        events = self._load_events()
        phase_events = [e for e in events if e.phase == phase]
        return phase_events[-n:]

    def get_recent_failures(self, n: int = 5) -> List[MemoryEvent]:
        """获取最近的失败记录，用于诊断问题。"""
        events = self._load_events()
        failures = [e for e in events if e.status in ("fail", "warn")]
        return failures[-n:]

    def build_context_prompt(self) -> str:
        """构建上下文注入 prompt — Context Engineering 的核心。

        将最近的运行历史和趋势摘要整合为一段文本，
        可在分析阶段注入给 LLM 作为上下文。
        """
        lines = []

        # 最近事件摘要
        recent = self.get_context_window(10)
        if recent:
            lines.append("## 最近的运行历史")
            for event in reversed(recent):
                icon = {"pass": "✓", "fail": "✗", "warn": "⚠", "skipped": "→"}.get(
                    event.status, "?"
                )
                lines.append(f"  [{icon}] {event.phase}: {event.summary}")

        # 失败趋势
        failures = self.get_recent_failures(5)
        if failures:
            lines.append("\n## 近期失败模式")
            phase_counts = {}
            for f in failures:
                phase_counts[f.phase] = phase_counts.get(f.phase, 0) + 1
            for phase, count in sorted(phase_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  - {phase}: 失败 {count} 次")

        return "\n".join(lines) if lines else "(无历史记录)"

    # ------------------------------------------------------------------
    # Layer 3: 长期摘要
    # ------------------------------------------------------------------

    def record_cycle_summary(self, summary: CycleSummary):
        """记录一次完整循环的摘要。"""
        data = self._load_summary()
        data["cycles"] = data.get("cycles", [])
        data["cycles"].append(asdict(summary))
        # 保留最近 100 次
        data["cycles"] = data["cycles"][-100:]
        self._save_summary(data)

    def get_trend_stats(self) -> Dict[str, Any]:
        """获取跨周期的趋势统计。"""
        data = self._load_summary()
        cycles = data.get("cycles", [])
        if not cycles:
            return {"total_runs": 0}

        total = len(cycles)
        avg_kp = sum(c.get("knowledge_points_added", 0) for c in cycles) / total
        avg_files = sum(c.get("files_archived", 0) for c in cycles) / total
        avg_eval_rounds = sum(c.get("evaluation_rounds", 0) for c in cycles) / total

        return {
            "total_runs": total,
            "avg_knowledge_points_per_run": round(avg_kp, 1),
            "avg_files_archived_per_run": round(avg_files, 1),
            "avg_evaluation_rounds": round(avg_eval_rounds, 1),
            "latest_run": cycles[-1] if cycles else None,
        }

    # ------------------------------------------------------------------
    # 内部存储
    # ------------------------------------------------------------------

    def _store_event(self, event: MemoryEvent):
        """将事件存入短期上下文存储。"""
        events = self._load_all_events_structured()
        events.append(asdict(event))
        # 只保留最近 500 条
        events = events[-500:]
        Path(self.context_path).write_text(
            json.dumps(events, ensure_ascii=False, indent=2)
        )

    def _load_events(self) -> List[MemoryEvent]:
        """从 append-only 日志加载所有事件。"""
        if not os.path.exists(self.memory_path):
            return []
        with open(self.memory_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        events = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|", 3)]
            if len(parts) == 4:
                events.append(MemoryEvent(
                    timestamp=parts[0],
                    phase=parts[1],
                    status=parts[2],
                    summary=parts[3],
                ))
        return events

    def _load_all_events_structured(self) -> List[Dict]:
        """从结构化存储加载所有事件。"""
        if not os.path.exists(self.context_path):
            return []
        try:
            data = json.loads(Path(self.context_path).read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, Exception):
            return []

    def _load_summary(self) -> Dict:
        """加载长期摘要。"""
        if not os.path.exists(self.summary_path):
            return {}
        try:
            return json.loads(Path(self.summary_path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            return {}

    def _save_summary(self, data: Dict):
        """保存长期摘要。"""
        Path(self.summary_path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2)
        )

    # ------------------------------------------------------------------
    # 兼容旧接口
    # ------------------------------------------------------------------

    def read_all(self) -> str:
        """读取所有记忆记录（兼容旧接口）。"""
        with open(self.memory_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_recent(self, n: int = 10) -> str:
        """获取最近 n 条记录（兼容旧接口）。"""
        events = self._load_events()
        data_lines = [f"{e.timestamp} | {e.phase} | {e.status} | {e.summary}" for e in events[-n:]]
        return "\n".join(data_lines) if data_lines else "(empty)"
