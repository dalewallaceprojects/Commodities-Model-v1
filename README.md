# ⬡ Commodity Risk Intelligence Terminal

A modular, real-time commodity risk intelligence dashboard built with Streamlit. Tracks environmental, geopolitical, and economic factors affecting global commodity supply chains — with live news scraping, technical analysis, and equity exposure mapping.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Architecture

The app is designed for **multi-commodity expansion** — adding a new commodity means creating one config file, not touching any engine or component code.

```
├── app.py                          # Entry point — thin orchestrator
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Dark theme defaults
│
├── config/                         # ← All configuration lives here
│   ├── __init__.py
│   ├── theme.py                    # Colours, fonts, CSS, HTML helpers
│   ├── settings.py                 # Global params (RSI period, cache TTL, etc.)
│   └── commodities/
│       ├── __init__.py             # Registry — add new commodities here
│       └── cobalt.py               # Cobalt-specific: regions, queries, stocks
│
├── engines/                        # ← Data fetching & processing
│   ├── __init__.py
│   ├── market_data.py              # Yahoo Finance, indicators, forecasting, beta
│   └── news_scraper.py             # Google News RSS, classification, region tagging
│
└── components/                     # ← UI rendering
    ├── __init__.py
    ├── sidebar.py                  # Sidebar controls
    ├── chart.py                    # Plotly price + RSI chart
    ├── tables.py                   # All HTML table renderers
    └── news_feed.py                # Risk feed, category breakdown, export
```

## Adding a new commodity

1. **Duplicate** `config/commodities/cobalt.py` → `config/commodities/lithium.py`
2. **Edit** the new file — change `COMMODITY`, `PRODUCING_REGIONS`, `RISK_CATEGORIES`, `LINKED_STOCKS`
3. **Register** it in `config/commodities/__init__.py`:
   ```python
   from config.commodities import cobalt, lithium

   REGISTRY = {
       "Cobalt": cobalt,
       "Lithium": lithium,
   }
   ```
4. **Run the app** — a commodity selector appears automatically when 2+ are registered

That's it. No engine or component changes needed.

## Editing specific parts

| I want to change...             | Edit this file                    |
|---------------------------------|-----------------------------------|
| Colours, fonts, CSS             | `config/theme.py`                 |
| RSI period, forecast length     | `config/settings.py`              |
| Cobalt news queries             | `config/commodities/cobalt.py`    |
| Cobalt linked stocks            | `config/commodities/cobalt.py`    |
| How indicators are computed     | `engines/market_data.py`          |
| How news is scraped/classified  | `engines/news_scraper.py`         |
| Chart appearance                | `components/chart.py`             |
| Table layout/HTML               | `components/tables.py`            |
| News feed rendering             | `components/news_feed.py`         |
| Sidebar controls                | `components/sidebar.py`           |
| Overall page flow               | `app.py`                          |

## Quick start

```bash
git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Features

- **Live market data** — Yahoo Finance with candlestick/line chart, Bollinger Bands, SMA overlays, RSI, Holt-Winters forecast
- **News scraping** — Google News RSS across ~25 targeted queries per commodity, keyword classification into 5 risk categories
- **Region tagging** — auto-identifies which producing region each article relates to
- **Equity exposure** — tracks linked stocks with live prices, returns, and computed Commodity Beta (β)
- **CSV export** — download the full scraped dataset

## Disclaimer

This tool is for informational and educational purposes only. It is not financial advice.

## License

MIT
