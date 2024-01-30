from typing import List, Union
from datetime import datetime
import json

import openai
import streamlit as st

from utils.intent import EnumPrimaryIntent, EnumMarketStrategyIntent, EnumIndustryStockIntent

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_embedding(text_list: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        input=text_list,
        model="text-embedding-3-large",
        dimensions=1024
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
You're a professional securities analyst.
Categorize the intent of the user's question into major categories.
Return the results in JSON format with "category" as the key.

Main categories: Policy, Economics, Stock market strategy, Bond market, Industries and sectors, Alternative assets, China, Others
    """.strip()
    intent = EnumPrimaryIntent.ECONOMICS
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
            intent_json = json.loads(response.choices[0].message.content)
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
    if primary_intent == EnumPrimaryIntent.STOCK_MARKET_STRATEGY:
        secondary_intent_list = [x for x in EnumMarketStrategyIntent]
    elif primary_intent == EnumPrimaryIntent.INDUSTRIES_AND_SECTORS:
        secondary_intent_list = [x for x in EnumIndustryStockIntent]
    system_message = f"""
You are a professional securities analyst.
You are given a user's question and its main category.
Use the subcategories to categorize the intent of the user's question.
Return the results in JSON format with "category" as the key.

Main Category: {primary_intent.value} 
Sub Categories: {[x.value for x in secondary_intent_list]}
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
            intent_json = json.loads(response.choices[0].message.content)
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
    if primary_intent == EnumPrimaryIntent.STOCK_MARKET_STRATEGY or primary_intent == EnumPrimaryIntent.INDUSTRIES_AND_SECTORS:
        secondary_intent = classify_secondary_intent(primary_intent, question)
    return primary_intent, secondary_intent


def extract_query(question: str) -> str:
    system_message = "You are a professional securities analyst.".strip()
    prompt = f"""
You want to search recent news to answer your users' questions.
Given today's date and the user's question, extract the queries you need for your search.
Return the results in JSON format with "query" as the key.    
---
today: {datetime.now().strftime("%Y-%m-%d")}
question: {question}
---
    """.strip()
    query = ""
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
            )
            query_json = json.loads(response.choices[0].message.content)
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
반드시 질문들은 30단어 이내로 간결하게 생성하세요.
생성하는 질문들은 유저의 질문과 비슷하면 안됩니다.
답변에서 새로운 종목이 언급되었다면, 그 종목과 관련된 질문을 반드시 포함해주세요.
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
                model="gpt-4-0125-preview",
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


def generate_search_query(question: str) -> List[str]:
    system_message = f"""
You are a professional securities analyst.
You want to use web search to answer a user's question.
Given the user's question and today's date, generate a query to use in a web search.
Return the result in JSON format with "query" as the key.
---
question: {question}
today: {datetime.now().strftime("%Y-%m-%d")}
---
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
            response_json = json.loads(response.choices[0].message.content)
            query = response_json["query"]
            break
        except Exception as e:
            print("RETRY GENERATE NEXT QUESTION", e)
            continue
    return query
