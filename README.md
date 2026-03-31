# ⬡ Commodity Risk Intelligence Terminal

Static site generator that builds commodity risk intelligence dashboards. Scrapes live data from Yahoo Finance and Google News RSS, computes technical indicators and commodity betas, then generates static HTML pages deployable to GitHub Pages.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## How it works

1. **`python build.py`** runs locally — fetches market data, scrapes news, computes everything
2. Generates static HTML files into `docs/`
3. Push to GitHub — GitHub Pages serves the `docs/` folder
4. Re-run `build.py` whenever you want fresh data

## Architecture

```
├── build.py                        # Run this to generate the site
├── requirements.txt
├── config/
│   ├── settings.py                 # Global params (RSI, cache, beta thresholds)
│   └── commodities/
│       ├── __init__.py             # Registry
│       ├── cobalt.py               # Cobalt: regions, queries, stocks
│       └── coffee.py               # Coffee: regions, queries, stocks
├── engines/
│   ├── market_data.py              # Yahoo Finance, indicators, beta
│   └── news_scraper.py             # Google News RSS, classification
├── templates/
│   ├── index.html                  # Landing page template
│   └── commodity.html              # Commodity dashboard template
└── docs/                           # Generated static site (GitHub Pages)
    ├── index.html
    ├── cobalt.html
    └── coffee.html
```

## Quick start

### First time setup

```powershell
cd "C:\Users\Dalew\Documents\Projects\Commodities Model"
python3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Build the site

```powershell
.\venv\Scripts\Activate.ps1
python build.py
```

### Preview locally

```powershell
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

### Deploy to GitHub Pages

```powershell
git add docs/
git commit -m "Rebuild site"
git push
```

Then in your GitHub repo: **Settings → Pages → Source → Deploy from branch → main → /docs → Save**

## Adding a new commodity

1. Duplicate `config/commodities/cobalt.py` → e.g. `lithium.py`
2. Edit the data (`COMMODITY`, `PRODUCING_REGIONS`, `RISK_CATEGORIES`, `LINKED_STOCKS`)
3. Register in `config/commodities/__init__.py`
4. Run `python build.py` — new page appears automatically

## Editing guide

| I want to change...             | Edit this file                    |
|---------------------------------|-----------------------------------|
| RSI period, beta thresholds     | `config/settings.py`              |
| Cobalt news queries / stocks    | `config/commodities/cobalt.py`    |
| Coffee news queries / stocks    | `config/commodities/coffee.py`    |
| How indicators are computed     | `engines/market_data.py`          |
| How news is scraped/classified  | `engines/news_scraper.py`         |
| Dashboard page design           | `templates/commodity.html`        |
| Landing page design             | `templates/index.html`            |
| Build process                   | `build.py`                        |

## Disclaimer

This tool is for informational and educational purposes only. It is not financial advice.

## License

MIT
