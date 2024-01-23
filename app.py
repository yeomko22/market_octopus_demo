import pandas as pd
from typing import Tuple
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
import yfinance as yf

from services.service_google import translate
from services.service_openai import get_embedding, get_streaming_response
from services.service_pinecone import search_seeking_alpha_summary, search_seeking_alpha_content
import plotly.graph_objects as go

st.set_page_config(
    page_icon="🤖",
    page_title="AI 애널리스트",
)
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


def generate_prompt(instruct: str, question: str, selected_item: dict) -> str:
    prompt = f"""
{instruct}
---
질문: {question}  
관련 리포트 

title: {selected_item["title"]}

summary: {selected_item["summary"]}

content: {selected_item["content"]}
---
""".strip()
    return prompt


st.title("AI 애널리스트")
NOT_GIVEN = "선택 안함"
auto_complete = st.selectbox("예시 질문 선택", options=[
    NOT_GIVEN,
    "최근 발표된 미국 금리 인하가 주식 시장에 어떤 영향을 미칠까?",
    "정부의 새로운 부동산 정책이 주식 시장에 어떤 영향을 미칠까?",
    "최근 주식시장의 전반적인 트렌드는?",
    "올해 주식시장의 주요 이벤트나 추세는?",
    "지금과 같은 금융시장 환경에서는 어떤 투자 전략을 취해야할까?",
    "생성 AI 기술에 영향을 받을 종목은 어떤 것들이 있을까?",
    "올해 어떤 산업군이 좋은 성괄르 낼 것으로 예상해?",
    "삼성 SDS의 주식은 현재 투자하기 좋은 선택일까?"
])
example_ai_role = "당신은 전문 증권 애널리스트입니다."
example_prompt = """
유저의 질문과 참고할만한 애널리스트 리포트 문단이 주어집니다.
기존에 알고 있었던 지식과 참고 자료를 활용해서 스스로 분석한 결과를 작성하세요.
구체적인 수치나 전문적인 자료를 언급해주세요.
반드시 한국어로 답변하세요.
두괄식으로 핵심을 먼저 말해주세요.
불릿 포인트를 사용해서 핵심을 정리해주세요.
""".strip()
with st.form("form"):
    system_message = st.text_input(label="AI 역할", value=example_ai_role)
    instruct = st.text_area(label="답변 생성시 고려사항", value=example_prompt, height=120)
    question = st.text_input(
        "질문",
        placeholder="질문을 입력해주세요",
        value=auto_complete if auto_complete != NOT_GIVEN else ""
    )
    submit = st.form_submit_button(label="제출")


def select_ticker(selected_report: dict) -> Optional[yf.Ticker]:
    selected_ticker = None
    # TODO: 오타, 고쳐야함
    if "parimary_tickers" not in selected_report["metadata"]:
        return selected_ticker
    primary_tickers = selected_report["metadata"]["parimary_tickers"]
    for primary_ticker in primary_tickers:
        ticker = yf.Ticker(primary_ticker)
        history = ticker.history(period="1d")
        if not history.empty:
            selected_ticker = ticker
            break
    return selected_ticker


def select_seeking_alpha_report(related_report_list: List[dict]) -> Optional[dict]:
    related_report_ids = [x["metadata"]["id"] for x in related_report_list]
    return search_seeking_alpha_content(question_embedding, related_report_ids)


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


def get_related_stock_data(ticker: yf.Ticker) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")
    df_1d = ticker.history(start=start, end=end, interval="1h").reset_index()
    df_1d["ds"] = df_1d["Datetime"].dt.strftime("%Y-%m-%d %H")

    df_5d = ticker.history(period="5d", interval="1h").reset_index()
    df_5d["ds"] = df_5d["Datetime"].dt.strftime("%Y-%m-%d %H")

    df_1mo = ticker.history(period="1mo").reset_index()
    df_1mo["ds"] = df_1mo["Date"].dt.strftime("%Y-%m-%d")

    df_6mo = ticker.history(period="6mo").reset_index()
    df_6mo["ds"] = df_6mo["Date"].dt.strftime("%Y-%m-%d")
    return df_1d, df_5d, df_1mo, df_6mo


def draw_trace(df: pd.DataFrame, name: str, visible=False) -> go.Scatter:
    return go.Scatter(
        x=df["ds"],
        y=df["High"],
        name=name,
        mode="lines",
        line=dict(color='#F06A6A'),
        visible=visible,
    )


def draw_stock_price(ticker: yf.Ticker):
    df_1d, df_5d, df_1mo, df_6mo = get_related_stock_data(ticker)
    trace_1d = draw_trace(df_1d, "1D", visible=False)
    trace_5d = draw_trace(df_5d, "5D", visible=True)
    trace_1mo = draw_trace(df_1mo, "1mo", visible=False)
    trace_6mo = draw_trace(df_6mo, "6mo", visible=False)
    updatemenus = [
        dict(
            type="buttons",
            direction="left",
            x=0.95,
            y=1.5,
            showactive=True,
            active=1,
            buttons=[
                dict(
                    label="1D",
                    method="update",
                    args=[{'visible': [True, False, False, False]}]
                ),
                dict(
                    label="5D",
                    method="update",
                    args=[{'visible': [False, True, False, False]}],
                ),
                dict(
                    label="1M",
                    method="update",
                    args=[{'visible': [False, False, True, False]}]
                ),
                dict(
                    label="6M",
                    method="update",
                    args=[{'visible': [False, False, False, True]}]
                ),
            ]
        )
    ]
    layout = go.Layout(
        xaxis=dict(
            type="category",
            showticklabels=False,
        ),
        height=150,
        margin=dict(l=0, r=0, t=0, b=0),
        updatemenus=updatemenus
    )
    st.markdown("**📈realted stock**")
    with st.expander(ticker.ticker, expanded=True):
        fig = go.Figure(
            data=[trace_1d, trace_5d, trace_1mo, trace_6mo],
            layout=layout
        )
        config = {'displayModeBar': False}
        st.plotly_chart(fig, use_container_width=True, config=config)


if submit:
    if not question:
        st.error("질문을 입력해주세요.")
        st.stop()
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        st.markdown("**📝seeking alpha report**")
        with st.spinner("관련 리포트 검색 중..."):
            eng_question = translate([question])[0]
            question_embedding = get_embedding([eng_question])[0]

            # 1. question과 summary의 유사도를 구해서 가장 유사한 리포트를 3개 찾는다.
            # 2. 3개의 리포트 중에서 질문과 가장 관련도가 높은 단락을 선택한다.
            related_report_list = search_seeking_alpha_summary(question_embedding, k=5)
            if not related_report_list:
                st.markdown("관련 리포트를 찾을 수 없습니다.")
            else:
                selected_report = select_seeking_alpha_report(related_report_list)
                draw_seeking_alpha_report(selected_report)
                selected_ticker = select_ticker(selected_report)
                if selected_ticker:
                    with st.spinner("관련 주식 정보 검색 중..."):
                        draw_stock_price(selected_ticker)
    with col2:
        st.markdown("**🧠AI 의견**")
        selected_report_metadata = selected_report["metadata"]
        with st.spinner("AI 의견 생성 중..."):
            prompt = generate_prompt(instruct, question, selected_report_metadata)
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
            streaming_response = get_streaming_response(messages)
        read_stream(streaming_response)
