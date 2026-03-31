"""
build.py — Static Site Generator
=================================
Fetches live data from Yahoo Finance and Google News RSS,
then generates static HTML pages into docs/ for GitHub Pages.

Run:  python build.py
Then: git add docs/ && git commit -m "Rebuild site" && git push

GitHub Pages serves from the docs/ folder on main branch.
"""

import os
import sys

def fix_antimeridian(routes):
    fixed = []
    for route in routes:
        new_waypoints = [route["waypoints"][0]]
        for i in range(1, len(route["waypoints"])):
            prev_lng = new_waypoints[-1][1]
            curr = route["waypoints"][i]
            lng = curr[1]
            if prev_lng - lng > 180:
                lng += 360
            elif lng - prev_lng > 180:
                lng -= 360
            new_waypoints.append([curr[0], lng])
        fixed.append({**route, "waypoints": new_waypoints})
    return fixed

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from config.commodities import list_commodities, get_commodity
from config.settings import Z_EXTREME, RSI_OB, RSI_OS, BETA_HIGH_THRESHOLD, BETA_LOW_THRESHOLD
from engines.market_data import load_price_data, get_derived_values, get_stock_metrics
from engines.news_scraper import fetch_all_risk_news


# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader("templates"))
build_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
all_commodity_names = list_commodities()


def format_stock_metrics(m: dict | None) -> dict:
    """Format raw stock metrics into display strings with colours."""
    if m is None:
        return {
            "price_str": "—", "day_str": "—", "day_color": "#555",
            "mo1_str": "—", "mo1_color": "#555",
            "mo3_str": "—", "mo3_color": "#555",
            "beta_str": "—", "beta_color": "#555",
        }

    day_color = "#00FF88" if m["day_change"] >= 0 else "#FF3B30"
    mo1_color = "#00FF88" if (m["mo1_change"] or 0) >= 0 else "#FF3B30"
    mo3_color = "#00FF88" if (m["mo3_change"] or 0) >= 0 else "#FF3B30"

    if m["commodity_beta"] is not None:
        bv = m["commodity_beta"]
        beta_str = f"{bv:+.2f}"
        beta_color = "#00FF88" if bv > BETA_HIGH_THRESHOLD else ("#FF3B30" if bv < BETA_LOW_THRESHOLD else "#FFD700")
    else:
        beta_str = "—"
        beta_color = "#555"

    return {
        "price_str": f"${m['price']:,.2f}",
        "day_str": f"{m['day_change']:+.2f}%",
        "day_color": day_color,
        "mo1_str": f"{m['mo1_change']:+.1f}%" if m["mo1_change"] is not None else "—",
        "mo1_color": mo1_color,
        "mo3_str": f"{m['mo3_change']:+.1f}%" if m["mo3_change"] is not None else "—",
        "mo3_color": mo3_color,
        "beta_str": beta_str,
        "beta_color": beta_color,
    }


def article_age_str(published) -> str:
    """Format article age as human-readable string."""
    if published is None:
        return ""
    try:
        age = datetime.now() - published
        if age.days == 0:
            return f"{age.seconds // 3600}h ago"
        elif age.days == 1:
            return "Yesterday"
        return f"{age.days}d ago"
    except Exception:
        return ""


# ─────────────────────────────────────────────
# BUILD INDEX PAGE
# ─────────────────────────────────────────────
def build_index():
    """Generate the landing page."""
    print("📄 Building index.html...")
    commodities = {}
    for name in all_commodity_names:
        mod = get_commodity(name)
        commodities[name] = mod.COMMODITY

    template = env.get_template("index.html")
    html = template.render(
        commodities=commodities,
        build_time=build_time,
    )
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print("   ✅ index.html")


# ─────────────────────────────────────────────
# BUILD COMMODITY PAGE
# ─────────────────────────────────────────────
def build_commodity(name: str):
    """Generate a single commodity dashboard page."""
    print(f"\n{'='*50}")
    print(f"📦 Building {name}...")
    print(f"{'='*50}")

    mod = get_commodity(name)
    commodity = mod.COMMODITY
    ticker = commodity["default_ticker"]
    producing_regions = mod.PRODUCING_REGIONS
    risk_categories = mod.RISK_CATEGORIES
    linked_stocks = mod.LINKED_STOCKS
    geo_raw = getattr(mod, "GEO", None)
    if geo_raw:
        geo_data = {
            "mines": geo_raw.get("mines", []),
            "refineries": geo_raw.get("refineries", []),
            "ports": geo_raw.get("ports", []),
            "chokepoints": geo_raw.get("chokepoints", []),
            "shipping_routes": fix_antimeridian(geo_raw.get("routes", [])),
            "mine_label": "Mines" if "cobalt" in name.lower() else "Plantations",
        }
    else:
        geo_data = None

    # ── Market data ──
    print(f"   📈 Fetching market data for {ticker}...")
    df = load_price_data(ticker)
    if df is None:
        print(f"   ❌ Could not load data for {ticker}. Skipping.")
        return

    vals = get_derived_values(df)

    # ── Technical signals ──
    z_sig = ("Extreme Extension", "#FF3B30") if abs(vals["last_z"]) > Z_EXTREME else ("Neutral", "#aaa")
    atr_sig = ("Expanding", "#FF9500") if vals["last_atr"] > vals["atr_mean"] else ("Contracting", "#aaa")
    rsi_sig = ("Overbought", "#FF3B30") if vals["last_rsi"] > RSI_OB else (("Oversold", "#00FF88") if vals["last_rsi"] < RSI_OS else ("Neutral", "#aaa"))

    tech_signals = [
        {"name": "Z-Score (Mean Rev.)", "value": f"{vals['last_z']:.2f}", "signal": z_sig[0], "color": z_sig[1]},
        {"name": "ATR (Volatility)", "value": f"{vals['last_atr']:.2f}", "signal": atr_sig[0], "color": atr_sig[1]},
        {"name": "RSI (Momentum)", "value": f"{vals['last_rsi']:.1f}", "signal": rsi_sig[0], "color": rsi_sig[1]},
    ]

    # ── Stock metrics ──
    print(f"   📊 Fetching equity data ({len(linked_stocks)} stocks)...")
    stock_groups = {"positive": [], "negative": [], "mixed": []}
    for tick, info in linked_stocks.items():
        print(f"      → {tick}...")
        m = get_stock_metrics(tick, ticker)
        formatted = format_stock_metrics(m)
        stock_groups[info["relationship"]].append((tick, info, formatted))

    # ── News ──
    print(f"   📰 Scraping news ({sum(len(c['queries']) for c in risk_categories.values())} queries)...")
    news_df = fetch_all_risk_news(risk_categories, producing_regions)

    article_count = len(news_df) if not news_df.empty else 0
    source_count = news_df["source"].nunique() if not news_df.empty else 0

    # Category counts
    cat_counts = {}
    if not news_df.empty:
        for _, row in news_df.iterrows():
            for cat in row["categories"]:
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

    category_counts = []
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        color = risk_categories.get(cat, {}).get("color", "#aaa")
        category_counts.append((cat, count, color))

    # Articles grouped by category
    articles_by_category = []
    for cat, config in risk_categories.items():
        if news_df.empty:
            continue
        cat_articles = news_df[news_df["categories"].apply(lambda cats: cat in cats)]
        if cat_articles.empty:
            continue

        articles = []
        for _, row in cat_articles.iterrows():
            articles.append({
                "title": row["title"],
                "source": row["source"],
                "link": row["link"],
                "age_str": article_age_str(row.get("published")),
                "regions": row.get("regions", []),
            })

        articles_by_category.append((cat, articles, config["color"]))

    # ── Geo data ──

    geo = getattr(mod, "GEO", None)

    # ── Render ──

    print(f"   🔨 Rendering HTML...")
    template = env.get_template("commodity.html")
    html = template.render(
        commodity=commodity,
        ticker=ticker,
        vals=vals,
        tech_signals=tech_signals,
        producing_regions=producing_regions,
        stock_groups=stock_groups,
        article_count=article_count,
        source_count=source_count,
        category_counts=category_counts,
        articles_by_category=articles_by_category,
        all_commodities=all_commodity_names,
        build_time=build_time,
        geo_data=geo_data,
        geo=geo,
    )

    filename = f"{name.lower()}.html"
    (DOCS_DIR / filename).write_text(html, encoding="utf-8")
    print(f"   ✅ {filename}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n⬡ Commodity Risk Terminal — Static Site Builder")
    print(f"  Build time: {build_time}")
    print(f"  Commodities: {', '.join(all_commodity_names)}")
    print(f"  Output: {DOCS_DIR.resolve()}\n")

    build_index()

    for name in all_commodity_names:
        build_commodity(name)

    print(f"\n{'='*50}")
    print(f"✅ Site built successfully!")
    print(f"   {len(all_commodity_names) + 1} pages in {DOCS_DIR.resolve()}")
    print(f"\n   To preview locally:")
    print(f"     cd docs && python -m http.server 8000")
    print(f"     Open http://localhost:8000")
    print(f"\n   To deploy:")
    print(f"     git add docs/")
    print(f'     git commit -m "Rebuild site"')
    print(f"     git push")
    print(f"     Then enable GitHub Pages from docs/ folder in repo settings.")
