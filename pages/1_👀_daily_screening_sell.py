import streamlit as st
from pytz import timezone
from datetime import datetime
from typing import Dict, Tuple
from utils.util import load_tickers

from services.service_db import select_daily_screening
from utils.util import convert_timezone

st.set_page_config(layout="wide")
st.title("Daily Screening")
st.write("전날 급격한 변화를 겪은 종목들을 마켓 옥토퍼스가 엄선해서 보여드립니다.")
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


def load_daily_screening() -> Tuple[datetime, Dict[str, list]]:
    created_at, daily_screening = select_daily_screening()
    daily_screening = eval(daily_screening)
    return created_at, daily_screening


tickers_dict, tickers_desc_dict = load_tickers_dict()
created_at, daily_screening = load_daily_screening()
created_at = created_at.replace(tzinfo=timezone("utc")).astimezone(
    timezone("Asia/Seoul")
)
st.write(f"마지막 집계: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")

cols = st.columns(3)
data = []
for key, value in daily_screening.items():
    if key.endswith("_2"):
        data.append((key, value[:5]))

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
