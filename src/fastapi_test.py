from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    content: str

@app.post("/send_message")
async def send_message(message: Message):
    return {"status": "Message received", "message": message.content}

@app.get("/get_messages")
async def get_messages():
    return {"messages": ["Hello!", "How are you?"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # 0.0.0.0을 사용하면 모든 네트워크 인터페이스에서 접근 가능합니다.
    # 주의: 개발 환경에서만 사용하세요. 프로덕션 환경에서는 보안 설정을 신중히 고려해야 합니다.
    