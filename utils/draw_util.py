from typing import List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.util import hash_string, base64_encode


def draw_candlestick_chart(stock_data: pd.DataFrame, ticker: str):
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


def draw_ticker_desc(ticker: str, ticker_desc: str):
    with st.expander(f"**{ticker} 종목 소개**", expanded=True):
        st.write(ticker_desc)


def draw_related_news(related_news: List[dict], expanded: bool = True):
    st.markdown(f"**🗞️ 주요 뉴스**")
    cols = st.columns(3)
    for i, news_item in enumerate(related_news):
        with cols[i]:
            title = news_item["title"]
            if len(title) > 40:
                title = title[:40] + "..."
            with st.expander(f"{title}", expanded=expanded):
                st.markdown(news_item["publishedAt"].split("T")[0])
                source = news_item["source"]
                if news_item.get("publisher"):
                    source += " - " + news_item["publisher"]
                st.markdown(source)
                hashed_url = hash_string(news_item["url"])
                encoded_paragraph = base64_encode(news_item["related_paragraph"])
                st.link_button(
                    label="📎 뉴스 원문 보기",
                    use_container_width=True,
                    url=f"article?id={hashed_url}&related_paragraph={encoded_paragraph}",
                )
