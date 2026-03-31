"""
config/settings.py
Global application settings — indicator params, forecast config, etc.
Shared across all commodities.
"""

# ─────────────────────────────────────────────
# CHART & INDICATOR PARAMETERS
# ─────────────────────────────────────────────
FORECAST_DAYS = 252          # trading days to project
RSI_PERIOD    = 14
BB_PERIOD     = 20
ATR_PERIOD    = 14

# ─────────────────────────────────────────────
# SIGNAL THRESHOLDS
# ─────────────────────────────────────────────
Z_EXTREME     = 2.0
RSI_OB        = 70           # overbought
RSI_OS        = 30           # oversold

# ─────────────────────────────────────────────
# NEWS SCRAPING
# ─────────────────────────────────────────────
NEWS_CACHE_TTL      = 1800   # seconds (30 min)
MARKET_CACHE_TTL    = 3600   # seconds (1 hour)
NEWS_DELAY_BETWEEN  = 0.3    # seconds between RSS requests
NEWS_MAX_PER_QUERY  = 10
NEWS_DEFAULT_AGE    = 30     # days

# ─────────────────────────────────────────────
# COMMODITY BETA
# ─────────────────────────────────────────────
BETA_LOOKBACK   = "2y"
BETA_MIN_WEEKS  = 20
BETA_HIGH_THRESHOLD  = 0.3
BETA_LOW_THRESHOLD   = -0.3
