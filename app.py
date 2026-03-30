"""
Cobalt Supply-Chain Risk Intelligence Terminal
===============================================
Streamlit dashboard that:
  1. Pulls live cobalt market data via yfinance
  2. Scrapes Google News RSS for cobalt-related articles across
     five risk categories (weather/climate, conflict, trade policy,
     environmental regulation, supply-chain/logistics)
  3. Classifies scraped articles by risk category via keyword matching
  4. Shows cobalt-linked stocks and whether they're positively or
     negatively correlated with cobalt price movements
  5. Displays everything vertically in a dark, terminal-style UI

Requirements:
  pip install streamlit yfinance pandas numpy plotly feedparser \
              statsmodels requests beautifulsoup4

Run:
  streamlit run cobalt_terminal.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote_plus

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Cobalt Risk Terminal",
    page_icon="⬡"
)

FORECAST_DAYS = 252
RSI_PERIOD    = 14
BB_PERIOD     = 20
ATR_PERIOD    = 14
Z_EXTREME     = 2.0
RSI_OB        = 70
RSI_OS        = 30

# ─────────────────────────────────────────────
# COBALT-LINKED STOCKS
# ─────────────────────────────────────────────
COBALT_STOCKS = {
    "GLNCY": {
        "name": "Glencore",
        "description": "World's largest cobalt producer; mines in DRC (Mutanda, Katanga). Revenue directly tied to cobalt prices.",
        "relationship": "positive",
        "exposure": "Direct producer — cobalt is a primary revenue stream",
    },
    "VALE": {
        "name": "Vale S.A.",
        "description": "Major nickel/cobalt producer in Canada (Voisey's Bay) and Indonesia. Cobalt is a byproduct of nickel operations.",
        "relationship": "positive",
        "exposure": "Cobalt byproduct from nickel mining",
    },
    "BHP": {
        "name": "BHP Group",
        "description": "Produces cobalt as a byproduct from its Nickel West operations in Australia.",
        "relationship": "positive",
        "exposure": "Cobalt byproduct from nickel mining",
    },
    "CMCLF": {
        "name": "CMOC Group",
        "description": "Operates the Tenke Fungurume mine in DRC, one of the world's largest cobalt-copper deposits.",
        "relationship": "positive",
        "exposure": "Direct producer — major DRC cobalt-copper mine",
    },
    "SBSW": {
        "name": "Sibanye Stillwater",
        "description": "South African miner with cobalt exposure through PGM and battery metals acquisitions.",
        "relationship": "positive",
        "exposure": "Growing battery metals portfolio including cobalt",
    },
    "TSLA": {
        "name": "Tesla",
        "description": "Major EV manufacturer and battery consumer. Higher cobalt prices increase battery input costs.",
        "relationship": "negative",
        "exposure": "Cobalt is a key battery cathode input — rising prices squeeze margins",
    },
    "6752.T": {
        "name": "Panasonic",
        "description": "Battery cell manufacturer for Tesla and others. Cobalt price increases raise cell production costs.",
        "relationship": "negative",
        "exposure": "Battery cell manufacturer — cobalt is a direct input cost",
    },
    "ALB": {
        "name": "Albemarle",
        "description": "Lithium producer that competes with cobalt in cathode chemistry. Higher cobalt prices can boost lithium demand as substitution.",
        "relationship": "mixed",
        "exposure": "Indirect — benefits from cobalt substitution trends",
    },
    "RIVN": {
        "name": "Rivian",
        "description": "EV manufacturer with high cobalt battery chemistry. Rising cobalt prices directly increase vehicle costs.",
        "relationship": "negative",
        "exposure": "EV producer — cobalt in NMC battery packs raises BOM costs",
    },
    "NIO": {
        "name": "NIO Inc.",
        "description": "Chinese EV manufacturer using NMC batteries. Cobalt price spikes compress already-thin margins.",
        "relationship": "negative",
        "exposure": "EV producer — cobalt is a significant battery material cost",
    },
    "FREY": {
        "name": "FREYR Battery",
        "description": "Battery cell developer. Higher cobalt costs make cobalt-free chemistries (LFP) more attractive, boosting their strategy.",
        "relationship": "mixed",
        "exposure": "Developing cobalt-free cells — benefits from high cobalt prices long-term",
    },
    "MP": {
        "name": "MP Materials",
        "description": "Rare earth producer. No direct cobalt exposure but benefits from critical minerals policy tailwinds that also lift cobalt.",
        "relationship": "mixed",
        "exposure": "Indirect — correlated through critical minerals policy sentiment",
    },
}

# ─────────────────────────────────────────────
# COBALT PRODUCING REGIONS
# ─────────────────────────────────────────────
PRODUCING_REGIONS = {
    "DRC (Democratic Republic of Congo)": {
        "share": "~74%",
        "keywords": ["DRC", "Congo", "Katanga", "Lualaba", "Kolwezi", "Likasi"],
    },
    "Indonesia": {
        "share": "~5%",
        "keywords": ["Indonesia", "Sulawesi", "Morowali", "HPAL"],
    },
    "Russia": {
        "share": "~4%",
        "keywords": ["Russia", "Norilsk", "Nornickel"],
    },
    "Australia": {
        "share": "~3%",
        "keywords": ["Australia", "Murrin Murrin", "Cobalt Blue"],
    },
    "Philippines": {
        "share": "~3%",
        "keywords": ["Philippines", "Mindanao", "Palawan"],
    },
    "Cuba": {
        "share": "~2%",
        "keywords": ["Cuba", "Moa"],
    },
    "Canada": {
        "share": "~2%",
        "keywords": ["Canada", "Voisey", "Sudbury", "Cobalt Ontario"],
    },
}

# ─────────────────────────────────────────────
# RISK CATEGORIES & SEARCH QUERIES
# ─────────────────────────────────────────────
RISK_CATEGORIES = {
    "🌪️ Weather & Climate": {
        "icon": "🌪️",
        "color": "#00BFFF",
        "queries": [
            "cobalt mining weather flooding DRC",
            "Congo mining rainy season disruption",
            "Indonesia nickel cobalt weather typhoon",
            "climate change cobalt mining",
            "cobalt mine flooding Katanga",
        ],
        "keywords": [
            "flood", "rain", "storm", "typhoon", "cyclone", "drought",
            "weather", "climate", "monsoon", "landslide", "erosion",
            "el nino", "la nina", "wet season", "dry season", "disaster",
        ],
    },
    "⚔️ Conflict & Instability": {
        "icon": "⚔️",
        "color": "#FF3B30",
        "queries": [
            "DRC Congo conflict mining cobalt",
            "DRC militia cobalt mine attack",
            "Congo political instability mining",
            "Russia sanctions cobalt nickel",
            "cobalt artisanal mining conflict",
        ],
        "keywords": [
            "conflict", "war", "militia", "rebel", "attack", "coup",
            "instability", "violence", "protest", "unrest", "military",
            "sanctions", "embargo", "tensions", "security", "armed",
            "M23", "rebel", "insurgent", "martial law", "political crisis",
        ],
    },
    "📜 Trade Policy & Sanctions": {
        "icon": "📜",
        "color": "#FFD700",
        "queries": [
            "cobalt export ban DRC policy",
            "cobalt tariff trade restriction",
            "DRC mining code royalty cobalt",
            "Indonesia export ban nickel cobalt",
            "cobalt critical mineral trade policy",
            "US EU cobalt supply chain regulation",
        ],
        "keywords": [
            "tariff", "ban", "export", "import", "sanction", "quota",
            "royalt", "tax", "levy", "duty", "trade war", "restriction",
            "regulation", "legislation", "policy", "law", "decree",
            "mining code", "beneficiation", "local processing",
        ],
    },
    "🌍 Environmental Regulation": {
        "icon": "🌍",
        "color": "#00FF88",
        "queries": [
            "cobalt mining environmental regulation",
            "DRC cobalt environmental impact",
            "cobalt ESG compliance mining",
            "cobalt child labour regulation",
            "responsible cobalt initiative",
            "cobalt mining pollution water contamination",
        ],
        "keywords": [
            "environment", "pollution", "contamination", "toxic",
            "ESG", "sustainability", "child labour", "child labor",
            "human rights", "due diligence", "responsible sourcing",
            "regulation", "compliance", "emission", "waste", "tailings",
            "deforestation", "biodiversity", "water quality",
        ],
    },
    "🚢 Supply Chain & Logistics": {
        "icon": "🚢",
        "color": "#FF9500",
        "queries": [
            "cobalt supply chain disruption",
            "cobalt shipping logistics delay",
            "cobalt stockpile shortage surplus",
            "cobalt refinery China processing",
            "cobalt battery demand EV supply",
            "cobalt mine shutdown closure",
        ],
        "keywords": [
            "supply chain", "logistics", "shipping", "transport",
            "shortage", "surplus", "stockpile", "inventory", "deficit",
            "refinery", "processing", "smelter", "shutdown", "closure",
            "delay", "bottleneck", "port", "rail", "infrastructure",
            "demand", "EV", "battery", "capacity", "production cut",
        ],
    },
}


# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

html, body, .stApp          { background-color: #000; color: #fff; font-family: 'JetBrains Mono', monospace; }
[data-testid="stSidebar"]   { background-color: #050505; border-right: 1px solid #1a1a1a; }
h1, h2, h3                  { font-family: 'Syne', sans-serif; letter-spacing: -0.02em; }

/* Tables — full dark mode */
thead tr th {
    background-color: #0a0a0a !important;
    color: #00FBFF !important;
    border-bottom: 1px solid #00FBFF !important;
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
tbody tr td {
    color: #ccc !important;
    background-color: #000 !important;
    border-bottom: 1px solid #111 !important;
    font-size: 0.82rem;
}
tbody tr:hover td { background-color: #0a0a0a !important; }

/* Streamlit dataframe / data_editor — force dark backgrounds */
[data-testid="stDataFrame"],
[data-testid="stTable"],
.stDataFrame {
    background-color: #000 !important;
}
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe {
    background-color: #000 !important;
}
/* Glide Data Grid (Streamlit's underlying table renderer) */
[data-testid="stDataFrame"] [role="grid"],
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="row"] {
    background-color: #000 !important;
    color: #ccc !important;
    border-color: #111 !important;
}
[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: #0a0a0a !important;
    color: #00FBFF !important;
}
/* Bottom toolbar / row count area */
[data-testid="stDataFrame"] [data-testid="glideDataEditor"],
[data-testid="stDataFrame"] .dvn-scroller,
[data-testid="stDataFrame"] canvas {
    background-color: #000 !important;
}
/* Search bar and status bar in dataframes */
[data-testid="stDataFrame"] > div > div {
    background-color: #000 !important;
    color: #888 !important;
}
[data-testid="stElementToolbar"] {
    background-color: #0a0a0a !important;
}
/* Override any white container backgrounds behind tables */
.element-container:has([data-testid="stDataFrame"]) {
    background-color: #000 !important;
}
/* Streamlit's stTable (static table) */
[data-testid="stTable"] table {
    background-color: #000 !important;
}
[data-testid="stTable"] th {
    background-color: #0a0a0a !important;
    color: #00FBFF !important;
    border-bottom: 1px solid #00FBFF !important;
}
[data-testid="stTable"] td {
    background-color: #000 !important;
    color: #ccc !important;
    border-bottom: 1px solid #111 !important;
}

/* Metrics */
[data-testid="stMetricValue"]       { color: #00FBFF !important; font-weight: 800; font-size: 1.6rem !important; }
[data-testid="stMetricDelta"]       { font-size: 0.85rem !important; }
[data-testid="stMetricLabel"]       { color: #555 !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.1em; }

hr { border-top: 1px solid #1a1a1a; }

/* Sidebar inputs */
.stTextInput input, .stMultiSelect div { background: #0a0a0a !important; border: 1px solid #222 !important; color: #fff !important; }
.stToggle label                        { color: #aaa !important; }

/* Section headers */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00FBFF;
    margin-bottom: 0.5rem;
    border-left: 2px solid #00FBFF;
    padding-left: 0.6rem;
}

/* Risk cards */
.risk-card {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}
.risk-card:hover { border-color: #333; }
.risk-badge {
    display: inline-block;
    padding: 2px 8px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-radius: 2px;
    margin-right: 6px;
}

/* Expander styling — always dark, never white */
[data-testid="stExpander"] {
    border: 1px solid #1a1a1a !important;
    background: #050505 !important;
}
[data-testid="stExpander"] details {
    background: #050505 !important;
    border: none !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active,
[data-testid="stExpander"] details[open] summary {
    background: #050505 !important;
    color: #00FBFF !important;
    border: none !important;
}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #00FBFF !important;
}
[data-testid="stExpander"] summary svg {
    fill: #00FBFF !important;
    stroke: #00FBFF !important;
}
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background: #050505 !important;
    border-top: 1px solid #1a1a1a !important;
}
[data-testid="stExpander"] summary::-webkit-details-marker {
    color: #00FBFF !important;
}
[data-testid="stExpander"]:hover {
    border-color: #333 !important;
    background: #050505 !important;
}

/* Stock cards */
.stock-card {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}
.stock-card:hover { border-color: #333; }
.stock-positive  { border-left: 3px solid #00FF88; }
.stock-negative  { border-left: 3px solid #FF3B30; }
.stock-mixed     { border-left: 3px solid #FFD700; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NEWS SCRAPING ENGINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def scrape_google_news_rss(query: str, max_results: int = 15) -> list[dict]:
    """Fetch articles from Google News RSS for a given query."""
    encoded_query = quote_plus(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:max_results]:
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "published"):
                try:
                    pub_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                except Exception:
                    pub_date = None

            title = entry.get("title", "")
            source = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                source = parts[1].strip()

            articles.append({
                "title": title,
                "source": source,
                "link": entry.get("link", ""),
                "published": pub_date,
                "summary": BeautifulSoup(
                    entry.get("summary", entry.get("description", "")),
                    "html.parser"
                ).get_text(strip=True)[:300],
                "query": query,
            })
        return articles
    except Exception:
        return []


def classify_article(article: dict) -> list[str]:
    text = f"{article['title']} {article['summary']}".lower()
    matched = []
    for category, config in RISK_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if kw.lower() in text)
        if score >= 1:
            matched.append(category)
    return matched if matched else ["📊 General Market"]


def identify_regions(article: dict) -> list[str]:
    text = f"{article['title']} {article['summary']}".lower()
    matched = []
    for region, info in PRODUCING_REGIONS.items():
        for kw in info["keywords"]:
            if kw.lower() in text:
                matched.append(region)
                break
    return matched


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_risk_news() -> pd.DataFrame:
    all_articles = []
    seen_titles = set()

    for category, config in RISK_CATEGORIES.items():
        for query in config["queries"]:
            articles = scrape_google_news_rss(query, max_results=10)
            for article in articles:
                title_key = article["title"].lower().strip()
                if title_key in seen_titles or len(title_key) < 10:
                    continue
                seen_titles.add(title_key)

                article["categories"] = classify_article(article)
                article["regions"] = identify_regions(article)
                article["primary_category"] = article["categories"][0]
                all_articles.append(article)

            time.sleep(0.3)

    if not all_articles:
        return pd.DataFrame()

    df = pd.DataFrame(all_articles)
    if "published" in df.columns:
        df = df.sort_values("published", ascending=False, na_position="last")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────
# STOCK DATA ENGINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_metrics(stock_ticker: str, commodity_ticker: str) -> dict | None:
    """Get current price, recent performance, and commodity beta for a stock."""
    try:
        stock_df = yf.download(stock_ticker, period="2y", multi_level_index=False, progress=False)
        if stock_df.empty or len(stock_df) < 30:
            return None

        stock_df.index = pd.to_datetime(stock_df.index).tz_localize(None)
        last = float(stock_df["Close"].iloc[-1])
        prev = float(stock_df["Close"].iloc[-2])
        day_chg = (last - prev) / prev * 100

        mo1_chg = ((last - float(stock_df["Close"].iloc[-21])) / float(stock_df["Close"].iloc[-21]) * 100) if len(stock_df) >= 21 else None
        mo3_chg = ((last - float(stock_df["Close"].iloc[-63])) / float(stock_df["Close"].iloc[-63]) * 100) if len(stock_df) >= 63 else None

        # Compute commodity beta
        # Beta = Cov(stock_returns, commodity_returns) / Var(commodity_returns)
        commodity_beta = None
        try:
            comm_df = yf.download(commodity_ticker, period="2y", multi_level_index=False, progress=False)
            if not comm_df.empty and len(comm_df) > 30:
                comm_df.index = pd.to_datetime(comm_df.index).tz_localize(None)
                # Align dates and compute weekly returns to reduce noise
                stock_weekly = stock_df["Close"].resample("W").last().pct_change().dropna()
                comm_weekly = comm_df["Close"].resample("W").last().pct_change().dropna()
                # Align on shared dates
                aligned = pd.DataFrame({
                    "stock": stock_weekly,
                    "commodity": comm_weekly,
                }).dropna()
                if len(aligned) >= 20:
                    cov = aligned["stock"].cov(aligned["commodity"])
                    var = aligned["commodity"].var()
                    if var > 0:
                        commodity_beta = cov / var
        except Exception:
            pass

        return {
            "price": last,
            "day_change": day_chg,
            "mo1_change": mo1_chg,
            "mo3_change": mo3_chg,
            "commodity_beta": commodity_beta,
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⬡ Cobalt Terminal")
    st.markdown("---")
    ticker = st.text_input("Ticker Symbol", "GC=F",
                           help="Cobalt has no direct futures ticker on Yahoo Finance. "
                                "Use a proxy like GC=F (Gold) or a cobalt-linked equity.")
    view_type = st.toggle("Candlestick Mode", value=True)
    overlays = st.multiselect(
        "Chart Overlays",
        ["Bollinger Bands", "Forecast", "SMA 50", "SMA 200"],
        default=["Forecast", "Bollinger Bands"]
    )
    st.markdown("---")
    st.markdown("##### 🔍 News Filters")
    selected_categories = st.multiselect(
        "Risk Categories",
        list(RISK_CATEGORIES.keys()),
        default=list(RISK_CATEGORIES.keys()),
    )
    selected_regions = st.multiselect(
        "Producing Regions",
        list(PRODUCING_REGIONS.keys()),
        default=[],
        help="Leave empty to show all regions"
    )
    max_age_days = st.slider("Max article age (days)", 1, 90, 30)
    st.markdown("---")
    st.caption("Market data via Yahoo Finance · News via Google News RSS · Forecast via Holt-Winters ES")


# ─────────────────────────────────────────────
# MARKET DATA ENGINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(symbol: str) -> pd.DataFrame | None:
    df = yf.download(symbol, period="max", multi_level_index=False)
    if df.empty:
        return None

    df.index = pd.to_datetime(df.index).tz_localize(None)

    df["SMA20"]  = df["Close"].rolling(BB_PERIOD).mean()
    df["STD20"]  = df["Close"].rolling(BB_PERIOD).std()
    df["BB_Up"]  = df["SMA20"] + df["STD20"] * 2
    df["BB_Low"] = df["SMA20"] - df["STD20"] * 2
    df["SMA50"]  = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    delta        = df["Close"].diff()
    gain         = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss         = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    df["RSI"]    = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    df["Z_Score"] = (df["Close"] - df["SMA20"]) / df["STD20"]
    df["ATR"]     = (df["High"] - df["Low"]).rolling(ATR_PERIOD).mean()

    return df.dropna()


with st.spinner("Pulling market data…"):
    df = load_data(ticker)

if df is None:
    st.error(f"❌ Could not load data for **{ticker}**. Check the ticker symbol and try again.")
    st.stop()

last_close  = float(df["Close"].iloc[-1])
prev_close  = float(df["Close"].iloc[-2])
day_chg     = last_close - prev_close
day_chg_pct = day_chg / prev_close * 100
last_rsi    = float(df["RSI"].iloc[-1])
last_z      = float(df["Z_Score"].iloc[-1])
last_atr    = float(df["ATR"].iloc[-1])
today_now   = df.index[-1]


@st.cache_data(ttl=3600)
def run_forecast(close_series: pd.Series, n: int):
    model          = ExponentialSmoothing(close_series, trend="add").fit()
    forecast_vals  = model.forecast(n)
    forecast_dates = pd.date_range(
        start=close_series.index[-1] + timedelta(days=1),
        periods=n,
        freq="B"
    )
    return forecast_dates, forecast_vals

forecast_dates, forecast_values = run_forecast(df["Close"], FORECAST_DAYS)


# ═════════════════════════════════════════════
# MAIN LAYOUT — EVERYTHING STACKED VERTICALLY
# ═════════════════════════════════════════════

st.markdown(
    f"# ⬡ Cobalt Risk Intelligence — <span style='color:#00FBFF'>{ticker.upper()}</span>",
    unsafe_allow_html=True
)

# Metrics — stacked vertically
st.metric("Last Price", f"${last_close:,.2f}", f"{day_chg:+.2f} ({day_chg_pct:+.2f}%)")
st.metric("RSI (14)", f"{last_rsi:.1f}",
          "Overbought" if last_rsi > RSI_OB else ("Oversold" if last_rsi < RSI_OS else "Neutral"))
st.metric("Z-Score", f"{last_z:.2f}",
          "Extended" if abs(last_z) > Z_EXTREME else "Within Range")
st.metric("ATR (14)", f"{last_atr:.2f}",
          "Expanding" if last_atr > df["ATR"].mean() else "Contracting")
st.metric("Data Points", f"{len(df):,}", f"Since {df.index[0].strftime('%Y')}")

st.divider()

# ─────────────────────────────────────────────
# DATE RANGE — Streamlit radio (no rerun issues)
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">📅 Chart Range</div>', unsafe_allow_html=True)

range_label = st.radio(
    "Select range",
    ["1D", "7D", "1M", "6M", "1Y", "MAX"],
    index=2,
    horizontal=True,
    label_visibility="collapsed",
)

range_deltas = {
    "1D": timedelta(days=1),
    "7D": timedelta(days=7),
    "1M": timedelta(days=30),
    "6M": timedelta(days=180),
    "1Y": timedelta(days=365),
}

today_actual = datetime.now()
if range_label == "MAX":
    chart_start = df.index[0]
else:
    chart_start = today_actual - range_deltas[range_label]

chart_end = forecast_dates[-1] if "Forecast" in overlays else today_actual


# ─────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.75, 0.25],
    subplot_titles=("", "RSI (14)")
)

if view_type:
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="Price",
        increasing_line_color="#00FF88",
        decreasing_line_color="#FF3B30"
    ), row=1, col=1)
else:
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        name="Price",
        line=dict(color="#00FBFF", width=1.5)
    ), row=1, col=1)

if "Bollinger Bands" in overlays:
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Up"],
        line=dict(color="rgba(255,255,255,0.12)", width=1),
        name="BB Upper", showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Low"],
        line=dict(color="rgba(255,255,255,0.12)", width=1),
        fill="tonexty",
        fillcolor="rgba(255,255,255,0.03)",
        name="BB Lower", showlegend=False
    ), row=1, col=1)

if "Forecast" in overlays:
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values,
        name="Projection",
        line=dict(color="#FFD700", dash="dash", width=1.5)
    ), row=1, col=1)

if "SMA 50" in overlays:
    fig.add_trace(go.Scatter(
        x=df.index, y=df["SMA50"],
        name="SMA 50",
        line=dict(color="#FF00FB", width=1)
    ), row=1, col=1)

if "SMA 200" in overlays:
    fig.add_trace(go.Scatter(
        x=df.index, y=df["SMA200"],
        name="SMA 200",
        line=dict(color="#00FF88", width=1)
    ), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["RSI"],
    name="RSI", line=dict(color="#FFFB00", width=1.2), showlegend=False
), row=2, col=1)
for level, colour in [(RSI_OB, "rgba(255,59,48,0.4)"), (RSI_OS, "rgba(0,255,136,0.4)")]:
    fig.add_hline(y=level, line=dict(color=colour, width=1, dash="dot"), row=2, col=1)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#000",
    plot_bgcolor="#000",
    height=820,
    margin=dict(l=0, r=0, t=20, b=0),
    legend=dict(
        orientation="h", x=0, y=1.02,
        font=dict(color="#aaa", size=11),
        bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(
        type="date",
        range=[chart_start, chart_end],
        rangeslider=dict(visible=False),
        gridcolor="#111",
    ),
    xaxis2=dict(gridcolor="#111"),
    yaxis=dict(
        gridcolor="#111",
        title=dict(text="PRICE (USD)", font=dict(color="#00FBFF", size=10)),
        tickfont=dict(color="#555", size=10),
    ),
    yaxis2=dict(
        gridcolor="#111",
        title=dict(text="RSI", font=dict(color="#FFFB00", size=10)),
        tickfont=dict(color="#555", size=10),
        range=[0, 100],
    ),
)

st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# TECHNICAL INTELLIGENCE (stacked)
# ─────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-label">🧬 Technical Intelligence</div>', unsafe_allow_html=True)

z_signal   = ("Extreme Extension", "#FF3B30") if abs(last_z) > Z_EXTREME else ("Neutral", "#aaa")
atr_signal = ("Expanding",         "#FF9500") if last_atr > df["ATR"].mean() else ("Contracting", "#aaa")
rsi_signal = ("Overbought",        "#FF3B30") if last_rsi > RSI_OB else (("Oversold", "#00FF88") if last_rsi < RSI_OS else ("Neutral", "#aaa"))

_th = 'style="background:#0a0a0a;color:#00FBFF;border-bottom:1px solid #00FBFF;padding:10px 12px;text-align:left;font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.08em;text-transform:uppercase;"'
_td = 'style="background:#000;color:#ccc;border-bottom:1px solid #111;padding:10px 12px;font-size:0.82rem;"'

intel_rows = ""
for ind_name, ind_val, (sig_text, sig_color) in [
    ("Z-Score (Mean Rev.)", f"{last_z:.2f}", z_signal),
    ("ATR (Volatility)", f"{last_atr:.2f}", atr_signal),
    ("RSI (Momentum)", f"{last_rsi:.1f}", rsi_signal),
]:
    intel_rows += f'<tr><td {_td}>{ind_name}</td><td {_td}>{ind_val}</td><td style="background:#000;border-bottom:1px solid #111;padding:10px 12px;color:{sig_color};font-size:0.82rem;font-weight:700;">{sig_text}</td></tr>'

st.markdown(
    f'<table style="width:100%;border-collapse:collapse;background:#000;font-family:JetBrains Mono,monospace;">'
    f'<thead><tr><th {_th}>Indicator</th><th {_th}>Value</th><th {_th}>Signal</th></tr></thead>'
    f'<tbody>{intel_rows}</tbody></table>',
    unsafe_allow_html=True,
)

st.markdown("")
st.markdown('<div class="section-label">🎯 Price Targets (Holt-Winters)</div>', unsafe_allow_html=True)

horizon_map = {"1 Week": 4, "1 Month": 20, "3 Months": 62, "1 Year": 251}
target_rows = ""
for label, idx in horizon_map.items():
    if idx < len(forecast_values):
        fv = float(forecast_values.iloc[idx])
        ret = (fv / last_close - 1) * 100
        ret_color = "#00FF88" if ret >= 0 else "#FF3B30"
        target_rows += (
            f'<tr><td {_td}>{label}</td>'
            f'<td {_td}>{forecast_dates[idx].strftime("%Y-%m-%d")}</td>'
            f'<td {_td}>${fv:,.2f}</td>'
            f'<td style="background:#000;border-bottom:1px solid #111;padding:10px 12px;color:{ret_color};font-size:0.82rem;font-weight:700;">{ret:+.2f}%</td></tr>'
        )

st.markdown(
    f'<table style="width:100%;border-collapse:collapse;background:#000;font-family:JetBrains Mono,monospace;">'
    f'<thead><tr><th {_th}>Horizon</th><th {_th}>Target Date</th><th {_th}>Target Price</th><th {_th}>Proj. Return</th></tr></thead>'
    f'<tbody>{target_rows}</tbody></table>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# PRODUCING REGIONS (stacked)
# ─────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-label">🌐 Key Producing Regions</div>', unsafe_allow_html=True)

region_rows = ""
for region, info in PRODUCING_REGIONS.items():
    region_rows += (
        f'<tr><td {_td}>{region}</td>'
        f'<td {_td}>{info["share"]}</td>'
        f'<td {_td}>{", ".join(info["keywords"][:3])}</td></tr>'
    )

st.markdown(
    f'<table style="width:100%;border-collapse:collapse;background:#000;font-family:JetBrains Mono,monospace;">'
    f'<thead><tr><th {_th}>Region</th><th {_th}>Global Share</th><th {_th}>Search Terms</th></tr></thead>'
    f'<tbody>{region_rows}</tbody></table>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# COBALT-LINKED STOCKS (stacked, HTML table)
# ─────────────────────────────────────────────
st.divider()
st.markdown("## 📈 Cobalt-Linked Equities")
st.caption(
    "Stocks with material exposure to cobalt prices — either as producers (positive correlation) "
    "or consumers (negative correlation). Commodity Beta measures how much the stock moves "
    f"relative to {ticker.upper()} — e.g. β=1.5 means a 1% commodity move → ~1.5% stock move."
)

# Fetch all stock metrics
with st.spinner("Loading equity data & computing commodity betas…"):
    all_stock_data = {}
    for tick in COBALT_STOCKS:
        all_stock_data[tick] = get_stock_metrics(tick, ticker)

for relationship, label, emoji, rel_color in [
    ("positive", "Positively Correlated — cobalt price rises benefit these stocks", "🟢", "#00FF88"),
    ("negative", "Negatively Correlated — cobalt price rises hurt these stocks", "🔴", "#FF3B30"),
    ("mixed",    "Mixed / Indirect — cobalt price rises have mixed effects", "🟡", "#FFD700"),
]:
    group = {k: v for k, v in COBALT_STOCKS.items() if v["relationship"] == relationship}
    if not group:
        continue

    st.markdown(
        f"<div style='font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.15em;"
        f"text-transform:uppercase;color:{rel_color};margin:1.5rem 0 0.8rem;border-left:2px solid {rel_color};"
        f"padding-left:0.6rem;'>{emoji} {label}</div>",
        unsafe_allow_html=True,
    )

    # Build HTML table — single-line construction to avoid Streamlit markdown parser issues
    _sth = 'style="background:#0a0a0a;color:#00FBFF;border-bottom:1px solid #00FBFF;padding:10px 12px;font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.08em;text-transform:uppercase;"'
    _std = 'style="background:#000;border-bottom:1px solid #111;padding:10px 12px;"'

    rows_html = ""
    for tick, info in group.items():
        m = all_stock_data.get(tick)
        if m:
            price_str = f"${m['price']:,.2f}"
            day_str = f"{m['day_change']:+.2f}%"
            day_color = "#00FF88" if m["day_change"] >= 0 else "#FF3B30"
            mo1_str = f"{m['mo1_change']:+.1f}%" if m["mo1_change"] is not None else "—"
            mo1_color = "#00FF88" if (m["mo1_change"] or 0) >= 0 else "#FF3B30"
            mo3_str = f"{m['mo3_change']:+.1f}%" if m["mo3_change"] is not None else "—"
            mo3_color = "#00FF88" if (m["mo3_change"] or 0) >= 0 else "#FF3B30"

            if m["commodity_beta"] is not None:
                beta_val = m["commodity_beta"]
                beta_str = f"{beta_val:+.2f}"
                beta_color = "#00FF88" if beta_val > 0.3 else ("#FF3B30" if beta_val < -0.3 else "#FFD700")
            else:
                beta_str = "—"
                beta_color = "#555"
        else:
            price_str = day_str = mo1_str = mo3_str = beta_str = "—"
            day_color = mo1_color = mo3_color = beta_color = "#555"

        rows_html += (
            f'<tr>'
            f'<td {_std}><span style="color:#00FBFF;font-family:Syne,sans-serif;font-weight:700;">{tick}</span><br><span style="color:#666;font-size:0.7rem;">{info["name"]}</span></td>'
            f'<td {_std} align="right"><span style="color:#ccc;">{price_str}</span></td>'
            f'<td {_std} align="right"><span style="color:{day_color};">{day_str}</span></td>'
            f'<td {_std} align="right"><span style="color:{mo1_color};">{mo1_str}</span></td>'
            f'<td {_std} align="right"><span style="color:{mo3_color};">{mo3_str}</span></td>'
            f'<td {_std} align="right"><span style="color:{beta_color};font-weight:700;">{beta_str}</span></td>'
            f'<td {_std}><span style="color:#555;font-size:0.7rem;">{info["exposure"]}</span></td>'
            f'</tr>'
        )

    table_html = (
        f'<table style="width:100%;border-collapse:collapse;background:#000;font-family:JetBrains Mono,monospace;font-size:0.8rem;">'
        f'<thead><tr>'
        f'<th {_sth} align="left">Ticker</th>'
        f'<th {_sth} align="right">Price</th>'
        f'<th {_sth} align="right">Day</th>'
        f'<th {_sth} align="right">1M</th>'
        f'<th {_sth} align="right">3M</th>'
        f'<th {_sth} align="right">Commodity &#946;</th>'
        f'<th {_sth} align="left">Exposure</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LIVE RISK INTELLIGENCE FEED
# ─────────────────────────────────────────────
st.divider()
st.markdown("## 📡 Live Risk Intelligence Feed")
st.caption("Scraped from Google News RSS · Articles classified by keyword matching across five risk categories")

with st.spinner("Scanning news sources across all risk categories…"):
    news_df = fetch_all_risk_news()

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
            filtered["published"].isna()
            | (filtered["published"] >= cutoff_date)
        ]

    st.markdown(
        f"**{len(filtered)}** articles found · "
        f"**{news_df['source'].nunique()}** sources · "
        f"Last {max_age_days} days"
    )

    # Category breakdown — stacked vertically
    cat_counts = {}
    for _, row in filtered.iterrows():
        for cat in row["categories"]:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    if cat_counts:
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            color = RISK_CATEGORIES.get(cat, {}).get("color", "#aaa")
            st.markdown(
                f"<div style='background:#0a0a0a;border:1px solid #1a1a1a;"
                f"border-left:3px solid {color};padding:10px 14px;margin-bottom:4px;"
                f"display:flex;justify-content:space-between;align-items:center;'>"
                f"<span style='font-size:0.75rem;color:#ccc;'>{cat}</span>"
                f"<span style='font-size:1rem;font-weight:800;color:{color}'>{count}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("")

    # Article feed
    for category in selected_categories:
        cat_articles = filtered[
            filtered["categories"].apply(lambda cats: category in cats)
        ]
        if cat_articles.empty:
            continue

        config = RISK_CATEGORIES.get(category, {})
        color = config.get("color", "#aaa")

        with st.expander(
            f"{category}  —  {len(cat_articles)} articles",
            expanded=True
        ):
            for _, article in cat_articles.iterrows():
                pub_str = ""
                if pd.notna(article["published"]):
                    age = datetime.now() - article["published"]
                    if age.days == 0:
                        pub_str = f"{age.seconds // 3600}h ago"
                    elif age.days == 1:
                        pub_str = "Yesterday"
                    else:
                        pub_str = f"{age.days}d ago"

                region_tags = ""
                if article["regions"]:
                    region_tags = " ".join(
                        f"<span style='background:#111;color:#888;padding:1px 6px;"
                        f"font-size:0.6rem;border:1px solid #222;'>{r.split('(')[0].strip()}</span>"
                        for r in article["regions"]
                    )

                st.markdown(
                    f"<div class='risk-card'>"
                    f"<div>"
                    f"<div style='margin-bottom:6px;'>"
                    f"<span class='risk-badge' style='background:{color};color:#000;'>{category.split(' ',1)[-1]}</span>"
                    f"<span style='color:#555;font-size:0.7rem;'>{article['source']}</span>"
                    f"<span style='color:#333;font-size:0.7rem;margin-left:8px;'>{pub_str}</span>"
                    f"</div>"
                    f"<a href='{article['link']}' target='_blank' "
                    f"style='color:#ddd;text-decoration:none;font-size:0.85rem;line-height:1.4;'>"
                    f"{article['title']}</a>"
                    f"<div style='margin-top:6px;'>{region_tags}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    general = filtered[filtered["primary_category"] == "📊 General Market"]
    if not general.empty:
        with st.expander(f"📊 General Market  —  {len(general)} articles", expanded=False):
            for _, article in general.iterrows():
                pub_str = ""
                if pd.notna(article["published"]):
                    age = datetime.now() - article["published"]
                    pub_str = f"{age.days}d ago" if age.days > 0 else f"{age.seconds // 3600}h ago"

                st.markdown(
                    f"<div class='risk-card'>"
                    f"<span style='color:#555;font-size:0.7rem;'>{article['source']} · {pub_str}</span><br>"
                    f"<a href='{article['link']}' target='_blank' "
                    f"style='color:#ddd;text-decoration:none;font-size:0.85rem;'>"
                    f"{article['title']}</a>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────
# RAW DATA EXPORT
# ─────────────────────────────────────────────
st.divider()
with st.expander("📥 Export Raw Data"):
    if not news_df.empty:
        export_df = news_df[["title", "source", "link", "published", "primary_category", "summary"]].copy()
        export_df["regions"] = news_df["regions"].apply(lambda x: "; ".join(x) if x else "")
        export_df["all_categories"] = news_df["categories"].apply(lambda x: "; ".join(x) if x else "")

        csv = export_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            "cobalt_risk_intelligence.csv",
            "text/csv"
        )

        # Build HTML table for export preview
        _eth = 'style="background:#0a0a0a;color:#00FBFF;border-bottom:1px solid #00FBFF;padding:8px 10px;text-align:left;font-family:Syne,sans-serif;font-size:0.65rem;letter-spacing:0.08em;text-transform:uppercase;"'
        _etd = 'style="background:#000;color:#ccc;border-bottom:1px solid #111;padding:8px 10px;font-size:0.72rem;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"'
        export_rows = ""
        for _, row in export_df.head(50).iterrows():
            pub = str(row["published"])[:10] if pd.notna(row["published"]) else "—"
            title_safe = str(row["title"]).replace("<", "&lt;").replace(">", "&gt;")[:80]
            src_safe = str(row["source"]).replace("<", "&lt;").replace(">", "&gt;")
            cat_safe = str(row["primary_category"]).replace("<", "&lt;").replace(">", "&gt;")
            export_rows += f'<tr><td {_etd}>{pub}</td><td {_etd}>{src_safe}</td><td {_etd}>{title_safe}</td><td {_etd}>{cat_safe}</td></tr>'

        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;background:#000;font-family:JetBrains Mono,monospace;">'
            f'<thead><tr><th {_eth}>Date</th><th {_eth}>Source</th><th {_eth}>Title</th><th {_eth}>Category</th></tr></thead>'
            f'<tbody>{export_rows}</tbody></table>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#333;font-size:0.65rem;letter-spacing:0.15em;'>"
    "COBALT RISK TERMINAL · NOT FINANCIAL ADVICE · DATA VIA YAHOO FINANCE & GOOGLE NEWS RSS"
    "</div>",
    unsafe_allow_html=True
)