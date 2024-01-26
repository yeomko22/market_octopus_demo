import streamlit as st
from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import classify_intent
from services.streamlit_util import write_common_style, \
    set_page_config, draw_auto_complete, NOT_GIVEN, draw_intent

set_page_config()
show_pages_from_config()
write_common_style()


st.title("🐙 intent classification")
st.markdown("""
질문 의도 분류 결과를 테스트해보는 페이지입니다. 
""".strip())
auto_complete = draw_auto_complete()
with st.form("form"):
    question = st.text_input(
        label="질문",
        placeholder="질문을 입력해주세요",
        value=auto_complete if auto_complete != NOT_GIVEN else ""
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
