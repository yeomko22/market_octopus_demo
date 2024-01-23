import streamlit as st

default_instruction = """
유저의 질문과 참고할만한 애널리스트 리포트 문단이 주어집니다.
기존에 알고 있었던 지식과 참고 자료를 활용해서 스스로 분석한 결과를 작성하세요.
구체적인 수치나 전문적인 자료를 언급해주세요.
반드시 한국어로 답변하세요.
두괄식으로 핵심을 먼저 말해주세요.
불릿 포인트를 사용해서 핵심을 정리해주세요.
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
