"""Column-chart rendering of the ProbeTask slice tables (question type / cognitive load).

Slices are ordered along x by Delta = Chart - Text, so text-advantaged slices sit on the
left of a dashed divider and chart-advantaged slices on the right. Slice sizes (n) are
shown either as donuts (v1, v2) or as a marginal strip above each panel (v3).

Usage:
    python paper_write/iclr2027/scripts/plot_slice_columns.py

Writes PNG + PDF into paper_write/iclr2027/figures/.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle

OUT_DIR = Path(__file__).resolve().parents[1] / "figures"

TEXT_WIDTH_IN = 5.5

C_NOTOOL = "#9199A1"
C_TEXT = "#35618F"
C_CHART = "#C05A24"
C_BOTH = "#7B5AA6"
C_CHART_WIN = "#1F7A6C"
C_TEXT_WIN = "#B0651F"
C_TIE = "#9AA1A8"
C_GRID = "#D8DCE0"
C_INK = "#1A1A1A"
C_MUTED = "#6B7278"

LOW_N = 8  # slices below this n are de-emphasised as exploratory

OVERALL_EXEC = 0.778  # Text / Chart / Text+Chart all land at ~0.78 over all tasks
OVERALL_NOTOOL = 0.296


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
    def side(self) -> int:
        if abs(self.delta) < 1e-9:
            return 0
        return 1 if self.delta > 0 else -1


QUESTION_TYPE = [
    Row("Numerical\nquery", 9, 0.139, 0.472, 0.250, 0.472),
    Row("Composition /\ndistribution", 43, 0.326, 0.924, 0.924, 0.907),
    Row("Ranking /\nextrema", 7, 0.429, 0.857, 0.857, 0.857),
    Row("Group\ncomparison", 63, 0.302, 0.758, 0.726, 0.762),
    Row("Temporal\nchange", 36, 0.278, 0.674, 0.799, 0.667),
    Row("Relationship\nanalysis", 18, 0.208, 0.708, 0.750, 0.764),
    Row("Anomaly /\nrisk", 13, 0.308, 0.808, 0.904, 0.827),
    Row("Diagnostic\nexplanation", 8, 0.469, 0.781, 0.750, 0.813),
    Row("Forecast /\nextrapolation", 3, 0.000, 1.000, 1.000, 1.000),
]

COGNITIVE = [
    Row("Lookup", 12, 0.146, 0.604, 0.521, 0.521),
    Row("Scan and\nselection", 24, 0.219, 0.958, 0.958, 0.958),
    Row("Comparative\njudgment", 69, 0.366, 0.801, 0.783, 0.808),
    Row("Pattern\nrecognition", 54, 0.306, 0.769, 0.833, 0.764),
    Row("Relational\nexplanation", 17, 0.221, 0.706, 0.735, 0.765),
    Row("Multidim.\nintegration", 20, 0.150, 0.575, 0.650, 0.600),
    Row("Conditional\nreasoning", 4, 0.813, 1.000, 0.750, 1.000),
]

# name, attribute, colour, filled
SERIES = [
    ("No-tool", "no_tool", C_NOTOOL, False),
    ("Text", "text", C_TEXT, True),
    ("Chart", "chart", C_CHART, True),
    ("Text+Chart", "both", C_BOTH, True),
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
            "xtick.color": C_INK,
            "ytick.color": C_MUTED,
            "axes.titlesize": 8.2,
            "legend.fontsize": 7.2,
            "savefig.dpi": 400,
        }
    )


def ordered(rows: list[Row]) -> list[Row]:
    """Left = text advantage, right = chart advantage."""
    return sorted(rows, key=lambda r: r.delta)


def divider_x(rows: list[Row]) -> float:
    """x position of the dashed text/chart separator (first non-negative slice)."""
    for i, row in enumerate(rows):
        if row.side >= 0:
            return i - 0.5
    return len(rows) - 0.5


def side_color(row: Row) -> str:
    return {1: C_CHART_WIN, -1: C_TEXT_WIN, 0: C_TIE}[row.side]


def wedge_colors(rows: list[Row]) -> list[str]:
    """Shade by advantage side; saturation tracks |Delta| so extremes read darkest."""
    shades: dict[int, str] = {}
    for side, base in ((-1, C_TEXT_WIN), (0, C_TIE), (1, C_CHART_WIN)):
        members = sorted(
            [r for r in rows if r.side == side], key=lambda r: abs(r.delta), reverse=True
        )
        rgb = np.array(mpl.colors.to_rgb(base))
        for k, row in enumerate(members):
            t = 0.0 if len(members) == 1 else 0.42 * k / (len(members) - 1)
            shades[id(row)] = mpl.colors.to_hex(rgb + (1.0 - rgb) * t)
    return [shades[id(r)] for r in rows]


# ------------------------------------------------------------------ panels


def draw_column_panel(
    ax,
    rows: list[Row],
    title: str,
    *,
    tick_colors: list[str] | None = None,
    show_n_in_tick: bool = True,
    label_size: float = 5.9,
    delta_size: float = 5.8,
    rotate: float = 0.0,
    advantage_labels: bool = True,
) -> None:
    xs = np.arange(len(rows), dtype=float)
    w = 0.19
    offsets = [-1.5 * w, -0.5 * w, 0.5 * w, 1.5 * w]
    xdiv = divider_x(rows)

    # faint side tinting
    ax.axvspan(-0.6, xdiv, color=C_TEXT_WIN, alpha=0.035, zorder=0)
    ax.axvspan(xdiv, len(rows) - 0.4, color=C_CHART_WIN, alpha=0.04, zorder=0)

    for x, row in zip(xs, rows):
        alpha = 0.55 if row.n < LOW_N else 1.0
        for off, (_, attr, color, filled) in zip(offsets, SERIES):
            ax.bar(
                x + off,
                getattr(row, attr),
                width=w,
                color=color if filled else "white",
                edgecolor=color,
                lw=0.55,
                alpha=alpha,
                zorder=3,
            )
        top = max(row.text, row.chart, row.both)
        txt = f"{row.delta:+.3f}" if row.side else "0.000"
        ax.text(
            x,
            top + 0.035,
            txt,
            ha="center",
            va="bottom",
            fontsize=delta_size,
            color=side_color(row),
            alpha=alpha,
            zorder=5,
        )

    ax.axhline(OVERALL_EXEC, color=C_MUTED, lw=0.6, ls=(0, (4, 2.5)), zorder=2)
    ax.axhline(OVERALL_NOTOOL, color=C_NOTOOL, lw=0.6, ls=(0, (1, 2)), zorder=2)
    ax.axvline(xdiv, color="#7F868D", lw=0.9, ls=(0, (3.5, 2.5)), zorder=4)

    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(0, 1.20)
    ax.set_xticks(xs)
    labels = [
        f"{r.label}\n" + r"$\it{n}$" + f"$\\,$={r.n}" if show_n_in_tick else r.label
        for r in rows
    ]
    ax.set_xticklabels(labels, fontsize=label_size, linespacing=1.15)
    for i, (tick, row) in enumerate(zip(ax.get_xticklabels(), rows)):
        if tick_colors is not None:
            tick.set_color(tick_colors[i])
        if row.n < LOW_N:
            tick.set_style("italic")
            if tick_colors is None:
                tick.set_color(C_MUTED)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_yticklabels([f"{v:.1f}" for v in np.arange(0, 1.01, 0.2)], fontsize=6.8)
    ax.yaxis.grid(True, color=C_GRID, lw=0.5, ls=(0, (1, 2.2)))
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.tick_params(axis="y", length=2.2, width=0.6)
    ax.set_ylabel("Judge score", fontsize=7.2, labelpad=2)
    ax.set_title(title, loc="left", pad=11, fontweight="bold")

    frac = (xdiv + 0.6) / (len(rows) + 0.2)
    ax.text(
        max(frac - 0.02, 0.0),
        1.005,
        r"$\leftarrow$ Text advantage",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.4,
        color=C_TEXT_WIN,
    )
    ax.text(
        min(frac + 0.02, 1.0),
        1.005,
        r"Chart advantage $\rightarrow$",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.4,
        color=C_CHART_WIN,
    )


def draw_donut(ax, rows: list[Row], title: str, colors: list[str]) -> None:
    sizes = [r.n for r in rows]
    total = sum(sizes)
    wedges, _ = ax.pie(
        sizes,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white", lw=0.7),
    )
    for wedge, row in zip(wedges, rows):
        ang = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        share = row.n / total
        r = 0.79
        if share >= 0.055:
            ax.text(
                r * np.cos(ang),
                r * np.sin(ang),
                f"{row.n}",
                ha="center",
                va="center",
                fontsize=5.8,
                color="white",
            )
        else:
            ax.text(
                1.16 * np.cos(ang),
                1.16 * np.sin(ang),
                f"{row.n}",
                ha="center",
                va="center",
                fontsize=5.4,
                color=C_MUTED,
            )
    ax.text(0, 0.06, f"{total}", ha="center", va="center", fontsize=8.0, weight="bold")
    ax.text(0, -0.17, "tasks", ha="center", va="center", fontsize=5.8, color=C_MUTED)
    ax.set_title(title, fontsize=6.6, color=C_MUTED, pad=1)


def draw_n_strip(ax, rows: list[Row], colors: list[str]) -> None:
    xs = np.arange(len(rows), dtype=float)
    ax.bar(xs, [r.n for r in rows], width=0.62, color=colors, zorder=3)
    for x, row in zip(xs, rows):
        ax.text(x, row.n + 2.5, str(row.n), ha="center", va="bottom", fontsize=5.4,
                color=C_MUTED)
    ax.axvline(divider_x(rows), color="#7F868D", lw=0.9, ls=(0, (3.5, 2.5)), zorder=4)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(0, max(r.n for r in rows) * 1.42)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_ylabel(r"$n$", fontsize=6.4, color=C_MUTED, rotation=0, labelpad=6,
                  va="center")


def legend_handles() -> list[Patch]:
    handles = [
        Patch(
            facecolor=color if filled else "white",
            edgecolor=color,
            lw=0.55,
            label=name,
        )
        for name, _attr, color, filled in SERIES
    ]
    handles.append(
        plt.Line2D([], [], color=C_MUTED, lw=0.6, ls=(0, (4, 2.5)),
                   label="all tasks (exec.) 0.78")
    )
    handles.append(
        plt.Line2D([], [], color=C_NOTOOL, lw=0.6, ls=(0, (1, 2)),
                   label="all tasks (no-tool) 0.30")
    )
    return handles


# ----------------------------------------------------------------- variants


def variant_1() -> None:
    """Single row: (a) (b) column charts, two donuts stacked at the far right."""
    q_rows, c_rows = ordered(QUESTION_TYPE), ordered(COGNITIVE)
    q_cols, c_cols = wedge_colors(q_rows), wedge_colors(c_rows)

    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 2.55))
    gs = fig.add_gridspec(
        1, 3, width_ratios=[len(q_rows), len(c_rows), 3.0], wspace=0.22,
        left=0.0, right=1.0, top=0.80, bottom=0.0,
    )
    ax_q = fig.add_subplot(gs[0, 0])
    ax_c = fig.add_subplot(gs[0, 1])
    gs_p = gs[0, 2].subgridspec(2, 1, hspace=0.30)
    ax_pq = fig.add_subplot(gs_p[0])
    ax_pc = fig.add_subplot(gs_p[1])

    draw_column_panel(ax_q, q_rows, "(a) By question type", tick_colors=q_cols,
                      show_n_in_tick=False, label_size=5.0, delta_size=4.8)
    draw_column_panel(ax_c, c_rows, "(b) By primary cognitive load",
                      tick_colors=c_cols, show_n_in_tick=False, label_size=5.0,
                      delta_size=4.8)
    ax_c.set_ylabel("")
    draw_donut(ax_pq, q_rows, "(c) slice sizes: question type", q_cols)
    draw_donut(ax_pc, c_rows, "(d) slice sizes: cognitive load", c_cols)

    fig.legend(
        handles=legend_handles(), loc="upper center", bbox_to_anchor=(0.44, 1.10),
        ncol=6, frameon=False, handletextpad=0.35, columnspacing=1.1,
        handlelength=1.3, fontsize=6.4,
    )
    save(fig, "probe_slice_columns_v1_row_donuts")


def variant_2() -> None:
    """Two rows, each column chart paired with its donut on the right."""
    q_rows, c_rows = ordered(QUESTION_TYPE), ordered(COGNITIVE)
    q_cols, c_cols = wedge_colors(q_rows), wedge_colors(c_rows)

    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 4.3))
    gs = fig.add_gridspec(
        2, 2, width_ratios=[1.0, 0.20], hspace=0.62, wspace=0.03,
        left=0.0, right=1.0, top=0.90, bottom=0.0,
    )
    ax_q = fig.add_subplot(gs[0, 0])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_pq = fig.add_subplot(gs[0, 1])
    ax_pc = fig.add_subplot(gs[1, 1])

    draw_column_panel(ax_q, q_rows, "(a) By question type", tick_colors=q_cols)
    draw_column_panel(ax_c, c_rows, "(b) By primary cognitive load",
                      tick_colors=c_cols)
    draw_donut(ax_pq, q_rows, "(c) slice sizes", q_cols)
    draw_donut(ax_pc, c_rows, "(d) slice sizes", c_cols)

    fig.legend(
        handles=legend_handles(), loc="upper center", bbox_to_anchor=(0.47, 1.005),
        ncol=6, frameon=False, handletextpad=0.35, columnspacing=1.2,
        handlelength=1.4, fontsize=6.6,
    )
    save(fig, "probe_slice_columns_v2_stacked_donuts")


def variant_3() -> None:
    """Two rows, slice size as a marginal bar strip above each column chart."""
    q_rows, c_rows = ordered(QUESTION_TYPE), ordered(COGNITIVE)
    q_cols, c_cols = wedge_colors(q_rows), wedge_colors(c_rows)

    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 4.35))
    gs = fig.add_gridspec(
        4, 1, height_ratios=[0.20, 1.0, 0.20, 1.0], hspace=0.10,
        left=0.0, right=1.0, top=0.90, bottom=0.0,
    )
    ax_qs = fig.add_subplot(gs[0])
    ax_q = fig.add_subplot(gs[1])
    ax_cs = fig.add_subplot(gs[2])
    ax_c = fig.add_subplot(gs[3])

    draw_n_strip(ax_qs, q_rows, q_cols)
    draw_column_panel(ax_q, q_rows, "", tick_colors=q_cols, show_n_in_tick=False,
                      label_size=6.2)
    draw_n_strip(ax_cs, c_rows, c_cols)
    draw_column_panel(ax_c, c_rows, "", tick_colors=c_cols, show_n_in_tick=False,
                      label_size=6.2)
    ax_qs.set_title("(a) By question type", loc="left", pad=10, fontweight="bold")
    ax_cs.set_title("(b) By primary cognitive load", loc="left", pad=10,
                    fontweight="bold")

    fig.legend(
        handles=legend_handles(), loc="upper center", bbox_to_anchor=(0.5, 1.005),
        ncol=6, frameon=False, handletextpad=0.35, columnspacing=1.2,
        handlelength=1.4, fontsize=6.6,
    )
    save(fig, "probe_slice_columns_v3_marginal_n")


def save(fig, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT_DIR / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"wrote {OUT_DIR / (name + '.png')}")


def main() -> None:
    set_style()
    variant_1()
    variant_2()
    variant_3()


if __name__ == "__main__":
    main()
