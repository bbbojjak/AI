import logging
from dotenv import load_dotenv
import openai
import json
import os
from openai import OpenAI
from config import setup_logging

# 로깅 설정
setup_logging()

# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# 템플릿 문자열 정의
template_string = """
작업: 다음 대화 내용을 분석하여 피싱 위험정도의 퍼센트를 판단하고, 그렇게 판단한 이유를 반환해라.

위험도 : 그 퍼센트 나타내라
판단기준: 그렇게 판단한 이유를 한줄로 요약해라.

대화 내용: {text}
"""

def detect_phishing(dialogue_content):
    """
    대화 내용을 GPT API로 분석하여 피싱 위험도를 계산하고, 긴급 및 주의 여부를 반환하는 함수.

    Args:
        dialogue_content (str): 대화 내용

    Returns:
        dict: 위험도, 긴급, 주의 여부를 포함한 결과 딕셔너리
    """
    # 템플릿 문자열을 대화 내용으로 완성
    prompt = template_string.format(text=dialogue_content)

    try:
        client = OpenAI(
            api_key=openai.api_key,
        )

        # OpenAI ChatGPT API를 호출하여 응답 받기
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Response in json format"},
                {"role": "user", "content": prompt}
            ],
            # response_format 지정하기
            response_format = {"type":"json_object"}
        )

        # 응답 메시지를 추출
        customer_response = response.choices[0].message.content

        # JSON 형식으로 파싱
        output_dict = json.loads(customer_response)

        # 위험도 값이 문자열인지 확인하고 숫자로 변환
        if isinstance(output_dict['위험도'], str):
            percent = int(output_dict['위험도'].strip('%'))  # 문자열이면 % 제거 후 변환
        else:
            percent = int(output_dict['위험도'])  # 이미 정수라면 바로 변환

        # 퍼센트에 따라 긴급/주의 설정
        if percent >= 70:
            output_dict['긴급'] = 'True'
            output_dict['주의'] = 'False'
        elif 40 <= percent < 70:
            output_dict['긴급'] = 'False'
            output_dict['주의'] = 'True'
        else:
            output_dict['긴급'] = 'False'
            output_dict['주의'] = 'False'

        return output_dict

    except Exception as e:
        # 오류가 발생할 경우 로깅
        logging.error(f"OpenAI API 호출 중 오류 발생: {e}")
        return None

#print(detect_phishing('안녕하세요, 고객님. 저는 OO은행의 직원입니다.귀하의 계좌에 이상 거래가 발생했습니다.보안 강화를 위해 계좌 정보를 확인해야 합니다.'))