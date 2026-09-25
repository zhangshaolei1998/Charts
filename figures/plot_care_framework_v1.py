#!/usr/bin/env python3
"""Draw the CARE framework figure used by the ICLR 2027 manuscript."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


HERE = Path(__file__).resolve().parent

COLORS = {
    "ink": "#25313C",
    "muted": "#66717C",
    "line": "#9AA4AE",
    "panel": "#F7F9FB",
    "analysis": "#2F6FAE",
    "analysis_fill": "#E9F2FB",
    "repr": "#D9792B",
    "repr_fill": "#FFF0E3",
    "green": "#2D8A62",
    "green_fill": "#E8F5EF",
    "red": "#B85B56",
    "red_fill": "#FAECEA",
    "purple": "#7356A8",
    "purple_fill": "#F1ECF8",
    "white": "#FFFFFF",
}


mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 14,
        "axes.linewidth": 0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def rounded_box(ax, x, y, w, h, *, face, edge, lw=1.4, radius=0.012, z=2):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(
    ax,
    start,
    end,
    *,
    color=None,
    lw=1.7,
    style="-|>",
    dashed=False,
    connectionstyle="arc3",
    z=3,
):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=14,
        linewidth=lw,
        color=color or COLORS["ink"],
        linestyle="--" if dashed else "-",
        connectionstyle=connectionstyle,
        shrinkA=2,
        shrinkB=2,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def label(ax, x, y, text, *, size=14, weight="normal", color=None, ha="center", va="center", z=5):
    return ax.text(
        x,
        y,
        text,
        fontsize=size,
        fontweight=weight,
        color=color or COLORS["ink"],
        ha=ha,
        va=va,
        zorder=z,
    )


def mini_text_icon(ax, x, y, w=0.030, h=0.050, color=None):
    color = color or COLORS["analysis"]
    ax.add_patch(Rectangle((x, y), w, h, facecolor=COLORS["white"], edgecolor=color, lw=1.2, zorder=5))
    for frac, length in [(0.72, 0.70), (0.50, 0.86), (0.28, 0.58)]:
        ax.plot([x + 0.16 * w, x + (0.16 + length) * w], [y + frac * h] * 2, color=color, lw=1.1, zorder=6)


def mini_chart_icon(ax, x, y, w=0.040, h=0.052, color=None):
    color = color or COLORS["repr"]
    ax.plot([x, x, x + w], [y + h, y, y], color=COLORS["line"], lw=1.0, zorder=5)
    xs = [x + 0.05 * w, x + 0.30 * w, x + 0.56 * w, x + 0.82 * w, x + 0.98 * w]
    ys = [y + 0.18 * h, y + 0.48 * h, y + 0.34 * h, y + 0.83 * h, y + 0.66 * h]
    ax.plot(xs, ys, color=color, lw=1.7, marker="o", markersize=2.7, zorder=6)


def score_badge(ax, x, y, text, good=True):
    face = COLORS["green_fill"] if good else COLORS["red_fill"]
    edge = COLORS["green"] if good else COLORS["red"]
    rounded_box(ax, x, y, 0.050, 0.041, face=face, edge=edge, lw=1.0, radius=0.009, z=5)
    label(ax, x + 0.025, y + 0.021, text, size=11.5, weight="bold", color=edge, z=6)


def dual_library(ax, x, y, w, h, *, title, frozen=False):
    rounded_box(ax, x, y, w, h, face=COLORS["white"], edge=COLORS["ink"], lw=1.5, radius=0.012)
    title_text = ("▣  " if frozen else "") + title
    label(ax, x + w / 2, y + h - 0.028, title_text, size=12.5, weight="bold")
    gap = 0.012
    inner_x = x + 0.012
    inner_w = w - 0.024
    card_h = (h - 0.060 - gap) / 2
    lower_y = y + 0.012
    upper_y = lower_y + card_h + gap
    rounded_box(ax, inner_x, upper_y, inner_w, card_h, face=COLORS["analysis_fill"], edge=COLORS["analysis"], lw=1.2, radius=0.008, z=3)
    rounded_box(ax, inner_x, lower_y, inner_w, card_h, face=COLORS["repr_fill"], edge=COLORS["repr"], lw=1.2, radius=0.008, z=3)
    label(ax, inner_x + 0.012, upper_y + card_h * 0.66, r"$E_A$  Analysis experience", size=10.8, weight="bold", color=COLORS["analysis"], ha="left")
    label(ax, inner_x + 0.012, upper_y + card_h * 0.30, "construct evidence", size=10.2, color=COLORS["muted"], ha="left")
    label(ax, inner_x + 0.012, lower_y + card_h * 0.66, r"$E_R$  Representation experience", size=10.5, weight="bold", color=COLORS["repr"], ha="left")
    label(ax, inner_x + 0.012, lower_y + card_h * 0.30, "represent and consume evidence", size=9.7, color=COLORS["muted"], ha="left")


def draw():
    fig, ax = plt.subplots(figsize=(14.2, 8.2))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Panel backgrounds and titles.
    rounded_box(ax, 0.012, 0.525, 0.976, 0.452, face=COLORS["panel"], edge="#D4DAE0", lw=1.1, radius=0.014, z=0)
    rounded_box(ax, 0.012, 0.022, 0.976, 0.465, face=COLORS["panel"], edge="#D4DAE0", lw=1.1, radius=0.014, z=0)
    label(ax, 0.030, 0.951, "(a) Outcome-guided dual-experience evolution", size=17.5, weight="bold", ha="left")
    label(ax, 0.030, 0.460, "(b) Experience-augmented online analysis", size=17.5, weight="bold", ha="left")

    # ---------------- Offline panel ----------------
    rounded_box(ax, 0.030, 0.675, 0.115, 0.150, face=COLORS["white"], edge=COLORS["ink"])
    label(ax, 0.0875, 0.796, "Curriculum task", size=11.8, weight="bold")
    mini_text_icon(ax, 0.046, 0.708, 0.030, 0.057, COLORS["purple"])
    label(ax, 0.084, 0.751, "Question", size=11.8, ha="left")
    label(ax, 0.084, 0.715, "+ schema", size=11.8, ha="left", color=COLORS["muted"])

    rounded_box(ax, 0.178, 0.595, 0.265, 0.292, face=COLORS["white"], edge=COLORS["line"], lw=1.2)
    label(ax, 0.3105, 0.856, "Multimodal analysis rollouts", size=12.7, weight="bold")
    label(ax, 0.3105, 0.827, "text and chart channels available", size=10.2, color=COLORS["muted"])
    lane_ys = [0.753, 0.684, 0.615]
    lane_texts = ["Text → Answer", "Chart → Answer", "Chart + Text → Answer"]
    scores = [("3.8", True), ("1.7", False), ("4.0", True)]
    for i, (yy, lane, (score, good)) in enumerate(zip(lane_ys, lane_texts, scores), start=1):
        rounded_box(ax, 0.193, yy, 0.232, 0.052, face="#FBFCFD", edge="#DDE2E7", lw=0.9, radius=0.007, z=3)
        label(ax, 0.204, yy + 0.026, rf"$\tau_{i}$", size=12.5, weight="bold", ha="left")
        if i == 1:
            mini_text_icon(ax, 0.242, yy + 0.007, 0.020, 0.036, COLORS["analysis"])
        elif i == 2:
            mini_chart_icon(ax, 0.240, yy + 0.007, 0.027, 0.038, COLORS["repr"])
        else:
            mini_chart_icon(ax, 0.238, yy + 0.008, 0.024, 0.035, COLORS["repr"])
            mini_text_icon(ax, 0.266, yy + 0.008, 0.018, 0.034, COLORS["analysis"])
        label(ax, 0.276 if i < 3 else 0.292, yy + 0.026, lane, size=9.0, ha="left")
        score_badge(ax, 0.366, yy + 0.006, score, good)

    rounded_box(ax, 0.474, 0.682, 0.098, 0.143, face=COLORS["purple_fill"], edge=COLORS["purple"])
    label(ax, 0.523, 0.785, "Outcome judge", size=10.4, weight="bold", color=COLORS["purple"])
    label(ax, 0.523, 0.749, "final answer", size=9.9)
    label(ax, 0.523, 0.720, "+ reference", size=9.9)
    label(ax, 0.523, 0.694, "scalar score only", size=9.5, weight="bold", color=COLORS["purple"])

    rounded_box(ax, 0.607, 0.675, 0.102, 0.155, face=COLORS["white"], edge=COLORS["ink"])
    label(ax, 0.658, 0.796, "Experience", size=11.8, weight="bold")
    label(ax, 0.658, 0.770, "evolver", size=11.8, weight="bold")
    label(ax, 0.658, 0.728, "compare scored", size=9.5)
    label(ax, 0.658, 0.704, "trajectories", size=9.5)
    label(ax, 0.658, 0.681, r"jointly update $E_A,E_R$", size=8.9, weight="bold", color=COLORS["purple"])

    rounded_box(ax, 0.753, 0.588, 0.158, 0.300, face=COLORS["white"], edge=COLORS["ink"], lw=1.5)
    label(ax, 0.832, 0.857, r"Candidate $\widetilde{E}^{(k+1)}$", size=11.2, weight="bold")
    rounded_box(ax, 0.765, 0.727, 0.134, 0.108, face=COLORS["analysis_fill"], edge=COLORS["analysis"], lw=1.2, radius=0.008)
    rounded_box(ax, 0.765, 0.605, 0.134, 0.108, face=COLORS["repr_fill"], edge=COLORS["repr"], lw=1.2, radius=0.008)
    label(ax, 0.832, 0.802, r"$E_A$  Analysis", size=10.4, weight="bold", color=COLORS["analysis"])
    label(ax, 0.832, 0.774, "experience", size=10.1, weight="bold", color=COLORS["analysis"])
    label(ax, 0.832, 0.745, "construct evidence", size=8.9, color=COLORS["muted"])
    label(ax, 0.832, 0.680, r"$E_R$  Representation", size=9.8, weight="bold", color=COLORS["repr"])
    label(ax, 0.832, 0.652, "experience", size=10.1, weight="bold", color=COLORS["repr"])
    label(ax, 0.832, 0.623, "represent & consume", size=8.9, color=COLORS["muted"])

    gate = Polygon(
        [[0.958, 0.805], [0.994, 0.748], [0.958, 0.691], [0.922, 0.748]],
        closed=True,
        facecolor=COLORS["green_fill"],
        edgecolor=COLORS["green"],
        linewidth=1.4,
        zorder=3,
    )
    ax.add_patch(gate)
    label(ax, 0.958, 0.761, "dev gain", size=11.3, weight="bold", color=COLORS["green"])
    label(ax, 0.958, 0.735, r"$\geq\delta$?", size=13.2, weight="bold", color=COLORS["green"])

    arrow(ax, (0.145, 0.750), (0.178, 0.750))
    arrow(ax, (0.443, 0.750), (0.474, 0.750), color=COLORS["purple"])
    arrow(ax, (0.572, 0.750), (0.607, 0.750), color=COLORS["purple"])
    arrow(ax, (0.709, 0.750), (0.753, 0.750))
    arrow(ax, (0.911, 0.748), (0.922, 0.748), color=COLORS["green"])

    # Reject loop: retain current version and resample.
    arrow(
        ax,
        (0.958, 0.691),
        (0.311, 0.888),
        color=COLORS["red"],
        lw=1.25,
        dashed=True,
        connectionstyle="arc3,rad=-0.19",
        z=1,
    )
    label(ax, 0.684, 0.900, r"reject: retain $E^{(k)}$", size=10.9, color=COLORS["red"])

    # Bridge from accepted candidate to the frozen online library.
    arrow(ax, (0.958, 0.691), (0.958, 0.515), color=COLORS["green"], lw=1.8, connectionstyle="arc3,rad=0.12")
    arrow(ax, (0.958, 0.515), (0.594, 0.414), color=COLORS["green"], lw=1.8, connectionstyle="arc3,rad=0.0")
    label(ax, 0.911, 0.533, "accept & freeze", size=11.3, weight="bold", color=COLORS["green"])

    # ---------------- Online panel ----------------
    rounded_box(ax, 0.034, 0.188, 0.120, 0.142, face=COLORS["white"], edge=COLORS["ink"])
    label(ax, 0.094, 0.299, "Current state", size=11.8, weight="bold")
    label(ax, 0.094, 0.263, "question + schema", size=11.4)
    label(ax, 0.094, 0.235, "+ trajectory", size=11.4)
    label(ax, 0.094, 0.205, r"$s_t$", size=13.5, weight="bold", color=COLORS["purple"])

    rounded_box(ax, 0.190, 0.188, 0.126, 0.142, face=COLORS["analysis_fill"], edge=COLORS["analysis"])
    label(ax, 0.253, 0.304, "Construct evidence", size=10.2, weight="bold", color=COLORS["analysis"])
    label(ax, 0.253, 0.264, "select operation", size=10.3)
    label(ax, 0.253, 0.232, "filter · aggregate", size=9.8, color=COLORS["muted"])
    label(ax, 0.253, 0.205, "align · test · stop", size=9.8, color=COLORS["muted"])

    rounded_box(ax, 0.351, 0.188, 0.115, 0.142, face=COLORS["white"], edge=COLORS["line"])
    label(ax, 0.4085, 0.304, "Intermediate view", size=9.9, weight="bold")
    mini_chart_icon(ax, 0.371, 0.216, 0.073, 0.060, COLORS["analysis"])
    label(ax, 0.4085, 0.203, r"$V_t$", size=12.8, weight="bold", color=COLORS["analysis"])

    rounded_box(ax, 0.370, 0.350, 0.255, 0.090, face=COLORS["white"], edge=COLORS["ink"], lw=1.4)
    label(ax, 0.408, 0.414, "▣  Frozen DEL", size=11.5, weight="bold")
    rounded_box(ax, 0.386, 0.365, 0.102, 0.032, face=COLORS["analysis_fill"], edge=COLORS["analysis"], lw=1.0, radius=0.006)
    rounded_box(ax, 0.504, 0.365, 0.105, 0.032, face=COLORS["repr_fill"], edge=COLORS["repr"], lw=1.0, radius=0.006)
    label(ax, 0.437, 0.381, r"$E_A$  analysis", size=9.6, weight="bold", color=COLORS["analysis"])
    label(ax, 0.5565, 0.381, r"$E_R$  representation", size=9.2, weight="bold", color=COLORS["repr"])

    rounded_box(ax, 0.508, 0.188, 0.145, 0.142, face=COLORS["repr_fill"], edge=COLORS["repr"])
    label(ax, 0.5805, 0.304, "Represent & consume", size=10.1, weight="bold", color=COLORS["repr"])
    mini_text_icon(ax, 0.530, 0.224, 0.026, 0.047, COLORS["analysis"])
    mini_chart_icon(ax, 0.570, 0.224, 0.038, 0.047, COLORS["repr"])
    label(ax, 0.628, 0.247, "hybrid", size=11.3, color=COLORS["muted"])
    label(ax, 0.5805, 0.204, "Text · Chart · Hybrid", size=11.0)

    rounded_box(ax, 0.688, 0.188, 0.132, 0.142, face=COLORS["white"], edge=COLORS["ink"])
    label(ax, 0.754, 0.304, "Reason over evidence", size=9.8, weight="bold")
    label(ax, 0.754, 0.262, "discover candidates", size=10.1)
    label(ax, 0.754, 0.232, "verify if needed", size=10.3, weight="bold", color=COLORS["repr"])
    label(ax, 0.754, 0.204, "revise or conclude", size=9.9, color=COLORS["muted"])

    rounded_box(ax, 0.866, 0.204, 0.100, 0.110, face=COLORS["green_fill"], edge=COLORS["green"])
    label(ax, 0.916, 0.279, "Final answer", size=11.5, weight="bold", color=COLORS["green"])
    label(ax, 0.916, 0.239, "grounded", size=11.2)
    label(ax, 0.916, 0.216, "insight", size=11.2)

    arrow(ax, (0.154, 0.259), (0.190, 0.259), color=COLORS["analysis"])
    arrow(ax, (0.316, 0.259), (0.351, 0.259), color=COLORS["analysis"])
    arrow(ax, (0.466, 0.259), (0.508, 0.259), color=COLORS["repr"])
    arrow(ax, (0.653, 0.259), (0.688, 0.259), color=COLORS["repr"])
    arrow(ax, (0.820, 0.259), (0.866, 0.259), color=COLORS["green"])

    # Retrieval arrows from the frozen library to the two decision points.
    arrow(ax, (0.421, 0.350), (0.270, 0.330), color=COLORS["analysis"], lw=1.5, connectionstyle="arc3,rad=0.10")
    label(ax, 0.337, 0.357, r"retrieve $E_A$", size=11.1, weight="bold", color=COLORS["analysis"])
    arrow(ax, (0.560, 0.350), (0.580, 0.330), color=COLORS["repr"], lw=1.5, connectionstyle="arc3,rad=-0.04")
    label(ax, 0.613, 0.357, r"retrieve $E_R$", size=11.1, weight="bold", color=COLORS["repr"])

    # Online revise loop.
    arrow(
        ax,
        (0.754, 0.188),
        (0.094, 0.188),
        color=COLORS["muted"],
        lw=1.35,
        dashed=True,
        connectionstyle="arc3,rad=-0.18",
        z=1,
    )
    label(ax, 0.420, 0.090, r"revise the plan and continue with $s_{t+1}$", size=11.5, color=COLORS["muted"])

    # Main conceptual takeaway.
    label(
        ax,
        0.500,
        0.047,
        "Decoupled storage  •  coordinated analytical decisions",
        size=13.3,
        weight="bold",
        color=COLORS["ink"],
    )

    for suffix in ("pdf", "png"):
        out = HERE / f"care_framework_v1.{suffix}"
        fig.savefig(out, dpi=320, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    draw()
