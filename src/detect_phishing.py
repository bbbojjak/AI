# detect_phising.py

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
import json
from config import setup_logging

# 로깅 설정
setup_logging()

# Ollama를 사용하여 Gemma2 모델 초기화
model = Ollama(model="gemma2:latest")

# 템플릿 문자열 정의
template_string = """
작업: 다음 대화 내용을 분석하여 피싱 위험정도의 퍼센트를 판단하고, 주의, 긴급의 여부를 반환해라.

위험도 : 그 퍼센트 나타내라
주의 : 퍼센트가 40%이상이고 70%미만이면 True, 아니면 False
긴급 : 퍼센트가 70%이상이면 같으면 True, 아니면 False

대화 내용: {text}

{format_instructions}
"""

# 출력 결과의 output format
response_schemas = [
    ResponseSchema(name="위험도", description="그 퍼센트 나타내라"),
    ResponseSchema(name="주의", description="퍼센트가 40%이상이고 80%미만이면 True, 아니면 False"),
    ResponseSchema(name="긴급", description="퍼센트가 70%이상이면 같으면 True, 아니면 False"),
]

# output parser 지정
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

# ChatPromptTemplate 정의
prompt_template = PromptTemplate.from_template(template_string)

# 피싱 분석 함수 정의
def detect_phishing(dialogue_content):
    # 템플릿 프롬프트 완성
    formatted_prompt = prompt_template.format(text=dialogue_content, format_instructions=format_instructions)

    # Gemma2 모델을 통해 분석 요청
    customer_response = model.invoke(formatted_prompt)

    # 응답을 딕셔너리 형태로 변환
    output_dict = output_parser.parse(customer_response)

    # hallucination 이슈 해결
    percent = int(output_dict['위험도'].strip('%'))

    # 위험도가 70% 이상이면 긴급을 True로 설정
    if percent >= 70:
        output_dict['긴급'] = 'True'
    
    # 긴급이 True이면 주의 설정을 False로 변경
    if output_dict['긴급'] == 'True':
        output_dict['주의'] = 'False'

    return output_dict
