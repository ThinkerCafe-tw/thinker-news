#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2html 函數 - 使用 Gemini 2.5 Flash 將 n8n 內容轉換為標準格式
將高品質的 n8n markdown 內容格式化為符合 2025-09-23.html 標準的完整 HTML
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 嘗試導入 Gemini
try:
    import google.generativeai as genai
except ImportError:
    print("❌ 請安裝 google-generativeai: pip install google-generativeai")
    sys.exit(1)

def md2html(markdown_path, output_date=None, gemini_api_key=None):
    """
    將 n8n 生成的 markdown 內容轉換為 2025-09-23.html 標準格式
    使用 Gemini 2.5 Flash 進行智能格式化
    
    Args:
        markdown_path: n8n 生成的 markdown 文件路徑
        output_date: 輸出日期 (預設為今天)
        gemini_api_key: Gemini API 金鑰 (預設從 .env 讀取)
    
    Returns:
        完整的 HTML 內容字串
    """
    
    # 設定日期
    if not output_date:
        output_date = datetime.now().strftime('%Y-%m-%d')
    
    # 設定 Gemini API
    if not gemini_api_key:
        # 從 .env 讀取 (需要你添加 GEMINI_API_KEY)
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / '.env')
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
    if not gemini_api_key:
        print("❌ 需要 Gemini API Key")
        print("請在 .env 文件中添加: GEMINI_API_KEY=your_key_here")
        return None
        
    # 初始化 Gemini
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # 讀取 n8n 生成的 markdown 內容
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"❌ 無法讀取文件 {markdown_path}: {str(e)}")
        return None
    
    # 建立 Gemini 提示詞
    system_prompt = """你是一個專業的 HTML 格式化專家。請將提供的 n8n 生成的高品質科技新聞內容，
轉換為符合指定標準格式的完整 HTML 頁面。

**重要要求:**
1. 保持所有新聞內容的品質和完整性
2. 按照標準格式組織內容結構
3. 確保包含完整的 CSS 樣式和 JavaScript
4. 特別注意要包含「LINE 精華版」區塊，使用漸層背景
5. 保持專業的視覺效果和響應式設計
6. 所有連結保持原始 URL
7. 使用繁體中文

**標準格式結構:**
- 頁面標題: "AI 科技日報精選"
- 主要區塊: "今日必讀 TOP 3", "AI工具與應用", "產業趨勢與新聞", "安全警報", "觀點與分析", "編輯後記"
- 特殊區塊: "LINE 精華版" (使用粉紅色漸層背景)
- 導航: 返回首頁連結和 GitHub 連結

**樣式要求:**
- 使用藍紫色漸層背景 (#667eea 到 #764ba2)
- 毛玻璃效果的白色內容區塊
- 漸層文字標題效果
- LINE 區塊使用粉紅色漸層 (#f093fb 到 #f5576c)
- 響應式設計支援手機版"""

    user_prompt = f"""請將以下 n8n 生成的科技新聞內容轉換為完整的 HTML 頁面:

日期: {output_date}

n8n 內容:
{markdown_content}

請輸出完整的 HTML 代碼，包含:
1. 完整的 DOCTYPE、head、body 結構
2. 內嵌的完整 CSS 樣式
3. JavaScript 動畫效果
4. 所有必要的 meta 標籤
5. 專業的內容組織和視覺效果

請確保輸出是可以直接保存為 .html 文件使用的完整代碼。"""

    try:
        print("🤖 正在使用 Gemini 2.5 Flash 進行智能格式化...")
        
        response = model.generate_content([system_prompt, user_prompt])
        html_content = response.text
        
        # 清理可能的 markdown 代碼塊標記
        if html_content.startswith('```html\n'):
            html_content = html_content[8:]
        if html_content.endswith('\n```'):
            html_content = html_content[:-4]
        
        print(f"✅ Gemini 格式化完成！")
        print(f"📄 生成的 HTML 長度: {len(html_content)} 字符")
        
        return html_content
        
    except Exception as e:
        print(f"❌ Gemini API 調用失敗: {str(e)}")
        return None

def save_html(html_content, output_path):
    """保存 HTML 內容到指定路徑"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML 已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 保存失敗: {str(e)}")
        return False

def main():
    """命令行使用範例"""
    if len(sys.argv) < 2:
        print("使用方法: python3 md2html.py <markdown_file> [output_date]")
        print("範例: python3 md2html.py 2025-09-25_community_digest.md 2025-09-25")
        return
    
    markdown_file = sys.argv[1]
    output_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 轉換為 HTML
    html_content = md2html(markdown_file, output_date)
    
    if html_content:
        # 決定輸出檔名
        if not output_date:
            output_date = datetime.now().strftime('%Y-%m-%d')
        
        output_path = f"{output_date}.html"
        
        # 保存文件
        if save_html(html_content, output_path):
            print("🎉 md2html 轉換完成！")
            print(f"🌐 網頁: https://thinkercafe-tw.github.io/thinker-news/{output_date}.html")
        else:
            print("❌ 保存失敗")
    else:
        print("❌ HTML 生成失敗")

if __name__ == "__main__":
    main()