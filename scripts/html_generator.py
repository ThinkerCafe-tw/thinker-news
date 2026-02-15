"""
HTML 生成模組
使用 Jinja2 模板生成 HTML 頁面
混合方式：固定的 <head> + AI 生成的 <body> 內容

模板檔案位於 scripts/templates/：
  - daily_news.html: 日報頁面模板
  - index.html: 首頁模板
"""

from pathlib import Path
from datetime import datetime, timedelta
from jinja2 import Template

from log_config import get_logger
logger = get_logger(__name__)

# 模板目錄
TEMPLATE_DIR = Path(__file__).parent / "templates"


def _load_template(name: str) -> Template:
    """從 templates/ 目錄載入 Jinja2 模板"""
    template_path = TEMPLATE_DIR / name
    if not template_path.exists():
        raise FileNotFoundError(f"模板檔案不存在: {template_path}")
    return Template(template_path.read_text(encoding="utf-8"))


def generate_daily_html(final_output: dict, html_full_content: str = None) -> str:
    """
    生成今日新聞 HTML 頁面
    完全對齊 n8n 架構：AI 生成完整的 HTML 文檔

    Args:
        final_output: 組裝後的最終輸出
        html_full_content: AI 生成的完整 HTML 文檔（可選）

    Returns:
        HTML 文件路徑
    """
    logger.info("📝 生成今日新聞 HTML...")

    date = final_output['final_date']

    # 如果有 AI 生成的完整 HTML，直接使用（對齊 n8n 架構）
    if html_full_content:
        html_content = html_full_content
    else:
        # 降級方案：使用模板方式
        logger.warning("⚠️  未提供 HTML body 內容，使用降級方案")
        notion_content = final_output['notion_content']
        line_content = final_output['line_content']

        template = _load_template("daily_news.html")
        html_content = template.render(
            date=date,
            notion_content=notion_content,
            line_content=line_content
        )

    # 寫入文件
    output_path = Path(f"{date}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"✅ HTML 文件已生成: {output_path}")
    return str(output_path)


def update_index_html(today_date: str) -> str:
    """
    更新首頁 index.html

    Args:
        today_date: 今日日期

    Returns:
        index.html 文件路徑
    """
    logger.info("📝 更新首頁 index.html...")

    # 計算明日日期
    today_dt = datetime.strptime(today_date, '%Y-%m-%d')
    tomorrow_dt = today_dt + timedelta(days=1)
    tomorrow_date = tomorrow_dt.strftime('%Y-%m-%d')

    # 從模板生成
    template = _load_template("index.html")
    html_content = template.render(
        today_date=today_date,
        tomorrow_date=tomorrow_date
    )

    # 寫入文件
    output_path = Path('index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"✅ index.html 已更新")
    return str(output_path)
