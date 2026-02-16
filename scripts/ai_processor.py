"""
AI 處理鏈
四段式處理：DeepSeek → OpenAI → OpenAI → DeepSeek

1. 數據煉金術師 (Data Alchemist) - DeepSeek
2. 科技導讀人 (Tech Narrator) - OpenAI
3. 總編輯 (Editor-in-Chief) - OpenAI
4. HTML 生成器 (HTML Generator) - DeepSeek
"""

import os
import json
import time
from typing import List, Dict, Callable, Any
from functools import wraps
from openai import OpenAI

from log_config import get_logger
from prompts import (
    DATA_ALCHEMIST_SYSTEM_PROMPT,
    TECH_NARRATOR_SYSTEM_PROMPT,
    EDITOR_IN_CHIEF_SYSTEM_PROMPT,
    HTML_GENERATOR_SYSTEM_PROMPT,
)

logger = get_logger(__name__)

# ============================================
# 重試裝飾器
# ============================================

def retry_on_failure(max_retries: int = 2, delay: int = 3):
    """
    重試裝飾器

    Args:
        max_retries: 最大重試次數
        delay: 重試延遲（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(f"⚠️  {func.__name__} 第 {attempt + 1} 次嘗試失敗: {str(e)}")
                        logger.info(f"🔄 等待 {delay} 秒後重試...")
                        time.sleep(delay)
                    else:
                        logger.error(f"❌ {func.__name__} 在 {max_retries + 1} 次嘗試後仍然失敗")
                        raise
            return None
        return wrapper
    return decorator

# ============================================
# API 配置（單例模式，避免每次呼叫重建 client）
# ============================================

_openai_client = None
_deepseek_client = None


def get_openai_client() -> OpenAI:
    """取得 OpenAI client（單例）"""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY 環境變數未設置")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def get_deepseek_client() -> OpenAI:
    """取得 DeepSeek client（單例）"""
    global _deepseek_client
    if _deepseek_client is None:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("❌ DEEPSEEK_API_KEY 環境變數未設置")
        _deepseek_client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return _deepseek_client


def _log_usage(response, provider: str):
    """記錄 API token 使用量"""
    if hasattr(response, 'usage') and response.usage:
        u = response.usage
        logger.info(f"📊 {provider} Token: prompt={u.prompt_tokens}, output={u.completion_tokens}, total={u.total_tokens}")


def call_deepseek(system_instruction: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 8192) -> str:
    """呼叫 DeepSeek API"""
    logger.info("🔑 呼叫 DeepSeek API...")
    client = get_deepseek_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    _log_usage(response, "DeepSeek")
    logger.info("✅ DeepSeek API 呼叫成功")
    return response.choices[0].message.content


def call_openai(system_instruction: str, user_prompt: str, model: str = "chatgpt-4o-latest", temperature: float = 0.7) -> str:
    """呼叫 OpenAI API"""
    logger.info(f"🔑 呼叫 OpenAI API ({model})...")
    client = get_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )
    _log_usage(response, "OpenAI")
    logger.info("✅ OpenAI API 呼叫成功")
    return response.choices[0].message.content


# ============================================
# 系統提示詞已移至 prompts.py
# ============================================
# DATA_ALCHEMIST_SYSTEM_PROMPT, TECH_NARRATOR_SYSTEM_PROMPT,
# EDITOR_IN_CHIEF_SYSTEM_PROMPT 透過檔案頂部 import 引入。


# ============================================
# AI 處理函數
# ============================================

@retry_on_failure(max_retries=2, delay=5)
def process_with_data_alchemist(filtered_news: List[Dict], today_date: str) -> str:
    """數據煉金術師 - 使用 DeepSeek，分析原始新聞並產出結構化 JSON"""
    logger.info("⚗️  數據煉金術師處理中...")

    news_data = [{'title': item['title'], 'link': item['link'], 'content': item['content']}
                 for item in filtered_news]

    user_prompt = f"""新聞標題
{json.dumps([n['title'] for n in news_data], ensure_ascii=False, indent=2)}

超鏈結
{json.dumps([n['link'] for n in news_data], ensure_ascii=False, indent=2)}

新聞內容
{json.dumps([n['content'] for n in news_data], ensure_ascii=False, indent=2)}

今日日期
{today_date}"""

    output = call_deepseek(DATA_ALCHEMIST_SYSTEM_PROMPT, user_prompt)
    logger.info("✅ 數據煉金術師處理完成")
    return output


@retry_on_failure(max_retries=2, delay=3)
def process_with_tech_narrator(alchemist_json: Dict, today_date: str) -> str:
    """科技導讀人 - 使用 OpenAI，將結構化新聞轉為 Notion 日報"""
    logger.info("📰 科技導讀人處理中...")

    user_prompt = f"""數據煉金術師 OUTPUT: {json.dumps(alchemist_json, ensure_ascii=False)}

今日日期
{today_date}"""

    output = call_openai(TECH_NARRATOR_SYSTEM_PROMPT, user_prompt)
    logger.info("✅ 科技導讀人處理完成")
    return output


@retry_on_failure(max_retries=2, delay=3)
def process_with_editor_in_chief(narrator_json: Dict, today_date: str) -> str:
    """總編輯 - 使用 OpenAI，產出 LINE 精華版"""
    logger.info("✍️  總編輯處理中...")

    notion_text = narrator_json.get('notion_daily_report_text', '')
    user_prompt = f"""【Notion 版 AI 日報】:
{notion_text}

今日日期
{today_date}"""

    output = call_openai(EDITOR_IN_CHIEF_SYSTEM_PROMPT, user_prompt)
    logger.info("✅ 總編輯處理完成")
    return output


@retry_on_failure(max_retries=2, delay=3)
def process_with_html_generator(notion_content: str, line_content: str, today_date: str) -> str:
    """HTML 生成器 - 使用 DeepSeek，將 Markdown 內容轉為完整 HTML 頁面"""
    logger.info("🎨 HTML 生成器處理中...")

    user_prompt = f"""請基於以下標準範本，將 n8n 新聞內容格式化為完全相同的格式。

標準範本 HTML:
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025-09-23 AI 科技日報 | Thinker News</title>
    <meta name="description" content="Nvidia投資OpenAI巨額資金，AI安全挑戰並存 - 今日AI科技重點新聞精選">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🤖</text></svg>">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft JhengHei', sans-serif;
            line-height: 1.7;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}

        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: white;
            text-decoration: none;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 20px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .back-link:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateX(-5px);
        }}

        .article-header {{
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}

        .article-date {{
            font-size: 1.1em;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
        }}

        .article-title {{
            font-size: 2.2em;
            font-weight: 800;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.3;
        }}

        .article-subtitle {{
            font-size: 1.2em;
            color: #666;
            font-weight: 400;
        }}

        .content-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}

        .content-section h2 {{
            color: #667eea;
            font-size: 1.6em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            font-weight: 700;
        }}

        .content-section h3 {{
            color: #555;
            font-size: 1.3em;
            margin: 25px 0 15px;
            font-weight: 600;
        }}

        .content-section p {{
            margin-bottom: 15px;
            line-height: 1.7;
            font-size: 1.05em;
        }}

        .content-section ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}

        .content-section li {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}

        .highlight-box {{
            background: linear-gradient(135deg, #667eea20, #764ba220);
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 15px 15px 0;
        }}

        .news-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .news-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}

        .external-link::after {{
            content: " 🔗";
            font-size: 0.8em;
        }}

        .footer-nav {{
            text-align: center;
            padding: 30px;
            color: white;
        }}

        .nav-button {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            margin: 0 10px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .nav-button:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}

        @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}

            .article-header {{
                padding: 25px 20px;
            }}

            .article-title {{
                font-size: 1.8em;
            }}

            .content-section {{
                padding: 25px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="./index.html" class="back-link">← 返回首頁</a>

        <header class="article-header">
            <div class="article-date">📅 2025年9月23日</div>
            <h1 class="article-title">🤖 AI 科技日報精選</h1>
            <p class="article-subtitle">Nvidia投資OpenAI巨額資金，AI安全挑戰並存</p>
        </header>

        <div class="content-section">
            <h2>✨ 今日必讀 TOP 3</h2>

            <h3>1. Nvidia投資OpenAI高達1000億美元</h3>
            <p>Nvidia 與 OpenAI 達成協議，部署價值10千萬瓦的 AI 晶片，目的為推動下一代的ChatGPT。這顯示出 AI 領域的龍頭企業對於人工智慧未來潛力的高度信心。</p>
            <div class="highlight-box">
                <strong>💡 學習價值：</strong><br>
                這筆巨額投資標誌著AI基礎設施建設進入新階段，對於想要學習AI的初學者來說，這意味著更強大的工具和更多的學習資源即將到來。
            </div>
            <p><a href="https://techcrunch.com/2025/09/22/nvidia-plans-to-invest-up-to-100b-in-openai/" class="news-link external-link" target="_blank">閱讀更多</a></p>

            <h3>2. ShadowLeak漏洞透過OpenAI ChatGPT洩漏Gmail數據</h3>
            <p>這是一個重要的安全警報，OpenAI ChatGPT的深度研究代理中的零點擊漏洞可能讓攻擊者通過一封精心製作的電子郵件洩漏敏感的Gmail收件箱數據。</p>
            <div class="highlight-box">
                <strong>💡 學習價值：</strong><br>
                此事提醒我們，在 AI 的發展同時，我們也需要更加關注其帶來的安全問題。初學者應該學習 AI 資安的基礎知識。
            </div>
            <p><a href="https://thehackernews.com/2025/09/shadowleak-zero-click-flaw-leaks-gmail.html" class="news-link external-link" target="_blank">閱讀更多</a></p>

            <h3>3. 基礎設施交易推動AI繁榮</h3>
            <p>大型科技公司如 Meta、Oracle、Microsoft、Google 和 OpenAI 的大筆支出推動 AI 的興起。</p>
            <div class="highlight-box">
                <strong>💡 學習價值：</strong><br>
                這不僅反映出 AI 的重要性，更顯示出了其在產業界的影響力。初學者可以從中了解 AI 產業的發展趨勢。
            </div>
            <p><a href="https://techcrunch.com/2025/09/22/the-billion-dollar-infrastructure-deals-powering-the-ai-boom/" class="news-link external-link" target="_blank">閱讀更多</a></p>
        </div>

        <div class="content-section" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
            <h2 style="color: white; border-bottom: 3px solid white;">📱 LINE 精華版</h2>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 20px 0;">
                <h3>🤖 今日AI重點 (LINE版)</h3>
                <p><strong>💰 大新聞：</strong>Nvidia砸1000億美元投資OpenAI，推動下一代ChatGPT！</p>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <p style="font-size: 0.9em; opacity: 0.8;">
                    💡 此精華版專為LINE推送設計 | 完整分析請閱讀上方詳細報告
                </p>
            </div>
        </div>

        <div class="footer-nav">
            <a href="./index.html" class="nav-button">🏠 返回首頁</a>
            <a href="https://github.com/ThinkerCafe-tw/thinker-news" class="nav-button" target="_blank">⭐ GitHub</a>
        </div>
    </div>

    <script>
        // 頁面載入動畫
        document.addEventListener('DOMContentLoaded', function() {{
            const sections = document.querySelectorAll('.content-section');
            sections.forEach((section, index) => {{
                section.style.opacity = '0';
                section.style.transform = 'translateY(20px)';
                setTimeout(() => {{
                    section.style.transition = 'all 0.6s ease';
                    section.style.opacity = '1';
                    section.style.transform = 'translateY(0)';
                }}, index * 150);
            }});
        }});
    </script>
<script src="./thinker_secret_entrance.js"></script>
</body>
</html>

要替換的內容:
- 日期: {today_date}
- 新聞內容: 以下 n8n 內容

n8n 新聞內容:
{notion_content}

LINE消息版：
{line_content}

執行指令:
1. 使用標準範本的完整格式
2. 只替換日期和新聞內容
3. 保持所有 CSS 和 JavaScript 不變
4. 確保輸出結束於 </html>
5. 不要添加任何說明文字

請輸出完整的 HTML 代碼"""

    output = call_deepseek(HTML_GENERATOR_SYSTEM_PROMPT, user_prompt, temperature=0.3)

    # 清理可能的 markdown 代碼塊標記
    if output.startswith('```html'):
        output = output[7:]
    if output.startswith('```'):
        output = output[3:]
    if output.endswith('```'):
        output = output[:-3]
    output = output.strip()

    logger.info("✅ HTML 生成器處理完成")
    return output
