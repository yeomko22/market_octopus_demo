import streamlit as st

from services.service_db import select_daily_screening
from utils.dateutil import get_last_trading_day
from utils.screening_util import draw_screening_result

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

with st.spinner("일일 스크리닝 결과 로딩 중..."):
    daily_screening = select_daily_screening()
    data = []
    for key, value in daily_screening.items():
        if key.endswith("_2"):
            data.append((key, value))
    last_trading_day = get_last_trading_day()
draw_screening_result(data)
