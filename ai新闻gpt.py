from dotenv import load_dotenv
import os
import requests

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取 API 密钥
API_KEY = os.getenv("API_KEY")
print(API_KEY)  # 确保 API 密钥被加载

# 如果没有加载密钥，输出错误信息并退出
if not API_KEY:
    print("API 密钥未加载，程序终止。")
    exit()

# 设置 Deepseek API 的 URL
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 请求 Deepseek Chat Completion API
def fetch_chat_completion(prompt: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",  # 使用 Bearer Token 进行身份验证
        "Content-Type": "application/json"  # 请求体类型为 JSON
    }
    
    data = {
        "model": "gpt-4",  # 选择模型（如果需要，可以根据实际情况修改）
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        print(response.text)  # 打印响应内容
        
        response.raise_for_status()  # 如果请求失败，会抛出异常

        completion_data = response.json()

        # 返回生成的聊天内容
        if 'choices' in completion_data:
            message = completion_data['choices'][0]['message']['content']
            return message
        else:
            return "没有返回聊天内容"

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 调用函数并打印结果
prompt = "请提供最新的 AI 发展状况新闻。"  # 你可以根据需求修改提示内容
result = fetch_chat_completion(prompt)
if result:
    print("AI Chat Completion Result:")
    print(result)  # 打印 API 返回的聊天结果