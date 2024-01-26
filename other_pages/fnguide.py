from datetime import datetime
from typing import List

import streamlit as st
from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding, generate_next_questions, classify_intent
from services.service_openai import get_streaming_response
from services.service_pinecone import search_fnguide
from services.streamlit_util import default_instruction, draw_fnguide_report, draw_auto_complete, write_common_style, \
    set_page_config, read_stream, draw_next_questions, write_common_session_state, get_question, draw_intent

set_page_config()
show_pages_from_config()
write_common_style()
write_common_session_state()

st.title("🐙 fnguide")
st.markdown("""
유저의 질문과 가장 관련도가 높은 fnguide 리포트 최대 3편을 참고해서 답변을 생성합니다.  
""".strip())
auto_complete = draw_auto_complete()
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
        st.markdown("**📝 국내 애널리스트 리포트**")
        with st.spinner("관련 리포트 검색 중..."):
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
        answer = read_stream(streaming_response)
        with st.spinner("다음에 물어보면 좋을 질문들..."):
            questions = generate_next_questions(question, answer)
        draw_next_questions(questions)
