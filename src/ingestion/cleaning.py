from __future__ import annotations

from dataclasses import asdict, fields
from datetime import datetime
import unicodedata

import pandas as pd

from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Normalize metadata and build embedding context without mutating records.

    Dates use UTC and are exported as YYYY-MM-DD; naive run_date means UTC.
    Drop rows lacking ID/title/summary or a valid publication date. Missing or
    invalid updated dates fall back to published. Keep the first valid row per
    paper_id, then sort by publication date (newest first) and paper_id.
    """
    def clean_text(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return " ".join(unicodedata.normalize("NFC", value).split())

    def clean_list(values: object) -> list[str]:
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, (list, tuple)):
            return []
        return [text for value in values if (text := clean_text(value))]

    run_timestamp = pd.to_datetime(run_date, utc=True, errors="raise")
    if pd.isna(run_timestamp):
        raise ValueError("run_date must be a valid datetime")

    columns = [field.name for field in fields(PaperRecord)]
    df = pd.DataFrame([asdict(record) for record in records], columns=columns)
    for column in columns:
        if column in {"authors", "categories"}:
            df[column] = df[column].map(clean_list)
        else:
            df[column] = df[column].map(clean_text)

    for column in ("published", "updated"):
        df[column] = pd.to_datetime(df[column], format="mixed", errors="coerce", utc=True).dt.normalize()
    valid = df["published"].notna()
    for column in ("paper_id", "title", "summary"):
        valid &= df[column].ne("")
    df = df.loc[valid].drop_duplicates(subset="paper_id", keep="first").copy()
    df["updated"] = df["updated"].fillna(df["published"])
    df["age_days"] = (run_timestamp - df["published"]).dt.days.astype("int64")
    for column in ("published", "updated"):
        df[column] = df[column].dt.strftime("%Y-%m-%d")

    df["authors_joined"] = df["authors"].map(lambda values: ", ".join(values))
    df["categories_joined"] = df["categories"].map(lambda values: ", ".join(values))
    df["summary_chars"] = df["summary"].map(len).astype("int64")
    df["text_for_embedding"] = [
        f"Title: {row.title}\n"
        f"Authors: {row.authors_joined}\n"
        f"Published: {row.published}\n"
        f"Categories: {row.categories_joined}\n"
        f"Summary: {row.summary}"
        for row in df.itertuples(index=False)
    ]
    return df.sort_values(["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)
