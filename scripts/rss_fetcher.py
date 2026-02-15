"""
RSS Feed 讀取模組
從多個來源讀取 RSS feeds，支援 timeout、retry 與容錯機制
"""

import feedparser
import logging
import time
import urllib.request
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# === RSS 來源配置 ===
# region: 'intl' 國際 | 'tw' 台灣 | 'ai' AI 專題
RSS_SOURCES = {
    # 國際科技
    'hackernews':  {'url': 'https://feeds.feedburner.com/TheHackersNews',             'region': 'intl'},
    'techcrunch':  {'url': 'https://techcrunch.com/feed/',                             'region': 'intl'},
    'arstechnica': {'url': 'http://feeds.arstechnica.com/arstechnica/index/',          'region': 'intl'},
    # AI 專題
    'openai':      {'url': 'https://openai.com/news/rss.xml',                         'region': 'ai'},
    'bair':        {'url': 'https://bair.berkeley.edu/blog/feed.xml',                  'region': 'ai'},
    # 台灣科技
    'technews':    {'url': 'https://technews.tw/feed/',                                'region': 'tw'},
    'ithome':      {'url': 'https://www.ithome.com.tw/rss',                            'region': 'tw'},
    'inside':      {'url': 'https://www.inside.com.tw/feed/rss',                       'region': 'tw'},
}

# 連線設定
FETCH_TIMEOUT_SECS = 15   # 單一 feed 讀取 timeout
MAX_RETRIES = 2            # 失敗重試次數
RETRY_DELAY_SECS = 2      # 重試間隔


def fetch_single_feed(source_name: str, url: str) -> List[Dict]:
    """
    讀取單一 RSS feed（含 timeout + retry）

    Args:
        source_name: 來源名稱
        url: RSS feed URL

    Returns:
        新聞列表（失敗回空 list，不會 raise）
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"  📡 讀取 {source_name}（attempt {attempt}）...")

            # 用 urllib 手動抓再餵給 feedparser，才能控制 timeout
            req = urllib.request.Request(url, headers={'User-Agent': 'ThinkerNews/1.0'})
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECS) as resp:
                raw = resp.read()

            feed = feedparser.parse(raw)

            if feed.bozo and not feed.entries:
                logger.warning(f"  ⚠️  {source_name} RSS 格式有問題且無條目")
                last_error = f"bozo feed: {feed.bozo_exception}"
                time.sleep(RETRY_DELAY_SECS)
                continue

            news_items = []
            for entry in feed.entries:
                try:
                    item = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'content': entry.get('summary', entry.get('description', '')),
                        'pubDate': entry.get('published', entry.get('updated', '')),
                        'isoDate': entry.get('published_parsed', entry.get('updated_parsed', None)),
                        'source': source_name
                    }

                    # 轉換日期格式
                    if item['isoDate']:
                        try:
                            dt = datetime(*item['isoDate'][:6])
                            item['isoDate'] = dt.isoformat()
                        except Exception:
                            item['isoDate'] = ''

                    news_items.append(item)

                except Exception as e:
                    logger.warning(f"  ⚠️  處理 {source_name} 的某則新聞時出錯: {e}")
                    continue

            logger.info(f"  ✅ {source_name}: 讀取 {len(news_items)} 則")
            return news_items

        except Exception as e:
            last_error = str(e)
            logger.warning(f"  ⚠️  {source_name} attempt {attempt} 失敗: {last_error}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECS)

    logger.error(f"  ❌ {source_name} 全部 {MAX_RETRIES} 次嘗試失敗: {last_error}")
    return []


def fetch_all_rss_feeds(today_date: str) -> List[Dict]:
    """
    並行讀取所有 RSS feeds

    Args:
        today_date: 今日日期（用於日誌）

    Returns:
        所有新聞的列表
    """
    all_news = []
    failed_sources = []

    max_workers = min(len(RSS_SOURCES), 8)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_source = {
            executor.submit(fetch_single_feed, name, cfg['url']): name
            for name, cfg in RSS_SOURCES.items()
        }

        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                news_items = future.result()
                if news_items:
                    all_news.extend(news_items)
                else:
                    failed_sources.append(source_name)
            except Exception as e:
                logger.error(f"❌ {source_name} 讀取任務失敗: {e}")
                failed_sources.append(source_name)

    if failed_sources:
        logger.warning(f"⚠️  本次失敗來源: {', '.join(failed_sources)}")

    logger.info(f"📊 總共讀取 {len(all_news)} 則新聞（來自 {len(RSS_SOURCES) - len(failed_sources)}/{len(RSS_SOURCES)} 個來源）")
    return all_news
