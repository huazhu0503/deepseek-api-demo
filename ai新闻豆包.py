import os
import json
import datetime
from dotenv import load_dotenv
import requests
import sys
import io

# 强制 Windows 编码 UTF-8，永不报错
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载 API 密钥
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_today_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def fetch_latest_ai_news():
    # 稳定新闻源
    news_sources = [
        "https://www.jiqizhixin.com/topics/3",
    ]
    
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

            articles = soup.find_all("div", class_="article-item__title")[:10]
            for item in articles:
                title = item.get_text(strip=True)
                raw_news.append({
                    "title": title,
                    "time": "最近发布",
                    "source": "机器之心",
                    "content": title
                })
        except:
            continue

    return raw_news[:8]

def extract_news_with_deepseek(raw_news):
    if not raw_news:
        return "今日暂无最新AI新闻"

    prompt = """
    你是AI新闻编辑，请生成AI行业日报。
    每条新闻包含：标题、来源、发布时间、简要描述。
    只输出标准JSON数组，不要其他任何文字。
    新闻：{}
    """.format(json.dumps(raw_news, ensure_ascii=False))

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
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

    print("正在处理新闻数据...")
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
                f.write(f"【{idx}】{news.get('标题')}\n")
                f.write(f"时间：{news.get('发布时间')}\n")
                f.write(f"来源：{news.get('来源')}\n")
                f.write(f"摘要：{news.get('简要描述')}\n\n")
        else:
            f.write(str(daily_report))
    
    print(f"日报已保存至文件：{filename}")
    print("=" * 60)

if __name__ == "__main__":
    generate_ai_daily_report()