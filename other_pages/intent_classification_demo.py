from st_pages import show_pages_from_config

from services.service_google import translate
from services.service_openai import classify_intent
from utils.categories import fnguide_category_dict
from utils.search_space import get_search_space, EnumDomain
from utils.streamlit_util import *

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
        domestic_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.FNGUIDE)
        oversea_search_space = get_search_space(primary_intent, secondary_intent, EnumDomain.SEEKING_ALPHA_ANALYSIS)
        st.markdown(f"fnguide 검색 범위: {[fnguide_category_dict[x] for x in domestic_search_space]}")
        st.markdown(f"seeking alpha 검색 범위: {[x.value for x in oversea_search_space]}")
