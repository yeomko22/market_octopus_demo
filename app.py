from datetime import datetime
from typing import Optional
from utils.streamlit_util import *
set_page_config()

from st_pages import show_pages_from_config
from services.service_google import translate
from services.service_openai import classify_intent
from services.service_openai import extract_query
from services.service_openai import generate_next_questions, generate_advanced_analytics, generate_main_ideas
from services.service_openai import get_embedding, get_streaming_response
from services.service_pinecone import search_fnguide, search_seeking_alpha_summary, search_seeking_alpha_content, search_investment_bank
from services.service_search import search_news
from services.service_db import insert_question_answer
from utils.intent import INTENT_DICT
from utils.search_space import get_search_space, EnumDomain


show_pages_from_config()
write_common_style()
write_common_session_state()


def generate_prompt(instruct: str, question: str, news: List[dict]) -> str:
    news_text = ""
    for i, content in enumerate(news):
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


def generate_analytics_prompt(instruct: str, paragraph: str, related_reports: List[dict]) -> str:
    report_text = ""
    for i, content in enumerate(report_text):
        domestic_metadata = content["metadata"]
        report_text += f"""
title: {domestic_metadata["title"]}  
content: {domestic_metadata["content"]}  
"""
    prompt = f"""
{instruct}
--- 
today: {datetime.now().strftime("%Y-%m-%d")}  
paragraph: {paragraph}  
"""
    if related_reports:
        prompt += f"analytics reports\n{report_text}"
    prompt += "---"
    return prompt.strip()


def get_fnguide_reports(question_range: str, question_embedding: List[float], categories: Optional[List[str]]) -> List[dict]:
    domestic_report_list = []
    if question_range == "전체" or question_range == "국내":
        with st.spinner("국내 애널리스트 리포트 검색 중..."):
            domestic_report_list = search_fnguide(
                question_embedding,
                k=3,
                categories=categories
            )
    return domestic_report_list


def get_oversea_reports(question_range: str, question_embedding: List[float], categories: Optional[List[str]] = None) -> List[dict]:
    oversea_report_list = []
    if question_range == "전체" or question_range == "해외":
        with st.spinner("해외 애널리스트 리포트 검색 중..."):
            seeking_alpha_summary_list = search_seeking_alpha_summary(question_embedding, k=3, categories=categories)
            if seeking_alpha_summary_list:
                oversea_report_ids = [x["metadata"]["id"] for x in seeking_alpha_summary_list]
                seeking_alpha_content_list = search_seeking_alpha_content(question_embedding, oversea_report_ids, k=3)
                oversea_report_list.extend(seeking_alpha_content_list)
            investment_bank_list = search_investment_bank(question_embedding, k=3)
            oversea_report_list.extend(investment_bank_list)
    return oversea_report_list


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
    col1, col2 = st.columns(2)
    with col1:
        question_range = st.selectbox(label="질문 범위", options=["전체", "국내", "해외"])
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


def search_related_reports(
        question_range: str,
        answer_embedding: List[float],
        primary_intent: EnumPrimaryIntent,
        secondary_intent: Union[EnumMarketStrategyIntent, EnumIndustryStockIntent]
) -> List[dict]:
    fnguide_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.FNGUIDE)
    fnguide_report_list = get_fnguide_reports(question_range, answer_embedding, fnguide_search_space)
    seeking_alpha_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.SEEKING_ALPHA_ANALYSIS)
    oversea_report_list = get_oversea_reports(question_range, answer_embedding, seeking_alpha_search_space)
    related_reports = fnguide_report_list + oversea_report_list
    related_reports = sorted(related_reports, key=lambda x: x["metadata"]["published_at"], reverse=True)
    return related_reports


if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()

    eng_question = translate([question])[0]
    kor_question_embedding, eng_question_embedding = get_embedding([question, eng_question])
    if intent != "자동 분류":
        primary_intent, secondary_intent = INTENT_DICT[intent]
    else:
        with st.spinner("질문 의도 분류 중..."):
            primary_intent, secondary_intent = classify_intent(eng_question)
    primary_intent_kor, secondary_intent_kor = draw_intent(primary_intent, secondary_intent)

    title_main_idea = extract_query(eng_question)
    kor_query = translate([title_main_idea], kor_to_eng=False)[0]
    news = []
    if question_range == "국내" or question_range == "전체":
        with st.spinner("국내 뉴스 검색 중..."):
            domestic_news = search_news(kor_query, kor_question_embedding, is_domestic=True)
            news.extend(domestic_news)
    if question_range == "해외" or question_range == "전체":
        with st.spinner("해외 뉴스 검색 중..."):
            oversea_news = search_news(title_main_idea, eng_question_embedding, is_domestic=False)
            news.extend(oversea_news)
    news = sorted(news, key=lambda x: x["similarity"], reverse=True)[:3]
    draw_news(news, question_range, expanded=False)

    prompt = generate_prompt(instruct, question, news)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]
    streaming_response = get_streaming_response(messages)
    news_based_answer = read_stream(streaming_response)
    answer_dict = {
        "primary_intent": primary_intent_kor,
        "secondary_intent": secondary_intent_kor,
        "related_news": news,
        "news_based_answer": news_based_answer,
        "report_based_answer": []
    }
    # 핵심 아이디어 3개 추출
    with st.spinner("핵심 아이디어 정리 중..."):
        main_ideas = generate_main_ideas(question, news_based_answer)
    st.markdown("**핵심 아이디어**")
    for i, main_idea in enumerate(main_ideas):
        st.write(f"{i+1}. {main_idea}")

    # 핵심 아이디어에 대한 애널리틱스 리포트 검색
    eng_main_ideas = translate(main_ideas)
    title_main_idea_list = [f"question{eng_question}\nmain idea: {x}" for x in eng_main_ideas]
    title_main_idea_embeddings = get_embedding(title_main_idea_list)
    for i, (title_main_idea, title_main_idea_embedding) in enumerate(zip(title_main_idea_list, title_main_idea_embeddings)):
        related_reports = search_related_reports(question_range, title_main_idea_embedding, primary_intent, secondary_intent)
        # top 1만 선택
        related_reports = related_reports[:1]
        draw_related_report(related_reports, expanded=False)
        streaming_response = generate_advanced_analytics(title_main_idea, related_reports)
        report_based_answer = read_stream(streaming_response)
        news_based_answer += f"\n\n{report_based_answer}"
        answer_dict["report_based_answer"].append({
            "main_idea": main_ideas[i],
            "related_reports": related_reports,
            "report_based_answer": report_based_answer
        })
    with st.spinner("다음에 물어보면 좋을 질문들..."):
        next_questions = generate_next_questions(question, news_based_answer)
    draw_next_questions(next_questions)
    answer_dict["next_questions"] = next_questions
    insert_question_answer(question, answer_dict)
