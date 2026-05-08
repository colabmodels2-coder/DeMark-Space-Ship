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


def build_figure(
    df: pd.DataFrame,
    symbol: str,
    timeframe_label: str = "Daily",
    show_td_flip: bool = False,
    show_td_9_count: bool = False,
) -> go.Figure:
    """Build a plain OHLC + volume figure with optional indicator overlays."""
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

    if show_td_9_count:
        buy_setup = df[df.get("buy_td_setup", 0) > 0]
        if not buy_setup.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_setup.index,
                    y=buy_setup["Low"] * 0.99,
                    mode="text",
                    text=[str(int(value)) for value in buy_setup["buy_td_setup"]],
                    textposition="bottom center",
                    textfont=dict(size=12, color="#2563eb", family="Courier New, monospace"),
                    name="Buy TD 9 Count",
                    hovertext=[f"Buy TD Setup {int(value)}/9" for value in buy_setup["buy_td_setup"]],
                    hoverinfo="x+text",
                ),
                row=1,
                col=1,
            )

        sell_setup = df[df.get("sell_td_setup", 0) > 0]
        if not sell_setup.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_setup.index,
                    y=sell_setup["High"] * 1.01,
                    mode="text",
                    text=[str(int(value)) for value in sell_setup["sell_td_setup"]],
                    textposition="top center",
                    textfont=dict(size=12, color="#dc2626", family="Courier New, monospace"),
                    name="Sell TD 9 Count",
                    hovertext=[f"Sell TD Setup {int(value)}/9" for value in sell_setup["sell_td_setup"]],
                    hoverinfo="x+text",
                ),
                row=1,
                col=1,
            )

    if show_td_flip and not show_td_9_count:
        bullish_flip = df[df.get("bullish_td_flip", False)]
        if not bullish_flip.empty:
            fig.add_trace(
                go.Scatter(
                    x=bullish_flip.index,
                    y=bullish_flip["High"] * 1.01,
                    mode="text",
                    text=["1"] * len(bullish_flip),
                    textposition="top center",
                    textfont=dict(size=12, color="#dc2626", family="Courier New, monospace"),
                    name="Bullish TD Flip",
                    hovertext=["Bullish TD Flip" for _ in bullish_flip.index],
                    hoverinfo="x+text",
                ),
                row=1,
                col=1,
            )

        bearish_flip = df[df.get("bearish_td_flip", False)]
        if not bearish_flip.empty:
            fig.add_trace(
                go.Scatter(
                    x=bearish_flip.index,
                    y=bearish_flip["Low"] * 0.99,
                    mode="text",
                    text=["1"] * len(bearish_flip),
                    textposition="bottom center",
                    textfont=dict(size=12, color="#2563eb", family="Courier New, monospace"),
                    name="Bearish TD Flip",
                    hovertext=["Bearish TD Flip" for _ in bearish_flip.index],
                    hoverinfo="x+text",
                ),
                row=1,
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
