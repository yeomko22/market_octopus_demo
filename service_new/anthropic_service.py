from typing import List
import streamlit as st

import anthropic


class AnthropicService:
    def __init__(self, claude_api_key: str):
        self.client = anthropic.Anthropic(api_key=claude_api_key)

    def generate_streaming_response(
        self, messages: List[dict], model="claude-3-opus-20240229"
    ):
        content = ""
        placeholder = st.empty()
        with self.client.messages.stream(
            model=model,
            max_tokens=1000,
            system="You are an professional financial analyst.",
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                content += text
                placeholder.markdown(content + "▌")
        placeholder.markdown(content)
