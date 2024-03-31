import json
from datetime import datetime
from typing import List, Union
from typing import Optional

import openai
import streamlit as st

from utils.intent import (
    EnumPrimaryIntent,
    EnumMarketStrategyIntent,
    EnumIndustryStockIntent,
)

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def get_embedding(text_list: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        input=text_list, model="text-embedding-3-large", dimensions=1024
    )
    return [x.embedding for x in response.data]


def paginated_get_embedding(text_list: List[str], page_size=5) -> List[List[float]]:
    result = []
    for i in range(0, len(text_list), page_size):
        queries = text_list[i : i + page_size]
        embedding_result = get_embedding(queries)
        result.extend(embedding_result)
    return result


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
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
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


def classify_secondary_intent(
    primary_intent: EnumPrimaryIntent, question: str
) -> Union[EnumMarketStrategyIntent, EnumIndustryStockIntent]:
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
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
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
    if (
        primary_intent == EnumPrimaryIntent.STOCK_MARKET_STRATEGY
        or primary_intent == EnumPrimaryIntent.INDUSTRIES_AND_SECTORS
    ):
        secondary_intent = classify_secondary_intent(primary_intent, question)
    return primary_intent, secondary_intent


def extract_query(question: str) -> List[str]:
    system_message = "You are a professional securities analyst.".strip()
    prompt = f"""
    You want to search recent news to answer your users' questions.
    Given today's date and the user's question, generate 3 queries you need for your search.
    Each query must be closely related to the user's question.
    Return the results in JSON format with "queries" as the key.    
    ---
    today: {datetime.now().strftime("%Y-%m-%d")}
    question: {question}
    ---
        """.strip()
    queries = ""
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            query_json = json.loads(response.choices[0].message.content)
            queries = query_json["queries"]
            break
        except Exception as e:
            print("RETRY INTENT CLASSIFICATION", e)
            continue
    return queries


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
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
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


def generate_main_ideas(question: str, answer: str) -> List[str]:
    system_message = f"""
당신은 전문 증권 애널리스트입니다.
유저의 질문과 그에 대해 생성한 AI의 답변이 주어집니다.
AI의 답변에서 핵심 아이디어를 최대 3개 추출하세요.
결과는 "ideas"를 key로 가지고, 핵심 아이디어를 담은 list를 value로 갖는 JSON 포맷으로 리턴하세요.
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
                    {"role": "user", "content": question},
                ],
                response_format={"type": "json_object"},
            )
            response_json = json.loads(response.choices[0].message.content)
            questions = response_json["ideas"]
            if not isinstance(questions, list):
                raise ValueError("ideas is not list")
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
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
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


def generate_analytics_prompt(
    instruct: str, paragraph: str, related_reports: List[dict]
) -> str:
    report_text = ""
    for i, related_report in enumerate(related_reports):
        metadata = related_report["metadata"]
        report_text += f"""
title: {metadata["title"] if "title" in metadata else metadata["filename"]}  
content: {metadata["content"] if "content" in metadata else metadata["eng_text"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
paragraph: {paragraph}  
"""
    if related_reports:
        prompt += f"analytics reports\n{report_text}"
    prompt += "---"
    return prompt.strip()


def generate_advanced_analytics(question_main_idea: str, related_reports: List[dict]):
    analytics_instruct = """
유저의 질문과 이에 대한 답변의 핵심 아이디어가 주어집니다.
이와 관련된 전문 애널리스트 리포트가 주어집니다.
이를 참고해서 더 심화된 내용들을 설명해주세요.
구체적인 수치와 디테일한 내용들을 언급해주세요.
반드시 한국어로 답변하세요.
반드시 한문단 이내로 작성하세요.
""".strip()
    prompt = generate_analytics_prompt(
        analytics_instruct, question_main_idea, related_reports
    )
    messages = [
        {"role": "system", "content": analytics_instruct},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        timeout=10,
        stream=True,
    )
    return response


def generate_conclusion(question: str, generated_answer: str):
    prompt = f"""
유저의 질문과 이에 대해 최신 뉴스와 애널리스트 리포트를 참고해서 생성한 답변이 주어집니다.
이를 참고해서 결론을 작성하세요. 
답변에서 구체적인 종목이나 지표를 언급했다면 포함해주세요.
반드시 한국어로 답변하세요.
반드시 한문단 이내로 간결하게 작성하세요.
---
question: {question}
generated_answer: {generated_answer}
---
""".strip()
    messages = [
        {"role": "system", "content": "당신은 전문 증권 애널리스트입니다."},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        timeout=10,
        stream=True,
    )
    return response


def generate_news_summary(
    ticker: str,
    ticker_name: str,
    news_items: List[dict],
    screening: Optional[str] = None,
):
    news_paragraph = ""
    for news_item in news_items:
        news_paragraph += f"""
title: {news_item["title"]}  
published_at: {news_item["publishedAt"]}  
summary: {news_item["summary"]}  
related_paragraph: {news_item["related_paragraph"]}  
    """

    if screening == "buy":
        instruct = "뉴스를 참고해서 해당 종목의 매수 신호 요인을 분석하세요."
    elif screening == "sell":
        instruct = "뉴스를 참고해서 해당 종목의 매도 신호 요인을 분석하세요."
    else:
        instruct = "뉴스를 참고해서 해당 종목 주가 변동에 대한 요약을 작성하세요."
    prompt = f"""
나스닥 종목 티커와 종목명, 그리고 종목과 관련된 최신 뉴스 3개가 주어집니다.  
{instruct}
반드시 100단어 이내로 작성하세요.  
반드시 한국어로 작성하세요.
불릿 포인트를 사용해서 핵심을 3가지로 정리해주세요.
각 불릿 포인트 별로 소제목을 진하게 표시해주세요.
절대로 뉴스의 출처를 언급하지 마세요.
ex) - **<소제목>**: <본문>
---
선택된 종목: {ticker} ({ticker_name})  
관련 최신 뉴스  
{news_paragraph}
---
""".strip()
    messages = [
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=messages,
        timeout=10,
        stream=True,
    )
    return response
