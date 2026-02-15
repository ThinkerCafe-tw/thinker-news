"""
台灣本地化新聞篩選器
移植自 n8n workflow 的 Code3 節點

核心功能：
1. 智能評分系統
2. 台灣視角優先
3. 來源平衡策略

篩選配置見 filter_config.py
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

from filter_config import (
    SOURCES, TAIWAN_SOURCES, INTERNATIONAL_SOURCES,
    TAIWAN_INTERESTS, GLOBAL_TAIWAN_FOCUS,
    MUST_KEEP_PHRASES, PRACTICAL_KEYWORDS,
    SOURCE_LABELS,
)

logger = logging.getLogger(__name__)


def calculate_relevance(item: Dict) -> int:
    """
    計算新聞的相關性分數

    Args:
        item: 新聞項目

    Returns:
        相關性分數
    """
    title = item.get('title', '').lower()
    content = item.get('content', '').lower()
    full_text = f"{title} {content}"

    source = item.get('source', 'unknown')
    config = SOURCES.get(source, {
        'priority_keywords': [],
        'exclude': [],
        'base_score': 0
    })

    score = config.get('base_score', 0)

    # 1. 必須保留
    for phrase in MUST_KEEP_PHRASES:
        if phrase.lower() in full_text:
            return 100

    # 2. 排除關鍵字
    for keyword in config.get('exclude', []):
        if keyword.lower() in full_text:
            score -= 5

    # 3. 來源優先關鍵字
    for keyword in config.get('priority_keywords', []):
        keyword_lower = keyword.lower()
        if keyword_lower in title:
            score += 10
        elif keyword_lower in content:
            score += 5

    # 4. 台灣興趣關鍵字（額外加分）
    for keyword in TAIWAN_INTERESTS:
        if keyword.lower() in full_text:
            score += 4

    # 5. 全球但台灣關注的主題
    for keyword in GLOBAL_TAIWAN_FOCUS:
        if keyword.lower() in full_text:
            score += 6

    # 6. 來源類型加分
    if source in TAIWAN_SOURCES:
        score += 5
        if '國際' in full_text or 'global' in full_text:
            score += 8

    if source in INTERNATIONAL_SOURCES:
        if 'taiwan' in full_text or 'asia' in full_text:
            score += 10

    # 7. 實用性加分
    for keyword in PRACTICAL_KEYWORDS:
        if keyword in title:
            score += 7

    # 8. 內容長度
    if len(content) > 300:
        score += 2
    if len(content) > 500:
        score += 2

    return score


def filter_and_score_news(all_news: List[Dict], target_date: str) -> List[Dict]:
    """
    篩選和評分新聞

    Args:
        all_news: 所有新聞列表
        target_date: 目標日期

    Returns:
        篩選後的新聞列表
    """
    logger.info("🔍 開始篩選新聞...")

    # 解析目標日期
    target_dt = datetime.strptime(target_date, '%Y-%m-%d')
    yesterday = target_dt - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # 分組處理
    grouped = {source: [] for source in SOURCES}
    grouped['unknown'] = []

    for item in all_news:
        # 檢查日期
        pub_date = item.get('isoDate', '')
        if pub_date:
            try:
                pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                if pub_dt.strftime('%Y-%m-%d') != yesterday_str:
                    continue
            except Exception:
                continue

        # 計算分數
        score = calculate_relevance(item)
        source = item.get('source', 'unknown')

        # 添加額外資訊
        enriched_item = {
            **item,
            'relevance_score': score,
            'source_label': SOURCE_LABELS.get(source, '📰 其他')
        }

        if source in grouped:
            grouped[source].append(enriched_item)
        else:
            grouped['unknown'].append(enriched_item)

    # 排序和限制
    taiwan_news = []
    international_news = []

    for source, items in grouped.items():
        if not items or source == 'unknown':
            continue

        config = SOURCES.get(source, {})
        max_items = config.get('max_items', 5)

        # 排序並篩選
        filtered = sorted(items, key=lambda x: x['relevance_score'], reverse=True)
        filtered = [item for item in filtered if item['relevance_score'] > 0]
        filtered = filtered[:max_items]

        # 分類本地與國際
        if source in TAIWAN_SOURCES:
            taiwan_news.extend(filtered)
        else:
            international_news.extend(filtered)

        logger.info(f"  {SOURCE_LABELS.get(source, source)}: {len(items)} → {len(filtered)}")

    # 混合排序策略：確保本地與國際新聞平衡
    final_items = []
    max_length = max(len(taiwan_news), len(international_news))

    for i in range(max_length):
        if i < len(taiwan_news):
            final_items.append(taiwan_news[i])
        if i < len(international_news):
            final_items.append(international_news[i])

    # 最終按分數重排（但保持一定多樣性）
    final_items.sort(key=lambda x: (
        # 先按分數分組
        -1 if x['relevance_score'] > 20 else (-2 if x['relevance_score'] > 10 else -3),
        # 同組內按分數排序
        -x['relevance_score']
    ))

    # 統計報告
    logger.info("\n📊 篩選結果總覽：")
    logger.info("【台灣新聞】")
    for source in TAIWAN_SOURCES:
        count = len([item for item in final_items if item['source'] == source])
        logger.info(f"  {SOURCE_LABELS[source]}: {count} 則")

    logger.info("\n【國際新聞】")
    for source in INTERNATIONAL_SOURCES:
        count = len([item for item in final_items if item['source'] == source])
        logger.info(f"  {SOURCE_LABELS[source]}: {count} 則")

    taiwan_count = len([i for i in final_items if i['source'] in TAIWAN_SOURCES])
    international_count = len(final_items) - taiwan_count

    logger.info(f"\n{'=' * 40}")
    logger.info(f"✅ 最終保留: {len(final_items)} 則")
    logger.info(f"  - 本地: {taiwan_count} 則")
    logger.info(f"  - 國際: {international_count} 則")
    logger.info(f"{'=' * 40}\n")

    return final_items
