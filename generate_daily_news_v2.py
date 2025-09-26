#!/usr/bin/env python3
"""
Thinker News Daily Generator V2
整合 n8n 高品質 4-Agent 工作流的新聞發布系統
完全移除低品質的 AveryNewsGenerator 依賴
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import requests

class ThinkerNewsPublisher:
    def __init__(self):
        self.repo_path = Path('/Users/thinkercafe/Documents/thinker-news')
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', '')  # n8n webhook URL
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        
    def wait_for_n8n_content(self, date_str: str, timeout=300) -> bool:
        """
        等待 n8n 生成內容
        檢查是否存在 {date}_community_digest.md 檔案
        """
        expected_file = self.repo_path / f'{date_str}_community_digest.md'
        
        print(f"🔍 等待 n8n 生成內容: {expected_file.name}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if expected_file.exists():
                print(f"✅ 找到 n8n 生成的內容: {expected_file.name}")
                return True
            
            print("⏳ 等待中... (每10秒檢查一次)")
            time.sleep(10)
        
        print(f"❌ 等待超時 ({timeout}秒)，未找到 n8n 生成的內容")
        return False
    
    def trigger_n8n_workflow(self, date_str: str) -> bool:
        """
        觸發 n8n 工作流程
        如果設定了 webhook URL，主動觸發 n8n
        """
        if not self.n8n_webhook_url:
            print("ℹ️ N8N_WEBHOOK_URL 未設定，將等待現有 n8n 內容 (正常模式)")
            return True
        
        try:
            payload = {
                "trigger": "daily_news",
                "date": date_str,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"🚀 觸發 n8n 工作流程: {date_str}")
            response = requests.post(self.n8n_webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ n8n 工作流程觸發成功")
                return True
            else:
                print(f"❌ n8n 觸發失敗: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ n8n 觸發請求失敗: {e}")
            return False
    
    def use_gemini_layout_agent(self, date_str: str) -> bool:
        """
        使用 Gemini Layout Agent 轉換 Markdown 為 HTML
        調用 md2html.py 的功能
        """
        try:
            md_file = self.repo_path / f'{date_str}_community_digest.md'
            
            if not md_file.exists():
                print(f"❌ 找不到 Markdown 檔案: {md_file}")
                return False
            
            print(f"🔄 使用 Gemini Layout Agent 轉換: {md_file.name}")
            
            # 導入 md2html 模組
            sys.path.append(str(self.repo_path))
            from md2html import md2html, save_html
            
            # 調用 Gemini Layout Agent 生成 HTML 內容
            html_content = md2html(
                str(md_file),
                output_date=date_str,
                gemini_api_key=self.gemini_api_key
            )
            
            if html_content:
                # 保存 HTML 檔案
                output_path = self.repo_path / f'{date_str}.html'
                if save_html(html_content, str(output_path)):
                    print(f"✅ HTML 檔案生成成功: {output_path.name}")
                    return True
                else:
                    print("❌ HTML 檔案保存失敗")
                    return False
            else:
                print("❌ HTML 內容生成失敗")
                return False
                
        except Exception as e:
            print(f"❌ Gemini Layout Agent 執行失敗: {e}")
            return False
    
    def update_index_page(self, date_str: str, title: str) -> bool:
        """更新首頁的新聞列表"""
        index_path = self.repo_path / 'index.html'
        
        if not index_path.exists():
            print("❌ index.html 不存在")
            return False
        
        try:
            # 讀取現有內容
            content = index_path.read_text(encoding='utf-8')
            
            # 新的新聞項目HTML
            new_item = f'''            <div class="news-item">
                <div class="news-date">📅 {date_str} (今日)</div>
                <div class="news-title">🚀 {title}</div>
                <div class="news-description">
                    今日AI科技重點新聞精選，涵蓋最新的工具應用、產業趨勢與安全警報。
                </div>
                <a href="./{date_str}.html" class="news-link">閱讀完整報告 📖</a>
            </div>'''
            
            # 替換第一個新聞項目
            start_marker = '<div class="news-item">'
            start_idx = content.find(start_marker)
            
            if start_idx != -1:
                # 找到第一個news-item的結束位置
                temp_content = content[start_idx:]
                count = 0
                end_idx = start_idx
                
                for i, char in enumerate(temp_content):
                    if temp_content[i:i+5] == '<div ':
                        count += 1
                    elif temp_content[i:i+6] == '</div>':
                        count -= 1
                        if count == 0:
                            end_idx = start_idx + i + 6
                            break
                
                # 替換內容
                updated_content = content[:start_idx] + new_item + content[end_idx:]
                
                # 更新明日日期顯示
                tomorrow = datetime.strptime(date_str, '%Y-%m-%d')
                tomorrow = tomorrow.replace(day=tomorrow.day + 1)
                tomorrow_str = tomorrow.strftime('%Y-%m-%d')
                
                # 修復「明日精彩內容」的錯誤顯示
                updated_content = updated_content.replace(
                    '📅 2025-09-26\n🔄 明日精彩內容準備中...',
                    f'📅 {tomorrow_str}\n🔄 明日精彩內容準備中...'
                )
                
                # 寫回檔案
                index_path.write_text(updated_content, encoding='utf-8')
                print("✅ 首頁已更新")
                return True
            
            print("❌ 無法找到要替換的新聞項目")
            return False
            
        except Exception as e:
            print(f"❌ 首頁更新失敗: {e}")
            return False
    
    def commit_and_push(self, date_str: str) -> bool:
        """提交並推送到GitHub"""
        try:
            os.chdir(self.repo_path)
            
            # Git操作
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Add high-quality news for {date_str} via n8n 4-Agent workflow'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ 已推送到GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失敗: {e}")
            return False
    
    def publish_daily(self) -> bool:
        """完整的每日發布流程 - n8n 4-Agent 版本"""
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 開始發布 {today} 的 AI 科技日報 (n8n 高品質版本)...")
        
        # 1. 觸發 n8n 工作流程 (可選)
        if not self.trigger_n8n_workflow(today):
            print("⚠️ n8n 觸發失敗，但繼續等待現有內容...")
        
        # 2. 等待 n8n 生成內容
        if not self.wait_for_n8n_content(today):
            print("❌ 未找到 n8n 生成的內容，發布失敗")
            return False
        
        # 3. 使用 Gemini Layout Agent 轉換為 HTML
        if not self.use_gemini_layout_agent(today):
            print("❌ HTML 轉換失敗，發布失敗")
            return False
        
        # 4. 更新首頁
        title = "今日AI科技重點新聞精選"
        if not self.update_index_page(today, title):
            print("❌ 首頁更新失敗，發布失敗")
            return False
        
        # 5. 提交到GitHub
        if not self.commit_and_push(today):
            print("❌ Git 推送失敗，發布失敗")
            return False
        
        # 發布成功
        print(f"""
🎉 發布完成！
📄 網頁: https://thinkercafe-tw.github.io/thinker-news/{today}.html
🏠 首頁: https://thinkercafe-tw.github.io/thinker-news/
💎 品質: n8n 4-Agent 高品質工作流
        """)
        
        return True

def main():
    """主函數"""
    publisher = ThinkerNewsPublisher()
    success = publisher.publish_daily()
    
    if success:
        print("🚀 Thinker News 每日發布成功！(n8n 4-Agent 版本)")
    else:
        print("❌ 發布失敗，請檢查錯誤訊息")
    
    return success

if __name__ == "__main__":
    main()