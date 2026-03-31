"""
components/news_feed.py
Renders the live risk intelligence feed with category breakdown,
article cards, and export functionality.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config.theme import (
    BG_PRIMARY, BG_SECONDARY, BG_CARD, BORDER, TEXT_SECONDARY, TEXT_MUTED,
    TEXT_FAINT, TH_STYLE, TD_STYLE, TABLE_WRAPPER,
)


def _article_age_str(published: datetime | None) -> str:
    """Format an article's age as a human-readable string."""
    if pd.isna(published):
        return ""
    age = datetime.now() - published
    if age.days == 0:
        return f"{age.seconds // 3600}h ago"
    elif age.days == 1:
        return "Yesterday"
    return f"{age.days}d ago"


def render_category_breakdown(filtered: pd.DataFrame, risk_categories: dict) -> None:
    """Render the vertical category count bars."""
    cat_counts = {}
    for _, row in filtered.iterrows():
        for cat in row["categories"]:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    if not cat_counts:
        return

    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        color = risk_categories.get(cat, {}).get("color", "#aaa")
        st.markdown(
            f"<div style='background:{BG_SECONDARY};border:1px solid {BORDER};"
            f"border-left:3px solid {color};padding:10px 14px;margin-bottom:4px;"
            f"display:flex;justify-content:space-between;align-items:center;'>"
            f"<span style='font-size:0.75rem;color:{TEXT_SECONDARY};'>{cat}</span>"
            f"<span style='font-size:1rem;font-weight:800;color:{color}'>{count}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("")


def render_article_cards(
    filtered: pd.DataFrame,
    selected_categories: list[str],
    risk_categories: dict,
) -> None:
    """Render article cards grouped by risk category in expanders."""
    for category in selected_categories:
        cat_articles = filtered[
            filtered["categories"].apply(lambda cats: category in cats)
        ]
        if cat_articles.empty:
            continue

        color = risk_categories.get(category, {}).get("color", "#aaa")
        with st.expander(f"{category}  —  {len(cat_articles)} articles", expanded=True):
            for _, article in cat_articles.iterrows():
                pub_str = _article_age_str(article["published"])
                region_tags = ""
                if article["regions"]:
                    region_tags = " ".join(
                        f"<span style='background:#111;color:#888;padding:1px 6px;"
                        f"font-size:0.6rem;border:1px solid #222;'>"
                        f"{r.split('(')[0].strip()}</span>"
                        for r in article["regions"]
                    )

                st.markdown(
                    f"<div class='risk-card'><div>"
                    f"<div style='margin-bottom:6px;'>"
                    f"<span class='risk-badge' style='background:{color};color:#000;'>"
                    f"{category.split(' ', 1)[-1]}</span>"
                    f"<span style='color:{TEXT_MUTED};font-size:0.7rem;'>{article['source']}</span>"
                    f"<span style='color:{TEXT_FAINT};font-size:0.7rem;margin-left:8px;'>{pub_str}</span>"
                    f"</div>"
                    f"<a href='{article['link']}' target='_blank' "
                    f"style='color:#ddd;text-decoration:none;font-size:0.85rem;line-height:1.4;'>"
                    f"{article['title']}</a>"
                    f"<div style='margin-top:6px;'>{region_tags}</div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

    # General / uncategorised
    general = filtered[filtered["primary_category"] == "📊 General Market"]
    if not general.empty:
        with st.expander(f"📊 General Market  —  {len(general)} articles", expanded=False):
            for _, article in general.iterrows():
                pub_str = _article_age_str(article["published"])
                st.markdown(
                    f"<div class='risk-card'>"
                    f"<span style='color:{TEXT_MUTED};font-size:0.7rem;'>{article['source']} · {pub_str}</span><br>"
                    f"<a href='{article['link']}' target='_blank' "
                    f"style='color:#ddd;text-decoration:none;font-size:0.85rem;'>"
                    f"{article['title']}</a></div>",
                    unsafe_allow_html=True,
                )


def render_export(news_df: pd.DataFrame) -> None:
    """Render the CSV export section."""
    with st.expander("📥 Export Raw Data"):
        if news_df.empty:
            st.info("No data to export.")
            return

        export_df = news_df[["title", "source", "link", "published", "primary_category", "summary"]].copy()
        export_df["regions"] = news_df["regions"].apply(lambda x: "; ".join(x) if x else "")
        export_df["all_categories"] = news_df["categories"].apply(lambda x: "; ".join(x) if x else "")

        csv = export_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "risk_intelligence.csv", "text/csv")

        _eth = f'style="background:{BG_SECONDARY};color:#00FBFF;border-bottom:1px solid #00FBFF;padding:8px 10px;text-align:left;font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.08em;text-transform:uppercase;"'
        _etd = f'style="background:{BG_PRIMARY};color:{TEXT_SECONDARY};border-bottom:1px solid {BORDER};padding:8px 10px;font-size:0.72rem;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"'

        rows = ""
        for _, row in export_df.head(50).iterrows():
            pub = str(row["published"])[:10] if pd.notna(row["published"]) else "—"
            title_safe = str(row["title"]).replace("<", "&lt;").replace(">", "&gt;")[:80]
            src_safe = str(row["source"]).replace("<", "&lt;").replace(">", "&gt;")
            cat_safe = str(row["primary_category"]).replace("<", "&lt;").replace(">", "&gt;")
            rows += f'<tr><td {_etd}>{pub}</td><td {_etd}>{src_safe}</td><td {_etd}>{title_safe}</td><td {_etd}>{cat_safe}</td></tr>'

        st.markdown(
            f'<table {TABLE_WRAPPER}>'
            f'<thead><tr><th {_eth}>Date</th><th {_eth}>Source</th><th {_eth}>Title</th><th {_eth}>Category</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>',
            unsafe_allow_html=True,
        )
