import streamlit as st

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response
from services.service_pinecone import search_seeking_alpha_summary, search_seeking_alpha_content
from services.service_yfinance import select_ticker, draw_stock_price
from services.streamlit_util import read_stream, default_instruction, example_questions, NOT_GIVEN, write_common_style, draw_seeking_alpha_report, set_page_config
from st_pages import show_pages_from_config


set_page_config()
show_pages_from_config()
write_common_style()


def generate_prompt(instruct: str, question: str, selected_item: dict) -> str:
    prompt = f"""
{instruct}
---
질문: {question}  
관련 리포트 

title: {selected_item["title"]}

summary: {selected_item["summary"]}

content: {selected_item["content"]}
---
""".strip()
    return prompt


st.title("🐙 seeking alpha single")
st.markdown("""
유저의 질문과 가장 관련도가 높은 seeking-alpha 리포트 1편을 참고해서 답변을 생성합니다.  
참고한 리포트가 특정 종목과 관련이 있을 경우, 현재 주가 데이터를 그려줍니다.
""".strip())
auto_complete = st.selectbox("예시 질문 선택", options=example_questions)
example_ai_role = "당신은 전문 증권 애널리스트입니다."

with st.form("form"):
    system_message = st.text_input(label="AI 역할", value=example_ai_role)
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
                matches = search_seeking_alpha_content(question_embedding, related_report_ids)

                # report 1개만 선택
                selected_report = matches[0]
                draw_seeking_alpha_report(selected_report)
                selected_ticker = select_ticker(selected_report)
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
        selected_report_metadata = selected_report["metadata"]
        with st.spinner("AI 의견 생성 중..."):
            prompt = generate_prompt(instruct, question, selected_report_metadata)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        read_stream(streaming_response)
