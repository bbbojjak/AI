import whisper
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from detect_phishing import detect_phishing  # 피싱 탐지 함수
import time  # 시간 측정 모듈

# Whisper 모델 로드
model = whisper.load_model("base")

# 시간을 측정하기 위한 시작 시간 기록
start_time = time.time()

# m4a 파일을 텍스트로 변환
result = model.transcribe("src/통화 녹음 아빠_220305_004438.m4a")

# 텍스트 변환이 완료된 후의 시간 기록
transcription_time = time.time()

# 변환된 텍스트 출력 (필요시)
#print(result['text'])

# 피싱 탐지 수행
result = detect_phishing(result['text'])

# 피싱 탐지 완료 후의 시간 기록
end_time = time.time()

# 각각의 작업에 걸린 시간 출력
print(f"텍스트 변환 시간: {transcription_time - start_time:.2f}초")
print(f"피싱 탐지 시간: {end_time - transcription_time:.2f}초")
print(f"총 작업 시간: {end_time - start_time:.2f}초")

# 결과 출력
print(result)