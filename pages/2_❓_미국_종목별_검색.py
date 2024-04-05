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

st.set_page_config(layout="wide")
st.markdown(
    """
<style>
[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 10rem 5rem 10rem;
}
</style>
""",
    unsafe_allow_html=True,
)
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

col1, col2 = st.columns([0.7, 0.3])
stock_data = container.yahoo_finance_service().get_stock_price(ticker)
with col1:
    draw_candlestick_chart(stock_data, ticker)
ticker_desc = container.yahoo_finance_service().get_ticker_description(ticker)
with col2:
    draw_ticker_desc(ticker, ticker_desc)
related_news = container.search_service().search_related_news(ticker, screening)
if not related_news:
    st.error("관련 뉴스가 없습니다.")
    st.stop()
draw_related_news(related_news)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**GPT 4 의견**")
    prompt = generate_news_based_answer_prompt(
        screening=screening,
        related_news=related_news,
        ticker=ticker,
    )
    openai_messages = [
        {"role": "system", "content": "You are a professional securities analyst."},
        {"role": "user", "content": prompt},
    ]
    with st.spinner("답변 생성 중..."):
        streaming_response = container.openai_service().get_streaming_response(
            openai_messages, model="gpt-4-0125-preview"
        )
    generated_answer = read_stream(streaming_response)
    summary = read_stream(streaming_response)
with col2:
    st.markdown("**claude 3 의견**")
    anthropic_messages = [
        {"role": "user", "content": prompt},
    ]
    container.anthropic_service().generate_streaming_response(
        anthropic_messages, model="claude-3-sonnet-20240229"
    )
