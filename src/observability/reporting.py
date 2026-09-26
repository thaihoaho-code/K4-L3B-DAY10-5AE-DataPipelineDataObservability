from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _format_value(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)
    if value is None:
        return "N/A"
    return str(value)


def _cell(value: Any) -> str:
    return _format_value(value).replace("|", "\\|").replace("\n", "<br>")


def _mapping_table(values: dict[str, Any]) -> list[str]:
    lines = ["| Field | Value |", "| --- | --- |"]
    if not values:
        lines.append("| No data | N/A |")
    else:
        lines.extend(f"| {_cell(key)} | {_cell(value)} |" for key, value in values.items())
    return lines


def _metric_keys(*metrics: dict[str, Any]) -> list[str]:
    preferred = (
        "samples",
        "retrieval_hit_rate",
        "mean_token_f1",
        "judge_accuracy",
        "mean_judge_score",
    )
    keys = list(dict.fromkeys(key for metric in metrics for key in metric))
    return [key for key in preferred if key in keys] + [key for key in keys if key not in preferred]


def _metrics_table(
    baseline: dict[str, Any],
    corrupted: dict[str, Any],
    repaired: dict[str, Any],
) -> list[str]:
    lines = [
        "| Metric | Baseline | Corrupted | Repaired |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key in _metric_keys(baseline, corrupted, repaired):
        lines.append(
            f"| {_cell(key)} | {_cell(baseline.get(key))} | "
            f"{_cell(corrupted.get(key))} | {_cell(repaired.get(key))} |"
        )
    if len(lines) == 2:
        lines.append("| No metrics | N/A | N/A | N/A |")
    return lines


def _comparison_table(
    first_name: str,
    first: dict[str, Any],
    second_name: str,
    second: dict[str, Any],
) -> list[str]:
    keys = list(dict.fromkeys([*first.keys(), *second.keys()]))
    lines = [
        f"| Field | {first_name} | {second_name} |",
        "| --- | --- | --- |",
    ]
    for key in keys:
        lines.append(f"| {_cell(key)} | {_cell(first.get(key))} | {_cell(second.get(key))} |")
    if len(lines) == 2:
        lines.append(f"| No data | N/A | N/A |")
    return lines


def _write_report(report_path: Any, lines: list[str]) -> None:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report cho baseline phase.

    Pseudo-code:
    1. Gom source summary.
    2. In metrics retrieval/evaluation.
    3. In data quality va freshness.
    4. Ghi markdown vao report_path.
    """
    lines = [
        "# Phase 1 Report",
        "",
        "## Source Summary",
        *_mapping_table(source_summary),
        "",
        "## Evaluation Metrics",
        *_mapping_table(metrics),
    ]
    if quality:
        lines.extend(["", "## Data Quality", *_mapping_table(quality)])
    if freshness:
        lines.extend(["", "## Freshness", *_mapping_table(freshness)])

    _write_report(report_path, lines)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    lines = [
        "# Corruption Comparison Report",
        "",
        "## Evaluation Metrics",
        *_metrics_table(baseline_metrics, corrupted_metrics, repaired_metrics),
        "",
        "## Data Quality Comparison",
        "Baseline quality is not provided by this function's existing API.",
        "",
        *_comparison_table("Corrupted", corrupted_quality, "Repaired", repaired_quality),
        "",
        "## Freshness Comparison",
        "Baseline freshness is not provided by this function's existing API.",
        "",
        *_comparison_table("Corrupted", corrupted_freshness, "Repaired", repaired_freshness),
    ]
    _write_report(report_path, lines)
