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


def _add_td_flip_reference_labels(fig: go.Figure, df: pd.DataFrame) -> None:
    """Add temporary debug labels for the bars referenced by TD Flip logic."""
    if len(df) < 6:
        return

    label_x: list[pd.Timestamp] = []
    label_x_y: list[float] = []
    label_x_text: list[str] = []

    label_xp: list[pd.Timestamp] = []
    label_xp_y: list[float] = []
    label_xp_text: list[str] = []

    label_y: list[pd.Timestamp] = []
    label_y_y: list[float] = []
    label_y_text: list[str] = []

    label_yp: list[pd.Timestamp] = []
    label_yp_y: list[float] = []
    label_yp_text: list[str] = []

    for i in range(len(df)):
        if not bool(df["bullish_td_flip"].iloc[i] or df["bearish_td_flip"].iloc[i]):
            continue
        if i < 5:
            continue

        x_idx = df.index[i - 5]
        xp_idx = df.index[i - 1]
        y_idx = df.index[i - 4]
        yp_idx = df.index[i]

        label_x.append(x_idx)
        label_x_y.append(float(df["High"].iloc[i - 5]) * 1.03)
        label_x_text.append("X")

        label_xp.append(xp_idx)
        label_xp_y.append(float(df["High"].iloc[i - 1]) * 1.045)
        label_xp_text.append("X'")

        label_y.append(y_idx)
        label_y_y.append(float(df["Low"].iloc[i - 4]) * 0.97)
        label_y_text.append("Y")

        label_yp.append(yp_idx)
        label_yp_y.append(float(df["Low"].iloc[i]) * 0.955)
        label_yp_text.append("Y'")

    if label_x:
        fig.add_trace(
            go.Scatter(
                x=label_x,
                y=label_x_y,
                mode="text",
                text=label_x_text,
                textposition="top center",
                textfont=dict(size=10, color="#7c3aed", family="Courier New, monospace"),
                name="TD Flip Ref X",
                hovertext=["Previous comparison reference: Close[5]" for _ in label_x],
                hoverinfo="x+text",
            ),
            row=1,
            col=1,
        )

    if label_xp:
        fig.add_trace(
            go.Scatter(
                x=label_xp,
                y=label_xp_y,
                mode="text",
                text=label_xp_text,
                textposition="top center",
                textfont=dict(size=10, color="#a855f7", family="Courier New, monospace"),
                name="TD Flip Ref X'",
                hovertext=["Previous bar under test" for _ in label_xp],
                hoverinfo="x+text",
            ),
            row=1,
            col=1,
        )

    if label_y:
        fig.add_trace(
            go.Scatter(
                x=label_y,
                y=label_y_y,
                mode="text",
                text=label_y_text,
                textposition="bottom center",
                textfont=dict(size=10, color="#0f766e", family="Courier New, monospace"),
                name="TD Flip Ref Y",
                hovertext=["Current comparison reference: Close[4]" for _ in label_y],
                hoverinfo="x+text",
            ),
            row=1,
            col=1,
        )

    if label_yp:
        fig.add_trace(
            go.Scatter(
                x=label_yp,
                y=label_yp_y,
                mode="text",
                text=label_yp_text,
                textposition="bottom center",
                textfont=dict(size=10, color="#14b8a6", family="Courier New, monospace"),
                name="TD Flip Ref Y'",
                hovertext=["Current bar under test" for _ in label_yp],
                hoverinfo="x+text",
            ),
            row=1,
            col=1,
        )


def build_figure(
    df: pd.DataFrame,
    symbol: str,
    timeframe_label: str = "Daily",
    show_td_flip: bool = False,
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

    if show_td_flip:
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

            _add_td_flip_reference_labels(fig, df)

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
