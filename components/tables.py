"""
components/tables.py
Renders all HTML tables with the terminal dark theme.
Uses config/theme.py constants for consistent styling.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from config.theme import (
    TH_STYLE, TD_STYLE, TABLE_WRAPPER, section_label, colored_cell,
    BG_PRIMARY, BG_SECONDARY, BORDER, PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    POSITIVE, NEGATIVE, MIXED, FONT_DISPLAY, FONT_MONO,
    RELATIONSHIP_COLOURS,
)
from config.settings import (
    Z_EXTREME, RSI_OB, RSI_OS,
    BETA_HIGH_THRESHOLD, BETA_LOW_THRESHOLD,
)


def render_technical_intelligence(vals: dict) -> None:
    """Render the technical intelligence table."""
    st.markdown(section_label("🧬", "Technical Intelligence"), unsafe_allow_html=True)

    z_sig   = ("Extreme Extension", NEGATIVE) if abs(vals["last_z"]) > Z_EXTREME else ("Neutral", "#aaa")
    atr_sig = ("Expanding", "#FF9500") if vals["last_atr"] > vals["atr_mean"] else ("Contracting", "#aaa")
    rsi_sig = ("Overbought", NEGATIVE) if vals["last_rsi"] > RSI_OB else (("Oversold", POSITIVE) if vals["last_rsi"] < RSI_OS else ("Neutral", "#aaa"))

    rows = ""
    for name, val, (sig_text, sig_color) in [
        ("Z-Score (Mean Rev.)", f"{vals['last_z']:.2f}", z_sig),
        ("ATR (Volatility)", f"{vals['last_atr']:.2f}", atr_sig),
        ("RSI (Momentum)", f"{vals['last_rsi']:.1f}", rsi_sig),
    ]:
        rows += f'<tr><td {TD_STYLE}>{name}</td><td {TD_STYLE}>{val}</td>{colored_cell(sig_text, sig_color, bold=True)}</tr>'

    st.markdown(
        f'<table {TABLE_WRAPPER}>'
        f'<thead><tr><th {TH_STYLE} align="left">Indicator</th><th {TH_STYLE} align="left">Value</th><th {TH_STYLE} align="left">Signal</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>',
        unsafe_allow_html=True,
    )


def render_price_targets(
    last_close: float,
    forecast_dates: pd.DatetimeIndex,
    forecast_values: pd.Series,
) -> None:
    """Render the Holt-Winters price targets table."""
    st.markdown(section_label("🎯", "Price Targets (Holt-Winters)"), unsafe_allow_html=True)

    horizon_map = {"1 Week": 4, "1 Month": 20, "3 Months": 62, "1 Year": 251}
    rows = ""
    for label, idx in horizon_map.items():
        if idx < len(forecast_values):
            fv = float(forecast_values.iloc[idx])
            ret = (fv / last_close - 1) * 100
            ret_color = POSITIVE if ret >= 0 else NEGATIVE
            rows += (
                f'<tr><td {TD_STYLE}>{label}</td>'
                f'<td {TD_STYLE}>{forecast_dates[idx].strftime("%Y-%m-%d")}</td>'
                f'<td {TD_STYLE}>${fv:,.2f}</td>'
                f'{colored_cell(f"{ret:+.2f}%", ret_color, bold=True)}</tr>'
            )

    st.markdown(
        f'<table {TABLE_WRAPPER}>'
        f'<thead><tr><th {TH_STYLE} align="left">Horizon</th><th {TH_STYLE} align="left">Target Date</th><th {TH_STYLE} align="left">Target Price</th><th {TH_STYLE} align="left">Proj. Return</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>',
        unsafe_allow_html=True,
    )


def render_producing_regions(producing_regions: dict) -> None:
    """Render the producing regions table."""
    st.markdown(section_label("🌐", "Key Producing Regions"), unsafe_allow_html=True)

    rows = ""
    for region, info in producing_regions.items():
        rows += (
            f'<tr><td {TD_STYLE}>{region}</td>'
            f'<td {TD_STYLE}>{info["share"]}</td>'
            f'<td {TD_STYLE}>{", ".join(info["keywords"][:3])}</td></tr>'
        )

    st.markdown(
        f'<table {TABLE_WRAPPER}>'
        f'<thead><tr><th {TH_STYLE} align="left">Region</th><th {TH_STYLE} align="left">Global Share</th><th {TH_STYLE} align="left">Search Terms</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>',
        unsafe_allow_html=True,
    )


def render_equity_table(
    linked_stocks: dict,
    stock_data: dict,
    commodity_ticker: str,
) -> None:
    """Render the cobalt-linked equities tables grouped by relationship."""
    _sth = (
        f'style="background:{BG_SECONDARY};color:{PRIMARY};'
        f'border-bottom:1px solid {PRIMARY};padding:10px 12px;'
        f'font-family:{FONT_DISPLAY};font-size:0.7rem;'
        f'letter-spacing:0.08em;text-transform:uppercase;"'
    )
    _std = (
        f'style="background:{BG_PRIMARY};border-bottom:1px solid {BORDER};'
        f'padding:10px 12px;"'
    )

    for relationship, label, emoji in [
        ("positive", "Positively Correlated — cobalt price rises benefit these stocks", "🟢"),
        ("negative", "Negatively Correlated — cobalt price rises hurt these stocks", "🔴"),
        ("mixed", "Mixed / Indirect — cobalt price rises have mixed effects", "🟡"),
    ]:
        group = {k: v for k, v in linked_stocks.items() if v["relationship"] == relationship}
        if not group:
            continue

        rel_color = RELATIONSHIP_COLOURS[relationship]
        st.markdown(
            f"<div style='font-family:{FONT_DISPLAY};font-size:0.7rem;letter-spacing:0.15em;"
            f"text-transform:uppercase;color:{rel_color};margin:1.5rem 0 0.8rem;"
            f"border-left:2px solid {rel_color};padding-left:0.6rem;'>{emoji} {label}</div>",
            unsafe_allow_html=True,
        )

        rows = ""
        for tick, info in group.items():
            m = stock_data.get(tick)
            if m:
                price_str = f"${m['price']:,.2f}"
                day_str = f"{m['day_change']:+.2f}%"
                day_color = POSITIVE if m["day_change"] >= 0 else NEGATIVE
                mo1_str = f"{m['mo1_change']:+.1f}%" if m["mo1_change"] is not None else "—"
                mo1_color = POSITIVE if (m["mo1_change"] or 0) >= 0 else NEGATIVE
                mo3_str = f"{m['mo3_change']:+.1f}%" if m["mo3_change"] is not None else "—"
                mo3_color = POSITIVE if (m["mo3_change"] or 0) >= 0 else NEGATIVE

                if m["commodity_beta"] is not None:
                    bv = m["commodity_beta"]
                    beta_str = f"{bv:+.2f}"
                    beta_color = POSITIVE if bv > BETA_HIGH_THRESHOLD else (NEGATIVE if bv < BETA_LOW_THRESHOLD else MIXED)
                else:
                    beta_str = "—"
                    beta_color = TEXT_MUTED
            else:
                price_str = day_str = mo1_str = mo3_str = beta_str = "—"
                day_color = mo1_color = mo3_color = beta_color = TEXT_MUTED

            rows += (
                f'<tr>'
                f'<td {_std}><span style="color:{PRIMARY};font-family:{FONT_DISPLAY};font-weight:700;">{tick}</span><br><span style="color:#666;font-size:0.7rem;">{info["name"]}</span></td>'
                f'<td {_std} align="right"><span style="color:{TEXT_SECONDARY};">{price_str}</span></td>'
                f'<td {_std} align="right"><span style="color:{day_color};">{day_str}</span></td>'
                f'<td {_std} align="right"><span style="color:{mo1_color};">{mo1_str}</span></td>'
                f'<td {_std} align="right"><span style="color:{mo3_color};">{mo3_str}</span></td>'
                f'<td {_std} align="right"><span style="color:{beta_color};font-weight:700;">{beta_str}</span></td>'
                f'<td {_std}><span style="color:{TEXT_MUTED};font-size:0.7rem;">{info["exposure"]}</span></td>'
                f'</tr>'
            )

        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;background:{BG_PRIMARY};font-family:{FONT_MONO};font-size:0.8rem;">'
            f'<thead><tr>'
            f'<th {_sth} align="left">Ticker</th>'
            f'<th {_sth} align="right">Price</th>'
            f'<th {_sth} align="right">Day</th>'
            f'<th {_sth} align="right">1M</th>'
            f'<th {_sth} align="right">3M</th>'
            f'<th {_sth} align="right">Commodity &#946;</th>'
            f'<th {_sth} align="left">Exposure</th>'
            f'</tr></thead>'
            f'<tbody>{rows}</tbody></table>',
            unsafe_allow_html=True,
        )
