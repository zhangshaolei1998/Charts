#!/usr/bin/env python3
"""Figure 4: validation trajectory during iterative experience distillation."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

try:
    from scipy.stats import t as student_t
except ImportError:  # pragma: no cover
    student_t = None

ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = (
    ROOT
    / "experiments"
    / "13_care_experience"
    / "outputs"
    / "build_opt"
    / "run_20260925T015252Z"
)
OUT_DIR = Path(__file__).resolve().parent
FIG_STEM = "experience_distillation_convergence_v2"

SCORE_SCALE = 100.0
CI_ALPHA = 0.05

# Canvas size from the pre–basic-style figure (half-column minipage).
FIG_W_IN = 3.42
FIG_H_IN = 2.35
SAVE_DPI = 400


def load_trace() -> tuple[float, list[dict[str, object]]]:
    history_path = RUN_DIR / "accepted_history.jsonl"
    events = [json.loads(line) for line in history_path.read_text().splitlines() if line]
    baseline = float(next(event for event in events if event["event"] == "baseline")["mean_final_score"])

    records: list[dict[str, object]] = []
    for summary_path in sorted(RUN_DIR.glob("iter_*/iter_summary.json")):
        summary = json.loads(summary_path.read_text())
        records.append(
            {
                "iteration": int(summary["iter"]),
                "score": float(summary["candidate_mean_final_score"]),
                "accepted": summary["gate_decision"] == "accept",
            }
        )
    return baseline, records


def retained_milestones(
    baseline: float,
    iterations: np.ndarray,
    scores: np.ndarray,
    accepted: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mx = [0.0]
    my = [SCORE_SCALE * baseline]
    for iteration, score, keep in zip(iterations, scores, accepted):
        if keep:
            mx.append(float(iteration))
            my.append(float(score))
    return np.array(mx), np.array(my)


def t_critical(dof: int, alpha: float = CI_ALPHA) -> float:
    if student_t is not None:
        return float(student_t.ppf(1.0 - alpha / 2.0, dof))
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
    return table.get(dof, 1.96)


def linear_mean_confidence_band(
    x: np.ndarray,
    y: np.ndarray,
    x_grid: np.ndarray,
    alpha: float = CI_ALPHA,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    slope, intercept = np.polyfit(x, y, deg=1)
    y_fit = slope * x + intercept
    n = len(x)
    dof = n - 2
    if dof < 1:
        y_grid = slope * x_grid + intercept
        return y_grid, y_grid, y_grid

    rss = float(np.sum((y - y_fit) ** 2))
    s_err = np.sqrt(rss / dof)
    x_mean = float(np.mean(x))
    ss_xx = float(np.sum((x - x_mean) ** 2))
    if ss_xx <= 0:
        y_grid = slope * x_grid + intercept
        return y_grid, y_grid, y_grid

    t_crit = t_critical(dof, alpha)
    se_mean = s_err * np.sqrt(1.0 / n + (x_grid - x_mean) ** 2 / ss_xx)
    y_grid = slope * x_grid + intercept
    return y_grid, y_grid - t_crit * se_mean, y_grid + t_crit * se_mean


def main() -> None:
    plt.rcdefaults()
    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
        }
    )

    baseline, records = load_trace()
    iterations = np.array([int(record["iteration"]) for record in records])
    scores = SCORE_SCALE * np.array([float(record["score"]) for record in records])
    accepted = np.array([bool(record["accepted"]) for record in records])

    milestone_x, milestone_y = retained_milestones(baseline, iterations, scores, accepted)
    init_score = float(milestone_y[0])

    rejected_mask = ~accepted
    accepted_mask = accepted

    ymin = min(scores.min(), init_score) - 4.0
    ymax = max(scores.max(), float(milestone_y[-1])) + 3.5
    ymin = max(50.0, np.floor(ymin / 5) * 5)
    ymax = min(92.0, np.ceil(ymax / 5) * 5)

    fig, ax = plt.subplots(figsize=(FIG_W_IN, FIG_H_IN))

    x_line = np.linspace(0.0, 30.0, 160)
    if len(milestone_x) >= 2:
        y_line, y_lo, y_hi = linear_mean_confidence_band(milestone_x, milestone_y, x_line)
        ax.fill_between(x_line, y_lo, y_hi, alpha=0.25)
        ax.plot(x_line, y_line, linewidth=1.7, label="Linear fit")

    ax.scatter(
        iterations[rejected_mask],
        scores[rejected_mask],
        s=11,
        c="0.75",
        label="Rejected",
    )
    ax.scatter(
        iterations[accepted_mask],
        scores[accepted_mask],
        s=28,
        c="C3",
        label="Accepted",
    )
    ax.scatter([0], [init_score], s=28, c="C0", label="_nolegend_")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Validation score")
    ax.set_xlim(-0.6, 30.6)
    ax.set_ylim(ymin, ymax)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.legend(loc="lower right")

    fig.tight_layout(pad=0.42)
    for suffix in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"{FIG_STEM}.{suffix}", dpi=SAVE_DPI, bbox_inches="tight")


if __name__ == "__main__":
    main()
