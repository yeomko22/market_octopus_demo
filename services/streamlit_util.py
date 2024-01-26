from typing import List, Union

import streamlit as st

from services.util import PRIMARY_INTENT_DICT, EnumPrimaryIntent, EnumIndustryStockIntent, EnumMarketStrategyIntent, ENUM_MARKET_STRATEGY_INTENT_DICT, ENUM_INDUSTRY_STOCK_INTENT_DICT

default_instruction = f"""
금융 관련 질문과 참고할만한 애널리스트 리포트 문단이 주어집니다.
리포트를 참고해서 직접 분석하여 답변을 작성해야합니다.

먼저 질문 내용과 질문 의도를 한 문장으로 정리하세요. 질문 내용을 칭찬해도 됩니다.
그 다음 질문에 대한 분석 결과를 한 문장으로 요약한 제목을 제시하세요.
제목 아래에 불릿포인트를 사용해서 핵심을 3~5가지 내용을 간결하게 설명하세요.

다음 문단부터 본격적으로 설명하세요.
이 때, 소제목을 적극적으로 활용하세요.

마지막 문단에서 결론을 한 문장으로 요약하세요.
투자 대가들의 명언을 인용하면서 마무리하세요.

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


def read_stream(response) -> str:
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
    return content


def set_page_config():
    st.set_page_config(
        page_icon="🐙",
        page_title="Mr. market octopus"
    )


def write_common_session_state():
    if "question" not in st.session_state:
        st.session_state["question"] = ""


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


def draw_seeking_alpha_report(related_contents: List[dict], expanded: bool = True):
    st.markdown("**해외 애널리스트 리포트**")
    for related_content in related_contents:
        selected_item_metadata = related_content["metadata"]
        with st.expander(selected_item_metadata["title"], expanded=expanded):
            st.markdown(selected_item_metadata['published_at'])
            st.markdown(f"score: {round(related_content['score'], 4)}")
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


def draw_fnguide_report(related_contents: List[dict], expanded: bool = True):
    st.markdown("**국내 애널리스트 리포트**")
    for related_content in related_contents:
        selected_item_metadata = related_content["metadata"]
        with st.expander(f"{selected_item_metadata['publisher']} - {selected_item_metadata['title']}", expanded=expanded):
            st.markdown(selected_item_metadata['published_at'])
            st.markdown(selected_item_metadata['writer'])
            st.markdown(f"score: {round(related_content['score'], 4)}")
            st.link_button(
                label="🌐 See full report",
                url=selected_item_metadata["public_url"],
                use_container_width=True
            )


def click_next_question(question: str):
    st.session_state.select = NOT_GIVEN
    st.session_state.question = question


def draw_next_questions(questions: List[str]):
    st.markdown("**다음에 물어보면 좋은 질문들**")
    for i, question in enumerate(questions):
        st.button(
            f"Q. {question}",
            key=f"question_{i}",
            on_click=click_next_question,
            args=(question,)
        )


def change_select():
    st.session_state.question = ""


def draw_auto_complete():
    return st.selectbox(
        label="예시 질문 선택",
        options=example_questions,
        on_change=change_select,
        key="select"
    )


def get_question(auto_complete: str):
    if st.session_state.question != "":
        return st.session_state.question
    elif auto_complete != "not select":
        return auto_complete
    return ""


def draw_intent(primary_intent: EnumPrimaryIntent, secondary_intent: Union[EnumMarketStrategyIntent, EnumIndustryStockIntent]):
    primary_intent_kor = PRIMARY_INTENT_DICT[primary_intent]
    write_markdown = f"**질문 의도: {primary_intent_kor}"
    if secondary_intent:
        if primary_intent == EnumPrimaryIntent.STOCK_MARKET_STRATEGY:
            secondary_intent_kor = ENUM_MARKET_STRATEGY_INTENT_DICT[secondary_intent]
        else:
            secondary_intent_kor = ENUM_INDUSTRY_STOCK_INTENT_DICT[secondary_intent]
        write_markdown += f" > {secondary_intent_kor}"
    write_markdown += "**"
    st.markdown(write_markdown)
