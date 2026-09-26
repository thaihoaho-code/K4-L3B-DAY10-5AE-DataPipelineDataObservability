# Phase 1 Report

## Source Summary
| Field | Value |
| --- | --- |
| total_records | 24 |
| total_cleaned | 24 |

## Evaluation Metrics
| Field | Value |
| --- | --- |
| samples | 10 |
| retrieval_hit_rate | 1.0 |
| mean_token_f1 | 0.48694444444444446 |
| judge_accuracy | 0.5 |
| mean_judge_score | 2.8 |
| ragas | {"skipped": "Set RUN_RAGAS=1 to enable the slower Ragas pass."} |

## Data Quality
| Field | Value |
| --- | --- |
| report_name | baseline_quality_report |
| success | True |
| gx_success | True |
| freshness_success | True |
| freshness | {"freshness_threshold_days": 180, "invalid_age_rows": 0, "is_fresh": true, "latest_published": "2026-09-15", "max_stale_ratio": 0.25, "oldest_published": "2026-04-01", "stale_ratio": 0.0, "stale_rows": 0, "total_rows": 24} |
| statistics | {"evaluated_expectations": 5, "success_percent": 100.0, "successful_expectations": 5, "unsuccessful_expectations": 0} |
| results | [{"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "max_value": 24, "min_value": 1}, "meta": {}, "severity": "critical", "type": "expect_table_row_count_to_be_between"}, "meta": {}, "result": {"observed_value": 24}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "paper_id"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_not_be_null"}, "meta": {}, "result": {"element_count": 24, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "paper_id"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_be_unique"}, "meta": {}, "result": {"element_count": 24, "missing_count": 0, "missing_percent": 0.0, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0, "unexpected_percent_nonmissing": 0.0, "unexpected_percent_total": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "title"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_not_be_null"}, "meta": {}, "result": {"element_count": 24, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "summary", "max_value": 5000, "min_value": 50}, "meta": {}, "severity": "critical", "type": "expect_column_value_lengths_to_be_between"}, "meta": {}, "result": {"element_count": 24, "missing_count": 0, "missing_percent": 0.0, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0, "unexpected_percent_nonmissing": 0.0, "unexpected_percent_total": 0.0}, "success": true}] |
| great_expectations_result | {"id": null, "meta": {"active_batch_definition": {"batch_identifiers": {"dataframe": "<DATAFRAME>"}, "data_asset_name": "papers_asset", "data_connector_name": "fluent", "datasource_name": "papers_source"}, "batch_markers": {"ge_load_time": "20260926T043230.365767Z", "pandas_data_fingerprint": "5a1c044d7cf7b25905b9e3bdb42c70a1"}, "batch_spec": {"batch_data": "PandasDataFrame"}, "great_expectations_version": "1.23.2"}, "results": [{"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "max_value": 24, "min_value": 1}, "meta": {}, "severity": "critical", "type": "expect_table_row_count_to_be_between"}, "meta": {}, "result": {"observed_value": 24}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "paper_id"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_not_be_null"}, "meta": {}, "result": {"element_count": 24, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "paper_id"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_be_unique"}, "meta": {}, "result": {"element_count": 24, "missing_count": 0, "missing_percent": 0.0, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0, "unexpected_percent_nonmissing": 0.0, "unexpected_percent_total": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "title"}, "meta": {}, "severity": "critical", "type": "expect_column_values_to_not_be_null"}, "meta": {}, "result": {"element_count": 24, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0}, "success": true}, {"exception_info": {"exception_message": null, "exception_traceback": null, "raised_exception": false}, "expectation_config": {"kwargs": {"batch_id": "papers_source-papers_asset", "column": "summary", "max_value": 5000, "min_value": 50}, "meta": {}, "severity": "critical", "type": "expect_column_value_lengths_to_be_between"}, "meta": {}, "result": {"element_count": 24, "missing_count": 0, "missing_percent": 0.0, "partial_unexpected_counts": [], "partial_unexpected_index_list": [], "partial_unexpected_list": [], "unexpected_count": 0, "unexpected_percent": 0.0, "unexpected_percent_nonmissing": 0.0, "unexpected_percent_total": 0.0}, "success": true}], "statistics": {"evaluated_expectations": 5, "success_percent": 100.0, "successful_expectations": 5, "unsuccessful_expectations": 0}, "success": true, "suite_name": "baseline_quality_report_quality_suite", "suite_parameters": {}} |

## Freshness
| Field | Value |
| --- | --- |
| latest_published | 2026-09-15 |
| oldest_published | 2026-04-01 |
| stale_rows | 0 |
| total_rows | 24 |
| stale_ratio | 0.0 |
| invalid_age_rows | 0 |
| freshness_threshold_days | 180 |
| max_stale_ratio | 0.25 |
| is_fresh | True |
