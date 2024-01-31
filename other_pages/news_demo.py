from datetime import datetime

from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import extract_query
from services.service_openai import get_embedding, get_streaming_response
from services.service_search import search_news
from utils.streamlit_util import *

set_page_config()
show_pages_from_config()
write_common_style()
write_common_session_state()


def generate_prompt(instruct: str, question: str, news: List[dict]) -> str:
    news_text = ""
    for i, content in enumerate(domestic_news):
        news_text += f"""
title: {content["title"]}  
url: {content["url"]}  
related_paragraph: {content["related_paragraph"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
question: {question}  
"""
    if news:
        prompt += f"news\n{news_text}"
    prompt += "---"
    return prompt.strip()


st.title("🐙 market octopus")
st.markdown("""
질문 범위를 선택한 다음, 질문을 입력합니다.   
범위에 따라서 국내 뉴스, 해외 뉴스를 가져와서 답변을 생성합니다.  
의도 분류는 적용하지 않습니다.  
""".strip())
auto_complete = draw_auto_complete()
example_ai_role = "당신은 전문 증권 애널리스트입니다."
with st.form("form"):
    system_message = st.text_input(label="AI 역할", value=example_ai_role)
    instruct = st.text_area(label="답변 생성시 고려사항", value=news_instruction, height=200)
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        target = st.selectbox(label="질문 범위", options=["전체", "국내", "해외"])
    with col2:
        question = st.text_input(
            "질문",
            placeholder="질문을 입력해주세요",
            value=get_question(auto_complete)
        )
    submit = st.form_submit_button(label="제출")

if submit:
    eng_question = translate([question])[0]
    kor_question_embedding, eng_question_embedding = get_embedding([question, eng_question])
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()

    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        with st.spinner("관련 뉴스 검색 중..."):
            eng_query = extract_query(eng_question)
            kor_query = translate([eng_query], kor_to_eng=False)[0]
            news = []
            if target == "국내" or target == "전체":
                domestic_news = search_news(kor_query, kor_question_embedding, is_domestic=True)
                news.extend(domestic_news)
            if target == "해외" or target == "전체":
                oversea_news = search_news(eng_query, eng_question_embedding, is_domestic=False)
                news.extend(oversea_news)
            news = sorted(news, key=lambda x: x["similarity"], reverse=True)[:3]
            draw_news(news, target)
    with col2:
        with st.spinner("의견 생성 중..."):
            prompt = generate_prompt(instruct, question, news)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        answer = read_stream(streaming_response)
