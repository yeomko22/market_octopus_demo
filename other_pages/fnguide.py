from typing import List
from datetime import datetime

import streamlit as st
from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding
from services.service_openai import get_streaming_response
from services.service_pinecone import search_fnguide
from services.service_yfinance import select_ticker, draw_stock_price
from services.streamlit_util import default_instruction, NOT_GIVEN, draw_fnguide_report
from services.streamlit_util import write_common_style, example_questions, set_page_config, read_stream

set_page_config()
show_pages_from_config()
write_common_style()

st.title("🐙 fnguide single")
st.markdown("""
유저의 질문과 가장 관련도가 높은 fnguide 리포트 최대 3편을 참고해서 답변을 생성합니다.  
""".strip())
auto_complete = st.selectbox("예시 질문 선택", options=example_questions)
example_ai_role = "당신은 전문 증권 애널리스트입니다."


def generate_prompt(instruct: str, question: str, related_contents: List[dict]) -> str:
    related_contents_text = ""
    for i, content in enumerate(related_contents):
        content_metadata = content["metadata"]
        related_contents_text += f"""
title: {content_metadata["title"]}  
published_at: {content_metadata["published_at"]}  
content: {content_metadata["eng_text"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
question: {question}  
related analysis
{related_contents_text}
---
""".strip()
    return prompt


with st.form("form"):
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        system_message = st.text_input(label="AI 역할", value=example_ai_role)
    with col2:
        num_reports = st.number_input(label="참고할 리포트 개수", min_value=1, max_value=3, value=1)
    instruct = st.text_area(label="답변 생성시 고려사항", value=default_instruction, height=200)
    question = st.text_input(
        "질문",
        placeholder="질문을 입력해주세요",
        value=auto_complete if auto_complete != NOT_GIVEN else ""
    )
    submit = st.form_submit_button(label="제출")
if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        st.markdown("**📝 국내 애널리스트 리포트**")
        with st.spinner("관련 리포트 검색 중..."):
            eng_question = translate([question])[0]
            question_embedding = get_embedding([eng_question])[0]
            related_report_list = search_fnguide(question_embedding, k=num_reports)
            if not related_report_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
            else:
                draw_fnguide_report(related_report_list)
    with col2:
        st.markdown("**🧠AI 의견**")
        with st.spinner("AI 의견 생성 중..."):
            prompt = generate_prompt(instruct, eng_question, related_report_list)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        read_stream(streaming_response)
