from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from database import get_all_sentences
from detect_phishing import detect_phishing

app = FastAPI()

# Pydantic 모델 정의
class PhishingResult(BaseModel):
    phone_number: str
    dialogue: str
    위험도: int
    판단기준: str
    주의: str
    긴급: str

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "01012345678",
                "dialogue": "안녕하세요, 고객님. 저는 OO은행의 직원입니다. 귀하의 계좌에 이상 거래가 발생했습니다. 보안 강화를 위해 계좌 정보를 확인해야 합니다.",
                "위험도": 85,
                "판단기준": "공식 기관을 사칭하며 민감한 정보(계좌 정보) 요청은 일반적인 피싱 수법.",
                "주의": "False",
                "긴급": "True"
            }
        }

# Root 엔드포인트 (확인용)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Phishing Detection API!"}

# 피싱 분석 엔드포인트
@app.get("/analyze", response_model=List[PhishingResult])
async def analyze_phishing():
    # 통화 데이터를 가져옴
    phone_calls = get_all_sentences()

    # 전화번호별로 대화를 저장할 딕셔너리
    phone_dialogues = {}

    # 전화번호별 대화를 누적하여 결합
    for call in phone_calls:
        phone_number = call[0][0]  # 전화번호는 동일하므로 첫 번째 데이터를 사용
        accumulated_dialogue = phone_dialogues.get(phone_number, "")

        # 누적하여 대화를 결합
        for _, sentence in call:
            accumulated_dialogue += sentence + " "
        
        phone_dialogues[phone_number] = accumulated_dialogue.strip()

    # 결과 저장을 위한 리스트
    phishing_analysis_results = []

    # 각 전화번호별로 누적된 대화에 대해 한 번만 피싱 분석 수행
    for phone_number, dialogue in phone_dialogues.items():
        # 피싱 분석 함수 호출
        result = detect_phishing(dialogue)

        # 분석 결과 저장
        analysis_result = {
            "phone_number": phone_number,
            "dialogue": dialogue,
            "위험도": result.get("위험도", "N/A"),
            "판단기준": result.get("판단기준", "N/A"),
            "주의": result.get("주의", "N/A"),
            "긴급": result.get("긴급", "N/A")
        }
        phishing_analysis_results.append(analysis_result)

    # results 키 없이 데이터를 바로 반환
    return phishing_analysis_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)
