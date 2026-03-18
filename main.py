from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

app = FastAPI(
    title="DeepSeek Text Generation API",
    description="使用 DeepSeek API 的简单文本生成服务",
    version="1.0.0"
)

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 请求体模型
class GenerateRequest(BaseModel):
    prompt: str
    model: str = "deepseek-chat"          # 可改成 "deepseek-coder"
    max_tokens: int = 512
    temperature: float = 0.7

@app.get("/")
async def root():
    return {"message": "DeepSeek API 服务已启动！访问 /docs 查看接口文档"}

@app.post("/generate")
async def generate_text(request: GenerateRequest):
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise HTTPException(status_code=500, detail="API Key 未配置")

    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        text = response.choices[0].message.content.strip()
        return {
            "prompt": request.prompt,
            "generated_text": text,
            "model": request.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API 调用失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)