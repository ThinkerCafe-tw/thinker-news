#!/usr/bin/env python3
"""
模型品質比較實驗
用同一批新聞測試不同模型，頂配模型當評審
"""
import json
import random
import os
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import google.generativeai as genai

# ============================================
# 模型配置
# ============================================

CP_MODELS = {
    "deepseek": {
        "provider": "deepseek",
        "model": "deepseek-chat",
    },
    "gemini-flash": {
        "provider": "google",
        "model": "gemini-2.0-flash",
    },
    "gemini-pro": {
        "provider": "google",
        "model": "gemini-1.5-pro",
    },
    "gpt4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
}

JUDGE_MODELS = {
    "gpt5": {
        "provider": "openai",
        "model": "gpt-5.3",  # 或實際可用的最新版
    },
    "claude-opus": {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
    },
    "gemini-pro-top": {
        "provider": "google",
        "model": "gemini-2.5-pro",  # 頂配
    },
}

# ============================================
# API 客戶端
# ============================================

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_deepseek_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

def get_anthropic_client():
    from anthropic import Anthropic
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def init_google():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ============================================
# 模型調用
# ============================================

def call_model(model_config: dict, system: str, user: str) -> str:
    """統一調用不同模型"""
    provider = model_config["provider"]
    model = model_config["model"]

    try:
        if provider == "openai":
            client = get_openai_client()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.7
            )
            return resp.choices[0].message.content

        elif provider == "deepseek":
            client = get_deepseek_client()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            return resp.choices[0].message.content

        elif provider == "google":
            init_google()
            gmodel = genai.GenerativeModel(model)
            resp = gmodel.generate_content(f"{system}\n\n{user}")
            return resp.text

        elif provider == "anthropic":
            client = get_anthropic_client()
            resp = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
            return resp.content[0].text

    except Exception as e:
        return f"[ERROR] {provider}/{model}: {e}"

# ============================================
# 實驗任務
# ============================================

TASK_PROMPT = """你是 AI 科技新聞編輯。請根據以下新聞資料，撰寫一段 150-200 字的精華摘要，包含：
1. 新聞重點（一句話）
2. 為什麼重要（對讀者的意義）
3. 學習建議（給 AI 初學者的啟發）

新聞資料：
標題：{title}
來源：{source}
摘要：{summary}
連結：{link}

請用繁體中文回覆，語氣專業但平易近人。"""

JUDGE_PROMPT = """你是資深 AI 內容品質評審。請評估以下由不同 AI 模型生成的新聞摘要。

原始新聞：
標題：{title}
摘要：{summary}

---

{outputs}

---

請針對每個輸出評分（1-10），並說明理由。評分標準：
- 準確性（是否正確理解新聞）
- 可讀性（是否流暢易懂）
- 價值性（是否提供有用觀點）
- 格式（是否符合要求的結構）

請用 JSON 格式回覆：
{{
  "rankings": [
    {{"model": "A", "score": 8, "reason": "..."}},
    ...
  ],
  "best": "A",
  "summary": "整體評語"
}}"""

# ============================================
# 主流程
# ============================================

def load_filtered_news(date: str) -> list:
    """載入篩選後的新聞"""
    path = Path(f"data/filtered_{date}.json")
    if not path.exists():
        raise FileNotFoundError(f"找不到 {path}，請先執行 pipeline")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sample_news(news_list: list, n: int = 3) -> list:
    """抽樣新聞"""
    # 優先選擇高分新聞
    sorted_news = sorted(news_list, key=lambda x: x.get('score', 0), reverse=True)
    return sorted_news[:n]

def run_experiment(date: str, sample_size: int = 3):
    """執行實驗"""
    print(f"📊 模型品質比較實驗 - {date}")
    print("=" * 50)

    # 1. 載入並抽樣新聞
    all_news = load_filtered_news(date)
    samples = sample_news(all_news, sample_size)
    print(f"📰 抽樣 {len(samples)} 則新聞進行測試\n")

    results = []

    for i, news in enumerate(samples, 1):
        print(f"\n--- 新聞 {i}/{len(samples)}: {news.get('title', 'N/A')[:50]}... ---\n")

        # 2. 每個 CP 模型生成摘要
        outputs = {}
        for name, config in CP_MODELS.items():
            print(f"  🔄 {name}...", end=" ", flush=True)
            prompt = TASK_PROMPT.format(
                title=news.get('title', ''),
                source=news.get('source', ''),
                summary=news.get('summary', ''),
                link=news.get('link', '')
            )
            output = call_model(config, "你是專業的 AI 科技新聞編輯。", prompt)
            outputs[name] = output
            print("✅" if not output.startswith("[ERROR]") else "❌")

        # 3. 頂配模型評審（用第一個可用的）
        outputs_text = "\n\n".join([
            f"【模型 {chr(65+i)}】\n{text}"
            for i, (name, text) in enumerate(outputs.items())
        ])
        model_map = {chr(65+i): name for i, name in enumerate(outputs.keys())}

        judge_prompt = JUDGE_PROMPT.format(
            title=news.get('title', ''),
            summary=news.get('summary', ''),
            outputs=outputs_text
        )

        print(f"\n  ⚖️ 評審中 (gemini-pro-top)...", end=" ", flush=True)
        try:
            judge_result = call_model(
                JUDGE_MODELS["gemini-pro-top"],
                "你是資深 AI 內容品質評審，請客觀公正地評估。",
                judge_prompt
            )
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
            judge_result = "{}"

        results.append({
            "news": news.get('title', ''),
            "outputs": outputs,
            "model_map": model_map,
            "judge_result": judge_result
        })

    # 4. 保存結果
    output_dir = Path("experiments")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"compare_{date}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 實驗完成！結果已保存: {output_path}")
    return results

def print_summary(results: list):
    """輸出摘要"""
    print("\n" + "=" * 50)
    print("📊 實驗結果摘要")
    print("=" * 50)

    for r in results:
        print(f"\n📰 {r['news'][:50]}...")
        print(f"   評審結果: {r['judge_result'][:200]}...")

if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    results = run_experiment(date, sample_size=sample_size)
    print_summary(results)
