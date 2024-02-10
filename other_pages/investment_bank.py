from datetime import datetime

from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response, generate_next_questions
from services.service_pinecone import search_investment_bank
from utils.streamlit_util import *

set_page_config()
show_pages_from_config()
write_common_style()
write_common_session_state()


def generate_prompt(instruct: str, question: str, oversea_reports: List[dict]) -> str:
    oversea_text = ""
    for i, content in enumerate(oversea_reports):
        oversea_metadata = content["metadata"]
        oversea_text += f"""
title: {oversea_metadata["filename"]}  
content: {oversea_metadata["content"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
question: {question}  
"""
    if oversea_reports:
        prompt += f"Oversea reports\n{oversea_text}"
    prompt += "---"
    return prompt.strip()


def get_oversea_reports(question_embedding: List[float]) -> List[dict]:
    with st.spinner("투자 은행 리포트를 검색 중입니다..."):
        oversea_report_list = search_investment_bank(
            question_embedding,
            k=3,
        )
        if not oversea_report_list:
            st.markdown("관련 리포트를 찾을 수 없습니다.")
    return oversea_report_list


st.title("🐙 market octopus")
st.markdown("""
질문 범위를 선택한 다음, 질문을 입력합니다.  
해외 투자 은행 분석 리포트를 바탕으로 답변을 생성합니다.
""".strip())
auto_complete = draw_auto_complete()
example_ai_role = "당신은 전문 증권 애널리스트입니다."
with st.form("form"):
    system_message = st.text_input(label="AI 역할", value=example_ai_role)
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
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        question_embedding = get_embedding([eng_question])[0]
        oversea_report_list = get_oversea_reports(question_embedding)
        if oversea_report_list:
            draw_oversea_report(oversea_report_list, expanded=False)
    with col2:
        with st.spinner("의견 생성 중..."):
            prompt = generate_prompt(instruct, question, oversea_report_list)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        answer = read_stream(streaming_response)
        with st.spinner("다음에 물어보면 좋을 질문들..."):
            questions = generate_next_questions(question, answer)
        draw_next_questions(questions)
