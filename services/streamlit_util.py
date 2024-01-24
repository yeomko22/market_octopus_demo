import streamlit as st


default_instruction = f"""
유저의 질문과 참고할만한 애널리스트 리포트 문단이 주어집니다.
리포트를 참고해서 직접 분석하여 답변을 작성해야합니다.

먼저 질문 내용과 질문 의도를 한 문장으로 정리하세요.
유저의 질문 내용을 칭찬해도 됩니다.
그 다음 유저의 질문에 대한 분석 결과를 한 문장으로 요약한 제목을 제시하세요.
제목 아래에 불릿포인트를 사용해서 핵심을 3~5가지 내용을 간결하게 설명하세요.

제목은 진하게과 기울임을 적용하세요.
반드시 친근한 구어체로 답하세요.
"질문 요약", "제목" 등의 단어는 반드시 생략하세요.
""".strip()

NOT_GIVEN = "선택 안함"
example_questions = [
    NOT_GIVEN,
    "최근 발표된 미국 금리 인하가 주식 시장에 어떤 영향을 미칠까?",
    "정부의 새로운 부동산 정책이 주식 시장에 어떤 영향을 미칠까?",
    "최근 주식시장의 전반적인 트렌드는?",
    "올해 주식시장의 주요 이벤트나 추세는?",
    "지금과 같은 금융시장 환경에서는 어떤 투자 전략을 취해야할까?",
    "생성 AI 기술에 영향을 받을 종목은 어떤 것들이 있을까?",
    "올해 어떤 산업군이 좋은 성괄르 낼 것으로 예상해?",
    "테슬라는 현재 투자하기 좋은 선택일까?"
]


def read_stream(response) -> None:
    content = ""
    placeholder = st.empty()
    for part in response:
        if not part.id:
            continue
        delta = part.choices[0].delta
        if delta.content:
            content += delta.content
            placeholder.markdown(content + "▌")
    placeholder.markdown(content)


def set_page_config():
    st.set_page_config(
        page_icon="🐙",
        page_title="Mr. market octopus"
    )


def write_common_style():
    st.markdown("""
    <style>
    [data-testid="stExpanderDetails"] p {
        font-size: 14px;
    }
    [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] {
        gap: 0.3rem;
    }
    [data-test-id="stExpanderToggleIcon"] {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)


def draw_seeking_alpha_report(selected_item: dict):
    selected_item_metadata = selected_item["metadata"]
    with st.expander(selected_item_metadata["title"], expanded=True):
        st.markdown(selected_item_metadata['published_at'])
        st.markdown(f"score: {round(selected_item['score'], 4)}")
        st.link_button(
            label="🌐 See full report",
            url=selected_item_metadata["public_url"],
            use_container_width=True
        )
        st.link_button(
            label="📝 See text chunk",
            url=f"https://storage.googleapis.com/mactopus-seeking-alpha/{selected_item_metadata['chunk_url']}",
            use_container_width=True
        )
