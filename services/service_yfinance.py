from datetime import datetime, timedelta
from typing import Optional, Tuple, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


def select_ticker(related_reports: List[dict]) -> Optional[yf.Ticker]:
    selected_ticker = None
    primary_tickers = []
    for related_report in related_reports:
        cur_tickers = related_report["metadata"].get("parimary_tickers", [])
        for ticker in cur_tickers:
            if ticker not in primary_tickers:
                primary_tickers.append(ticker)
    for primary_ticker in primary_tickers:
        ticker = yf.Ticker(primary_ticker)
        history = ticker.history(period="1mo")
        if not history.empty:
            selected_ticker = ticker
            break
    return selected_ticker


def get_related_stock_data(ticker: yf.Ticker) -> List[Tuple[str, pd.DataFrame]]:
    dataframe_list: List[Tuple[str, pd.DataFrame]] = []
    start = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")
    df_1d = ticker.history(start=start, end=end, interval="1h").reset_index()
    if not df_1d.empty:
        df_1d["ds"] = df_1d["Datetime"].dt.strftime("%Y-%m-%d %H")
        dataframe_list.append(("1D", df_1d))

    df_5d = ticker.history(period="5d", interval="1h").reset_index()
    if not df_5d.empty:
        df_5d["ds"] = df_5d["Datetime"].dt.strftime("%Y-%m-%d %H")
        dataframe_list.append(("5D", df_5d))

    df_1mo = ticker.history(period="1mo").reset_index()
    if not df_1mo.empty:
        df_1mo["ds"] = df_1mo["Date"].dt.strftime("%Y-%m-%d")
        dataframe_list.append(("1M", df_1mo))

    df_6mo = ticker.history(period="6mo").reset_index()
    if not df_6mo.empty:
        df_6mo["ds"] = df_6mo["Date"].dt.strftime("%Y-%m-%d")
        dataframe_list.append(("6M", df_6mo))
    return dataframe_list


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
    dataframe_list = get_related_stock_data(ticker)
    trace_list = []
    buttons = []
    for i, (label, dataframe) in enumerate(dataframe_list):
        trace = draw_trace(dataframe, label, visible=True if i == 0 else False)
        trace_list.append(trace)
        buttons.append({
            "label": label,
            "method": "update",
            "args": [{"visible": [x == i for x in range(len(dataframe_list))]}]
        })
    updatemenus = [
        dict(
            type="buttons",
            direction="left",
            x=0.95,
            y=1.5,
            showactive=True,
            active=0,
            buttons=buttons
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
    return go.Figure(
        data=trace_list,
        layout=layout
    )


def draw_ticker_information(oversea_report_list: List[dict]):
    selected_ticker = select_ticker(oversea_report_list)
    if selected_ticker:
        st.markdown("**📈realted stock**")
        with st.expander(selected_ticker.ticker, expanded=True):
            fig = draw_stock_price(selected_ticker)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={'displayModeBar': False}
            )
