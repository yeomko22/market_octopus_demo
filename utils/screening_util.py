import csv
from typing import List, Dict, Tuple

import streamlit as st

from utils.dateutil import get_last_trading_day


select_desc = {
    "select_1_1": {
        "name": "거래 증가 & 장대 양봉",
        "desc": "거래 증가는 투자자들이 매수에 동참, 장대양봉은 매수세력의 강한 자신감 신호",
        "image": "images/graph_1_1.png",
    },
    "select_1_2": {
        "name": "거래 증가 & 장대 음봉",
        "desc": "거래 증가는 투자자들이 매도에 동참, 장대음봉은 매도세력의 강한 자신감 신호",
        "image": "images/graph_1_2.png",
    },
    "select_2_1": {
        "name": "박스 상향 돌파",
        "desc": "새로운 상승 추세 시작, 신규 투자자 유입, 심리적 저항선 극복 신호",
        "image": "images/graph_2_1.png",
    },
    "select_2_2": {
        "name": "박스 하향 돌파",
        "desc": "하락 추세 시작, 심리적 저항선 극복, 신규 투자자 유출 신호",
        "image": "images/graph_2_2.png",
    },
    "select_3_1": {
        "name": "스매시 상승",
        "desc": "하락하던 주가가 전일 고점을 웃도는 종가로 마감되며 반전 가능 시사",
        "image": "images/graph_3_1.png",
    },
    "select_3_2": {
        "name": "스매시 하락",
        "desc": "상승하던 주가가 전일 저점을 밑돌며 하락 가능 시사",
        "image": "images/graph_3_2.png",
    },
    "select_4_1": {
        "name": "하락 후 횡보",
        "desc": "가격 안정화, 매도세 약화, 추세 전환 가능성 시사",
        "image": "images/graph_4_1.png",
    },
    "select_4_2": {
        "name": "상승 후 횡보",
        "desc": "가격 안정화, 매수세 약화, 추세 전환 가능성 시사",
        "image": "images/graph_4_2.png",
    },
    "select_5_1": {
        "name": "주가 3개월 저점",
        "desc": "주가 3개월 지지선 부근에 근접, 지지선 지탱될 경우 주가 반등 신호",
        "image": "images/graph_5_1.png",
    },
    "select_5_2": {
        "name": "주가 3개월 고점",
        "desc": "주가 3개월 저항선 부근에 근접, 저항선 돌파 시 주가 하락 신호",
        "image": "images/graph_5_2.png",
    },
}


def load_tickers() -> Tuple[Dict[str, str], Dict[str, str]]:
    ticker_dict = {}
    ticker_desc_dict = {}
    with open("data/ticker_translation.csv") as fr:
        reader = csv.reader(fr)
        next(reader)
        for i, (ticker, name, description, kor_description) in enumerate(reader):
            if i > 500:
                break
            ticker_dict[ticker] = name
            ticker_desc_dict[ticker] = kor_description
    return ticker_dict, ticker_desc_dict


@st.cache_data
def load_tickers_dict() -> Tuple[Dict[str, str], Dict[str, str]]:
    tickers_dict, tickers_desc_dict = load_tickers()
    return tickers_dict, tickers_desc_dict


def draw_screening_result(data: List[dict], screening: str):
    tickers_dict, tickers_desc_dict = load_tickers_dict()
    last_trading_day = get_last_trading_day()
    st.write(f"기준 날짜: {last_trading_day}")
    column_size = 5
    for i in range(0, len(data), column_size):
        cols = st.columns(column_size)
        batch = data[i : i + column_size]
        for j, (key, value) in enumerate(batch):
            with cols[j]:
                st.markdown(f"**{select_desc[key]['name']}**")
                st.image(select_desc[key]["image"])
                st.markdown(select_desc[key]["desc"])
                for i in range(min(5, len(value))):
                    ticker = value[i]
                    st.link_button(
                        label=f"{i+1}\. {ticker} ({tickers_dict[ticker]})",
                        url=f"미국_종목별_검색?ticker={ticker}&screening={screening}",
                    )
                if len(value) > 5:
                    with st.expander(f"{len(value) - 5} 종목 더보기"):
                        for k in range(5, len(value)):
                            cur_ticker = value[k]
                            st.link_button(
                                label=f"{k+1}\. {cur_ticker} ({tickers_dict[cur_ticker]})",
                                url=f"미국_종목별_검색?ticker={cur_ticker}&screening={screening}",
                            )
