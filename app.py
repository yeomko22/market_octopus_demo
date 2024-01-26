from datetime import datetime
from typing import List

import streamlit as st
from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response, generate_next_questions, classify_intent
from services.service_pinecone import search_seeking_alpha_summary, search_seeking_alpha_content
from services.service_yfinance import draw_ticker_information
from services.streamlit_util import read_stream, default_instruction, write_common_style, \
    draw_seeking_alpha_report, set_page_config, draw_next_questions, draw_auto_complete, get_question, \
    write_common_session_state, draw_intent

set_page_config()
show_pages_from_config()
write_common_style()
write_common_session_state()


def generate_prompt(instruct: str, question: str, related_contents: List[dict]) -> str:
    related_contents_text = ""
    for i, content in enumerate(related_contents):
        content_metadata = content["metadata"]
        related_contents_text += f"""
title: {content_metadata["title"]}  
published_at: {content_metadata["published_at"]}  
summary: {content_metadata["summary"]}  
content: {content_metadata["content"]}  
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


st.title("🐙 seeking alpha")
st.markdown("""
유저의 질문과 가장 관련도가 높은 seeking-alpha 리포트 최대 3편을 참고해서 답변을 생성합니다.  
참고한 리포트가 특정 종목과 관련이 있을 경우, 현재 주가 데이터를 그려줍니다.
""".strip())

auto_complete = draw_auto_complete()
example_ai_role = "당신은 전문 증권 애널리스트입니다."
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
        value=get_question(auto_complete)
    )
    submit = st.form_submit_button(label="제출")


if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()
    eng_question = translate([question])[0]
    with st.spinner("질문 의도 분류 중..."):
        primary_intent, secondary_intent = classify_intent(eng_question)
    draw_intent(primary_intent, secondary_intent)
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        with st.spinner("관련 리포트 검색 중..."):
            question_embedding = get_embedding([eng_question])[0]

            # 1. question과 summary의 유사도를 구해서 가장 유사한 리포트를 3개 찾는다.
            # 2. 3개의 리포트 중에서 질문과 가장 관련도가 높은 단락을 선택한다.
            related_report_list = search_seeking_alpha_summary(question_embedding, k=5)
            if not related_report_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
            else:
                related_report_ids = [x["metadata"]["id"] for x in related_report_list]
                related_contents = search_seeking_alpha_content(question_embedding, related_report_ids, k=num_reports)
                draw_seeking_alpha_report(related_contents)
                draw_ticker_information(related_report_list)
    with col2:
        st.markdown("**🧠AI 의견**")
        with st.spinner("AI 의견 생성 중..."):
            prompt = generate_prompt(instruct, question, related_contents)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        answer = read_stream(streaming_response)
        with st.spinner("다음에 물어보면 좋을 질문들..."):
            questions = generate_next_questions(question, answer)
        draw_next_questions(questions)
