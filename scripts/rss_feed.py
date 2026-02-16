"""
RSS Feed 生成模組
產生 RSS 2.0 XML feed，讓讀者可以透過 RSS 閱讀器訂閱 Thinker News。

輸出檔案：feed.xml（根目錄）
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from xml.etree.ElementTree import Element, SubElement, tostring, indent

from log_config import get_logger
logger = get_logger(__name__)

# 站點資訊
SITE_URL = "https://thinkercafe-tw.github.io/thinker-news"
SITE_NAME = "Thinker News — AI 科技日報"
SITE_DESCRIPTION = "每日精選 AI 科技新聞，專為資料科學初學者設計。涵蓋 AI 工具、產業趨勢、資安快訊與職涯觀察。"
FEED_FILENAME = "feed.xml"
MAX_ITEMS = 20  # RSS feed 最多列幾篇

# 時區
TW_TZ = timezone(timedelta(hours=8))


def _extract_title_from_html(html_path: Path) -> str:
    """從 HTML 的 <title> 標籤提取標題"""
    try:
        content = html_path.read_text(encoding="utf-8")
        m = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
        if m:
            title = m.group(1).strip()
            # 移除尾巴的 " | Thinker News"
            title = re.sub(r"\s*\|\s*Thinker News$", "", title)
            return title
    except Exception:
        pass
    return None


def _extract_description_from_html(html_path: Path) -> str:
    """從 HTML 的 meta description 提取摘要"""
    try:
        content = html_path.read_text(encoding="utf-8")
        m = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return None


def _scan_reports() -> list:
    """
    掃描 archive/ 目錄 + 根目錄，收集所有日報 HTML。

    Returns:
        list of dict，按日期倒序排列：
        [{'date': '2026-02-11', 'path': Path(...), 'url': '...'}, ...]
    """
    date_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})\.html$")
    reports = []

    # 掃描 archive/
    archive_dir = Path("archive")
    if archive_dir.exists():
        for f in archive_dir.iterdir():
            m = date_pattern.match(f.name)
            if m:
                reports.append({
                    "date": m.group(1),
                    "path": f,
                    "url": f"{SITE_URL}/archive/{f.name}",
                })

    # 掃描根目錄（今日可能還沒移入 archive/）
    for f in Path(".").iterdir():
        m = date_pattern.match(f.name)
        if m and m.group(1) not in {r["date"] for r in reports}:
            reports.append({
                "date": m.group(1),
                "path": f,
                "url": f"{SITE_URL}/{f.name}",
            })

    reports.sort(key=lambda r: r["date"], reverse=True)
    return reports[:MAX_ITEMS]


def generate_rss_feed() -> str:
    """
    產生 RSS 2.0 feed.xml。

    Returns:
        輸出檔案路徑
    """
    logger.info("📡 產生 RSS feed...")

    reports = _scan_reports()
    if not reports:
        logger.warning("⚠️  找不到任何日報 HTML，跳過 RSS 生成")
        return None

    # 建構 XML
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = SubElement(rss, "channel")

    # Channel metadata
    SubElement(channel, "title").text = SITE_NAME
    SubElement(channel, "link").text = SITE_URL
    SubElement(channel, "description").text = SITE_DESCRIPTION
    SubElement(channel, "language").text = "zh-TW"
    SubElement(channel, "lastBuildDate").text = datetime.now(TW_TZ).strftime(
        "%a, %d %b %Y %H:%M:%S %z"
    )
    SubElement(channel, "generator").text = "Thinker News RSS Generator"

    # Atom self-link（RSS 最佳實踐）
    atom_link = SubElement(channel, "atom:link")
    atom_link.set("href", f"{SITE_URL}/{FEED_FILENAME}")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # 嘗試從 latest.json 取得最新一篇的豐富摘要
    latest_summary = {}
    latest_json = Path("latest.json")
    if latest_json.exists():
        try:
            data = json.loads(latest_json.read_text(encoding="utf-8"))
            latest_summary[data.get("date", "")] = data.get("line_content", "")
        except Exception:
            pass

    # Items
    for report in reports:
        item = SubElement(channel, "item")

        date_str = report["date"]

        # 標題
        title = _extract_title_from_html(report["path"])
        if not title:
            title = f"{date_str} AI 科技日報"
        SubElement(item, "title").text = title

        # 連結
        SubElement(item, "link").text = report["url"]

        # GUID
        guid = SubElement(item, "guid")
        guid.set("isPermaLink", "true")
        guid.text = report["url"]

        # 發佈日期（假設每日 08:30 發佈）
        try:
            pub_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=8, minute=30, tzinfo=TW_TZ
            )
            SubElement(item, "pubDate").text = pub_dt.strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            )
        except ValueError:
            pass

        # 摘要：優先用 latest.json 內容，其次用 meta description
        description = ""
        if date_str in latest_summary:
            description = latest_summary[date_str]
        else:
            meta_desc = _extract_description_from_html(report["path"])
            if meta_desc:
                description = meta_desc

        if description:
            SubElement(item, "description").text = description

        # 分類
        SubElement(item, "category").text = "AI 科技新聞"

    # 格式化 XML
    indent(rss, space="  ")
    xml_bytes = tostring(rss, encoding="unicode", xml_declaration=False)
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes

    # 寫入
    output_path = Path(FEED_FILENAME)
    output_path.write_text(xml_content, encoding="utf-8")

    logger.info(f"✅ RSS feed 已生成: {output_path}（{len(reports)} 篇文章）")
    return str(output_path)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    result = generate_rss_feed()
    if result:
        print(f"RSS feed generated: {result}")
    else:
        print("No reports found, feed not generated.")
