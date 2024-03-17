import pandas as pd
from datetime import datetime
from utils.streamlit_util import news_instruction
from services.service_openai import (
    generate_advanced_analytics,
    generate_conclusion,
    generate_next_questions,
)
import plotly.graph_objs as go

import streamlit as st
from utils.util import load_tickers
from typing import Dict, Tuple, List
from services.service_yfinance import get_stock_price
from services.service_superbsearch import search_news
from services.service_google import translate
from services.service_openai import get_embedding, generate_news_summary
from utils.streamlit_util import (
    draw_horizontal_news,
    draw_next_questions,
    read_stream,
    draw_main_ideas,
    draw_related_report,
)
from services.service_prompt import generate_news_based_answer_prompt
from services.service_openai import get_streaming_response, generate_main_ideas
from services.service_pinecone import search_related_reports

st.set_page_config(layout="centered")
st.title("Ask Questions")


if "related_paragraph" not in st.session_state:
    st.session_state.related_paragraph = ""


@st.cache_data
def load_tickers_dict() -> Tuple[Dict[str, str], Dict[str, str]]:
    tickers_dict, tickers_desc_dict = load_tickers()
    return tickers_dict, tickers_desc_dict


@st.cache_data
def load_price(ticker: str) -> pd.DataFrame:
    price_df = get_stock_price(ticker)
    return price_df


ticker = st.query_params.get("ticker")
tickers_dict, tickers_desc_dict = load_tickers_dict()

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


def generate_news_based_answer(
    ticker: str, eng_question: str, news_items: List[dict]
) -> str:
    prompt = generate_news_based_answer_prompt(
        news_instruction,
        eng_question,
        news_items,
        ticker=ticker,
        ticker_name=tickers_dict[ticker],
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]
    streaming_response = get_streaming_response(messages)
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

stock_data = load_price(ticker)
candlestick_chart = go.Figure(
    data=[
        go.Candlestick(
            x=stock_data.index,
            open=stock_data["Open"],
            high=stock_data["High"],
            low=stock_data["Low"],
            close=stock_data["Close"],
        )
    ]
)
candlestick_chart.update_layout(
    title={"text": f"선택한 종목: {ticker}", "font_size": 24},
    xaxis_rangeslider_visible=True,
    margin=dict(t=50, b=30),
    height=300,
)
st.plotly_chart(candlestick_chart, use_container_width=True)
ticker_desc = tickers_desc_dict.get(ticker)
if ticker_desc:
    with st.expander(f"**{ticker} 종목 소개**: {ticker_desc[:80]}..."):
        st.write(ticker_desc)
query = f"What happend to the stock price of {tickers_dict[ticker]}({ticker})"
results = search_news(query)
items = results["result"]
news_items = results["result"]
draw_horizontal_news(news_items)
response = generate_news_summary(ticker, tickers_dict[ticker], news_items)
summary = read_stream(response)
with st.form("form"):
    system_message = "당신은 전문 증권 애널리스트입니다."
    question = st.text_input(
        "질문", label_visibility="collapsed", placeholder="질문을 입력해주세요"
    )
    submit = st.form_submit_button(label="제출")


if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()
    eng_question = translate([question])[0]
    query = f"""
selected_ticker: {ticker} ({tickers_dict[ticker]})
question: {eng_question}
""".strip()
    question_related_news = search_news(query)
    if question_related_news:
        draw_horizontal_news(question_related_news["result"])
    generated_answer = generate_news_based_answer(ticker, eng_question, news_items)

    # 핵심 아이디어 3개 추출
    with st.spinner("핵심 아이디어 정리 중..."):
        main_ideas = generate_main_ideas(question, generated_answer)
        eng_main_ideas = translate(main_ideas)
    draw_main_ideas(main_ideas)

    # 핵심 아이디어에 대한 애널리틱스 리포트 검색
    title_main_idea_list = [
        f"question: {eng_question}  \nmain idea: {x}" for x in eng_main_ideas
    ]
    title_main_idea_embeddings = get_embedding(title_main_idea_list)
    visited_report = set()
    for i, (title_main_idea, title_main_idea_embedding) in enumerate(
        zip(title_main_idea_list, title_main_idea_embeddings)
    ):
        related_reports = search_related_reports(title_main_idea_embedding)
        selected_report = None
        for related_report in related_reports:
            report_id = related_report["id"].split("_")[0]
            if report_id in visited_report:
                continue
            visited_report.add(report_id)
            selected_report = [related_report]
            break
        if not selected_report:
            continue
        draw_related_report(i + 1, selected_report, expanded=False)
        streaming_response = generate_advanced_analytics(
            title_main_idea, selected_report
        )
        report_based_answer = read_stream(streaming_response)
    with st.spinner("종합 정리 중..."):
        streaming_response = generate_conclusion(question, generated_answer)
    st.markdown("**결론**")
    conclusion = read_stream(streaming_response)
    with st.spinner("다음에 물어보면 좋을 질문들..."):
        next_questions = generate_next_questions(question, generated_answer)
    draw_next_questions(next_questions)
