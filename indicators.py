from __future__ import annotations

import pandas as pd


def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Apply currently implemented DeMark indicators to OHLC data."""
    out = df.copy()
    bullish_flip, bearish_flip = _td_price_flips(out["Close"])
    buy_td_setup, sell_td_setup = _td_setup_counts(out["Close"], bullish_flip, bearish_flip)
    out["bullish_td_flip"] = bullish_flip
    out["bearish_td_flip"] = bearish_flip
    out["buy_td_setup"] = buy_td_setup
    out["sell_td_setup"] = sell_td_setup
    return out


def _td_price_flips(close: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Compute bullish and bearish TD Price Flips using a 4-bar close comparison."""
    shifted_4 = close.shift(4)
    prev_close = close.shift(1)
    prev_shifted_4 = close.shift(5)

    bullish_flip = (close > shifted_4) & (prev_close < prev_shifted_4)
    bearish_flip = (close < shifted_4) & (prev_close > prev_shifted_4)
    return bullish_flip.fillna(False), bearish_flip.fillna(False)


def _td_setup_counts(
    close: pd.Series,
    bullish_flip: pd.Series,
    bearish_flip: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Compute TD 9 Count setup sequences that begin on a valid TD Price Flip."""
    buy_setup = pd.Series(0, index=close.index, dtype="int64")
    sell_setup = pd.Series(0, index=close.index, dtype="int64")

    buy_active = False
    sell_active = False
    buy_count = 0
    sell_count = 0

    for i in range(len(close)):
        if i < 5:
            continue

        if bool(bearish_flip.iloc[i]):
            buy_active = True
            sell_active = False
            buy_count = 1
            sell_count = 0
            buy_setup.iloc[i] = 1
            continue

        if bool(bullish_flip.iloc[i]):
            sell_active = True
            buy_active = False
            sell_count = 1
            buy_count = 0
            sell_setup.iloc[i] = 1
            continue

        if buy_active:
            if close.iloc[i] < close.iloc[i - 4]:
                buy_count += 1
                buy_setup.iloc[i] = buy_count
                if buy_count >= 9:
                    buy_active = False
                    buy_count = 0
            else:
                buy_active = False
                buy_count = 0

        if sell_active:
            if close.iloc[i] > close.iloc[i - 4]:
                sell_count += 1
                sell_setup.iloc[i] = sell_count
                if sell_count >= 9:
                    sell_active = False
                    sell_count = 0
            else:
                sell_active = False
                sell_count = 0

    return buy_setup, sell_setup
