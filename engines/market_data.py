"""
engines/market_data.py
Handles all market data operations:
  - Price data loading from Yahoo Finance
  - Technical indicator computation (BB, SMA, RSI, Z-Score, ATR)
  - Holt-Winters forecasting
  - Stock metrics and commodity beta calculation
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from config.settings import (
    BB_PERIOD, RSI_PERIOD, ATR_PERIOD, FORECAST_DAYS,
    MARKET_CACHE_TTL, BETA_LOOKBACK, BETA_MIN_WEEKS,
)


@st.cache_data(ttl=MARKET_CACHE_TTL)
def load_price_data(symbol: str) -> pd.DataFrame | None:
    """Load full price history and compute technical indicators."""
    df = yf.download(symbol, period="max", multi_level_index=False)
    if df.empty:
        return None

    df.index = pd.to_datetime(df.index).tz_localize(None)

    # Bollinger Bands
    df["SMA20"]  = df["Close"].rolling(BB_PERIOD).mean()
    df["STD20"]  = df["Close"].rolling(BB_PERIOD).std()
    df["BB_Up"]  = df["SMA20"] + df["STD20"] * 2
    df["BB_Low"] = df["SMA20"] - df["STD20"] * 2

    # Moving averages
    df["SMA50"]  = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    # RSI
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(RSI_PERIOD).mean()
    loss  = (-delta.clip(upper=0)).rolling(RSI_PERIOD).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # Z-Score and ATR
    df["Z_Score"] = (df["Close"] - df["SMA20"]) / df["STD20"]
    df["ATR"]     = (df["High"] - df["Low"]).rolling(ATR_PERIOD).mean()

    return df.dropna()


@st.cache_data(ttl=MARKET_CACHE_TTL)
def run_forecast(close_series: pd.Series, n: int = FORECAST_DAYS):
    """Run Holt-Winters exponential smoothing forecast."""
    model = ExponentialSmoothing(close_series, trend="add").fit()
    forecast_vals = model.forecast(n)
    forecast_dates = pd.date_range(
        start=close_series.index[-1] + timedelta(days=1),
        periods=n,
        freq="B",
    )
    return forecast_dates, forecast_vals


def get_derived_values(df: pd.DataFrame) -> dict:
    """Extract the latest derived values from a price dataframe."""
    last_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])
    day_chg    = last_close - prev_close
    day_chg_pct = day_chg / prev_close * 100

    return {
        "last_close":  last_close,
        "prev_close":  prev_close,
        "day_chg":     day_chg,
        "day_chg_pct": day_chg_pct,
        "last_rsi":    float(df["RSI"].iloc[-1]),
        "last_z":      float(df["Z_Score"].iloc[-1]),
        "last_atr":    float(df["ATR"].iloc[-1]),
        "atr_mean":    float(df["ATR"].mean()),
        "last_date":   df.index[-1],
        "first_date":  df.index[0],
        "data_points": len(df),
    }


@st.cache_data(ttl=MARKET_CACHE_TTL, show_spinner=False)
def get_stock_metrics(stock_ticker: str, commodity_ticker: str) -> dict | None:
    """Get current price, recent performance, and commodity beta for a stock."""
    try:
        stock_df = yf.download(
            stock_ticker, period=BETA_LOOKBACK,
            multi_level_index=False, progress=False,
        )
        if stock_df.empty or len(stock_df) < 30:
            return None

        stock_df.index = pd.to_datetime(stock_df.index).tz_localize(None)
        last = float(stock_df["Close"].iloc[-1])
        prev = float(stock_df["Close"].iloc[-2])
        day_chg = (last - prev) / prev * 100

        mo1_chg = (
            (last - float(stock_df["Close"].iloc[-21]))
            / float(stock_df["Close"].iloc[-21]) * 100
        ) if len(stock_df) >= 21 else None

        mo3_chg = (
            (last - float(stock_df["Close"].iloc[-63]))
            / float(stock_df["Close"].iloc[-63]) * 100
        ) if len(stock_df) >= 63 else None

        # Commodity beta
        commodity_beta = None
        try:
            comm_df = yf.download(
                commodity_ticker, period=BETA_LOOKBACK,
                multi_level_index=False, progress=False,
            )
            if not comm_df.empty and len(comm_df) > 30:
                comm_df.index = pd.to_datetime(comm_df.index).tz_localize(None)
                stock_weekly = stock_df["Close"].resample("W").last().pct_change().dropna()
                comm_weekly  = comm_df["Close"].resample("W").last().pct_change().dropna()
                aligned = pd.DataFrame(
                    {"stock": stock_weekly, "commodity": comm_weekly}
                ).dropna()
                if len(aligned) >= BETA_MIN_WEEKS:
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
