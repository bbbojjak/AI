import logging
from dotenv import load_dotenv
import openai
import json
from config import setup_logging
import os
from openai import OpenAI


# 로깅 설정
setup_logging()

# OpenAI API 키 설정
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')
# 템플릿 문자열 정의
template_string = """
작업: 다음 대화 내용을 분석하여 피싱 위험정도의 퍼센트를 판단하고, 그렇게 판단한 이유를 반환해라.

위험도 : 그 퍼센트 나타내라
판단기준: 그렇게 판단한 이유를 한줄로 요약해라.

대화 내용: {text}
"""


# 템플릿 문자열을 대화 내용으로 완성
dialogue_content = '''네. 고객님 00저축은행 상담원 100입니다. 무엇을 도와드릴까요?
                    문자내용대로 정말로 2.5%로 대출이 가능한거에요?
                    네 코로나19로 어려움에 빠져 있는 국민들을 위한 정부특별지원상품이라서 간단한 대출조건만 갖추면 가능합니다. 지금 다른 은행에서 대출받으신 거 있으세요?
                    신한은행에서 5천만원 대출한게 있습니다.
                    네, 그럼 먼저 고객님 신용등급 조회를 해야 하니 지금 보내드리는 문자에 있는 링크를 누르셔서 앱을 설치하세요.
                    조회해보니 고객님의 XX은행 기존대출건을 일부 상환하셔야합니다. 그래야 신용등급이 상향되서 연이율 2.5%로 최대 9천만원까지 대출이 가능하세요. 신한은행에 전화하셔서 상환절차부터 진행하시면 됩니다.
                    ''' 
prompt = template_string.format(text=dialogue_content)

try:
    client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key = openai.api_key,
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

    # 위험도 값이 문자열인지 확인
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
    
    print(output_dict)
    
except Exception as e:
    # 오류가 발생할 경우 로깅
    logging.error(f"OpenAI API 호출 중 오류 발생: {e}")