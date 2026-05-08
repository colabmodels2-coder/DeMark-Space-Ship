from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _missing_date_rangebreaks(index: pd.Index) -> list[dict]:
    """Build Plotly range breaks so missing calendar dates don't render as gaps."""
    if len(index) < 2:
        return []

    dt_index = pd.DatetimeIndex(index).sort_values().normalize().unique()
    full_range = pd.date_range(dt_index.min(), dt_index.max(), freq="D")
    missing_days = full_range.difference(dt_index)
    if missing_days.empty:
        return []

    return [{"values": missing_days.to_pydatetime().tolist()}]


def build_figure(df: pd.DataFrame, symbol: str, timeframe_label: str = "Daily") -> go.Figure:
    """Build a plain OHLC + volume figure with no indicator overlays."""
    rangebreaks = _missing_date_rangebreaks(df.index)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.76, 0.24],
    )

    fig.add_trace(
        go.Ohlc(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=f"{symbol} OHLC",
            increasing_line_color="#16a34a",
            decreasing_line_color="#dc2626",
            line_width=1,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color="#64748b",
            opacity=0.55,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        template="plotly_white",
        height=760,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_xaxes(rangebreaks=rangebreaks)

    return fig
