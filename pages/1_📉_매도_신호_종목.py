from typing import Dict, Tuple

import streamlit as st

from services.service_db import select_daily_screening
from utils.dateutil import get_last_trading_day
from utils.util import load_tickers

st.set_page_config(layout="wide")
st.title("📉 매도 신호 종목")
st.write("매수, 매도 신호는 기술적 지표에 따른 추정이며 참고용입니다. 투자 결정은 가격 패턴과 기본 분석을 종합적으로 고려해주세요.")
st.markdown(
    """
<style>
[data-testid="stLinkButton"] a {
    display: flex;
    justify-content: flex-start;
}
[data-testid="stAppViewBlockContainer"] {
    padding: 2rem 5rem 0rem 5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

select_desc = {
    "select_1_1": "거래 증가 & 장대 양봉",
    "select_1_2": "거래 증가 & 장대 음봉",
    "select_2_1": "박스 상향 돌파",
    "select_2_2": "박스 하향 돌파",
    "select_3_1": "스매시 상승",
    "select_3_2": "스매시 하락",
    "select_4_1": "하락 후 횡보",
    "select_4_2": "상승 후 횡보",
    "select_5_1": "주가 3개월 저점",
    "select_5_2": "주가 3개월 고점",
}


@st.cache_data
def load_tickers_dict() -> Tuple[Dict[str, str], Dict[str, str]]:
    tickers_dict, tickers_desc_dict = load_tickers()
    return tickers_dict, tickers_desc_dict


tickers_dict, tickers_desc_dict = load_tickers_dict()
with st.spinner("일일 스크리닝 결과 로딩 중..."):
    daily_screening = select_daily_screening()
    data = []
    for key, value in daily_screening.items():
        if key.endswith("_2"):
            data.append((key, value[:5]))
    last_trading_day = get_last_trading_day()

st.write(f"기준 날짜: {last_trading_day}")
cols = st.columns(3)
column_size = 5
for i in range(0, len(data), column_size):
    cols = st.columns(column_size)
    batch = data[i : i + column_size]
    for j, (key, value) in enumerate(batch):
        with cols[j]:
            with st.expander(f"{select_desc[key]} ({len(value)})", expanded=True):
                st.image(f"images/graph_{i + j + 1}.png")
                if not value:
                    st.write("해당하는 종목이 없습니다.")
                for ticker in value:
                    st.link_button(
                        label=f"{ticker} ({tickers_dict[ticker]})",
                        url=f"ask?ticker={ticker}",
                    )
