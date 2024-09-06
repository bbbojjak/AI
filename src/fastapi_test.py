import os
import whisper
from fastapi import FastAPI, File, UploadFile
from detect_phishing import detect_phishing
from pydantic import BaseModel
from typing import Dict, Union  # Union 추가
import shutil
import time

# FastAPI 인스턴스 생성
app = FastAPI()

# Whisper 모델 로드 (한 번만 로드)
model = whisper.load_model("base")

# Pydantic 모델 정의
class PhishingResult(BaseModel):
    transcribed_text: str
    phishing_result: Dict[str, Union[str, int]]  # 위험도는 int 또는 str로 가능하도록 Union 사용
    timing: Dict[str, float]

    class Config:
        schema_extra = {
            "example": {
                "transcribed_text": "안녕하세요, 고객님. 저는 OO은행의 직원입니다.",
                "phishing_result": {
                    "위험도": 85,  # 정수형
                    "판단기준": "공식 기관을 사칭하며 민감한 정보(계좌 정보) 요청은 일반적인 피싱 수법.",
                    "주의": "False",
                    "긴급": "True"
                },
                "timing": {
                    "transcription_time": 5.24,
                    "phishing_time": 1.35,
                    "total_time": 6.59
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

    # 시간을 측정하기 위한 시작 시간 기록
    start_time = time.time()

    # Whisper를 사용하여 음성 파일을 텍스트로 변환
    transcription_result = model.transcribe(file_path)
    transcription_time = time.time()

    # 변환된 텍스트
    transcribed_text = transcription_result['text']
    print(f"Transcribed text: {transcribed_text}")

    # 피싱 탐지 수행
    phishing_result = detect_phishing(transcribed_text)
    phishing_time = time.time()

    # 각각의 작업에 걸린 시간 출력
    print(f"텍스트 변환 시간: {transcription_time - start_time:.2f}초")
    print(f"피싱 탐지 시간: {phishing_time - transcription_time:.2f}초")
    print(f"총 작업 시간: {phishing_time - start_time:.2f}초")

    # 결과 반환
    return {
        "transcribed_text": transcribed_text,
        "phishing_result": phishing_result,
        "timing": {
            "transcription_time": transcription_time - start_time,
            "phishing_time": phishing_time - transcription_time,
            "total_time": phishing_time - start_time
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_test:app", host="0.0.0.0", port=8000, reload=True)
