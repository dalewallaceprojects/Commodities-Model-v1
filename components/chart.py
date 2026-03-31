"""
components/chart.py
Builds the main Plotly price chart with overlays and RSI subplot.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd

from config.theme import (
    BG_PRIMARY, CHART_UP, CHART_DOWN, CHART_LINE, CHART_FORECAST,
    CHART_SMA50, CHART_SMA200, CHART_BB, CHART_BB_FILL, CHART_RSI,
    CHART_GRID, PRIMARY, NEUTRAL, NEGATIVE, POSITIVE,
)
from config.settings import RSI_OB, RSI_OS


def render_date_range_selector() -> str:
    """Render date range radio buttons and return the selected label."""
    label = st.radio(
        "Select range",
        ["1D", "7D", "1M", "6M", "1Y", "MAX"],
        index=2,
        horizontal=True,
        label_visibility="collapsed",
    )
    return label


def get_chart_range(
    range_label: str,
    df: pd.DataFrame,
    forecast_dates: pd.DatetimeIndex | None,
    overlays: list[str],
) -> tuple[datetime, datetime]:
    """Calculate chart x-axis start and end from range selection."""
    deltas = {
        "1D": timedelta(days=1),
        "7D": timedelta(days=7),
        "1M": timedelta(days=30),
        "6M": timedelta(days=180),
        "1Y": timedelta(days=365),
    }

    today = datetime.now()
    chart_start = df.index[0] if range_label == "MAX" else today - deltas[range_label]
    chart_end = forecast_dates[-1] if ("Forecast" in overlays and forecast_dates is not None) else today

    return chart_start, chart_end


def build_price_chart(
    df: pd.DataFrame,
    candlestick: bool,
    overlays: list[str],
    forecast_dates: pd.DatetimeIndex | None,
    forecast_values: pd.Series | None,
    chart_start: datetime,
    chart_end: datetime,
) -> go.Figure:
    """Build the main price + RSI chart figure."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.75, 0.25],
        subplot_titles=("", "RSI (14)"),
    )

    # Price
    if candlestick:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name="Price",
            increasing_line_color=CHART_UP,
            decreasing_line_color=CHART_DOWN,
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"],
            name="Price", line=dict(color=CHART_LINE, width=1.5),
        ), row=1, col=1)

    # Bollinger Bands
    if "Bollinger Bands" in overlays:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Up"],
            line=dict(color=CHART_BB, width=1),
            name="BB Upper", showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_Low"],
            line=dict(color=CHART_BB, width=1),
            fill="tonexty", fillcolor=CHART_BB_FILL,
            name="BB Lower", showlegend=False,
        ), row=1, col=1)

    # Forecast
    if "Forecast" in overlays and forecast_dates is not None:
        fig.add_trace(go.Scatter(
            x=forecast_dates, y=forecast_values,
            name="Projection",
            line=dict(color=CHART_FORECAST, dash="dash", width=1.5),
        ), row=1, col=1)

    # SMAs
    if "SMA 50" in overlays:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA50"],
            name="SMA 50", line=dict(color=CHART_SMA50, width=1),
        ), row=1, col=1)

    if "SMA 200" in overlays:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA200"],
            name="SMA 200", line=dict(color=CHART_SMA200, width=1),
        ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI", line=dict(color=CHART_RSI, width=1.2), showlegend=False,
    ), row=2, col=1)

    for level, colour in [(RSI_OB, "rgba(255,59,48,0.4)"), (RSI_OS, "rgba(0,255,136,0.4)")]:
        fig.add_hline(y=level, line=dict(color=colour, width=1, dash="dot"), row=2, col=1)

    # Layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_PRIMARY,
        height=820,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation="h", x=0, y=1.02,
            font=dict(color=NEUTRAL, size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(type="date", range=[chart_start, chart_end], rangeslider=dict(visible=False), gridcolor=CHART_GRID),
        xaxis2=dict(gridcolor=CHART_GRID),
        yaxis=dict(gridcolor=CHART_GRID, title=dict(text="PRICE (USD)", font=dict(color=PRIMARY, size=10)), tickfont=dict(color=NEUTRAL, size=10)),
        yaxis2=dict(gridcolor=CHART_GRID, title=dict(text="RSI", font=dict(color=CHART_RSI, size=10)), tickfont=dict(color=NEUTRAL, size=10), range=[0, 100]),
    )

    return fig
