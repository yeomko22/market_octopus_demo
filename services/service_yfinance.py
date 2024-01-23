from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf


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
    return go.Figure(
        data=[trace_1d, trace_5d, trace_1mo, trace_6mo],
        layout=layout
    )
