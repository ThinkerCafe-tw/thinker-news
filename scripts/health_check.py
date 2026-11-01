#!/usr/bin/env python3
"""
Thinker News — Health Check 模組

執行環境與依賴健檢，在 pipeline 跑之前確認一切就緒。
可當獨立腳本跑（python health_check.py），也可被 main.py import。

檢查項目：
  1. 必要環境變數
  2. Python 依賴可 import
  3. 模板檔案存在
  4. 輸出目錄可寫
  5. RSS 來源可連線（選配，預設跳過以加速）
  6. API endpoint 可連線（選配）
"""

import os
import sys
import json
import time
import importlib
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

from dotenv import load_dotenv
load_dotenv()

from log_config import get_logger
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------

REQUIRED_ENV_VARS = [
    "GEMINI_API_KEY",
]

OPTIONAL_ENV_VARS = [
    "SLACK_WEBHOOK_URL",
]

REQUIRED_PACKAGES = [
    "feedparser",
    "openai",
    "requests",
    "jinja2",
    "json_repair",
    "dotenv",
]

REQUIRED_TEMPLATES = [
    "scripts/templates/daily_news.html",
    "scripts/templates/index.html",
]

# API 健檢 endpoint（只做 TCP 連線測試，不消耗 token）
API_ENDPOINTS = {
    "Gemini": "https://generativelanguage.googleapis.com",
}

PROJECT_ROOT = Path(__file__).parent.parent
CONNECT_TIMEOUT_SECS = 5


# ---------------------------------------------------------------------------
# 檢查函式
# ---------------------------------------------------------------------------

def check_env_vars() -> List[str]:
    """檢查必要環境變數是否已設定。回傳錯誤訊息列表。"""
    errors = []
    for var in REQUIRED_ENV_VARS:
        val = os.getenv(var, "")
        if not val:
            errors.append(f"缺少必要環境變數: {var}")
        elif len(val) < 8:
            errors.append(f"環境變數 {var} 看起來太短（可能無效）")

    for var in OPTIONAL_ENV_VARS:
        if not os.getenv(var, ""):
            logger.info(f"  ℹ️  選配環境變數未設定: {var}（不影響核心功能）")

    return errors


def check_packages() -> List[str]:
    """檢查 Python 依賴是否可 import。"""
    errors = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            errors.append(f"Python 套件無法 import: {pkg}")
    return errors


def check_templates() -> List[str]:
    """檢查模板檔案是否存在。"""
    errors = []
    for tpl in REQUIRED_TEMPLATES:
        path = PROJECT_ROOT / tpl
        if not path.exists():
            errors.append(f"模板檔案不存在: {tpl}")
    return errors


def check_output_dirs() -> List[str]:
    """確認輸出目錄可寫入。"""
    errors = []
    # 日報 HTML 寫在 project root
    test_file = PROJECT_ROOT / ".healthcheck_write_test"
    try:
        test_file.write_text("ok")
        test_file.unlink()
    except Exception as e:
        errors.append(f"專案根目錄無法寫入: {e}")

    # archive/ 目錄
    archive_dir = PROJECT_ROOT / "archive"
    if archive_dir.exists() and not os.access(archive_dir, os.W_OK):
        errors.append("archive/ 目錄無法寫入")

    return errors


def check_rss_connectivity() -> Tuple[List[str], List[str]]:
    """快速測試 RSS 來源是否可連線（HEAD request）。

    Returns:
        (warnings, errors) — RSS 失敗算 warning 不算 fatal
    """
    from rss_fetcher import RSS_SOURCES

    warnings = []
    reachable = 0

    for name, cfg in RSS_SOURCES.items():
        url = cfg["url"]
        try:
            req = urllib.request.Request(url, method="HEAD",
                                        headers={"User-Agent": "ThinkerNews-HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT_SECS):
                reachable += 1
        except Exception as e:
            warnings.append(f"RSS 來源 {name} 無法連線: {e}")

    logger.info(f"  📡 RSS 連線: {reachable}/{len(RSS_SOURCES)} 可達")
    return warnings, []


def check_api_connectivity() -> Tuple[List[str], List[str]]:
    """測試 API endpoint 是否可連線（不消耗 token）。

    Returns:
        (warnings, errors) — API 不可達算 error
    """
    errors = []
    for name, url in API_ENDPOINTS.items():
        try:
            req = urllib.request.Request(url, method="HEAD",
                                        headers={"User-Agent": "ThinkerNews-HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT_SECS):
                pass
            logger.info(f"  ✅ {name} API 可連線")
        except Exception as e:
            errors.append(f"{name} API 無法連線 ({url}): {e}")

    return [], errors


# ---------------------------------------------------------------------------
# 主函式
# ---------------------------------------------------------------------------

def run_health_check(include_network: bool = False) -> Dict:
    """執行完整健檢。

    Args:
        include_network: 是否包含 RSS/API 連線測試（較慢）

    Returns:
        {
            "healthy": bool,
            "errors": [...],
            "warnings": [...],
            "checks": {"env": "ok"|"fail", ...},
            "timestamp": "...",
            "duration_ms": int,
        }
    """
    start = time.time()
    all_errors: List[str] = []
    all_warnings: List[str] = []
    checks: Dict[str, str] = {}

    logger.info("🏥 開始健檢...")

    # 1. 環境變數
    errs = check_env_vars()
    all_errors.extend(errs)
    checks["env_vars"] = "fail" if errs else "ok"
    logger.info(f"  {'❌' if errs else '✅'} 環境變數")

    # 2. Python 套件
    errs = check_packages()
    all_errors.extend(errs)
    checks["packages"] = "fail" if errs else "ok"
    logger.info(f"  {'❌' if errs else '✅'} Python 套件")

    # 3. 模板
    errs = check_templates()
    all_errors.extend(errs)
    checks["templates"] = "fail" if errs else "ok"
    logger.info(f"  {'❌' if errs else '✅'} 模板檔案")

    # 4. 輸出目錄
    errs = check_output_dirs()
    all_errors.extend(errs)
    checks["output_dirs"] = "fail" if errs else "ok"
    logger.info(f"  {'❌' if errs else '✅'} 輸出目錄")

    # 5 & 6. 網路（選配）
    if include_network:
        warns, errs = check_rss_connectivity()
        all_warnings.extend(warns)
        all_errors.extend(errs)
        checks["rss"] = "warn" if warns else "ok"

        warns, errs = check_api_connectivity()
        all_warnings.extend(warns)
        all_errors.extend(errs)
        checks["api"] = "fail" if errs else "ok"
    else:
        checks["rss"] = "skipped"
        checks["api"] = "skipped"

    duration_ms = int((time.time() - start) * 1000)
    healthy = len(all_errors) == 0

    result = {
        "healthy": healthy,
        "errors": all_errors,
        "warnings": all_warnings,
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "duration_ms": duration_ms,
    }

    if healthy:
        logger.info(f"🏥 健檢通過 ✅（{duration_ms}ms）")
    else:
        logger.error(f"🏥 健檢失敗 ❌（{len(all_errors)} 個錯誤）")
        for e in all_errors:
            logger.error(f"  💔 {e}")

    if all_warnings:
        for w in all_warnings:
            logger.warning(f"  ⚠️  {w}")

    return result


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Thinker News 健檢工具")
    parser.add_argument("--network", action="store_true",
                        help="包含 RSS/API 連線測試（較慢）")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式輸出結果")
    args = parser.parse_args()

    result = run_health_check(include_network=args.network)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result["healthy"] else 1)
