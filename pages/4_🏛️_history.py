import streamlit as st

from services.service_db import select_total_questions, select_questions
from utils.util import convert_timezone

st.set_page_config(layout="centered")
st.title("History")
st.write("유저가 마켓 옥토퍼스에게 물어본 질문들을 조회합니다. 클릭하면 답변을 확인할 수 있습니다.")

with st.spinner("Loading..."):
    total_questions = select_total_questions()
total_pages = total_questions // 10 + 1

st.markdown(
    """
<style>
[data-testid="stLinkButton"] a {
    display: flex;
    justify-content: flex-start;
}
</style>
""",
    unsafe_allow_html=True,
)
cols = st.columns(4)
with cols[0]:
    selected_page = st.selectbox(
        label="페이지",
        options=[x + 1 for x in range(total_pages)],
        key="page",
    )

with st.spinner("Loading..."):
    total_questions = select_questions(page=selected_page)
for id_, question, created_at in total_questions:
    created_at = convert_timezone(created_at)
    st.link_button(
        label=f"{id_}\. ({created_at.strftime('%Y-%m-%d %H:%M')}) {question}",
        url=f"/question_answer?question={id_}",
        use_container_width=True,
    )
