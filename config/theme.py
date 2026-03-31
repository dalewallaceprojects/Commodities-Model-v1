"""
config/theme.py
Global theme constants and CSS injection for the terminal aesthetic.
Edit this file to change colours, fonts, or styling across the entire app.
"""

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
PRIMARY       = "#00FBFF"
ACCENT        = "#FFD700"
POSITIVE      = "#00FF88"
NEGATIVE      = "#FF3B30"
WARNING       = "#FF9500"
MIXED         = "#FFD700"
NEUTRAL       = "#aaa"
BG_PRIMARY    = "#000000"
BG_SECONDARY  = "#0a0a0a"
BG_CARD       = "#0a0a0a"
BG_HOVER      = "#050505"
BORDER        = "#1a1a1a"
BORDER_HOVER  = "#333"
TEXT_PRIMARY   = "#fff"
TEXT_SECONDARY = "#ccc"
TEXT_MUTED     = "#555"
TEXT_FAINT     = "#333"

# ─────────────────────────────────────────────
# TYPOGRAPHY
# ─────────────────────────────────────────────
FONT_MONO     = "'JetBrains Mono', monospace"
FONT_DISPLAY  = "'Syne', sans-serif"
FONT_IMPORT   = "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@700;800&display=swap"

# ─────────────────────────────────────────────
# CHART COLOURS
# ─────────────────────────────────────────────
CHART_UP      = "#00FF88"
CHART_DOWN    = "#FF3B30"
CHART_LINE    = "#00FBFF"
CHART_FORECAST = "#FFD700"
CHART_SMA50   = "#FF00FB"
CHART_SMA200  = "#00FF88"
CHART_BB      = "rgba(255,255,255,0.12)"
CHART_BB_FILL = "rgba(255,255,255,0.03)"
CHART_RSI     = "#FFFB00"
CHART_GRID    = "#111"

# ─────────────────────────────────────────────
# RISK CATEGORY COLOURS
# ─────────────────────────────────────────────
RISK_COLOURS = {
    "weather":        "#00BFFF",
    "conflict":       "#FF3B30",
    "trade_policy":   "#FFD700",
    "environmental":  "#00FF88",
    "supply_chain":   "#FF9500",
    "general":        "#aaa",
}

# ─────────────────────────────────────────────
# RELATIONSHIP COLOURS (for equity tables)
# ─────────────────────────────────────────────
RELATIONSHIP_COLOURS = {
    "positive": POSITIVE,
    "negative": NEGATIVE,
    "mixed":    MIXED,
}

# ─────────────────────────────────────────────
# HTML TABLE HELPERS
# ─────────────────────────────────────────────
TH_STYLE = (
    f'style="background:{BG_SECONDARY};color:{PRIMARY};'
    f'border-bottom:1px solid {PRIMARY};padding:10px 12px;'
    f'font-family:{FONT_DISPLAY};font-size:0.7rem;'
    f'letter-spacing:0.08em;text-transform:uppercase;"'
)

TD_STYLE = (
    f'style="background:{BG_PRIMARY};color:{TEXT_SECONDARY};'
    f'border-bottom:1px solid {BORDER};padding:10px 12px;'
    f'font-size:0.82rem;"'
)

TABLE_WRAPPER = (
    f'style="width:100%;border-collapse:collapse;background:{BG_PRIMARY};'
    f'font-family:{FONT_MONO};"'
)

SECTION_LABEL_STYLE = (
    f'font-family:{FONT_DISPLAY};font-size:0.65rem;letter-spacing:0.2em;'
    f'text-transform:uppercase;color:{PRIMARY};margin-bottom:0.5rem;'
    f'border-left:2px solid {PRIMARY};padding-left:0.6rem;'
)


def section_label(icon: str, text: str) -> str:
    """Generate a styled section label HTML string."""
    return f'<div style="{SECTION_LABEL_STYLE}">{icon} {text}</div>'


def colored_cell(value: str, color: str, bold: bool = False) -> str:
    """Generate a TD with a specific colour."""
    weight = "font-weight:700;" if bold else ""
    return (
        f'<td style="background:{BG_PRIMARY};border-bottom:1px solid {BORDER};'
        f'padding:10px 12px;color:{color};font-size:0.82rem;{weight}">{value}</td>'
    )


# ─────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────
def get_css() -> str:
    """Return the full CSS string for injection via st.markdown."""
    return f"""
<style>
@import url('{FONT_IMPORT}');

html, body, .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; font-family: {FONT_MONO}; }}
[data-testid="stSidebar"] {{ background-color: {BG_HOVER}; border-right: 1px solid {BORDER}; }}
h1, h2, h3 {{ font-family: {FONT_DISPLAY}; letter-spacing: -0.02em; }}

/* Tables — full dark mode */
thead tr th {{
    background-color: {BG_SECONDARY} !important;
    color: {PRIMARY} !important;
    border-bottom: 1px solid {PRIMARY} !important;
    font-family: {FONT_DISPLAY};
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
tbody tr td {{
    color: {TEXT_SECONDARY} !important;
    background-color: {BG_PRIMARY} !important;
    border-bottom: 1px solid {BORDER} !important;
    font-size: 0.82rem;
}}
tbody tr:hover td {{ background-color: {BG_SECONDARY} !important; }}

/* Streamlit dataframe overrides */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe,
[data-testid="stDataFrame"] [role="grid"],
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [role="row"],
[data-testid="stDataFrame"] [data-testid="glideDataEditor"],
[data-testid="stDataFrame"] .dvn-scroller,
[data-testid="stDataFrame"] canvas,
[data-testid="stDataFrame"] > div > div,
[data-testid="stTable"] table,
.element-container:has([data-testid="stDataFrame"]) {{
    background-color: {BG_PRIMARY} !important;
    color: {TEXT_SECONDARY} !important;
}}
[data-testid="stDataFrame"] [role="columnheader"] {{
    background-color: {BG_SECONDARY} !important;
    color: {PRIMARY} !important;
}}
[data-testid="stElementToolbar"] {{
    background-color: {BG_SECONDARY} !important;
}}

/* Metrics */
[data-testid="stMetricValue"] {{ color: {PRIMARY} !important; font-weight: 800; font-size: 1.6rem !important; }}
[data-testid="stMetricDelta"]  {{ font-size: 0.85rem !important; }}
[data-testid="stMetricLabel"]  {{ color: {TEXT_MUTED} !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.1em; }}

hr {{ border-top: 1px solid {BORDER}; }}

/* Sidebar inputs */
.stTextInput input, .stMultiSelect div {{ background: {BG_SECONDARY} !important; border: 1px solid #222 !important; color: {TEXT_PRIMARY} !important; }}
.stToggle label {{ color: #aaa !important; }}

/* Risk cards */
.risk-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}}
.risk-card:hover {{ border-color: {BORDER_HOVER}; }}
.risk-badge {{
    display: inline-block;
    padding: 2px 8px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-radius: 2px;
    margin-right: 6px;
}}

/* Expander styling — always dark */
[data-testid="stExpander"] {{ border: 1px solid {BORDER} !important; background: {BG_HOVER} !important; }}
[data-testid="stExpander"] details {{ background: {BG_HOVER} !important; border: none !important; }}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active,
[data-testid="stExpander"] details[open] summary {{
    background: {BG_HOVER} !important;
    color: {PRIMARY} !important;
    border: none !important;
}}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {{ color: {PRIMARY} !important; }}
[data-testid="stExpander"] summary svg {{ fill: {PRIMARY} !important; stroke: {PRIMARY} !important; }}
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
    background: {BG_HOVER} !important;
    border-top: 1px solid {BORDER} !important;
}}
[data-testid="stExpander"]:hover {{ border-color: {BORDER_HOVER} !important; background: {BG_HOVER} !important; }}
</style>
"""
