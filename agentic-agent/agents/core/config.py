"""配置管理 — 从 .env 加载环境变量。"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import dotenv


@dataclass
class Config:
    """全局配置，从 .env 文件加载。"""

    # Agnes AI
    agnes_api_key: str
    agnes_base_url: str = "https://apihub.agnes-ai.com/v1"
    agnes_model: str = "agnes-2.0-flash"

    # 路径
    bookmarks_path: str = ""
    knowledge_base_path: str = ""
    workspace_path: str = ""

    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> "Config":
        """从 .env 文件加载配置。"""
        if env_path is None:
            project_root = Path(__file__).parent.parent.parent
            env_path = str(project_root / ".env")

        dotenv.load_dotenv(env_path, override=True)

        return cls(
            agnes_api_key=os.getenv("AGNES_API_KEY", ""),
            agnes_base_url=os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
            agnes_model=os.getenv("AGNES_MODEL", "agnes-2.0-flash"),
            bookmarks_path=os.getenv("BOOKMARKS_PATH", ""),
            knowledge_base_path=os.getenv("KNOWLEDGE_BASE_PATH", ""),
            workspace_path=os.getenv("WORKSPACE_PATH", str(Path(__file__).parent.parent.parent)),
        )


# 全局配置单例
config = Config.from_env()
