from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env

print("当前工作目录:", os.getcwd())
print(".env 文件路径:", os.path.abspath(".env"))
print("读取到的 DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))