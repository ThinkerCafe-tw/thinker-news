#!/usr/bin/env python3
"""
Email 訂閱管理系統
用於管理和發送 email 訂閱內容
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

class EmailSubscriptionManager:
    def __init__(self):
        # Supabase 配置
        supabase_url = "https://ygcmxeimfjaivzdtzpct.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnY214ZWltZmphaXZ6ZHR6cGN0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg0NTI5MjYsImV4cCI6MjA3NDAyODkyNn0.qWA3Jj0muFqZbVx-3Jf2JKfb3Ch9Pb5VbpsU_nD8x5A"
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
    def get_all_subscribers(self, status: str = 'active') -> List[Dict]:
        """
        從 semantic_insights 表獲取所有訂閱者
        """
        try:
            response = self.supabase.table("semantic_insights").select("*").eq("category", "email_subscription").execute()
            
            subscribers = []
            for record in response.data:
                try:
                    content = json.loads(record['content'])
                    if content.get('status') == status:
                        subscribers.append({
                            'id': record['id'],
                            'email': content.get('email'),
                            'name': content.get('name'),
                            'interested_topics': content.get('interested_topics', []),
                            'subscription_date': content.get('subscription_date'),
                            'status': content.get('status'),
                            'created_at': record['created_at']
                        })
                except json.JSONDecodeError:
                    continue
            
            return subscribers
        except Exception as e:
            print(f"❌ 獲取訂閱者失敗: {str(e)}")
            return []
    
    def get_subscriber_count(self) -> Dict[str, int]:
        """
        獲取訂閱者統計
        """
        try:
            response = self.supabase.table("semantic_insights").select("content").eq("category", "email_subscription").execute()
            
            total = 0
            active = 0
            
            for record in response.data:
                try:
                    content = json.loads(record['content'])
                    total += 1
                    if content.get('status') == 'active':
                        active += 1
                except json.JSONDecodeError:
                    continue
            
            return {
                'total': total,
                'active': active,
                'inactive': total - active
            }
        except Exception as e:
            print(f"❌ 獲取統計失敗: {str(e)}")
            return {'total': 0, 'active': 0, 'inactive': 0}
    
    def get_subscribers_by_interests(self, topic: str) -> List[Dict]:
        """
        根據興趣主題獲取訂閱者
        """
        try:
            all_subscribers = self.get_all_subscribers('active')
            interested_subscribers = []
            
            for subscriber in all_subscribers:
                if topic in subscriber.get('interested_topics', []):
                    interested_subscribers.append(subscriber)
            
            return interested_subscribers
        except Exception as e:
            print(f"❌ 獲取主題訂閱者失敗: {str(e)}")
            return []
    
    def update_last_sent_date(self, email: str) -> bool:
        """
        更新最後發送日期
        """
        try:
            response = self.supabase.table("email_subscriptions").update({
                "last_sent_date": datetime.now().isoformat()
            }).eq("email", email).execute()
            return True
        except Exception as e:
            print(f"❌ 更新發送日期失敗: {str(e)}")
            return False
    
    def unsubscribe_email(self, email: str) -> bool:
        """
        取消訂閱
        """
        try:
            response = self.supabase.table("email_subscriptions").update({
                "status": "unsubscribed",
                "updated_at": datetime.now().isoformat()
            }).eq("email", email).execute()
            return True
        except Exception as e:
            print(f"❌ 取消訂閱失敗: {str(e)}")
            return False
    
    def create_insight_email_content(self, insight_data: Dict) -> Dict[str, str]:
        """
        創建洞察郵件內容
        """
        title = insight_data.get('title', '新學習洞察')
        content = insight_data.get('content', '')
        category = insight_data.get('category', '學習洞察')
        url = insight_data.get('url', 'https://thinkercafe-tw.github.io/thinker-news/')
        
        # HTML 版本
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; margin: 20px 0; border-radius: 10px; }}
                .button {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 {title}</h1>
                    <p>{category}</p>
                </div>
                
                <div class="content">
                    <p>{content}</p>
                    
                    <a href="{url}" class="button">🔗 查看完整內容</a>
                </div>
                
                <div class="footer">
                    <p>📧 來自 ThinkerCafe 的學習洞察</p>
                    <p><a href="{url}#unsubscribe">取消訂閱</a> | <a href="{url}">訪問網站</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 純文字版本
        text_content = f"""
🧠 {title}

{category}

{content}

🔗 完整內容：{url}

---
📧 來自 ThinkerCafe 的學習洞察
取消訂閱：{url}#unsubscribe
        """
        
        return {
            'subject': f"🧠 {title} - ThinkerCafe 學習洞察",
            'html': html_content,
            'text': text_content
        }
    
    def export_subscribers_for_email_service(self, format: str = 'csv') -> str:
        """
        匯出訂閱者資料供外部郵件服務使用
        """
        subscribers = self.get_all_subscribers()
        
        if format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 標題行
            writer.writerow(['Email', 'Name', 'Subscription Date', 'Interests'])
            
            # 資料行
            for sub in subscribers:
                writer.writerow([
                    sub.get('email', ''),
                    sub.get('name', ''),
                    sub.get('subscription_date', ''),
                    ', '.join(sub.get('interested_topics', []))
                ])
            
            return output.getvalue()
        
        elif format == 'json':
            return json.dumps(subscribers, indent=2, ensure_ascii=False)

def main():
    """
    測試和管理功能
    """
    manager = EmailSubscriptionManager()
    
    print("📊 Email 訂閱系統狀態")
    print("=" * 30)
    
    # 顯示統計
    stats = manager.get_subscriber_count()
    print(f"📧 總訂閱者: {stats['total']}")
    print(f"✅ 活躍訂閱者: {stats['active']}")
    print(f"❌ 非活躍訂閱者: {stats['inactive']}")
    
    # 顯示最近訂閱者
    subscribers = manager.get_all_subscribers()
    if subscribers:
        print(f"\n📝 最近 5 位訂閱者:")
        for sub in subscribers[-5:]:
            print(f"  • {sub.get('email')} ({sub.get('subscription_date', '')[:10]})")
    
    print("\n🎯 各主題訂閱者分布:")
    topics = ['AI開發', '團隊協作', '學習方法', '工具應用']
    for topic in topics:
        topic_subs = manager.get_subscribers_by_interests(topic)
        print(f"  • {topic}: {len(topic_subs)} 人")

if __name__ == "__main__":
    main()