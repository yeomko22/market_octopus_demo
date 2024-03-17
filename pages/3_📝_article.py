import streamlit as st
from typing import Tuple
from utils.util import base64_decode
from services.service_db import select_stored_html_url

st.set_page_config(layout="wide")
st.markdown(
    """
<style>
[data-testid="stAppViewBlockContainer"] {
    padding: 0rem 5rem 0rem 5rem;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_article(hashid: str) -> Tuple[str, str]:
    stored_html_url, url = select_stored_html_url(hashid)
    return stored_html_url, url


st.title("Article")
id = st.query_params.get("id")
if not id:
    st.error("기사 id가 선택되지 않았습니다.")
    st.stop()
stored_html_url, url = select_stored_html_url(id)
article_url = f"https://storage.googleapis.com/superbsearch-prod/{stored_html_url}"
col1, col2 = st.columns([7, 3])
with col1:
    st.components.v1.iframe(article_url, height=800, scrolling=True)
with col2:
    encoded_related_paragraph = st.query_params.get("related_paragraph")
    related_paragraph = base64_decode(encoded_related_paragraph)
    st.subheader("URL")
    st.write(url)
    st.subheader("Related Paragraph")
    st.markdown(related_paragraph)
