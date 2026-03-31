"""
app.py — Commodity Risk Intelligence Terminal
==============================================
Main entry point. This file is intentionally thin — it wires together
config, engines, and components. All logic lives in the modules.

Run:  streamlit run app.py
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# ── Config ──────────────────────────────────
from config.theme import get_css, section_label, PRIMARY, FONT_DISPLAY
from config.settings import Z_EXTREME, RSI_OB, RSI_OS
from config.commodities import list_commodities, get_commodity

# ── Engines ─────────────────────────────────
from engines.market_data import load_price_data, run_forecast, get_derived_values, get_stock_metrics
from engines.news_scraper import fetch_all_risk_news

# ── Components ──────────────────────────────
from components.sidebar import render_sidebar
from components.chart import render_date_range_selector, get_chart_range, build_price_chart
from components.tables import (
    render_technical_intelligence,
    render_price_targets,
    render_producing_regions,
    render_equity_table,
)
from components.news_feed import (
    render_category_breakdown,
    render_article_cards,
    render_export,
)


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Risk Terminal", page_icon="⬡")
st.markdown(get_css(), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# COMMODITY SELECTION
# ─────────────────────────────────────────────
available = list_commodities()
if len(available) == 1:
    commodity_module = get_commodity(available[0])
else:
    # Future: multi-commodity selector in sidebar
    with st.sidebar:
        chosen = st.selectbox("Commodity", available)
    commodity_module = get_commodity(chosen)

# Unpack commodity config
COMMODITY         = commodity_module.COMMODITY
PRODUCING_REGIONS = commodity_module.PRODUCING_REGIONS
RISK_CATEGORIES   = commodity_module.RISK_CATEGORIES
LINKED_STOCKS     = commodity_module.LINKED_STOCKS


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
ui = render_sidebar(
    commodity_name=COMMODITY["name"],
    commodity_symbol=COMMODITY["symbol"],
    default_ticker=COMMODITY["default_ticker"],
    ticker_help=COMMODITY["ticker_help"],
    risk_categories=RISK_CATEGORIES,
    producing_regions=PRODUCING_REGIONS,
)

ticker             = ui["ticker"]
candlestick        = ui["candlestick"]
overlays           = ui["overlays"]
selected_categories = ui["selected_categories"]
selected_regions   = ui["selected_regions"]
max_age_days       = ui["max_age_days"]


# ─────────────────────────────────────────────
# LOAD MARKET DATA
# ─────────────────────────────────────────────
with st.spinner("Pulling market data…"):
    df = load_price_data(ticker)

if df is None:
    st.error(f"❌ Could not load data for **{ticker}**. Check the ticker symbol and try again.")
    st.stop()

vals = get_derived_values(df)
forecast_dates, forecast_values = run_forecast(df["Close"])


# ═════════════════════════════════════════════
# LAYOUT — EVERYTHING STACKED VERTICALLY
# ═════════════════════════════════════════════

# ── Title + Metrics ─────────────────────────
st.markdown(
    f"# {COMMODITY['symbol']} {COMMODITY['name']} Risk Intelligence "
    f"— <span style='color:{PRIMARY}'>{ticker.upper()}</span>",
    unsafe_allow_html=True,
)

st.metric("Last Price", f"${vals['last_close']:,.2f}",
          f"{vals['day_chg']:+.2f} ({vals['day_chg_pct']:+.2f}%)")
st.metric("RSI (14)", f"{vals['last_rsi']:.1f}",
          "Overbought" if vals["last_rsi"] > RSI_OB else ("Oversold" if vals["last_rsi"] < RSI_OS else "Neutral"))
st.metric("Z-Score", f"{vals['last_z']:.2f}",
          "Extended" if abs(vals["last_z"]) > Z_EXTREME else "Within Range")
st.metric("ATR (14)", f"{vals['last_atr']:.2f}",
          "Expanding" if vals["last_atr"] > vals["atr_mean"] else "Contracting")
st.metric("Data Points", f"{vals['data_points']:,}",
          f"Since {vals['first_date'].strftime('%Y')}")

st.divider()


# ── Chart ───────────────────────────────────
st.markdown(section_label("📅", "Chart Range"), unsafe_allow_html=True)
range_label = render_date_range_selector()
chart_start, chart_end = get_chart_range(range_label, df, forecast_dates, overlays)

fig = build_price_chart(
    df, candlestick, overlays,
    forecast_dates, forecast_values,
    chart_start, chart_end,
)
st.plotly_chart(fig, width="stretch")


# ── Technical Intelligence ──────────────────
st.divider()
render_technical_intelligence(vals)

st.markdown("")
render_price_targets(vals["last_close"], forecast_dates, forecast_values)


# ── Producing Regions ───────────────────────
st.divider()
render_producing_regions(PRODUCING_REGIONS)


# ── Linked Equities ────────────────────────
st.divider()
st.markdown(f"## 📈 {COMMODITY['name']}-Linked Equities")
st.caption(
    f"Stocks with material exposure to {COMMODITY['name'].lower()} prices. "
    f"Commodity Beta (β) computed against {ticker.upper()} weekly returns over 2 years."
)

with st.spinner("Loading equity data & computing commodity betas…"):
    all_stock_data = {}
    for tick in LINKED_STOCKS:
        all_stock_data[tick] = get_stock_metrics(tick, ticker)

render_equity_table(LINKED_STOCKS, all_stock_data, ticker)


# ── Live Risk Intelligence Feed ─────────────
st.divider()
st.markdown("## 📡 Live Risk Intelligence Feed")
st.caption("Scraped from Google News RSS · Articles classified by keyword matching")

with st.spinner("Scanning news sources across all risk categories…"):
    news_df = fetch_all_risk_news(RISK_CATEGORIES, PRODUCING_REGIONS)

if news_df.empty:
    st.warning("No articles found. This may be due to rate limiting. Try again in a few minutes.")
else:
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    filtered = news_df.copy()

    if selected_categories:
        filtered = filtered[
            filtered["primary_category"].isin(selected_categories)
            | filtered["categories"].apply(
                lambda cats: any(c in selected_categories for c in cats)
            )
        ]

    if selected_regions:
        filtered = filtered[
            filtered["regions"].apply(
                lambda regs: any(r in selected_regions for r in regs) if regs else False
            )
        ]

    if "published" in filtered.columns:
        filtered = filtered[
            filtered["published"].isna() | (filtered["published"] >= cutoff_date)
        ]

    st.markdown(
        f"**{len(filtered)}** articles found · "
        f"**{news_df['source'].nunique()}** sources · "
        f"Last {max_age_days} days"
    )

    render_category_breakdown(filtered, RISK_CATEGORIES)
    render_article_cards(filtered, selected_categories, RISK_CATEGORIES)


# ── Export ──────────────────────────────────
st.divider()
render_export(news_df if not news_df.empty else pd.DataFrame())


# ── Footer ──────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#333;font-size:0.65rem;letter-spacing:0.15em;'>"
    f"{COMMODITY['name'].upper()} RISK TERMINAL · NOT FINANCIAL ADVICE · DATA VIA YAHOO FINANCE & GOOGLE NEWS RSS"
    "</div>",
    unsafe_allow_html=True,
)
