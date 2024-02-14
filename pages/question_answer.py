import streamlit as st

from services.service_db import select_question_answer
from utils.streamlit_util import draw_news, draw_main_ideas, draw_related_report, draw_next_questions
from utils.util import convert_timezone

st.title("Question & Answer")
st.write("유저의 질문에 대해서 마켓 옥토퍼스의 답변을 확인합니다.")

question_id = st.query_params.get("question")
if not question_id:
    st.error("질문 아이디가 선택되지 않았습니다.")
    st.stop()

with st.spinner("답변 데이터 가져오는 중..."):
    created_at, question, answer = select_question_answer(question_id)
    created_at = convert_timezone(created_at)

st.write(f"**질문 생성일: {created_at.strftime('%Y-%m-%d %H:%M:%S')}**")
st.write(f"**질문: {question}**")
answer = eval(answer)
if "question_range" in answer:
    st.write(f"**질문 범위: {answer['question_range']}**")
draw_news(answer["related_news"], expanded=False)
st.write(answer["news_based_answer"])
main_ideas = [x["main_idea"] for x in answer["report_based_answer"]]
draw_main_ideas(main_ideas)

for i, report_based_answer in enumerate(answer["report_based_answer"]):
    related_reports = [eval(x) for x in report_based_answer["related_reports"]]
    draw_related_report(i+1, related_reports, expanded=False)
    st.write(report_based_answer["report_based_answer"])

if "conclusion" in answer:
    st.markdown("**결론**")
    st.write(answer["conclusion"])

draw_next_questions(answer["next_questions"])
