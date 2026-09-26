from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


_FRESHNESS_MAX_STALE_RATIO = 0.25
_SUMMARY_MIN_LENGTH = 50
_SUMMARY_MAX_LENGTH = 5_000


def _quality_report_path(settings: Settings, report_name: str) -> Path:
    """Return a safe, predictable path for a named quality report."""
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", report_name).strip("-_")
    safe_name = safe_name or "quality"
    if not safe_name.endswith("_quality_report"):
        safe_name = f"{safe_name}_quality_report"
    return settings.paths.quality_dir / f"{safe_name}.json"


def _freshness_metrics(df: pd.DataFrame, settings: Settings) -> dict[str, Any]:
    """Calculate freshness metrics without creating an artifact."""
    total_rows = len(df)

    if "published" in df.columns:
        published = pd.to_datetime(df["published"], errors="coerce", utc=True)
        valid_published = published.dropna()
    else:
        valid_published = pd.Series(dtype="datetime64[ns, UTC]")

    if "age_days" in df.columns:
        ages = pd.to_numeric(df["age_days"], errors="coerce")
    else:
        ages = pd.Series(float("nan"), index=df.index, dtype="float64")

    invalid_age_rows = int(ages.isna().sum())
    stale_rows = int(ages.gt(settings.freshness_threshold_days).sum())
    stale_ratio = stale_rows / total_rows if total_rows else 0.0

    # Missing/invalid ages make the SLA unverifiable, so they fail closed.
    is_fresh = bool(
        total_rows > 0
        and invalid_age_rows == 0
        and stale_ratio <= _FRESHNESS_MAX_STALE_RATIO
    )

    return {
        "latest_published": (
            valid_published.max().date().isoformat() if not valid_published.empty else None
        ),
        "oldest_published": (
            valid_published.min().date().isoformat() if not valid_published.empty else None
        ),
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "stale_ratio": stale_ratio,
        "invalid_age_rows": invalid_age_rows,
        "freshness_threshold_days": settings.freshness_threshold_days,
        "max_stale_ratio": _FRESHNESS_MAX_STALE_RATIO,
        "is_fresh": is_fresh,
    }


def run_data_quality_checks(
    df: pd.DataFrame,
    settings: Settings,
    report_name: str,
) -> dict[str, Any]:
    """Run the GX 1.x quality gate and persist its JSON result.

    The gate combines structural/content expectations with the freshness SLA.
    A dataset passes only when both parts pass.
    """
    # Import lazily so freshness reporting remains usable by itself and so that
    # importing this module does not eagerly initialize the relatively heavy GX
    # runtime.
    import great_expectations as gx

    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(name="papers_source")
    data_asset = data_source.add_dataframe_asset(name="papers_asset")
    batch_definition = data_asset.add_batch_definition_whole_dataframe("papers_batch")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    expectations = [
        gx.expectations.ExpectTableRowCountToBeBetween(
            min_value=1,
            max_value=settings.max_results,
        ),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="paper_id"),
        gx.expectations.ExpectColumnValuesToBeUnique(column="paper_id"),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="title"),
        gx.expectations.ExpectColumnValueLengthsToBeBetween(
            column="summary",
            min_value=_SUMMARY_MIN_LENGTH,
            max_value=_SUMMARY_MAX_LENGTH,
        ),
    ]
    suite = gx.ExpectationSuite(name=f"{report_name}_quality_suite", expectations=expectations)
    validation = batch.validate(suite, result_format="SUMMARY")
    validation_payload = validation.to_json_dict()

    freshness = _freshness_metrics(df, settings)
    gx_success = bool(validation.success)
    payload: dict[str, Any] = {
        "report_name": report_name,
        "success": gx_success and freshness["is_fresh"],
        "gx_success": gx_success,
        "freshness_success": freshness["is_fresh"],
        "freshness": freshness,
        "statistics": validation_payload.get("statistics", {}),
        "results": validation_payload.get("results", []),
        "great_expectations_result": validation_payload,
    }

    write_json(_quality_report_path(settings, report_name), payload)
    return payload


def build_freshness_report(
    df: pd.DataFrame,
    settings: Settings,
    report_path: str | Path,
) -> dict[str, Any]:
    """Build and persist the freshness SLA report for a dataframe."""
    payload = _freshness_metrics(df, settings)
    write_json(Path(report_path), payload)
    return payload
