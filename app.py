from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import build_figure
from config import COMMODITIES, EQUITIES, FX, INDICATOR_PLACEHOLDERS, PERIOD_OPTIONS
from data import load_ohlc
from indicators import apply_indicators


st.set_page_config(page_title="DeMark Dashboard Scaffold", layout="wide")

st.title("DeMark Dashboard")
st.caption("Scaffold version: no indicator logic or overlays yet. Left-panel checkboxes are placeholders.")

with st.sidebar:
    st.header("Configuration")

    universe = sorted(set(EQUITIES + FX + COMMODITIES))

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["SPY"]

    ticker_query = st.text_input("Ticker search / add", placeholder="e.g. AAPL, EURUSD=X")
    if ticker_query:
        q = ticker_query.strip().upper()
        matches = [s for s in universe if q in s.upper()][:8]
        if matches:
            st.caption("Matches: " + ", ".join(matches))
        else:
            st.caption("No preset match. You can still add custom Yahoo ticker.")

    if st.button("Add ticker", use_container_width=True):
        candidate = ticker_query.strip().upper()
        if candidate:
            if candidate not in st.session_state.watchlist:
                st.session_state.watchlist.append(candidate)
                st.success(f"Added {candidate}")
            else:
                st.info(f"{candidate} is already in watchlist")

    selected = st.multiselect(
        "Watchlist",
        options=sorted(set(universe + st.session_state.watchlist)),
        default=st.session_state.watchlist,
    )
    st.session_state.watchlist = selected

    st.divider()
    st.subheader("Indicators")

    if "indicator_flags" not in st.session_state:
        st.session_state.indicator_flags = {name: False for name in INDICATOR_PLACEHOLDERS}

    for name in INDICATOR_PLACEHOLDERS:
        st.session_state.indicator_flags[name] = st.checkbox(
            name,
            value=st.session_state.indicator_flags.get(name, False),
            key=f"chk_{name}",
        )

    st.divider()
    period = st.selectbox("Period", PERIOD_OPTIONS, index=1)
    interval = "1d"
    st.caption("Data interval: Daily OHLC (1d)")

if not selected:
    st.info("Select at least one symbol in the sidebar.")
    st.stop()

summary_rows = []
for symbol in selected:
    data = load_ohlc(symbol=symbol, period="5y", interval=interval)
    if data.empty:
        st.warning(f"No data available for {symbol}.")
        continue

    data = apply_indicators(data)

    period_days = {"6mo": 183, "1y": 365, "2y": 730, "5y": 1825}.get(period, 365)
    cutoff = pd.Timestamp("today") - pd.Timedelta(days=period_days)
    display_df = data[data.index >= cutoff]
    if display_df.empty:
        display_df = data

    latest = display_df.iloc[-1]
    summary_rows.append(
        {
            "Symbol": symbol,
            "Close": f"{float(latest['Close']):,.2f}",
            "High": f"{float(latest['High']):,.2f}",
            "Low": f"{float(latest['Low']):,.2f}",
        }
    )

    st.subheader(symbol)
    fig = build_figure(
        display_df,
        symbol=symbol,
        timeframe_label="Daily",
        show_td_flip=st.session_state.indicator_flags.get("TD Flip", False),
        show_td_9_count=st.session_state.indicator_flags.get("TD 9 Count", False),
    )
    st.plotly_chart(fig, use_container_width=True)

if summary_rows:
    st.subheader("Summary")
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

checked = [name for name, on in st.session_state.indicator_flags.items() if on]
with st.expander("Indicator Scaffold Status"):
    st.write("These are UI placeholders only; no logic is attached yet.")
    if checked:
        st.write("Selected placeholders: " + ", ".join(checked))
    else:
        st.write("No indicator placeholders selected.")
