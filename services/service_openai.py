from typing import List

import openai
import streamlit as st

from services.util import parse_first_json, EnumPrimaryIntent

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
        model="gpt-4-1106-preview",
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
                model="gpt-4-1106-preview",
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
                model="gpt-4-1106-preview",
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

