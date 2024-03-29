from datetime import datetime
from typing import List, Optional

import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from services.service_openai import get_streaming_response
from services.service_superbsearch import search_news
from services.service_yfinance import get_stock_price
from utils.screening_util import load_tickers_dict
from utils.streamlit_util import (
    draw_horizontal_news,
    read_stream,
)

st.set_page_config(layout="centered")
st.title("Ask Questions")
tickers_dict, tickers_desc_dict = load_tickers_dict()

instruct_by_screening = {
    "": "",
    "1_1": "The stock has recently seen increased volume and a long white candlestick, which shows that investors are buying in and that the buyers are confident.",
    "1_2": "The stock has recently seen increased volume and a long black candlestick, which shows that investors are joining the sell-off and the confidence of the hawks",
    "2_1": "The stock recently broke above its range, signaling the start of a new uptrend. It's a sign of new investors coming in and psychological resistance being overcome.",
    "2_2": "The stock recently broke below its range, signaling the start of a new downtrend. It signals an outflow of new investors.",
    "3_1": "This stock is showing smash gains. A stock that was falling closes above the previous day's high, suggesting a possible reversal.",
    "3_2": "This stock is showing a smash downtrend. A stock that was rising closes below the previous day's low, suggesting a possible pullback.",
    "4_1": "This stock shows a sideways movement after a pullback. This suggests price stabilization, weakening selling pressure, and a possible trend reversal.",
    "4_2": "This stock shows a recent price increase followed by sideways movement. This suggests that the price is stabilizing, buying interest is weakening, and a trend reversal is possible.",
    "5_1": "The stock is nearing its 3-month support level, which, if held, would signal a bounce in the stock.",
    "5_2": "The stock's price is near its 3-month support level, which is a sign that the stock is headed lower.",
}

if "related_paragraph" not in st.session_state:
    st.session_state.related_paragraph = ""


@st.cache_data
def load_price(ticker: str) -> pd.DataFrame:
    price_df = get_stock_price(ticker)
    return price_df


ticker = st.query_params.get("ticker")
screening = st.query_params.get("screening", "")
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


def get_instruct(screening: str, ticker: str):
    instruct = f"""
You need to analyze the factors that caused the recent stock price movements of {tickers_dict[ticker]} ({ticker}).
{instruct_by_screening[screening]}
Refer to news articles to explain the causes of recent stock price movements.
Don't just say the stock price changes, dig deeper into what caused it to change.
Zacks Rank is not reliable and never be used as a guide.
        """
    return instruct


def get_news_paragraph(news: List[dict]) -> str:
    news_text = ""
    for i, content in enumerate(news):
        news_text += f"""
title: {content["title"]}  
url: {content["url"]}  
summary: {content["summary"]}  
related_paragraph: {content["relatedParagraph"]}  
    """
    return news_text


def generate_news_based_answer_prompt(
    screening: str,
    news: List[dict],
    ticker: Optional[str] = None,
) -> str:
    instruct = get_instruct(screening, ticker)
    news_text = get_news_paragraph(news)
    prompt = f"""
today: {datetime.now().strftime("%Y-%m-%d")}  
{instruct}
---
{news_text}
---
You must provide 3 key points using bullet points with following format:
- **<point>**: <content> 
Don't use title.
""".strip()
    return prompt


def get_news_search_query(ticker: str, screening: str) -> str:
    return f"""
Recent news about {ticker} ({tickers_dict[ticker]}).
    """.strip()


def generate_news_based_answer(
    screening: str, ticker: str, news_items: List[dict]
) -> str:
    prompt = generate_news_based_answer_prompt(
        screening=screening,
        news=news_items,
        ticker=ticker,
    )
    messages = [
        {"role": "system", "content": "You are a professional securities analyst."},
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
    xaxis_rangeslider_visible=False,
    margin=dict(t=50, b=30),
    height=300,
)
st.plotly_chart(candlestick_chart, use_container_width=True)
ticker_desc = tickers_desc_dict.get(ticker)
if ticker_desc:
    with st.expander(f"**{ticker} 종목 소개**: {ticker_desc[:50]}..."):
        st.write(ticker_desc)
query = get_news_search_query(ticker, screening)
results = search_news(query)
items = results.get("result")
if not items:
    st.error("관련 뉴스가 없습니다.")
    st.stop()
news_items = results["result"]
response = generate_news_based_answer(screening, ticker, news_items)
summary = read_stream(response)
draw_horizontal_news(news_items)
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
