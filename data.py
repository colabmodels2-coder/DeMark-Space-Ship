from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(show_spinner=False, ttl=60 * 30)
def load_ohlc(symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Load OHLCV data with a deterministic synthetic fallback for offline environments."""
    try:
        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
        if data is not None and not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            required = ["Open", "High", "Low", "Close", "Volume"]
            out = data[[c for c in required if c in data.columns]].copy()
            out = out.dropna(subset=["Open", "High", "Low", "Close"])
            if not out.empty:
                if "Volume" not in out.columns:
                    out["Volume"] = 0
                return out
    except Exception:
        pass

    n_by_period = {"6mo": 130, "1y": 260, "2y": 520, "5y": 1300}
    n = n_by_period.get(period, 260)
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="B")

    x = np.linspace(0, 14 * np.pi, n)
    base = 100 + 6 * np.sin(x) + 0.03 * np.arange(n)

    close = pd.Series(base, index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = np.maximum(open_, close) + 0.8
    low = np.minimum(open_, close) - 0.8
    volume = pd.Series(1_000_000, index=idx)

    return pd.DataFrame(
        {
            "Open": open_.astype(float),
            "High": high.astype(float),
            "Low": low.astype(float),
            "Close": close.astype(float),
            "Volume": volume.astype(float),
        }
    )
