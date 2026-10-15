"""Overlay summary metrics from saved benchmark experiments.

Example:
    python compare_experiments.py --experiments 025 026 027
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import ScalarFormatter

ROOT = Path(__file__).resolve().parent
EXPERIMENTS_DIR = ROOT / "experiments"
CONDITION_MARKERS = {"eager": "o", "dynamic": "^"}
METRICS = [
    ("mean_input_tokens", "Mean Input Tokens", "tokens", False),
    ("mean_cached_tokens", "Mean Cached Input Tokens", "tokens", False),
    ("mean_output_tokens", "Mean Output Tokens", "tokens", False),
    ("mean_reasoning_tokens", "Mean Reasoning Tokens", "tokens", False),
    ("mean_total_tokens", "Mean Total Tokens", "tokens", False),
    ("cached_input_rate", "Cached Share of Input Tokens", "cache hit rate", True),
    ("mean_input_cost_usd", "Estimated Input Cost per Task", "USD", False),
    ("mean_output_cost_usd", "Estimated Output Cost per Task", "USD", False),
    ("mean_estimated_cost_usd", "Estimated Total Cost per Task", "USD", False),
    ("mean_cache_savings_usd", "Cache Savings per Task", "USD", False),
    (
        "cache_cost_savings_rate",
        "Cache Savings Rate on Total Cost",
        "savings rate",
        True,
    ),
    (
        "cost_per_correct_selection_usd",
        "Actual Spend per Correct Tool Selection",
        "USD",
        False,
    ),
    (
        "wrong_routing_spend_rate",
        "Spend Wasted on Wrong Tool Routing",
        "wasted spend rate",
        True,
    ),
    ("mean_latency_ms", "Mean End-to-End Latency", "milliseconds", False),
    ("p95_latency_ms", "P95 End-to-End Latency", "milliseconds", False),
    ("tool_selection_accuracy", "Tool Selection Accuracy", "accuracy", True),
    (
        "mean_decision_callable_tools",
        "Mean Callable Tools at Final Selection",
        "tools per question",
        False,
    ),
]


def parse_experiment_ids(raw_ids: list[str]) -> list[str]:
    ids = [
        item.strip() for value in raw_ids for item in value.split(",") if item.strip()
    ]
    if len(ids) < 2:
        raise ValueError(
            "Provide at least two experiments, for example: --experiments 025 026"
        )
    missing = [
        item for item in ids if not (EXPERIMENTS_DIR / item / "summary.csv").exists()
    ]
    if missing:
        raise FileNotFoundError(
            f"Missing summary.csv for experiment(s): {', '.join(missing)}"
        )
    return ids


def load_summaries(experiment_ids: list[str]) -> pd.DataFrame:
    frames = []
    for experiment_id in experiment_ids:
        frame = pd.read_csv(EXPERIMENTS_DIR / experiment_id / "summary.csv")
        frame["experiment"] = experiment_id
        if "catalog_size" not in frame:
            frame["catalog_size"] = 20
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def format_axis(ax: plt.Axes, ylabel: str, percent: bool) -> None:
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    if percent:
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
    elif ylabel == "USD":
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda value, _: f"${value:.6f}")
        )
    elif ylabel == "milliseconds":
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda value, _: f"{value:,.0f}")
        )
    else:
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(formatter)


def plot_metric(
    summary: pd.DataFrame,
    column: str,
    title: str,
    ylabel: str,
    percent: bool,
    output_path: Path,
) -> bool:
    frame = summary.dropna(subset=[column]).copy()
    if frame.empty:
        return False
    frame["point_label"] = frame.apply(
        lambda row: f"exp {row['experiment']}\n{int(row['catalog_size'])} tools", axis=1
    )
    frame = frame.sort_values(["experiment", "catalog_size", "condition"])
    labels = list(dict.fromkeys(frame["point_label"]))
    x_positions = {label: index for index, label in enumerate(labels)}
    colors = dict(
        zip(frame["experiment"].drop_duplicates(), plt.cm.tab10.colors, strict=False)
    )
    fig, ax = plt.subplots(figsize=(max(9, len(labels) * 1.25), 5))
    for _, row in frame.iterrows():
        x = x_positions[row["point_label"]]
        condition = str(row["condition"])
        ax.scatter(
            x,
            row[column],
            color=colors[row["experiment"]],
            marker=CONDITION_MARKERS.get(condition, "s"),
            s=88,
            zorder=3,
        )
    for experiment, subset in frame.groupby("experiment", sort=False):
        for condition, condition_subset in subset.groupby("condition", sort=False):
            condition_subset = condition_subset.sort_values("catalog_size")
            xs = [x_positions[label] for label in condition_subset["point_label"]]
            ax.plot(
                xs,
                condition_subset[column],
                color=colors[experiment],
                linestyle="-" if condition == "eager" else "--",
                alpha=0.65,
                zorder=2,
            )
    ax.set(
        title=title,
        xlabel="experiment and catalog size",
        xticks=range(len(labels)),
        xticklabels=labels,
    )
    format_axis(ax, ylabel, percent)
    experiment_handles = [
        plt.Line2D(
            [],
            [],
            color=color,
            marker="o",
            linestyle="",
            label=f"experiment {experiment}",
        )
        for experiment, color in colors.items()
    ]
    condition_handles = [
        plt.Line2D(
            [],
            [],
            color="#555555",
            marker=marker,
            linestyle="-" if condition == "eager" else "--",
            label=condition,
        )
        for condition, marker in CONDITION_MARKERS.items()
    ]
    first_legend = ax.legend(
        handles=experiment_handles, title="color", loc="upper left"
    )
    ax.add_artist(first_legend)
    ax.legend(handles=condition_handles, title="shape / line", loc="upper right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare metrics from two or more saved benchmark experiments."
    )
    parser.add_argument(
        "--experiments",
        nargs="+",
        required=True,
        help="Experiment IDs, e.g. 025 026 or 025,026",
    )
    args = parser.parse_args()
    experiment_ids = parse_experiment_ids(args.experiments)
    summary = load_summaries(experiment_ids)
    output_dir = EXPERIMENTS_DIR / f"compare_{'_'.join(experiment_ids)}" / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for index, (column, title, ylabel, percent) in enumerate(METRICS, start=1):
        if column in summary.columns:
            written += plot_metric(
                summary,
                column,
                title,
                ylabel,
                percent,
                output_dir / f"{index:02d}_{column}.png",
            )
    combined_path = output_dir.parent / "combined_summary.csv"
    summary.to_csv(combined_path, index=False)
    print(f"Compared experiments: {', '.join(experiment_ids)}")
    print(f"Generated {written} PNG files in: {output_dir}")
    print(f"Combined summary: {combined_path}")


if __name__ == "__main__":
    main()
