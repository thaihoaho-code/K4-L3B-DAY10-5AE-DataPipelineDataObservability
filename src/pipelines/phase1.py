from __future__ import annotations

from core.config import load_settings, require_llm_credentials
from evaluation.metrics import evaluate_pipeline
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from core.utils import save_dataframe_to_csv, save_dataframe_to_json
import pandas as pd
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex

def main() -> None:
    """TODO(student): xay dung baseline pipeline end-to-end.

    Pseudo-code:
    1. Load settings.
    2. Load hoac fetch raw records.
    3. Clean data.
    4. Save clean CSV/JSON.
    5. Build Chroma index.
    6. Tao hoac load evaluation set.
    7. Evaluate.
    8. Run quality checks va freshness report.
    9. Tao markdown report.
    10. Co the demo agent tren vai sample question.
    """

    settings = load_settings()
    
    require_llm_credentials(settings)

    print("✅ Đã load settings thành công!")
    
    print(f"- Thư mục dự án: {settings.paths.project_dir}")
    print(f"- Đường dẫn file raw: {settings.paths.raw_api_response}")

    if settings.refresh_source:
        print("🔄 Fetching source records...")
        records = fetch_source_records(settings)
    else:
        print("📥 Loading raw records from JSON...")
        records = load_raw_records(settings.paths.raw_records_json)
    
    clean_df = build_clean_dataframe(records, run_date=None)
    
    print(f"✅ Đã clean xong dữ liệu, tổng số bản ghi: {len(clean_df)}")
    
    save_dataframe_to_csv(clean_df, settings.paths.clean_csv)
    save_dataframe_to_json(clean_df, settings.paths.clean_json)
    
    index = LocalEmbeddingIndex.build(
        df=clean_df, 
        settings=settings, 
        embeddings_output_path=settings.paths.embeddings_json # Chỗ lưu manifest
    )

    print(f"✅ Đã build xong Vector Index tại: {settings.paths.chroma_dir}")

    if settings.refresh_test_set:
        from evaluation.testset import build_test_set
        build_test_set(clean_df, settings.paths.eval_testset)
        print(f"✅ Đã tạo xong evaluation set tại: {settings.paths.eval_testset}")
    else:
        print(f"📥 Dùng evaluation set có sẵn từ: {settings.paths.eval_testset}")
        
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers
    )
    
    quality = run_data_quality_checks(clean_df, settings, report_name="baseline_quality_report")
    freshness = build_freshness_report(clean_df, settings, report_path=settings.paths.freshness_report)

    generate_phase1_report(report_path=settings.paths.baseline_report,
                           source_summary={"total_records": len(records), "total_cleaned": len(clean_df)},
                           metrics=eval_bundle.summary,
                           quality=quality,
                           freshness=freshness
                           )
