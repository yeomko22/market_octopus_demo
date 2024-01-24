from datetime import datetime
from typing import List

import streamlit as st
from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response
from services.service_pinecone import search_seeking_alpha_summary, search_seeking_alpha_content
from services.service_yfinance import select_ticker, draw_stock_price
from services.streamlit_util import read_stream, default_instruction, example_questions, NOT_GIVEN, write_common_style, \
    draw_seeking_alpha_report, set_page_config

set_page_config()
show_pages_from_config()
write_common_style()


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


st.title("🐙 seeking alpha single")
st.markdown("""
유저의 질문과 가장 관련도가 높은 seeking-alpha 리포트 최대 3편을 참고해서 답변을 생성합니다.  
참고한 리포트가 특정 종목과 관련이 있을 경우, 현재 주가 데이터를 그려줍니다.
""".strip())
auto_complete = st.selectbox("예시 질문 선택", options=example_questions)
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
        value=auto_complete if auto_complete != NOT_GIVEN else ""
    )
    submit = st.form_submit_button(label="제출")


if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        st.markdown("**📝seeking alpha report**")
        with st.spinner("관련 리포트 검색 중..."):
            eng_question = translate([question])[0]
            question_embedding = get_embedding([eng_question])[0]

            # 1. question과 summary의 유사도를 구해서 가장 유사한 리포트를 3개 찾는다.
            # 2. 3개의 리포트 중에서 질문과 가장 관련도가 높은 단락을 선택한다.
            related_report_list = search_seeking_alpha_summary(question_embedding, k=5)
            if not related_report_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
            else:
                related_report_ids = [x["metadata"]["id"] for x in related_report_list]
                related_contents = search_seeking_alpha_content(question_embedding, related_report_ids, k=num_reports)

                # report 1개만 선택
                draw_seeking_alpha_report(related_contents)
                selected_ticker = select_ticker(related_contents)
                if selected_ticker:
                    st.markdown("**📈realted stock**")
                    with st.expander(selected_ticker.ticker, expanded=True):
                        fig = draw_stock_price(selected_ticker)
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            config={'displayModeBar': False}
                        )
    with col2:
        st.markdown("**🧠AI 의견**")
        with st.spinner("AI 의견 생성 중..."):
            prompt = generate_prompt(instruct, question, related_contents)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        read_stream(streaming_response)
