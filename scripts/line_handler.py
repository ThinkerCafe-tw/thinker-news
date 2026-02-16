"""
LINE /news 確定性處理模組

接收 LINE Webhook 事件，對 /news 指令直接回傳 latest.json 內容，
不經任何 AI 加工，確保每次回覆一致。

用法:
  # 作為獨立 Flask 伺服器
  python line_handler.py

  # 作為模組引入
  from line_handler import handle_line_event

環境變數:
  LINE_CHANNEL_ACCESS_TOKEN  — LINE Bot channel access token
  LINE_CHANNEL_SECRET        — LINE Bot channel secret（用於驗證簽名）
"""
from __future__ import annotations

import hashlib
import hmac
import base64
import json
import os
import sys
from pathlib import Path

from log_config import get_logger
from get_latest_news import get_latest_news, format_news_reply

logger = get_logger(__name__)

# ── 指令定義 ──────────────────────────────────────────────

COMMANDS = {
    "/news": "回傳今日 AI 新聞日報",
    "/help": "顯示可用指令",
}

HELP_TEXT = (
    "📋 可用指令：\n"
    "/news — 查看今日 AI 新聞日報\n"
    "/help — 顯示此說明"
)


# ── 核心處理 ──────────────────────────────────────────────

def handle_command(text: str) -> str | None:
    """
    處理使用者訊息，回傳確定性回覆。
    非指令訊息回傳 None（不處理）。
    """
    cmd = text.strip().lower()

    if cmd == "/news":
        data = get_latest_news("all")
        return format_news_reply(data)

    if cmd == "/help":
        return HELP_TEXT

    # 非指令 → 不回覆
    return None


# ── LINE Webhook 驗證 ─────────────────────────────────────

def verify_signature(body: bytes, signature: str, channel_secret: str) -> bool:
    """驗證 LINE Webhook 簽名"""
    mac = hmac.new(
        channel_secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature)


# ── LINE 回覆 API ────────────────────────────────────────

def reply_message(reply_token: str, text: str, access_token: str) -> bool:
    """透過 LINE Messaging API 回覆訊息"""
    import requests

    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("✅ LINE 回覆成功")
            return True
        else:
            logger.error(f"❌ LINE 回覆失敗: {resp.status_code} — {resp.text}")
            return False
    except Exception as e:
        logger.error(f"❌ LINE 回覆例外: {e}")
        return False


# ── Webhook 事件處理 ──────────────────────────────────────

def handle_line_event(event: dict, access_token: str) -> bool:
    """
    處理單一 LINE Webhook 事件。

    Args:
        event: LINE event dict
        access_token: LINE channel access token

    Returns:
        True if replied, False if skipped or failed
    """
    if event.get("type") != "message":
        return False

    message = event.get("message", {})
    if message.get("type") != "text":
        return False

    text = message.get("text", "")
    reply_token = event.get("replyToken", "")

    reply = handle_command(text)
    if reply is None:
        return False

    logger.info(f"📨 收到指令: {text}")
    return reply_message(reply_token, reply, access_token)


# ── Flask 伺服器（可選） ──────────────────────────────────

def create_app():
    """建立 Flask 應用（僅在需要時 import flask）"""
    try:
        from flask import Flask, request, abort
    except ImportError:
        logger.error("❌ 需要安裝 flask: pip install flask")
        sys.exit(1)

    app = Flask(__name__)

    channel_secret = os.getenv("LINE_CHANNEL_SECRET", "")
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

    @app.route("/webhook/line", methods=["POST"])
    def webhook():
        # 驗證簽名
        signature = request.headers.get("X-Line-Signature", "")
        body = request.get_data()

        if channel_secret and not verify_signature(body, signature, channel_secret):
            logger.warning("⚠️ 簽名驗證失敗")
            abort(403)

        # 處理事件
        data = request.get_json(silent=True) or {}
        events = data.get("events", [])

        for event in events:
            handle_line_event(event, access_token)

        return "OK", 200

    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    return app


# ── CLI 模式 ──────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LINE /news 確定性處理")
    parser.add_argument(
        "--serve", action="store_true",
        help="啟動 Flask webhook 伺服器"
    )
    parser.add_argument(
        "--port", type=int, default=5000,
        help="伺服器埠號（預設: 5000）"
    )
    parser.add_argument(
        "--test", type=str, default=None,
        help="測試指令處理（例: --test '/news'）"
    )
    args = parser.parse_args()

    if args.test:
        result = handle_command(args.test)
        if result:
            print(result)
        else:
            print(f"（非指令訊息: {args.test}）")
    elif args.serve:
        app = create_app()
        app.run(host="0.0.0.0", port=args.port)
    else:
        # 預設: 測試 /news
        result = handle_command("/news")
        print(result or "（無內容）")
