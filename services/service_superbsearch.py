import requests
import streamlit as st


def search_news(query: str) -> dict:
    url = "https://superbsearch.io/api/v1/search"
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
