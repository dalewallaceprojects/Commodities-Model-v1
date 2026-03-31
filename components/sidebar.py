"""
components/sidebar.py
Renders the sidebar with ticker input, chart controls, and news filters.
Returns a dict of all user selections.
"""

import streamlit as st
from config.settings import NEWS_DEFAULT_AGE


def render_sidebar(
    commodity_name: str,
    commodity_symbol: str,
    default_ticker: str,
    ticker_help: str,
    risk_categories: dict,
    producing_regions: dict,
) -> dict:
    """Render the sidebar and return user selections."""
    with st.sidebar:
        st.markdown(f"## {commodity_symbol} {commodity_name} Terminal")
        st.markdown("---")

        ticker = st.text_input("Ticker Symbol", default_ticker, help=ticker_help)
        view_type = st.toggle("Candlestick Mode", value=True)
        overlays = st.multiselect(
            "Chart Overlays",
            ["Bollinger Bands", "Forecast", "SMA 50", "SMA 200"],
            default=["Forecast", "Bollinger Bands"],
        )

        st.markdown("---")
        st.markdown("##### 🔍 News Filters")

        selected_categories = st.multiselect(
            "Risk Categories",
            list(risk_categories.keys()),
            default=list(risk_categories.keys()),
        )
        selected_regions = st.multiselect(
            "Producing Regions",
            list(producing_regions.keys()),
            default=[],
            help="Leave empty to show all regions",
        )
        max_age_days = st.slider("Max article age (days)", 1, 90, NEWS_DEFAULT_AGE)

        st.markdown("---")
        st.caption("Market data via Yahoo Finance · News via Google News RSS · Forecast via Holt-Winters ES")

    return {
        "ticker": ticker,
        "candlestick": view_type,
        "overlays": overlays,
        "selected_categories": selected_categories,
        "selected_regions": selected_regions,
        "max_age_days": max_age_days,
    }
