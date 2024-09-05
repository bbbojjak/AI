# main.py

from database import get_all_sentences
from detect_phising import detect_phishing
import json

# 모든 문장을 가져와서 바이너리 데이터를 UTF-8로 디코딩
decoded_data = [item.decode('utf-8') for item in get_all_sentences()]

# 디코딩된 문장을 하나의 문자열로 결합
combined_dialogue = " ".join([sentence.strip('"') for sentence in decoded_data])

# 피싱 분석 함수 호출
result = detect_phishing(combined_dialogue)

# 결과 출력
print(json.dumps(result, ensure_ascii=False, indent=4))

# 결과를 json 파일로 저장 (선택적)
with open('phishing_analysis_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
