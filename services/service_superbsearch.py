import requests
import streamlit as st


@st.cache_data
def search_news(ticker: str, ticker_name: str, eng_question: str) -> dict:
    query = f"""
selected_ticker: {ticker} ({ticker_name})
question: {eng_question}
""".strip()
    url = "https://superbsearch-dev.vercel.app/api/search/v1"
    response = requests.post(
        url,
        json={"query": query},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.secrets['SUPERBSEARCH_API_KEY']}",
        },
    )
    response_json = response.json()
    return response_json
