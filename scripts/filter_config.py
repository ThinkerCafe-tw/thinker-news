"""
新聞篩選配置
從 news_filter.py 抽取，集中管理所有篩選規則與關鍵字

修改篩選行為只需改此檔，不動邏輯。
"""

# ============================================
# 來源配置
# ============================================

SOURCES = {
    # === 台灣本地來源 ===
    'technews': {
        'priority_keywords': [
            # AI 相關
            'AI', '人工智慧', 'ChatGPT', 'Claude', 'Gemini',
            '生成式', 'LLM', '大型語言模型',
            # 台灣關鍵字
            '台積電', 'TSMC', '聯發科', '鴻海', '華碩', '宏碁',
            '台灣', 'Taiwan', '數位發展部', '資策會',
            # 實用工具
            '工具', 'App', '應用程式', '開源', '免費'
        ],
        'exclude': [
            '股價', '財報', '營收', '法說會',
            '併購', '投資', '基金'
        ],
        'max_items': 12,
        'base_score': 8
    },

    'ithome': {
        'priority_keywords': [
            'AI', '資安', 'Cloud', '雲端', 'DevOps',
            '開發', 'Python', 'JavaScript', 'API',
            '微軟', 'Google', 'AWS', 'Azure',
            '企業應用', '數位轉型', '自動化'
        ],
        'exclude': [
            '研討會', '論壇', '招標', '採購'
        ],
        'max_items': 10,
        'base_score': 7
    },

    'inside': {
        'priority_keywords': [
            'startup', '新創', 'AI', '創新', 'Web3',
            'NFT', '區塊鏈', 'Fintech', '金融科技',
            '電商', 'SaaS', 'B2B', 'B2C',
            '使用者體驗', 'UX', '產品設計'
        ],
        'exclude': [
            '募資', '種子輪', 'Series', 'IPO'
        ],
        'max_items': 8,
        'base_score': 6
    },

    # === 國際來源 ===
    'hackernews': {
        'priority_keywords': [
            'AI', 'ChatGPT', 'Claude', 'Gemini', 'OpenAI',
            'tool', 'app', 'browser', 'Python', 'npm'
        ],
        'exclude': [
            'CVE-2025', 'CVSS', 'vulnerability', 'ransomware'
        ],
        'max_items': 8,
        'base_score': 0
    },

    'techcrunch': {
        'priority_keywords': [
            'AI', 'ChatGPT', 'OpenAI', 'Anthropic',
            'app', 'tool', 'feature', 'launch'
        ],
        'exclude': [
            'raises', 'funding', 'valuation', 'layoffs'
        ],
        'max_items': 6,
        'base_score': 0
    },

    'openai': {
        'priority_keywords': ['GPT', 'API', 'model', 'release'],
        'exclude': [],
        'max_items': 5,
        'base_score': 15
    },

    'arstechnica': {
        'priority_keywords': [
            'AI', 'science', 'research', 'quantum', 'space'
        ],
        'exclude': ['gaming', 'review', 'streaming'],
        'max_items': 4,
        'base_score': 0
    },

    'bair': {
        'priority_keywords': ['research', 'paper', 'algorithm'],
        'exclude': [],
        'max_items': 3,
        'base_score': 3
    }
}

# 台灣本地來源名稱集合（用於邏輯判斷）
TAIWAN_SOURCES = {'technews', 'ithome', 'inside'}
INTERNATIONAL_SOURCES = {'hackernews', 'techcrunch', 'openai', 'arstechnica', 'bair'}

# ============================================
# 關鍵字集合
# ============================================

# 台灣民眾特別關注的關鍵字
TAIWAN_INTERESTS = [
    # 本土企業與產業
    '半導體', '晶片', '晶圓', 'IC設計', '封測',
    '電動車', '儲能', '綠能', '太陽能', '風電',

    # 台灣相關國際新聞
    'Taiwan', '台灣', 'Taipei', '台北',
    'Asia', '亞洲', '東南亞', 'ASEAN',

    # 實用性高的內容
    '教學', '懶人包', '比較', '推薦', '免費',
    '中文', '繁體', '在地化', '本土化',

    # 熱門應用
    'LINE', 'Instagram', 'YouTube', '抖音', 'TikTok',
    '街口', 'PChome', '蝦皮', 'momo'
]

# 全球趨勢但台灣特別關注
GLOBAL_TAIWAN_FOCUS = [
    'NVIDIA', 'AMD', 'Intel',
    'Apple', 'iPhone',
    '供應鏈', 'supply chain',
    '中美', 'US-China', '晶片戰'
]

# 無條件保留的短語
MUST_KEEP_PHRASES = [
    '台積電', 'TSMC',
    '數位發展部',
    'ChatGPT 開放台灣',
    'Google 台灣',
    'Microsoft 台灣'
]

# 實用性加分關鍵字
PRACTICAL_KEYWORDS = ['教學', 'tutorial', 'guide', '實測', '評測', '比較']

# ============================================
# 來源中文標籤
# ============================================

SOURCE_LABELS = {
    'technews': '🇹🇼 科技新報',
    'ithome': '🇹🇼 iThome',
    'inside': '🇹🇼 INSIDE',
    'hackernews': '🌍 Hacker News',
    'techcrunch': '🌍 TechCrunch',
    'arstechnica': '🌍 Ars Technica',
    'openai': '🤖 OpenAI',
    'bair': '🎓 Berkeley AI'
}
