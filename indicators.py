from __future__ import annotations

import pandas as pd


def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Apply currently implemented DeMark indicators to OHLC data."""
    out = df.copy()
    bullish_flip, bearish_flip = _td_price_flips(out["Close"])
    out["bullish_td_flip"] = bullish_flip
    out["bearish_td_flip"] = bearish_flip
    return out


def _td_price_flips(close: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Compute bullish and bearish TD Price Flips using a 4-bar close comparison."""
    shifted_4 = close.shift(4)
    prev_close = close.shift(1)
    prev_shifted_4 = close.shift(5)

    bullish_flip = (close > shifted_4) & (prev_close < prev_shifted_4)
    bearish_flip = (close < shifted_4) & (prev_close > prev_shifted_4)
    return bullish_flip.fillna(False), bearish_flip.fillna(False)
