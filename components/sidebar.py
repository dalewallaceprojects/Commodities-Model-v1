"""
components/sidebar.py
Renders the sidebar with commodity selector, ticker input, chart controls, and news filters.
Returns a dict of all user selections.
"""

import streamlit as st
from config.settings import NEWS_DEFAULT_AGE
from config.commodities import list_commodities, get_commodity


def render_sidebar() -> dict:
    """Render the full sidebar and return user selections + commodity module."""
    available = list_commodities()

    with st.sidebar:
        # Commodity selector (only shows if 2+ registered)
        if len(available) > 1:
            chosen = st.selectbox("Commodity", available)
        else:
            chosen = available[0]

        commodity_module = get_commodity(chosen)
        COMMODITY = commodity_module.COMMODITY
        risk_categories = commodity_module.RISK_CATEGORIES
        producing_regions = commodity_module.PRODUCING_REGIONS

        st.markdown(f"## {COMMODITY['symbol']} {COMMODITY['name']} Terminal")
        st.markdown("---")

        ticker = st.text_input("Ticker Symbol", COMMODITY["default_ticker"], help=COMMODITY["ticker_help"])
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
        "commodity_module": commodity_module,
        "ticker": ticker,
        "candlestick": view_type,
        "overlays": overlays,
        "selected_categories": selected_categories,
        "selected_regions": selected_regions,
        "max_age_days": max_age_days,
    }
