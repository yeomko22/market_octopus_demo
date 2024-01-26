from typing import List, Union
import json

import openai
import streamlit as st

from services.util import parse_first_json, EnumPrimaryIntent, EnumMarketStrategyIntent, EnumIndustryStockIntent

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_embedding(text_list: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
       input=text_list,
       model="text-embedding-ada-002"
    )
    return [x.embedding for x in response.data]


def paginated_get_embedding(text_list: List[str], page_size=5) -> List[List[float]]:
    result = []
    for i in range(0, len(text_list), page_size):
        queries = text_list[i:i+page_size]
        embedding_result = get_embedding(queries)
        result.extend(embedding_result)
    return result


def get_streaming_response(messages: List[dict]):
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        timeout=10,
        stream=True,
    )
    return response


def classify_primary_intent(question: str) -> EnumPrimaryIntent:
    system_message = """
당신은 전문 증권 애널리스트입니다.
주요 카테고리로 유저의 질문의 의도를 분류하세요.
결과는 "category"를 키로 갖는 JSON 포맷으로 리턴하세요.

주요 카테고리: 정책, 경제, 주식시장 전략, 채권시장, 산업 및 종목, 대체자산, 기타 
    """.strip()
    intent = EnumPrimaryIntent.ECONOMY
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ],
                response_format={"type": "json_object"},
            )
            intent_json = parse_first_json(response.choices[0].message.content)
            category = intent_json["category"]
            for intent in EnumPrimaryIntent:
                if intent.value == category:
                    return intent
        except Exception as e:
            print("RETRY INTENT CLASSIFICATION", e)
            continue
    return intent


def classify_secondary_intent(primary_intent: EnumPrimaryIntent, question: str) \
        -> Union[EnumMarketStrategyIntent, EnumIndustryStockIntent]:
    secondary_intent_list = []
    if primary_intent == EnumPrimaryIntent.MARKET_STRATEGY:
        secondary_intent_list = [x for x in EnumMarketStrategyIntent]
    elif primary_intent == EnumPrimaryIntent.INDUSTRY_STOCK:
        secondary_intent_list = [x for x in EnumIndustryStockIntent]
    system_message = f"""
당신은 전문 증권 애널리스트입니다.
유저의 질문과 질문의 주 카테고리가 주어집니다.
세부 카테고리로 유저의 질문의 의도를 분류하세요.
결과는 "category"를 키로 갖는 JSON 포맷으로 리턴하세요.

주요 카테고리: {primary_intent.value} 
세부 카테고리: {[x.value for x in secondary_intent_list]}
    """.strip()
    intent = None
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ],
                response_format={"type": "json_object"},
            )
            intent_json = parse_first_json(response.choices[0].message.content)
            category = intent_json["category"]
            for intent in secondary_intent_list:
                if intent.value == category:
                    return intent
        except Exception as e:
            print("RETRY INTENT CLASSIFICATION", e)
            continue
    return intent


def classify_intent(question: str):
    primary_intent = classify_primary_intent(question)
    secondary_intent = None
    if primary_intent == EnumPrimaryIntent.MARKET_STRATEGY or primary_intent == EnumPrimaryIntent.INDUSTRY_STOCK:
        secondary_intent = classify_secondary_intent(primary_intent, question)
    return primary_intent, secondary_intent


def extract_query(question: str) -> str:
    system_message = """
당신은 전문 증권 애널리스트입니다.
유저의 질문에 답변하기 위해서 웹 검색을 사용하고자 합니다.
검색에 필요한 쿼리를 추출하세요.
쿼리는 반드시 한국어여야 합니다.
결과는 "query"를 키로 갖는 JSON 포맷으로 리턴하세요.
    """.strip()
    query = ""
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ],
                response_format={"type": "json_object"},
            )
            query_json = parse_first_json(response.choices[0].message.content)
            query = query_json["query"]
            break
        except Exception as e:
            print("RETRY INTENT CLASSIFICATION", e)
            continue
    return query


def generate_next_questions(question: str, answer: str) -> List[str]:
    system_message = f"""
당신은 전문 증권 애널리스트입니다.
유저의 질문과 그에 대한 답변이 주어집니다.
이를 참고해서 이어서 물어볼 질문을 3개 생성하세요. 
반드시 질문들은 20단어 이내로 간결하게 생성하세요.
결과는 "questions"를 key로 가지고, 이어서 물어볼 질문들을 담은 list를 value로 갖는 JSON 포맷으로 리턴하세요.
---
질문: {question}
답변: {answer}
---
        """.strip()
    questions = []
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ],
                response_format={"type": "json_object"},
            )
            response_json = json.loads(response.choices[0].message.content)
            questions = response_json["questions"]
            if not isinstance(questions, list):
                raise ValueError("questions is not list")
            break
        except Exception as e:
            print("RETRY GENERATE NEXT QUESTION", e)
            continue
    return questions
