from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def _as_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return "" if value is None else str(value)


def _first_sentence(summary: Any) -> str:
    text = _as_text(summary).strip()
    return re.split(r"[.!?]", text, maxsplit=1)[0].strip()


def _date_text(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    try:
        return pd.Timestamp(value).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return _as_text(value)


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Build and persist a deterministic ten-question evaluation set."""
    required_columns = {
        "paper_id",
        "title",
        "summary",
        "authors",
        "categories",
        "published",
    }
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(df) < 10:
        raise ValueError("At least 10 documents are required to build the test set.")

    question_types = ["summary", "authors", "date", "categories"]
    test_set: list[dict[str, Any]] = []

    for index, (_, row) in enumerate(df.head(10).iterrows(), start=1):
        question_type = question_types[(index - 1) % len(question_types)]
        title = _as_text(row["title"])
        if question_type == "summary":
            question = f"What is the summary of the paper '{title}'?"
            ground_truth = _first_sentence(row["summary"])
        elif question_type == "authors":
            question = f"Who are the authors of \"{title}\"?"
            ground_truth = _as_text(row["authors"])
        elif question_type == "date":
            question = f"When was \"{title}\" published?"
            ground_truth = _date_text(row["published"])
        else:
            question = f"What are the categories of \"{title}\"?"
            ground_truth = _as_text(row["categories"])

        test_set.append(
            {
                "id": f"eval_{index:03d}",
                "question_type": question_type,
                "question": question,
                "ground_truth": ground_truth,
                "ground_truth_doc_ids": [_as_text(row["paper_id"])],
            }
        )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        json.dump(test_set, file, ensure_ascii=False, indent=2)

    return test_set
