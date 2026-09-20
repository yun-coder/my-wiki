#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容入口：统一转调 daily_collector，避免两套采集流程分叉。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import daily_collector


def main() -> int:
    daily_collector.main()
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n  [digest_ai_news] 主采集器异常: {error}", file=sys.stderr)
        daily_collector._cleanup_and_exit(1)
    else:
        daily_collector._cleanup_and_exit(0)
