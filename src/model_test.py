import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from detect_phishing import detect_phishing  # 피싱 탐지 함수

# 엑셀 파일을 읽음
data_file_path = 'data/성능평가_데이터.xlsx'
df = pd.read_excel(data_file_path)

# 실제 값 (spam, ham)
actual_labels = df['유형']

# 예측 값 리스트를 초기화
predicted_labels = []

# 각 텍스트에 대해 피싱 탐지 모델을 사용하여 예측
for text in df['텍스트']:
    # detect_phishing 함수로 위험도 계산
    result = detect_phishing(text)
    
    # 위험도가 70% 이상이면 spam으로 예측
    if isinstance(result['위험도'], str):
        percent = int(result['위험도'].strip('%'))  # 문자열이면 % 제거 후 변환
    else:
        percent = int(result['위험도'])  # 이미 정수라면 바로 변환

    if percent >= 70:
        predicted_labels.append('spam')
    else:
        predicted_labels.append('ham')


## 성능 평가
accuracy = accuracy_score(actual_labels, predicted_labels)

# 다중 클래스 문제이므로 average='macro' 또는 'weighted'로 설정
precision = precision_score(actual_labels, predicted_labels, average='weighted')
recall = recall_score(actual_labels, predicted_labels, average='weighted')
f1 = f1_score(actual_labels, predicted_labels, average='weighted')

# 성능 평가 결과를 딕셔너리로 저장
evaluation_results = {
    "Metric": ["Accuracy", "Precision", "Recall", "F1 Score"],
    "Score": [accuracy, precision, recall, f1]
}

# DataFrame으로 변환하여 표로 출력
df_results = pd.DataFrame(evaluation_results)
print(df_results)

# 결과를 CSV로 저장 (선택사항)
df_results.to_csv('performance_evaluation_results.csv', index=False)
