from datetime import datetime
from typing import Optional

from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response, generate_next_questions, classify_intent
from services.service_pinecone import search_fnguide
from services.service_pinecone import search_seeking_alpha_summary, search_seeking_alpha_content
from services.service_yfinance import draw_ticker_information
from utils.intent import INTENT_DICT
from utils.search_space import get_search_space, EnumDomain
from utils.streamlit_util import *

set_page_config()
show_pages_from_config()
write_common_style()
write_common_session_state()


def generate_prompt(instruct: str, question: str, domestic_reports: List[dict], oversea_reports: List[dict]) -> str:
    domestic_text = ""
    for i, content in enumerate(domestic_text):
        domestic_metadata = content["metadata"]
        domestic_text += f"""
title: {domestic_metadata["title"]}  
summary: {domestic_metadata["summary"]}  
content: {domestic_metadata["content"]}  
"""
    oversea_text = ""
    for i, content in enumerate(oversea_reports):
        oversea_metadata = content["metadata"]
        oversea_text += f"""
title: {oversea_metadata["title"]}  
summary: {oversea_metadata["summary"]}  
content: {oversea_metadata["content"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
question: {question}  
"""
    if domestic_reports:
        prompt += f"Korean domestic reports\n{domestic_text}"
    if oversea_reports:
        prompt += f"Oversea reports\n{oversea_text}"
    prompt += "---"
    return prompt.strip()


def get_domestic_reports(question_embedding: List[float], categories: Optional[List[str]] = None) -> List[dict]:
    domestic_report_list = []
    if question_rage == "전체" or question_rage == "국내":
        with st.spinner("국내 애널리스트 리포트 검색 중..."):
            domestic_report_list = search_fnguide(
                question_embedding,
                k=3,
                categories=categories
            )
            if not domestic_report_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
    return domestic_report_list


def get_oversea_reports(question_embedding: List[float], categories: Optional[List[str]] = None) -> List[dict]:
    oversea_report_list = []
    if question_rage == "전체" or question_rage == "해외":
        with st.spinner("해외 애널리스트 리포트를 검색 중입니다..."):
            oversea_summary_list = search_seeking_alpha_summary(
                question_embedding,
                k=10,
                categories=categories
            )
            if not oversea_summary_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
            else:
                oversea_report_ids = [x["metadata"]["id"] for x in oversea_summary_list]
                oversea_report_list = search_seeking_alpha_content(question_embedding, oversea_report_ids, k=3)
    return oversea_report_list


st.title("🐙 market octopus")
st.markdown("""
질문 범위를 선택한 다음, 질문을 입력합니다.  
전체를 선택하면 국내 리포트 3편, 해외 리포트 3편을 참고하여 답변을 생성합니다.  
국내나 해외를 선택하면 해당 범위의 리포트 3편을 참고하여 답변을 생성합니다.  
의도 분류 결과에 따라서 카테고리를 좁혀서 리포트를 검색합니다.  
""".strip())
auto_complete = draw_auto_complete()
example_ai_role = "당신은 전문 증권 애널리스트입니다."
with st.form("form"):
    system_message = st.text_input(label="AI 역할", value=example_ai_role)
    instruct = st.text_area(label="답변 생성시 고려사항", value=default_instruction, height=200)
    col1, col2 = st.columns(2)
    with col1:
        question_rage = st.selectbox(label="질문 범위", options=["전체", "국내", "해외"])
    with col2:
        intent = st.selectbox(
            label="질문 의도",
            options=["자동 분류"] + list(INTENT_DICT.keys()),
        )
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
    if intent != "자동 분류":
        primary_intent, secondary_intent = INTENT_DICT[intent]
    else:
        with st.spinner("질문 의도 분류 중..."):
            primary_intent, secondary_intent = classify_intent(eng_question)
    draw_intent(primary_intent, secondary_intent)
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        question_embedding = get_embedding([eng_question])[0]
        domestic_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.FNGUIDE)
        domestic_report_list = get_domestic_reports(question_embedding, categories=domestic_search_space)
        if domestic_report_list:
            draw_fnguide_report(domestic_report_list, expanded=False)
        oversea_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.SEEKING_ALPHA_ANALYSIS)
        oversea_report_list = get_oversea_reports(question_embedding, categories=oversea_search_space)
        if oversea_report_list:
            draw_oversea_report(oversea_report_list, expanded=False)
            draw_ticker_information(oversea_report_list)
    with col2:
        with st.spinner("의견 생성 중..."):
            prompt = generate_prompt(instruct, question, domestic_report_list, oversea_report_list)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        answer = read_stream(streaming_response)
        with st.spinner("다음에 물어보면 좋을 질문들..."):
            questions = generate_next_questions(question, answer)
        draw_next_questions(questions)
