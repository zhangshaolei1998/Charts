"""v3: 0–100 judge scores; separate (a) question-type and (b) cognitive-load figures.

Scores and Δ Chart−Text are ×100 with one decimal (round half to even).
Panel (b): legend below axes. Both panels: Text/Chart better on Δ.

Usage:
    python paper_write/iclr2027/figures/plot_probe_slices_v3.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

OUT_DIR = Path(__file__).resolve().parent
FIG_STEM_A = "probe_slices_dotplot_v3_a"
FIG_STEM_B = "probe_slices_dotplot_v3_b"

TEXT_WIDTH_IN = 6.4
ROW_HEIGHT_IN = 0.19
ROW_PANEL_VSPACE = 0.30

SCORE_SCALE = 100.0

C_NOTOOL = "#9199A1"
C_BOTH = "#7B5AA6"
C_CHART_WIN = "#1F7A6C"  # chart-only (judge) / chart-better (Δ)
C_TEXT_WIN = "#B0651F"  # text-only (judge) / text-better (Δ)
C_TEXT = C_TEXT_WIN
C_CHART = C_CHART_WIN
C_GRID = "#D8DCE0"
C_BAND = "#F2F4F6"
C_INK = "#1A1A1A"
C_MUTED = "#6B7278"


@dataclass
class Row:
    label: str
    n: int
    no_tool: float
    text: float
    chart: float
    both: float

    @property
    def delta(self) -> float:
        return self.chart - self.text

    @property
    def delta_display(self) -> float:
        return round(self.delta * SCORE_SCALE, 1)


QUESTION_TYPE = [
    Row("Numerical query", 9, 0.139, 0.472, 0.250, 0.472),
    Row("Composition / distribution", 43, 0.326, 0.924, 0.924, 0.907),
    Row("Ranking / extrema", 7, 0.429, 0.857, 0.857, 0.857),
    Row("Group comparison", 63, 0.302, 0.758, 0.726, 0.762),
    Row("Temporal change", 36, 0.278, 0.674, 0.799, 0.667),
    Row("Relationship analysis", 18, 0.208, 0.708, 0.750, 0.764),
    Row("Anomaly / risk", 13, 0.308, 0.808, 0.904, 0.827),
    Row("Diagnostic explanation", 8, 0.469, 0.781, 0.750, 0.813),
    Row("Forecast / extrapolation", 3, 0.000, 1.000, 1.000, 1.000),
]

COGNITIVE = [
    Row("Lookup", 12, 0.146, 0.604, 0.521, 0.521),
    Row("Scan and selection", 24, 0.219, 0.958, 0.958, 0.958),
    Row("Comparative judgment", 69, 0.366, 0.801, 0.783, 0.808),
    Row("Pattern recognition", 54, 0.306, 0.769, 0.833, 0.764),
    Row("Relational explanation", 17, 0.221, 0.706, 0.735, 0.765),
    Row("Multidim. integration", 20, 0.150, 0.575, 0.650, 0.600),
    Row("Conditional reasoning", 4, 0.813, 1.000, 0.750, 1.000),
]

SERIES = [
    ("No-tool", "no_tool", C_NOTOOL, "o", 4.2, False),
    ("Text-only", "text", C_TEXT, "s", 4.6, True),
    ("Chart-only", "chart", C_CHART, "o", 5.2, True),
    ("Free-style", "both", C_BOTH, "D", 4.0, False),
]

MODALITY_ORDER = ["no_tool", "text", "chart", "both"]
MARKER_ZORDER = {"no_tool": 6, "both": 6, "text": 5, "chart": 5}


def set_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["STIXGeneral", "Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.edgecolor": "#B8BEC4",
            "axes.linewidth": 0.6,
            "text.color": C_INK,
            "axes.labelcolor": C_INK,
            "xtick.color": C_MUTED,
            "ytick.color": C_INK,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.4,
            "axes.titlesize": 8.2,
            "legend.fontsize": 7.4,
            "savefig.dpi": 400,
        }
    )


def score_display(v: float) -> float:
    return round(v * SCORE_SCALE, 1)


def row_modality_scores(row: Row) -> dict[str, float]:
    return {attr: score_display(getattr(row, attr)) for attr in MODALITY_ORDER}


def plot_score_marker(
    ax,
    x: float,
    y: float,
    color: str,
    marker: str,
    size: float,
    filled: bool,
    alpha: float,
    zorder: int,
) -> None:
    halo = size + 1.25
    ax.plot(
        [x],
        [y],
        marker=marker,
        ms=halo,
        mfc="white",
        mec="white",
        mew=0.0,
        alpha=alpha,
        linestyle="none",
        zorder=zorder - 1,
    )
    ax.plot(
        [x],
        [y],
        marker=marker,
        ms=size,
        mfc=color if filled else "white",
        mec=color,
        mew=1.0 if filled else 1.1,
        alpha=alpha,
        linestyle="none",
        zorder=zorder,
    )


def by_delta(rows: list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r: r.delta, reverse=True)


def row_label(r: Row) -> str:
    return f"{r.label}  " + r"$\it{n}$" + f"$\\,$={r.n}"


def style_yticks(ax, rows: list[Row]) -> None:
    for tick, row in zip(ax.get_yticklabels(), rows):
        if row.label == "All tasks":
            tick.set_weight("bold")


def band(ax, y: float, xmin: float, xmax: float) -> None:
    ax.add_patch(
        Rectangle(
            (xmin, y - 0.5),
            xmax - xmin,
            1.0,
            transform=ax.transData,
            facecolor=C_BAND,
            edgecolor="none",
            zorder=0,
        )
    )


def delta_label(ax, row: Row, y: float, lim: float, alpha: float, fontsize: float) -> None:
    d = row.delta_display
    color = C_CHART_WIN if d >= 0 else C_TEXT_WIN
    txt = f"{d:+.1f}" if abs(d) > 1e-9 else "0.0"
    inside = abs(d) > 0.62 * lim
    if inside:
        ax.text(
            d - np.sign(d) * 1.2,
            y,
            txt,
            va="center",
            ha="right" if d >= 0 else "left",
            fontsize=fontsize,
            color="white",
            alpha=alpha,
            zorder=5,
        )
    else:
        ax.text(
            d + np.sign(d or 1.0) * 1.6,
            y,
            txt,
            va="center",
            ha="left" if d >= 0 else "right",
            fontsize=fontsize,
            color=color if abs(d) > 1e-9 else C_MUTED,
            alpha=alpha,
            zorder=5,
        )


def draw_dot_panel(ax, rows: list[Row], show_xlabel: bool) -> None:
    ys = np.arange(len(rows))[::-1]
    ax.set_xlim(-2.0, 102.0)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.margins(x=0)
    xmin, xmax = ax.get_xlim()
    for y, row in zip(ys, rows):
        alpha = 1.0
        if y % 2 == 0:
            band(ax, y, xmin, xmax)
        scores = row_modality_scores(row)
        vals = list(scores.values())
        ax.plot(
            [min(vals), max(vals)],
            [y, y],
            color="#C4CAD0",
            lw=0.7,
            alpha=alpha,
            zorder=1,
            solid_capstyle="round",
        )
        seg_color = C_CHART_WIN if row.delta >= 0 else C_TEXT_WIN
        ax.plot(
            [scores["text"], scores["chart"]],
            [y, y],
            color=seg_color,
            lw=2.8,
            alpha=0.30 * alpha,
            zorder=2,
            solid_capstyle="round",
        )
        for _, attr, color, marker, size, filled in SERIES:
            plot_score_marker(
                ax,
                scores[attr],
                y,
                color,
                marker,
                size,
                filled,
                alpha,
                MARKER_ZORDER[attr],
            )
        if row.label == "All tasks":
            ax.axhline(y + 0.5, color="#9AA1A8", lw=0.6, ls=(0, (3, 2)), zorder=1.5)
    ax.set_yticks(ys)
    ax.set_yticklabels([row_label(r) for r in rows])
    style_yticks(ax, rows)
    ticks = np.arange(0, 100.1, 20)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{int(v)}" for v in ticks])
    ax.xaxis.grid(True, color=C_GRID, lw=0.5, ls=(0, (1, 2.2)))
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=2.5, width=0.6)
    if show_xlabel:
        ax.set_xlabel("Judge score (task mean)", fontsize=7.6, labelpad=1)


def draw_delta_panel(
    ax, rows: list[Row], show_xlabel: bool, annotate: bool = False
) -> list[mpl.text.Text]:
    ys = np.arange(len(rows))[::-1]
    lim = 30.0
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    xmin, xmax = ax.get_xlim()
    for y, row in zip(ys, rows):
        alpha = 1.0
        if y % 2 == 0:
            band(ax, y, xmin, xmax)
        d = row.delta_display
        color = C_CHART_WIN if d >= 0 else C_TEXT_WIN
        ax.barh(y, d, height=0.44, color=color, alpha=alpha, zorder=3)
        delta_label(ax, row, y, lim, alpha, 6.4)
        if row.label == "All tasks":
            ax.axhline(y + 0.5, color="#9AA1A8", lw=0.6, ls=(0, (3, 2)), zorder=1.5)

    ax.set_yticks([])
    ax.axvline(0, color="#8A9097", lw=0.6, zorder=2)
    ax.set_xticks([-20.0, 0.0, 20.0])
    ax.set_xticklabels(["$-$20", "0", "+20"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=2.5, width=0.6)
    if show_xlabel:
        ax.set_xlabel(r"$\Delta$ Chart$-$Text", fontsize=7.6, labelpad=1)
    header: list[mpl.text.Text] = []
    if annotate:
        header.append(
            ax.text(
                0.95,
                1.008,
                "Chart better",
                transform=ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=6.4,
                color=C_CHART_WIN,
                clip_on=False,
            )
        )
        header.append(
            ax.text(
                0.02,
                1.012,
                "Text better",
                transform=ax.transAxes,
                ha="left",
                va="bottom",
                fontsize=6.4,
                color=C_TEXT_WIN,
                clip_on=False,
            )
        )
    return header


FIG_TOP_MARGIN = 0.96
FIG_BOTTOM_MARGIN = 0.07
FIG_BOTTOM_MARGIN_LEGEND = 0.11
FIG_LEFT_MARGIN = 0.22
FIG_RIGHT_MARGIN = 0.022
FIGURE_CENTER_X = 0.5
LEGEND_GAP_BELOW_XLABEL = 0.008


def panel_height_in(n_rows: int, bottom_margin: float, top_margin: float = FIG_TOP_MARGIN) -> float:
    """Match v2 row pitch for an isolated dot+delta row block."""
    n_top, n_bot = len(by_delta(QUESTION_TYPE)), len(by_delta(COGNITIVE))
    n_total = n_top + n_bot
    plot_frac_combined = FIG_TOP_MARGIN - 0.11
    combined_h = (
        ROW_HEIGHT_IN * n_total * (1.0 + ROW_PANEL_VSPACE / 2.0) / plot_frac_combined
    )
    plot_frac_single = top_margin - bottom_margin
    block_frac = n_rows / n_total
    block_h_in = combined_h * plot_frac_combined * block_frac
    return block_h_in / plot_frac_single


def place_legend_below_xlabels(
    fig: plt.Figure,
    ax_left: plt.Axes,
    ax_right: plt.Axes,
    handles: list[Line2D],
) -> plt.Legend:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    to_fig = fig.transFigure.inverted()
    y_label_bottom = min(
        ax_left.xaxis.label.get_window_extent(renderer).transformed(to_fig).y0,
        ax_right.xaxis.label.get_window_extent(renderer).transformed(to_fig).y0,
    )
    return fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(FIGURE_CENTER_X, y_label_bottom - LEGEND_GAP_BELOW_XLABEL),
        bbox_transform=fig.transFigure,
        ncol=4,
        frameon=False,
        handletextpad=0.35,
        columnspacing=1.4,
    )


def legend_handles() -> list[Line2D]:
    return [
        Line2D(
            [],
            [],
            marker=marker,
            ms=size,
            mfc=color if filled else "white",
            mec=color,
            mew=1.0,
            linestyle="none",
            label=name,
        )
        for name, _attr, color, marker, size, filled in SERIES
    ]


def save_pair(
    rows: list[Row],
    stem: str,
    show_xlabel: bool,
    delta_annotate: bool,
    legend_below: bool,
) -> None:
    top = FIG_TOP_MARGIN
    bottom = FIG_BOTTOM_MARGIN_LEGEND if legend_below else FIG_BOTTOM_MARGIN
    fig_h = panel_height_in(len(rows), bottom, top_margin=top)
    fig = plt.figure(figsize=(TEXT_WIDTH_IN, fig_h))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[1.0, 0.36],
        wspace=0.038,
        left=FIG_LEFT_MARGIN,
        right=1.0 - FIG_RIGHT_MARGIN,
        top=top,
        bottom=bottom,
    )
    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])

    draw_dot_panel(ax_left, rows, show_xlabel=show_xlabel)
    delta_headers = draw_delta_panel(
        ax_right, rows, show_xlabel=show_xlabel, annotate=delta_annotate
    )

    extra: list = [*delta_headers]
    if legend_below:
        leg = place_legend_below_xlabels(fig, ax_left, ax_right, legend_handles())
        extra.append(leg)

    save_kw = {
        "dpi": mpl.rcParams["savefig.dpi"],
        "bbox_inches": "tight",
        "pad_inches": 0.025,
        "bbox_extra_artists": extra,
    }
    for ext in ("png", "pdf"):
        fig.savefig(OUT_DIR / f"{stem}.{ext}", **save_kw)
    plt.close(fig)
    print(f"wrote {OUT_DIR / (stem + '.png')}")


def main() -> None:
    set_style()
    q_rows = by_delta(QUESTION_TYPE)
    c_rows = by_delta(COGNITIVE)

    save_pair(
        q_rows,
        FIG_STEM_A,
        show_xlabel=True,
        delta_annotate=True,
        legend_below=False,
    )
    save_pair(
        c_rows,
        FIG_STEM_B,
        show_xlabel=True,
        delta_annotate=True,
        legend_below=True,
    )


if __name__ == "__main__":
    main()
