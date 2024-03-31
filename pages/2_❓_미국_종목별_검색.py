from datetime import datetime
from typing import List, Optional

import streamlit as st

from container import Container
from utils.draw_util import draw_candlestick_chart, draw_ticker_desc
from utils.draw_util import draw_related_news
from utils.screening_util import load_tickers_dict
from utils.streamlit_util import (
    read_stream,
)

container = Container()

st.set_page_config(layout="centered")
st.title("Ask Questions")
tickers_dict, tickers_desc_dict = load_tickers_dict()


ticker = st.query_params.get("ticker")
screening = st.query_params.get("screening", "")

st.markdown("궁금한 종목의 티커를 선택해주세요.")
not_select = "not select"
tickers = list(tickers_dict.keys())
ticker_options = [f"{ticker}({name})" for ticker, name in tickers_dict.items()]
cur_index = 0
if ticker and ticker != not_select:
    cur_index = tickers.index(ticker) + 1


def update_ticker():
    selected_ticker_option = st.session_state.select_ticker
    ticker = selected_ticker_option.split("(")[0]
    st.query_params.update(ticker=ticker)


def get_news_paragraph(news: List[dict]) -> str:
    news_text = ""
    for i, content in enumerate(news):
        news_text += f"""
title: {content["title"]}  
url: {content["url"]}  
summary: {content["summary"]}  
related_paragraph: {content["related_paragraph"]}  
    """
    return news_text


def generate_news_based_answer_prompt(
    screening: str,
    related_news: List[dict],
    ticker: Optional[str] = None,
) -> str:
    screening_desc = container.search_service().get_screening_desc(screening)
    news_text = get_news_paragraph(related_news)
    prompt = f"""
today: {datetime.now().strftime("%Y-%m-%d")}
You need to analyze the factors that caused the recent stock price movements of {tickers_dict[ticker]} ({ticker}).
{screening_desc}
Refer to news articles to explain the causes of recent stock price movements.
Don't just say the stock price changes, dig deeper into what caused it to change.
---
{news_text}
---
You must provide 3 key points using bullet points with following format:
- **<point>**: <content>
Don't use title.
You must answer in Korean.
""".strip()
    return prompt


def generate_news_based_answer(
    screening: str, ticker: str, news_items: List[dict]
) -> str:
    prompt = generate_news_based_answer_prompt(
        screening=screening,
        related_news=news_items,
        ticker=ticker,
    )
    messages = [
        {"role": "system", "content": "You are a professional securities analyst."},
        {"role": "user", "content": prompt},
    ]
    streaming_response = container.openai_service().get_streaming_response(
        messages, model="gpt-4-0125-preview"
    )
    generated_answer = read_stream(streaming_response)
    return generated_answer


selected_ticker = st.selectbox(
    label="ticker",
    label_visibility="collapsed",
    options=[not_select] + ticker_options,
    index=cur_index,
    on_change=update_ticker,
    key="select_ticker",
)
if not ticker or ticker == not_select:
    st.error("티커를 선택해주세요.")
    st.stop()

stock_data = container.yahoo_finance_service().get_stock_price(ticker)
draw_candlestick_chart(stock_data, ticker)
ticker_desc = container.yahoo_finance_service().get_ticker_description(ticker)
draw_ticker_desc(ticker, ticker_desc)
related_news = container.search_service().search_related_news(ticker, screening)
if not related_news:
    st.error("관련 뉴스가 없습니다.")
    st.stop()
streaming_response = generate_news_based_answer(
    screening=screening,
    ticker=ticker,
    news_items=related_news,
)
summary = read_stream(streaming_response)
draw_related_news(related_news)
# with st.form("form"):
#     system_message = "당신은 전문 증권 애널리스트입니다."
#     question = st.text_input("전문가에게 질문해보세요", placeholder="질문을 입력해주세요")
#     submit = st.form_submit_button(label="제출")
#
#
# if submit:
#     if not question:
#         st.error("질문을 입력해주세요.")
#         st.stop()
#     eng_question = translate([question])[0]
#     query = f"""
# selected_ticker: {ticker} ({tickers_dict[ticker]})
# question: {eng_question}
# """.strip()
#     question_related_news = search_news(query)
#     if question_related_news:
#         draw_horizontal_news(question_related_news["result"])
#     generated_answer = generate_news_based_answer(ticker, eng_question, news_items)
#
#     # 핵심 아이디어 3개 추출
#     with st.spinner("핵심 아이디어 정리 중..."):
#         main_ideas = generate_main_ideas(question, generated_answer)
#         eng_main_ideas = translate(main_ideas)
#     draw_main_ideas(main_ideas)
#
#     # 핵심 아이디어에 대한 애널리틱스 리포트 검색
#     title_main_idea_list = [
#         f"question: {eng_question}  \nmain idea: {x}" for x in eng_main_ideas
#     ]
#     title_main_idea_embeddings = get_embedding(title_main_idea_list)
#     visited_report = set()
#     for i, (title_main_idea, title_main_idea_embedding) in enumerate(
#         zip(title_main_idea_list, title_main_idea_embeddings)
#     ):
#         related_reports = search_related_reports(title_main_idea_embedding)
#         selected_report = None
#         for related_report in related_reports:
#             report_id = related_report["id"].split("_")[0]
#             if report_id in visited_report:
#                 continue
#             visited_report.add(report_id)
#             selected_report = [related_report]
#             break
#         if not selected_report:
#             continue
#         draw_related_report(i + 1, selected_report, expanded=False)
#         streaming_response = generate_advanced_analytics(
#             title_main_idea, selected_report
#         )
#         report_based_answer = read_stream(streaming_response)
#     with st.spinner("종합 정리 중..."):
#         streaming_response = generate_conclusion(question, generated_answer)
#     st.markdown("**결론**")
#     conclusion = read_stream(streaming_response)
#     with st.spinner("다음에 물어보면 좋을 질문들..."):
#         next_questions = generate_next_questions(question, generated_answer)
#     draw_next_questions(next_questions)
