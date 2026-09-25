#!/usr/bin/env python3
"""Plot candidate and retained validation scores during experience distillation."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


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


def main() -> None:
    baseline, records = load_trace()
    iterations = [int(record["iteration"]) for record in records]
    scores = [100 * float(record["score"]) for record in records]
    accepted = [bool(record["accepted"]) for record in records]

    retained_x = [0]
    retained_y = [100 * baseline]
    current = 100 * baseline
    for iteration, score, keep in zip(iterations, scores, accepted):
        if keep:
            current = score
        retained_x.append(iteration)
        retained_y.append(current)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7,
            "axes.labelsize": 7.5,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.2,
        }
    )
    fig, ax = plt.subplots(figsize=(3.35, 2.25))

    rejected_x = [x for x, keep in zip(iterations, accepted) if not keep]
    rejected_y = [y for y, keep in zip(scores, accepted) if not keep]
    accepted_x = [x for x, keep in zip(iterations, accepted) if keep]
    accepted_y = [y for y, keep in zip(scores, accepted) if keep]

    ax.scatter(
        rejected_x,
        rejected_y,
        s=15,
        color="#B7BEC8",
        edgecolors="white",
        linewidths=0.35,
        label="Rejected candidate",
        zorder=2,
    )
    ax.scatter(
        accepted_x,
        accepted_y,
        s=24,
        color="#E07A5F",
        edgecolors="white",
        linewidths=0.45,
        label="Accepted candidate",
        zorder=4,
    )
    ax.step(
        retained_x,
        retained_y,
        where="post",
        color="#2F6690",
        linewidth=1.6,
        label="Retained package",
        zorder=3,
    )
    ax.scatter([0], [100 * baseline], s=22, color="#2F6690", edgecolors="white", linewidths=0.4, zorder=5)

    ax.annotate(
        f"{retained_y[-1]:.1f}",
        xy=(retained_x[-1], retained_y[-1]),
        xytext=(-2, 5),
        textcoords="offset points",
        ha="right",
        color="#2F6690",
        fontsize=6.5,
    )
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Validation score")
    ax.set_xlim(-0.8, 30.8)
    ax.set_ylim(53, 88)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.55, alpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False, handlelength=1.8)
    fig.tight_layout(pad=0.35)

    for suffix in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"experience_distillation_convergence.{suffix}", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()
