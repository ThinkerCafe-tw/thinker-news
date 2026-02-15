"""
/news 回覆一致性模組

讀取 latest.json，原文照發，不經 AI 加工。
確保每次 /news 查詢拿到的內容與生成時完全一致。

用法:
  # 作為模組引入
  from get_latest_news import get_latest_news
  result = get_latest_news()            # 回傳完整 dict
  result = get_latest_news("line")      # 僅回傳 LINE 精華文字
  result = get_latest_news("notion")    # 僅回傳 Notion 詳細文字
  result = get_latest_news("url")       # 僅回傳網頁連結

  # 作為 CLI
  python get_latest_news.py              # 輸出 LINE 精華版（預設）
  python get_latest_news.py --format line
  python get_latest_news.py --format notion
  python get_latest_news.py --format url
  python get_latest_news.py --format json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from log_config import get_logger
logger = get_logger(__name__)

# latest.json 位於 repo 根目錄
LATEST_JSON_PATH = Path(__file__).parent.parent / "latest.json"


def get_latest_news(fmt: str = "all") -> dict | str | None:
    """
    讀取 latest.json，依 fmt 回傳對應內容。

    Args:
        fmt: "all" (完整 dict), "line" (LINE 精華文字),
             "notion" (Notion 詳細文字), "url" (網頁連結),
             "json" (原始 JSON 字串)

    Returns:
        依 fmt 回傳 dict / str，檔案不存在時回傳 None。
    """
    if not LATEST_JSON_PATH.exists():
        logger.warning("⚠️ latest.json 不存在，尚未生成今日日報")
        return None

    try:
        with open(LATEST_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"❌ 讀取 latest.json 失敗: {e}")
        return None

    if fmt == "all":
        return data
    elif fmt == "line":
        return data.get("line_content", "（LINE 內容不可用）")
    elif fmt == "notion":
        return data.get("notion_content", "（Notion 內容不可用）")
    elif fmt == "url":
        return data.get("website_url", "（網址不可用）")
    elif fmt == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        logger.warning(f"⚠️ 未知格式: {fmt}，回傳完整資料")
        return data


def format_news_reply(data: dict | None) -> str:
    """
    將 latest.json 資料格式化為友善的回覆訊息。
    適用於 LINE/Telegram 等訊息平台的 /news 回覆。
    """
    if data is None:
        return "📭 今日日報尚未生成，請稍後再試。"

    date = data.get("date", "未知日期")
    line_content = data.get("line_content", "")
    url = data.get("website_url", "")

    if not line_content:
        return f"📭 {date} 的日報內容暫時無法取得。"

    reply = line_content.strip()
    if url:
        reply += f"\n\n🔗 完整報告: {url}"

    return reply


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="讀取今日 AI 新聞日報")
    parser.add_argument(
        "--format", "-f",
        choices=["line", "notion", "url", "json", "reply"],
        default="reply",
        help="輸出格式（預設: reply）"
    )
    args = parser.parse_args()

    if args.format == "reply":
        data = get_latest_news("all")
        print(format_news_reply(data))
    else:
        result = get_latest_news(args.format)
        if result is None:
            print("❌ latest.json 不存在", file=sys.stderr)
            sys.exit(1)
        print(result)
