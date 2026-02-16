"""
錯誤通知模組 — 生成失敗時通知相關人員

支援通知管道：
  1. Slack Webhook（主要，透過 SLACK_WEBHOOK_URL）
  2. LINE Push Message（備用，透過 LINE_CHANNEL_ACCESS_TOKEN + LINE_NOTIFY_USER_ID）

環境變數：
  SLACK_WEBHOOK_URL          — Slack incoming webhook URL
  LINE_CHANNEL_ACCESS_TOKEN  — LINE Bot channel access token（選填）
  LINE_NOTIFY_USER_ID        — 接收錯誤通知的 LINE user ID（選填）

用法：
  # 在 main.py 中
  from error_notifier import notify_error
  notify_error("RSS 讀取失敗", "TimeoutError: connection timed out")

  # 獨立測試
  python error_notifier.py
"""
from __future__ import annotations

import json
import os
import traceback
from datetime import datetime

from log_config import get_logger

logger = get_logger(__name__)

# 延遲 import requests，避免在未安裝時 import 階段就報錯
_requests = None


def _get_requests():
    global _requests
    if _requests is None:
        import requests
        _requests = requests
    return _requests


def _get_timestamp():
    """取得台灣時間字串"""
    from utils import get_taiwan_date
    try:
        date_str = get_taiwan_date()
    except Exception:
        date_str = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")
    return f"{date_str} {now}"


def _send_slack(step: str, error_msg: str, timestamp: str) -> bool:
    """透過 Slack Webhook 發送錯誤通知"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        logger.debug("SLACK_WEBHOOK_URL 未設置，跳過 Slack 通知")
        return False

    requests = _get_requests()
    payload = {
        "text": f"❌ Thinker News 生成失敗\n步驟: {step}\n錯誤: {error_msg}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Thinker News 生成失敗",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*步驟:*\n{step}"},
                    {"type": "mrkdwn", "text": f"*時間:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*錯誤訊息:*\n```{error_msg[:1500]}```",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔧 請檢查 <https://github.com/ThinkerCafe-tw/thinker-news/actions|GitHub Actions> 日誌",
                    }
                ],
            },
        ],
    }

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code == 200:
            logger.info("✅ Slack 錯誤通知已發送")
            return True
        else:
            logger.warning(f"Slack 通知失敗: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.warning(f"Slack 通知發送例外: {e}")
        return False


def _send_line(step: str, error_msg: str, timestamp: str) -> bool:
    """透過 LINE Push Message 發送錯誤通知"""
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    user_id = os.getenv("LINE_NOTIFY_USER_ID", "")

    if not access_token or not user_id:
        logger.debug("LINE_CHANNEL_ACCESS_TOKEN 或 LINE_NOTIFY_USER_ID 未設置，跳過 LINE 通知")
        return False

    requests = _get_requests()
    text = (
        f"❌ Thinker News 生成失敗\n"
        f"━━━━━━━━━━━━━━\n"
        f"📍 步驟: {step}\n"
        f"⏰ 時間: {timestamp}\n"
        f"💥 錯誤:\n{error_msg[:800]}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔧 請查看 GitHub Actions 日誌"
    )

    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }

    try:
        resp = requests.post(
            "https://api.line.me/v2/bot/message/push",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            logger.info("✅ LINE 錯誤通知已發送")
            return True
        else:
            logger.warning(f"LINE 通知失敗: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.warning(f"LINE 通知發送例外: {e}")
        return False


def notify_error(step: str, error: str | Exception, tb: str | None = None):
    """發送錯誤通知到所有已配置的管道

    Args:
        step: 失敗的步驟名稱（如 "RSS 讀取"、"AI 處理鏈"）
        error: 錯誤訊息或 Exception 物件
        tb: 可選的 traceback 字串；若 error 為 Exception 且未提供 tb，
            會自動擷取 traceback
    """
    if isinstance(error, Exception):
        error_msg = f"{type(error).__name__}: {error}"
        if tb is None:
            tb = traceback.format_exc()
    else:
        error_msg = str(error)

    # 組合完整錯誤訊息（含 traceback 摘要）
    full_msg = error_msg
    if tb and tb.strip() != "NoneType: None":
        # 取 traceback 最後 500 字
        tb_tail = tb.strip()[-500:]
        full_msg = f"{error_msg}\n\n{tb_tail}"

    timestamp = _get_timestamp()
    logger.error(f"🚨 錯誤通知: [{step}] {error_msg}")

    sent = False
    sent |= _send_slack(step, full_msg, timestamp)
    sent |= _send_line(step, full_msg, timestamp)

    if not sent:
        logger.warning("⚠️ 沒有任何通知管道可用（SLACK_WEBHOOK_URL / LINE 皆未設置）")


# ---------------------------------------------------------------------------
# 獨立測試
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🧪 測試錯誤通知...")
    notify_error("測試步驟", "這是一條測試錯誤訊息")
    print("完成。檢查 Slack / LINE 是否收到通知。")
