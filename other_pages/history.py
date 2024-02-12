import streamlit as st
from services.service_db import select_questions, select_total_questions

st.title("History")
st.write("유저가 마켓 옥토퍼스에게 물어본 질문들과 그에 대한 답변을 조회합니다.")

total_questions = select_total_questions()
total_pages = total_questions // 10 + 1

cols = st.columns(4)
with cols[0]:
    selected_page = st.selectbox(
        label="페이지",
        options=[x+1 for x in range(10)],
        key="page",
    )

total_questions = select_questions(page=selected_page)
cols = st.columns([0.1, 0.1, 0.7, 0.1])
with cols[0]:
    st.markdown("id")
with cols[1]:
    st.markdown("created_at")
with cols[2]:
    st.markdown("question")
with cols[3]:
    st.markdown("detail")

for id_, question, created_at in total_questions:
    with cols[0]:
        st.write(id_)
    with cols[1]:
        st.write(created_at)
    with cols[2]:
        st.write(question)



