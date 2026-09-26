#!/usr/bin/env python3
"""Interface ablation on ProbeBench: four matched settings under one backbone.

The three tool-enabled interfaces sit within about one point of each other,
so a single 0-100 axis would flatten them. The panel is split instead: the
upper segment zooms on the tool-enabled range, the lower segment keeps the
No-tool bar on a shared baseline.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent
FIG_STEM = "interface_ablation"

# Palette shared with the ProbeBench slice figure.
C_NOTOOL = "#9199A1"
C_TEXT = "#B0651F"
C_CHART = "#1F7A6C"
C_BOTH = "#7B5AA6"
C_GRID = "#D8DCE0"
C_INK = "#1A1A1A"
C_MUTED = "#6B7278"

LABELS = ["No-\ntool", "Text-\nonly", "Chart-\nonly", "Free-\nstyle"]
SCORES = [29.4, 77.2, 78.4, 77.6]
COLORS = [C_NOTOOL, C_TEXT, C_CHART, C_BOTH]

FIG_W_IN = 2.00
FIG_H_IN = 1.52

HI_LO, HI_HI = 74.0, 80.5
LO_LO, LO_HI = 0.0, 34.0


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
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 6.8,
            "axes.labelsize": 7.4,
            "savefig.dpi": 400,
        }
    )


def draw_bars(ax, annotate: bool) -> None:
    x = range(len(SCORES))
    ax.bar(x, SCORES, width=0.66, color=COLORS, edgecolor="none", zorder=3)
    if annotate:
        for xi, score in zip(x, SCORES):
            if score < HI_LO:
                continue
            ax.text(
                xi,
                score + 0.22,
                f"{score:.1f}",
                ha="center",
                va="bottom",
                fontsize=6.4,
                color=C_INK,
                zorder=4,
            )


def main() -> None:
    plt.rcdefaults()
    set_style()

    fig, (ax_hi, ax_lo) = plt.subplots(
        2,
        1,
        figsize=(FIG_W_IN, FIG_H_IN),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0], "hspace": 0.14},
    )

    for ax in (ax_hi, ax_lo):
        draw_bars(ax, annotate=ax is ax_hi)
        ax.yaxis.grid(True, color=C_GRID, lw=0.5, ls=(0, (1, 2.2)), zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", length=0)

    ax_hi.set_ylim(HI_LO, HI_HI)
    ax_hi.set_yticks([75, 77, 79])
    ax_hi.spines["bottom"].set_visible(False)
    ax_hi.spines["top"].set_visible(False)
    ax_hi.spines["right"].set_visible(False)

    ax_lo.set_ylim(LO_LO, LO_HI)
    ax_lo.set_yticks([0, 30])
    ax_lo.spines["top"].set_visible(False)
    ax_lo.spines["right"].set_visible(False)
    ax_lo.text(
        0,
        SCORES[0] + 1.0,
        f"{SCORES[0]:.1f}",
        ha="center",
        va="bottom",
        fontsize=6.4,
        color=C_INK,
        zorder=4,
    )

    ax_lo.set_xticks(range(len(LABELS)))
    ax_lo.set_xticklabels(LABELS, linespacing=0.95)

    # Break marks on the two facing edges.
    kwargs = dict(
        transform=ax_hi.transAxes,
        color="#8A9097",
        clip_on=False,
        lw=0.7,
    )
    dx, dy = 0.022, 0.030
    ax_hi.plot((-dx, +dx), (-dy, +dy), **kwargs)
    ax_hi.plot((1 - dx, 1 + dx), (-dy, +dy), **kwargs)
    kwargs.update(transform=ax_lo.transAxes)
    dy_lo = dy * 2.4
    ax_lo.plot((-dx, +dx), (1 - dy_lo, 1 + dy_lo), **kwargs)
    ax_lo.plot((1 - dx, 1 + dx), (1 - dy_lo, 1 + dy_lo), **kwargs)

    fig.tight_layout(pad=0.3)
    for suffix in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"{FIG_STEM}.{suffix}", dpi=400, bbox_inches="tight")


if __name__ == "__main__":
    main()
