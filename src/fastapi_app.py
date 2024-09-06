import os
import whisper
from fastapi import FastAPI, File, UploadFile
from detect_phishing import detect_phishing
from pydantic import BaseModel
from typing import Dict, Union
import shutil

# FastAPI 인스턴스 생성
app = FastAPI()

# Whisper 모델 로드 (한 번만 로드)
model = whisper.load_model("base")

# Pydantic 모델 정의
class PhishingResult(BaseModel):
    phishing_result: Dict[str, Union[str, int]]  # 위험도는 int 또는 str로 가능하도록 Union 사용
    
    class Config:
        schema_extra = {
            "example": {
                "phishing_result": {
                    "위험도": 85,
                    "판단기준": "공식 기관을 사칭하며 민감한 정보(계좌 정보) 요청은 일반적인 피싱 수법.",
                    "주의": "False",
                    "긴급": "True"
                }
            }
        }

# Root 엔드포인트 (확인용)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Phishing Detection API!"}

# 통화 녹음 파일을 받아서 텍스트로 변환하고 피싱 탐지 결과 반환
@app.post("/analyze", response_model=PhishingResult)
async def analyze_call_recording(file: UploadFile = File(...)):
    # 파일 저장
    file_path = f"data/{file.filename}"
    os.makedirs("data", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Whisper를 사용하여 음성 파일을 텍스트로 변환
    transcription_result = model.transcribe(file_path)

    # 변환된 텍스트
    transcribed_text = transcription_result['text']

    # 피싱 탐지 수행
    phishing_result = detect_phishing(transcribed_text)

    # 반환된 phishing_result 구조가 예상된 형식인지 확인
    if isinstance(phishing_result.get('위험도'), str):
        try:
            phishing_result['위험도'] = int(phishing_result['위험도'].strip('%'))  # 문자열이면 % 제거 후 변환
        except ValueError:
            pass  # 변환 실패 시 원본 유지

    # 결과 반환
    return {
        "phishing_result": phishing_result,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
