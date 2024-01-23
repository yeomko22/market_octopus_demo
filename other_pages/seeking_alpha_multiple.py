import streamlit as st
from st_pages import show_pages_from_config

from services.streamlit_util import write_common_style, example_questions

st.set_page_config(
    page_icon="🐙",
    page_title="Mr. market octopus"
)
show_pages_from_config()
write_common_style()

st.title("🐙 Mr. Market Octopus")
st.markdown("""
유저의 질문과 가장 관련도가 높은 seeking-alpha 리포트 3편을 참고해서 답변을 생성합니다.  
참고한 리포트가 특정 종목과 관련이 있을 경우, 현재 주가 데이터를 그려줍니다.
""".strip())
auto_complete = st.selectbox("예시 질문 선택", options=example_questions)
example_ai_role = "당신은 전문 증권 애널리스트입니다."

