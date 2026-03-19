# ===================== 编码修复（Windows必加）=====================
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# ==================================================================

import os
import json
import datetime
from dotenv import load_dotenv
import requests

# ===================== 配置 =====================
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

WEEK_START = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
WEEK_END = datetime.date.today().strftime("%Y-%m-%d")
REPORT_FILE = f"AI_weekly_report_{WEEK_START}_{WEEK_END}.html"

# ===================== 读取本地txt数据 =====================
def load_local_data():
    try:
        with open("local_data.txt", "r", encoding="utf-8") as f:
            return f.read().replace("\n", "<br>")
    except:
        return "暂无本地团队动态"

# ===================== 获取AI新闻 =====================
def get_ai_news():
    prompt = f"""
    请提供最近一周（{WEEK_START} 至 {WEEK_END}）全球AI行业重要新闻。
    每条新闻必须包含：标题、发布时间、来源、简要描述（100字内）。
    只输出标准JSON数组，不要任何多余文字。
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        res = requests.post(API_URL, headers=headers, json=data, timeout=30)
        res.raise_for_status()
        return json.loads(res.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"API错误：{e}")
        return []

# ===================== 生成精美 HTML 报告 =====================
def generate_html(news, local):
    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 每周动态报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "Microsoft YaHei", Arial, sans-serif;
        }}
        body {{
            background: #f5f7fa;
            padding: 30px 20px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 24px;
            background: #4e83df;
            color: white;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 26px;
            margin-bottom: 8px;
        }}
        .header p {{
            font-size: 15px;
            opacity: 0.95;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .card h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 16px;
            border-left: 5px solid #4e83df;
            padding-left: 12px;
        }}
        .news-item {{
            padding: 16px;
            border-bottom: 1px solid #eee;
            margin-bottom: 12px;
        }}
        .news-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        .news-title {{
            font-size: 17px;
            font-weight: bold;
            color: #2962cc;
            margin-bottom: 8px;
        }}
        .info {{
            font-size: 14px;
            color: #666;
            margin-bottom: 6px;
        }}
        .desc {{
            font-size: 15px;
            color: #444;
            line-height: 1.6;
        }}
        .local-content {{
            font-size: 15px;
            line-height: 1.7;
            color: #333;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #888;
            font-size: 14px;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>📊 AI 行业每周动态报告</h1>
        <p>报告周期：{WEEK_START} ～ {WEEK_END}</p>
        <p>生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="card">
        <h2>🧾 本地团队动态</h2>
        <div class="local-content">{local}</div>
    </div>

    <div class="card">
        <h2>🌍 全球AI行业新闻</h2>
    '''

    if not news:
        html += "<div style='padding:16px;color:#666'>本周暂无新闻</div>"
    else:
        for item in news:
            html += f'''
            <div class="news-item">
                <div class="news-title">{item.get('标题', '无标题')}</div>
                <div class="info">📅 发布时间：{item.get('时间', '未知')}</div>
                <div class="info">🔗 新闻来源：{item.get('来源', '未知')}</div>
                <div class="desc">{item.get('描述', '无描述')}</div>
            </div>
            '''

    html += '''
    </div>
    <div class="footer">
        本报告由自动化脚本生成 | 每周自动更新
    </div>
</body>
</html>
    '''
    return html

# ===================== 保存报告 =====================
def save_report(content):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 精美 HTML 报告已生成：{REPORT_FILE}")

# ===================== 主程序 =====================
def main():
    print("=" * 70)
    print("           📅 每周 AI 动态报告（HTML 美化版）           ")
    print("=" * 70)

    local_data = load_local_data()
    ai_news = get_ai_news()
    html_content = generate_html(ai_news, local_data)
    save_report(html_content)

    print("\n🎉 报告生成完成！双击文件即可打开查看")
    print("=" * 70)

if __name__ == "__main__":
    main()