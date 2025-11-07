#!/usr/bin/env python3
"""
Thinker News 每日新聞自動生成系統
從 n8n 遷移到 GitHub Actions

核心流程：
1. 讀取 RSS feeds
2. 台灣本地化篩選
3. AI 處理鏈（Gemini → OpenAI → OpenAI）
4. 生成 HTML 頁面
5. 更新 GitHub repo
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 導入自定義模組
from rss_fetcher import fetch_all_rss_feeds
from news_filter import filter_and_score_news
from ai_processor import (
    setup_apis,
    process_with_data_alchemist,
    process_with_tech_narrator,
    process_with_editor_in_chief
)
from html_generator import generate_daily_html, update_index_html
from utils import get_taiwan_date, validate_json_output


def main():
    """主執行流程"""
    try:
        # ============================================
        # 步驟 0: 設置 API Keys
        # ============================================
        logger.info("🔑 設置 API Keys...")
        openai_client = setup_apis()
        logger.info("✅ API Keys 設置完成")

        # ============================================
        # 步驟 1: 生成今日日期（台灣時區）
        # ============================================
        today_date = get_taiwan_date()
        logger.info(f"📅 生成今日日期: {today_date}")
        
        # ============================================
        # 步驟 2: 讀取所有 RSS feeds
        # ============================================
        logger.info("📡 開始讀取 RSS feeds...")
        all_feeds = fetch_all_rss_feeds(today_date)
        logger.info(f"✅ 成功讀取 {len(all_feeds)} 則新聞")
        
        # ============================================
        # 步驟 3: 台灣本地化篩選與評分
        # ============================================
        logger.info("🔍 執行台灣本地化篩選...")
        filtered_news = filter_and_score_news(all_feeds, today_date)
        logger.info(f"✅ 篩選後保留 {len(filtered_news)} 則新聞")
        
        if len(filtered_news) == 0:
            logger.error("❌ 沒有新聞通過篩選，流程終止")
            sys.exit(1)
        
        # ============================================
        # 步驟 4: AI 處理鏈
        # ============================================
        logger.info("🤖 開始 AI 處理鏈...")
        
        # 4.1 數據煉金術師 (Gemini)
        logger.info("  ⚗️  數據煉金術師處理中...")
        alchemist_output = process_with_data_alchemist(filtered_news, today_date)
        alchemist_json = validate_json_output(alchemist_output, "數據煉金術師")
        
        # 4.2 科技導讀人 (OpenAI)
        logger.info("  📰 科技導讀人處理中...")
        narrator_output = process_with_tech_narrator(alchemist_json, today_date)
        narrator_json = validate_json_output(narrator_output, "科技導讀人")
        
        # 4.3 總編輯 (OpenAI)
        logger.info("  ✍️  總編輯處理中...")
        editor_output = process_with_editor_in_chief(narrator_json, today_date)
        editor_json = validate_json_output(editor_output, "總編輯")
        
        logger.info("✅ AI 處理鏈完成")
        
        # ============================================
        # 步驟 5: 組裝最終輸出
        # ============================================
        logger.info("📦 組裝最終輸出...")
        
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
        
        # ============================================
        # 步驟 6: 生成 HTML 文件
        # ============================================
        logger.info("📝 生成 HTML 文件...")
        
        # 6.1 生成今日新聞頁面
        daily_html_path = generate_daily_html(final_output)
        logger.info(f"✅ 今日新聞頁面: {daily_html_path}")
        
        # 6.2 更新首頁 index.html
        index_html_path = update_index_html(today_date)
        logger.info(f"✅ 首頁更新: {index_html_path}")
        
        # ============================================
        # 步驟 7: 儲存 latest.json
        # ============================================
        logger.info("💾 儲存 latest.json...")
        latest_json_path = Path('latest.json')
        with open(latest_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_output['news_json'], f, ensure_ascii=False, indent=2)
        logger.info(f"✅ latest.json 已儲存")
        
        # ============================================
        # 完成
        # ============================================
        logger.info("🎉 新聞生成流程完成！")
        logger.info(f"📊 統計資訊:")
        logger.info(f"  - 原始新聞數: {len(all_feeds)}")
        logger.info(f"  - 篩選後數量: {len(filtered_news)}")
        logger.info(f"  - 生成日期: {today_date}")
        logger.info(f"  - 網站 URL: {website_url}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ 執行過程發生錯誤: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
