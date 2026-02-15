#!/usr/bin/env python3
"""
Thinker News 每日新聞自動生成系統

核心流程：
1. RSS feeds 讀取
2. 台灣本地化篩選
3. AI 處理鏈（DeepSeek → OpenAI → OpenAI → DeepSeek）
4. HTML 頁面生成
5. 輸出 latest.json
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from rss_fetcher import fetch_all_rss_feeds
from news_filter import filter_and_score_news
from ai_processor import (
    get_openai_client,
    get_deepseek_client,
    process_with_data_alchemist,
    process_with_tech_narrator,
    process_with_editor_in_chief,
    process_with_html_generator
)
from html_generator import generate_daily_html, update_index_html
from utils import get_taiwan_date, validate_json_output
from execution_logger import ExecutionLogger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def retry_call(fn, args=(), kwargs=None, max_retries=2, step_name=""):
    """對函式做 retry，每次失敗等待 5 秒再重試。

    Returns:
        fn 的回傳值
    Raises:
        最後一次例外（若全部失敗）
    """
    kwargs = kwargs or {}
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_error = e
            logger.warning(f"⚠️ [{step_name}] 第 {attempt} 次失敗: {e}")
            if attempt < max_retries:
                logger.info(f"⏳ [{step_name}] {5}s 後重試...")
                time.sleep(5)
    raise last_error


def log_step(exec_logger, name, node_type, description, fn, *args, **kwargs):
    """執行一個 pipeline 步驟並自動記錄 exec_logger。

    Returns:
        fn 的回傳值
    Raises:
        fn 拋出的例外（已記錄到 exec_logger）
    """
    exec_logger.log_node_start(name, node_type, description)
    try:
        result = fn(*args, **kwargs)
        return result
    except Exception as e:
        exec_logger.log_node_error(name, e)
        raise


# ---------------------------------------------------------------------------
# Pipeline Steps
# ---------------------------------------------------------------------------

def step_fetch_rss(today_date):
    """步驟 2: 讀取 RSS feeds"""
    all_feeds = fetch_all_rss_feeds(today_date)
    if not all_feeds:
        raise RuntimeError("RSS 讀取結果為空，無法繼續")
    logger.info(f"📡 讀取 {len(all_feeds)} 則新聞")
    return all_feeds


def step_filter_news(all_feeds, today_date):
    """步驟 3: 篩選與評分"""
    filtered = filter_and_score_news(all_feeds, today_date)
    if not filtered:
        raise RuntimeError("沒有新聞通過篩選，流程終止")
    local = sum(1 for n in filtered if n.get('is_taiwan_news', False))
    logger.info(f"🔍 篩選後 {len(filtered)} 則（台灣 {local} / 國際 {len(filtered) - local}）")
    return filtered


def step_ai_chain(filtered_news, today_date):
    """步驟 4: AI 四階段處理鏈，每階段帶 retry"""

    # 4.1 數據煉金術師 (DeepSeek)
    logger.info("  ⚗️  數據煉金術師...")
    raw = retry_call(
        process_with_data_alchemist,
        args=(filtered_news, today_date),
        step_name="數據煉金術師"
    )
    alchemist_json = validate_json_output(raw, "數據煉金術師")

    # 4.2 科技導讀人 (OpenAI)
    logger.info("  📰 科技導讀人...")
    raw = retry_call(
        process_with_tech_narrator,
        args=(alchemist_json, today_date),
        step_name="科技導讀人"
    )
    narrator_json = validate_json_output(raw, "科技導讀人")

    # 4.3 總編輯 (OpenAI)
    logger.info("  ✍️  總編輯...")
    raw = retry_call(
        process_with_editor_in_chief,
        args=(narrator_json, today_date),
        step_name="總編輯"
    )
    editor_json = validate_json_output(raw, "總編輯")

    # 4.4 HTML 生成器 (DeepSeek)
    logger.info("  🎨 HTML 生成器...")
    html_content = retry_call(
        process_with_html_generator,
        kwargs={
            "notion_content": narrator_json.get('notion_daily_report_text', ''),
            "line_content": editor_json.get('line_message_text', ''),
            "today_date": today_date,
        },
        step_name="HTML 生成器"
    )

    return narrator_json, editor_json, html_content


def step_generate_output(today_date, narrator_json, editor_json, html_content):
    """步驟 5-7: 組裝輸出、寫 HTML、寫 latest.json"""

    notion_content = narrator_json.get('notion_daily_report_text', '')
    line_content = editor_json.get('line_message_text', '')
    website_url = f"https://thinkercafe-tw.github.io/thinker-news/{today_date}.html"

    final_output = {
        'final_date': today_date,
        'notion_content': notion_content,
        'line_content': line_content,
        'website_url': website_url,
        'news_json': {
            'date': today_date,
            'line_content': line_content,
            'notion_content': notion_content,
            'website_url': website_url,
            'generated_at': datetime.now().isoformat()
        }
    }

    # 生成 HTML
    daily_path = generate_daily_html(final_output, html_content)
    index_path = update_index_html(today_date)
    logger.info(f"📝 HTML: {daily_path}, {index_path}")

    # 寫入 latest.json
    with open('latest.json', 'w', encoding='utf-8') as f:
        json.dump(final_output['news_json'], f, ensure_ascii=False, indent=2)
    logger.info("💾 latest.json 已儲存")

    return final_output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """主執行流程"""
    exec_logger = ExecutionLogger()

    try:
        # 步驟 0: 驗證 API Keys（單例初始化）
        logger.info("🔑 驗證 API Keys...")
        get_openai_client()
        get_deepseek_client()

        # 步驟 1: 今日日期
        today_date = get_taiwan_date()
        logger.info(f"📅 今日日期: {today_date}")

        # 步驟 2: RSS
        all_feeds = log_step(
            exec_logger, "RSS Feed 讀取", "rss",
            "讀取所有新聞來源的 RSS feeds",
            step_fetch_rss, today_date
        )
        sources = {}
        for f in all_feeds:
            s = f.get('source', 'unknown')
            sources[s] = sources.get(s, 0) + 1
        exec_logger.log_node_success("RSS Feed 讀取", {"total": len(all_feeds), "sources": sources},
                                     {"總新聞數": f"{len(all_feeds)} 則"})

        # 步驟 3: 篩選
        filtered_news = log_step(
            exec_logger, "台灣本地化篩選", "filter",
            "篩選和排序新聞",
            step_filter_news, all_feeds, today_date
        )
        local_count = sum(1 for n in filtered_news if n.get('is_taiwan_news', False))
        exec_logger.log_node_success("台灣本地化篩選", {"count": len(filtered_news)},
                                     {"篩選後": f"{len(filtered_news)} 則",
                                      "台灣": f"{local_count}", "國際": f"{len(filtered_news) - local_count}"})

        # 步驟 4: AI 處理鏈
        exec_logger.log_node_start("AI 處理鏈", "ai", "四階段 AI 處理")
        narrator_json, editor_json, html_content = step_ai_chain(filtered_news, today_date)
        exec_logger.log_node_success("AI 處理鏈", None, {"階段": "4/4 完成"})
        logger.info("✅ AI 處理鏈完成")

        # 步驟 5-7: 輸出
        final_output = log_step(
            exec_logger, "輸出生成", "html",
            "生成 HTML + latest.json",
            step_generate_output, today_date, narrator_json, editor_json, html_content
        )
        exec_logger.log_node_success("輸出生成", None, {"檔案": "3 個"})

        # 完成
        logger.info("🎉 新聞生成流程完成！")
        logger.info(f"📊 原始 {len(all_feeds)} → 篩選 {len(filtered_news)} → {today_date}.html")

        exec_logger.complete_execution("success")
        exec_logger.save_to_file("execution_log.json")
        return 0

    except Exception as e:
        logger.error(f"❌ 執行錯誤: {e}", exc_info=True)
        try:
            exec_logger.complete_execution("error")
            exec_logger.save_to_file("execution_log.json")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
