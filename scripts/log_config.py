"""
Thinker News — 統一 logging 設定

所有模組統一使用此設定，確保格式一致。
使用方式:
    from log_config import get_logger
    logger = get_logger(__name__)
"""

import sys
import logging
from pathlib import Path

# 全域只初始化一次
_initialized = False

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = Path(__file__).parent.parent / "news_generation.log"


def setup_logging(level: int = logging.INFO) -> None:
    """初始化 root logger（只執行一次）。"""
    global _initialized
    if _initialized:
        return
    _initialized = True

    root = logging.getLogger()
    root.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # 檔案 handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # 終端 handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter)
    root.addHandler(sh)


def get_logger(name: str) -> logging.Logger:
    """取得已設定格式的 logger。首次呼叫會自動初始化。"""
    setup_logging()
    return logging.getLogger(name)
