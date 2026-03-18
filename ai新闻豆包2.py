import os
import json
import datetime
from dotenv import load_dotenv
import requests

# 修复 Windows 编码问题
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def fetch_latest_ai_news():
    news_sources = [
        "https://www.jiqizhixin.com/topics/3",
    ]
    
    today = get_today_date()
    raw_news = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for url in news_sources:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = "utf-8"
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            articles = soup.find_all("article")[:10]
            for article in articles:
                title = article.find("h2") or article.find("h3")
                time_elem = article.find("time")
                source = url.split("//")[1].split("/")[0]
                
                if title and time_elem:
                    news_time = time_elem.get_text(strip=True)
                    if today in news_time:
                        raw_news.append({
                            "title": title.get_text(strip=True),
                            "time": news_time,
                            "source": source,
                            "content": article.get_text(strip=True)[:500]
                        })
        except Exception as e:
            print(f"抓取失败：{str(e)}")
    
    return raw_news

def extract_news_with_deepseek(raw_news):
    if not raw_news:
        return "今日暂无最新AI新闻"

    prompt = f"""
    你是AI新闻编辑，请生成AI行业日报。
    每条新闻必须包含：标题、来源、发布时间、简要描述（100字内）。
    只输出标准JSON数组，不要其他任何文字。
    日期：{get_today_date()}
    新闻：{json.dumps(raw_news, ensure_ascii=False)}
    """

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        return f"API调用失败：{str(e)}"

def generate_ai_daily_report():
    print("=" * 60)
    print(f"AI 行业日报 - {get_today_date()}")
    print("=" * 60)

    print("正在抓取最新AI新闻...")
    raw_news = fetch_latest_ai_news()

    print("正在通过DeepSeek处理新闻数据...")
    daily_report = extract_news_with_deepseek(raw_news)

    print("\n日报生成完成：\n")
    if isinstance(daily_report, list):
        for idx, news in enumerate(daily_report, 1):
            print(f"【{idx}】{news.get('标题', '无标题')}")
            print(f"时间：{news.get('发布时间', '无时间')}")
            print(f"来源：{news.get('来源', '无来源')}")
            print(f"摘要：{news.get('简要描述', '无描述')}\n")
    else:
        print(daily_report)

    filename = f"AI日报_{get_today_date()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"AI 行业日报 - {get_today_date()}\n")
        f.write("=" * 60 + "\n")
        if isinstance(daily_report, list):
            for idx, news in enumerate(daily_report, 1):
                f.write(f"【{idx}】{news.get('标题', '无标题')}\n")
                f.write(f"时间：{news.get('发布时间', '无时间')}\n")
                f.write(f"来源：{news.get('来源', '无来源')}\n")
                f.write(f"摘要：{news.get('简要描述', '无描述')}\n\n")
        else:
            f.write(str(daily_report))
    
    print(f"日报已保存至文件：{filename}")
    print("=" * 60)

if __name__ == "__main__":
    generate_ai_daily_report()