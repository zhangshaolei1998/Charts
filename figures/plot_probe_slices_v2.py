"""v1 snapshot: renders probe_slices_dotplot.{png,pdf} (stacked dot plot, all slices).

Frozen copy of the generator behind Figure `probe_slices_dotplot`, kept next to the
figure so the paper source stays reproducible on its own. Self-contained: the slice
values are the ones in Tables `tab:question-type-slices` and `tab:cognitive-main`.

Usage:
    python paper_write/iclr2027/figures/plot_probe_slices_v1.py
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
FIG_NAME = "probe_slices_dotplot_v2"

TEXT_WIDTH_IN = 6.4
# Inches per slice row (top/bottom panels use height_ratios = row counts → equal row pitch).
ROW_HEIGHT_IN = 0.19
ROW_PANEL_VSPACE = 0.30  # gridspec hspace; keep in sync with main()

C_NOTOOL = "#9199A1"
C_TEXT = "#35618F"
C_CHART = "#C05A24"
C_BOTH = "#7B5AA6"
C_CHART_WIN = "#1F7A6C"
C_TEXT_WIN = "#B0651F"
C_GRID = "#D8DCE0"
C_BAND = "#F2F4F6"
C_INK = "#1A1A1A"
C_MUTED = "#6B7278"

LOW_N = 8  # rows below this n are de-emphasised as exploratory


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
ALL_TASKS = Row("All tasks", 202, 0.296, 0.774, 0.783, 0.778)

COGNITIVE = [
    Row("Lookup", 12, 0.146, 0.604, 0.521, 0.521),
    Row("Scan and selection", 24, 0.219, 0.958, 0.958, 0.958),
    Row("Comparative judgment", 69, 0.366, 0.801, 0.783, 0.808),
    Row("Pattern recognition", 54, 0.306, 0.769, 0.833, 0.764),
    Row("Relational explanation", 17, 0.221, 0.706, 0.735, 0.765),
    Row("Multidim. integration", 20, 0.150, 0.575, 0.650, 0.600),
    Row("Conditional reasoning", 4, 0.813, 1.000, 0.750, 1.000),
]

# name, attribute, colour, marker, size, filled
SERIES = [
    ("No-tool", "no_tool", C_NOTOOL, "o", 4.2, False),
    ("Text", "text", C_TEXT, "s", 4.6, True),
    ("Chart", "chart", C_CHART, "o", 5.2, True),
    ("Text+Chart", "both", C_BOTH, "D", 4.0, False),
]


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


def by_delta(rows: list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r: r.delta, reverse=True)


def row_label(r: Row) -> str:
    return f"{r.label}  " + r"$\it{n}$" + f"$\\,$={r.n}"


def style_yticks(ax, rows: list[Row]) -> None:
    for tick, row in zip(ax.get_yticklabels(), rows):
        if row.n < LOW_N:
            tick.set_color(C_MUTED)
            tick.set_style("italic")
        if row.label == "All tasks":
            tick.set_weight("bold")


def band(ax, y: float, xmin: float, xmax: float) -> None:
    """Alternating row stripe across the full judge-score x span."""
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
    color = C_CHART_WIN if row.delta >= 0 else C_TEXT_WIN
    txt = f"{row.delta:+.3f}" if abs(row.delta) > 1e-9 else "0.000"
    inside = abs(row.delta) > 0.62 * lim
    if inside:
        ax.text(
            row.delta - np.sign(row.delta) * 0.012,
            y,
            txt,
            va="center",
            ha="right" if row.delta >= 0 else "left",
            fontsize=fontsize,
            color="white",
            alpha=alpha,
            zorder=5,
        )
    else:
        ax.text(
            row.delta + np.sign(row.delta or 1.0) * 0.016,
            y,
            txt,
            va="center",
            ha="left" if row.delta >= 0 else "right",
            fontsize=fontsize,
            color=color if abs(row.delta) > 1e-9 else C_MUTED,
            alpha=alpha,
            zorder=5,
        )


def draw_dot_panel(ax, rows: list[Row], show_xlabel: bool) -> None:
    ys = np.arange(len(rows))[::-1]
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.margins(x=0)
    xmin, xmax = ax.get_xlim()
    for y, row in zip(ys, rows):
        alpha = 0.5 if row.n < LOW_N else 1.0
        if y % 2 == 0:
            band(ax, y, xmin, xmax)
        vals = [row.no_tool, row.text, row.chart, row.both]
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
            [row.text, row.chart],
            [y, y],
            color=seg_color,
            lw=2.8,
            alpha=0.30 * alpha,
            zorder=2,
            solid_capstyle="round",
        )
        for _, attr, color, marker, size, filled in SERIES:
            ax.plot(
                [getattr(row, attr)],
                [y],
                marker=marker,
                ms=size,
                mfc=color if filled else "white",
                mec=color,
                mew=1.0,
                alpha=alpha,
                linestyle="none",
                zorder=4,
            )
        if row.label == "All tasks":
            ax.axhline(y + 0.5, color="#9AA1A8", lw=0.6, ls=(0, (3, 2)), zorder=1.5)
    ax.set_yticks(ys)
    ax.set_yticklabels([row_label(r) for r in rows])
    style_yticks(ax, rows)
    ticks = np.arange(0, 1.01, 0.2)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{v:.1f}" for v in ticks])
    ax.xaxis.grid(True, color=C_GRID, lw=0.5, ls=(0, (1, 2.2)))
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=2.5, width=0.6)
    if show_xlabel:
        ax.set_xlabel("Judge score (task mean)", fontsize=7.6, labelpad=1)


def draw_delta_panel(ax, rows: list[Row], show_xlabel: bool, annotate: bool = False) -> None:
    ys = np.arange(len(rows))[::-1]
    lim = 0.30
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    xmin, xmax = ax.get_xlim()
    for y, row in zip(ys, rows):
        alpha = 0.5 if row.n < LOW_N else 1.0
        if y % 2 == 0:
            band(ax, y, xmin, xmax)
        color = C_CHART_WIN if row.delta >= 0 else C_TEXT_WIN
        ax.barh(y, row.delta, height=0.44, color=color, alpha=alpha, zorder=3)
        delta_label(ax, row, y, lim, alpha, 6.4)
        if row.label == "All tasks":
            ax.axhline(y + 0.5, color="#9AA1A8", lw=0.6, ls=(0, (3, 2)), zorder=1.5)

    ax.set_yticks([])
    ax.axvline(0, color="#8A9097", lw=0.6, zorder=2)
    ax.set_xticks([-0.2, 0.0, 0.2])
    ax.set_xticklabels(["$-$.2", "0", "+.2"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=2.5, width=0.6)
    if show_xlabel:
        ax.set_xlabel(r"$\Delta$ Chart$-$Text", fontsize=7.6, labelpad=1)
    if annotate:
        ax.text(
            0.95,
            1.008,
            "chart better",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=6.4,
            color=C_CHART_WIN,
        )
        ax.text(
            0.02,
            1.012,
            "text better",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=6.4,
            color=C_TEXT_WIN,
        )


FIG_TOP_MARGIN = 0.96
FIG_BOTTOM_MARGIN = 0.11  # room below bottom-row axes for xlabels + legend
FIG_LEFT_MARGIN = 0.22  # long y tick labels extend left of the axes box
FIG_RIGHT_MARGIN = 0.022  # Δ panel tick labels / annotations
FIGURE_CENTER_X = 0.5
LEGEND_GAP_BELOW_XLABEL = 0.008  # figure fraction between xlabel and legend


def place_row_title(
    fig: plt.Figure,
    ax_left: plt.Axes,
    ax_right: plt.Axes,
    title: str,
) -> None:
    pos_l = ax_left.get_position()
    pos_r = ax_right.get_position()
    y = max(pos_l.y1, pos_r.y1) + 0.008
    fig.text(
        FIGURE_CENTER_X,
        y,
        title,
        ha="center",
        va="bottom",
        fontweight="bold",
        fontsize=8.2,
        transform=fig.transFigure,
    )


def figure_height_in(n_top: int, n_bot: int) -> float:
    plot_frac = FIG_TOP_MARGIN - FIG_BOTTOM_MARGIN
    n_rows = n_top + n_bot
    # height_ratios = row counts → each slice row is ROW_HEIGHT_IN inches tall.
    return ROW_HEIGHT_IN * n_rows * (1.0 + ROW_PANEL_VSPACE / 2.0) / plot_frac


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


def main() -> None:
    set_style()
    q_rows = by_delta(QUESTION_TYPE)
    c_rows = by_delta(COGNITIVE)
    n_top, n_bot = len(q_rows), len(c_rows)

    fig = plt.figure(figsize=(TEXT_WIDTH_IN, figure_height_in(n_top, n_bot)))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.0, 0.36],
        height_ratios=[n_top, n_bot],
        hspace=ROW_PANEL_VSPACE,
        wspace=0.038,
        left=FIG_LEFT_MARGIN,
        right=1.0 - FIG_RIGHT_MARGIN,
        top=FIG_TOP_MARGIN,
        bottom=FIG_BOTTOM_MARGIN,
    )
    ax_q = fig.add_subplot(gs[0, 0])
    ax_qd = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_cd = fig.add_subplot(gs[1, 1])

    draw_dot_panel(ax_q, q_rows, show_xlabel=False)
    draw_delta_panel(ax_qd, q_rows, show_xlabel=False, annotate=True)
    draw_dot_panel(ax_c, c_rows, show_xlabel=True)
    draw_delta_panel(ax_cd, c_rows, show_xlabel=True)

    place_row_title(fig, ax_q, ax_qd, "(a) By question type")
    place_row_title(fig, ax_c, ax_cd, "(b) By primary cognitive load")

    leg = place_legend_below_xlabels(fig, ax_c, ax_cd, legend_handles())

    save_kw = {
        "dpi": mpl.rcParams["savefig.dpi"],
        "bbox_inches": "tight",
        "pad_inches": 0.025,
        "bbox_extra_artists": [*fig.texts, leg],
    }
    for ext in ("png", "pdf"):
        fig.savefig(OUT_DIR / f"{FIG_NAME}.{ext}", **save_kw)
    plt.close(fig)
    print(f"wrote {OUT_DIR / (FIG_NAME + '.png')}")


if __name__ == "__main__":
    main()
