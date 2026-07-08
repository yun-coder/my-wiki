"""Agentic AI 系统入口。

用法：
  python main.py              # 知识库分析模式
  python main.py --daily      # 每日 AI资讯 采集模式
"""

import sys
import argparse
from pathlib import Path

# 确保项目根目录在 path 中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.scheduler.loop import run_loop
from agents.scheduler.daily_task import run_daily_task
from agents.core.config import Config


def main():
    parser = argparse.ArgumentParser(description="Agentic AI 系统")
    parser.add_argument("--daily", action="store_true",
                        help="执行每日 AI资讯 采集任务")
    args = parser.parse_args()

    cfg = Config.from_env()

    if args.daily:
        run_daily_task(cfg)
    else:
        run_loop(cfg)


if __name__ == "__main__":
    main()
