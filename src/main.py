# main.py

from database import get_all_sentences
from detect_phising import detect_phishing
import json

# 통화 데이터를 가져옴
phone_calls = get_all_sentences()

# 결과 저장을 위한 리스트
phishing_analysis_results = []

# 각 통화 건에 대해 누적해서 피싱 분석 수행
for call in phone_calls:
    phone_number = call[0][0]  # 전화번호는 동일하므로 첫 번째 데이터를 사용
    accumulated_dialogue = ""

    # 누적하여 대화를 결합하고 매번 피싱 분석
    for _, sentence in call:
        accumulated_dialogue += sentence + " "

        # 피싱 분석 함수 호출
        result = detect_phishing(accumulated_dialogue.strip())

        # 분석 결과 저장
        analysis_result = {
            "phone_number": phone_number,
            "dialogue": accumulated_dialogue.strip(),
            "위험도": result['위험도'],
            "주의": result['주의'],
            "긴급": result['긴급']
        }
        phishing_analysis_results.append(analysis_result)

# 결과 출력
# for result in phishing_analysis_results:
#     print(json.dumps(result, ensure_ascii=False, indent=4))

# 결과를 json 파일로 저장 (선택적)
with open('phishing_analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(phishing_analysis_results, f, ensure_ascii=False, indent=4)
