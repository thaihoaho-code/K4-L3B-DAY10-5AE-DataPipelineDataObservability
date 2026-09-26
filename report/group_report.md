# Group Report — Day 10: Data Pipeline & Data Observability

> Dùng mẫu này cho báo cáo chung của nhóm 3–5 thành viên. Thay toàn bộ nội dung trong dấu `[ ]` bằng thông tin và kết quả thực tế. Xóa các dòng hướng dẫn không còn cần thiết trước khi nộp.

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Khóa/Lớp         | K4-L3B-DAY10               |
| Tên nhóm         | Nhóm Data Pipeline Observability |
| Repository         | K4-L3B-DAY10--TenNhom--DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26               |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Nguyễn Đình Lâm Phúc | N/A | Data Ingestion | `src/ingestion/crossref.py`, `src/ingestion/cleaning.py` |
| 2 | Lê Minh Sang | N/A | Data Observability | `src/observability/quality.py` |
| 3 | Nguyễn Việt Hoàng | N/A | Data Corruption & Repair | `src/ingestion/corruption.py`, `src/pipelines/corruption_flow.py` |
| 4 | Nguyễn Văn Hồng | N/A | Evaluation & Reporting | `src/evaluation/testset.py`, `src/observability/reporting.py` |
| 5 | Hồ Thái Hòa | N/A | Pipeline Orchestration | `src/pipelines/phase1.py` |

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành toàn bộ vòng đời của Data Pipeline (Baseline), hệ thống Giám sát (Data Observability) và cơ chế tự phục hồi (Repair). Baseline pipeline đã tạo ra thành công tập dữ liệu sạch, vector embeddings trong ChromaDB, test set 10 câu hỏi ngẫu nhiên và file báo cáo Metrics/Quality.

Khi chạy kịch bản Corruption, việc làm hỏng dữ liệu (xóa ID, cắt cụt Summary) đã ảnh hưởng rõ rệt nhất đến hệ thống: Quality Gate báo lỗi (0.0 success) và khả năng tìm kiếm của Agent (retrieval_hit_rate) giảm từ 100% xuống 50%. Nhờ cơ chế Repair bằng cách reload lại dữ liệu nguyên bản từ raw snapshot, nhóm đã phục hồi 100% toàn bộ chỉ số về lại trạng thái Baseline. Hiện tại nhóm không còn blocker nào và toàn bộ yêu cầu bài lab đã đạt chuẩn.

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API
    -> raw response/raw records
    -> cleaning và data modeling
    -> embedding + ChromaDB index
    -> evaluation baseline
    -> quality/freshness reports
    -> corruption
    -> re-index và re-evaluate
    -> repair từ dữ liệu nguồn
    -> comparison report
```

### Trách nhiệm của từng khối

| Khối             | Input          | Xử lý chính             | Output/artifact          | Owner          |
| ----------------- | -------------- | -------------------------- | ------------------------ | -------------- |
| Ingestion         | Crossref API   | Fetch, retry, parse        | `data/raw/crossref_records.json` | Nguyễn Đình Lâm Phúc |
| Cleaning          | Raw JSON       | Xóa null, định dạng UTC    | `data/clean/papers_clean.csv` | Nguyễn Đình Lâm Phúc |
| Embedding/index   | Cleaned data   | MiniLM, lưu ChromaDB       | `data/chroma/`, `embeddings.json`| Nhóm chung |
| Evaluation        | ChromaDB Index | Chấm điểm LLM/Ragas        | `data/results/`, `data/eval/` | Nguyễn Văn Hồng |
| Observability     | Cleaned data   | Kiểm tra Great Expectations| `data/quality/`          | Lê Minh Sang |
| Corruption/repair | Cleaned/Raw    | Xóa data, reload snapshot  | Các file *corrupted, *repaired | Nguyễn Việt Hoàng |
| Orchestration     | Cấu hình .env  | Tích hợp module theo thứ tự| Markdown Reports         | Hồ Thái Hòa |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình             | Giá trị sử dụng |
| ---------------------------- | ------------------- |
| `LLM_PROVIDER`             | gemini              |
| `LLM_MODEL`                | gemini-2.5-flash    |
| Embedding model              | sentence-transformers/all-MiniLM-L6-v2 |
| Số lượng Crossref records | 24                  |
| Retrieval `top_k`          | 4                   |
| Freshness threshold          | 180                 |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

Baseline:

```bash
python script/run_phase1.py
```

Corruption flow:

```bash
python script/run_corruption_flow.py
```

### Kết quả tái hiện

| Lệnh             | Trạng thái                                    | Thời điểm chạy gần nhất | Bằng chứng                         |
| ----------------- | ----------------------------------------------- | ----------------------------- | ------------------------------------ |
| Baseline pipeline | Thành công | 2026-09-26 | `data/reports/phase1_report.md` |
| Corruption flow   | Thành công | 2026-09-26 | `data/reports/corruption_report.md` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính                | Giá trị                             |
| --------------------------- | ------------------------------------- |
| Source                      | Crossref REST API (`https://api.crossref.org/works`) |
| Query/filter                | `agentic retrieval augmented generation large language model` |
| Thời điểm lấy dữ liệu | 2026-09-26                           |
| Số record nhận được    | 24                         |
| Cơ chế retry/backoff      | Exponential backoff 3 lần, fallback về file json offline nếu lỗi mạng |

### Raw và clean schema

| Trường        | Kiểu dữ liệu | Bắt buộc?  | Ý nghĩa   | Xử lý khi thiếu/sai |
| --------------- | --------------- | ------------ | ----------- | ---------------------- |
| paper_id      | string         | Có         | DOI bài báo | Loại bỏ dòng (drop) |
| title         | string         | Có         | Tiêu đề | Loại bỏ dòng (drop) |
| summary       | string         | Có         | Tóm tắt nội dung | Loại bỏ dòng (drop) |
| published     | datetime string| Có         | Ngày xuất bản | Bỏ qua nếu ko thể parse |

### Quy tắc cleaning

| Quy tắc                                 | Quality dimension liên quan | Số record bị tác động | Cách xác minh      |
| ---------------------------------------- | ---------------------------- | -------------------------: | -------------------- |
| Loại bỏ record không có title/id       | Completeness                 | 0 (vì raw data tốt) | `expect_column_values_to_not_be_null` |
| Ngày xuất bản phải đúng định dạng YYYY-MM-DD | Validity                   | 24 (chuẩn hóa toàn bộ) | Check field `published` |

Giải thích cách nhóm tạo `text_for_embedding`, document ID và `age_days`:
- `text_for_embedding`: Nối chuỗi Title, Authors, Published, Categories, và Summary theo định dạng rõ ràng để tối ưu cho Vector DB.
- Document ID: Trùng với `paper_id` từ hệ thống DOI.
- `age_days`: Dùng `run_date` trừ đi `published` (đã convert về UTC) để tính số ngày trôi qua từ khi xuất bản.

## 6. Evaluation setup

| Thành phần                             | Cấu hình thực tế          |
| ---------------------------------------- | ----------------------------- |
| Số câu hỏi                            | 10                 |
| Các `question_type`                    | summary, authors, date, categories |
| Ground-truth document ID                 | Từ `paper_id` của record tương ứng |
| Embedding model                          | sentence-transformers/all-MiniLM-L6-v2 |
| Vector store/collection                  | ChromaDB (`papers-baseline` / `papers-corrupted`...) |
| Retrieval `top_k`                      | 4                   |
| LLM provider/model                       | gemini / gemini-2.5-flash |
| Test set dùng chung cho ba trạng thái | `data/eval/test_set.json` |

Giải thích vì sao test set được giữ nguyên khi đánh giá baseline, corrupted và repaired:
Để đảm bảo tính công bằng (fairness). Nếu bộ câu hỏi thay đổi liên tục, sự biến động của điểm số LLM có thể do bộ câu hỏi khó/dễ hơn chứ không phải do sự suy giảm chất lượng dữ liệu (Corruption). Giữ nguyên test set giúp cô lập biến số data.

## 7. Kết quả baseline

### Artifact checklist

| Artifact                 | Đường dẫn thực tế                | Trạng thái | Ghi chú   |
| ------------------------ | -------------------------------------- | ------------ | ---------- |
| Raw response/records     | `data/raw/`                          | Có | Crossref payload và snapshot JSON |
| Cleaned dataset          | `data/clean/`                        | Có | Cả CSV và JSON |
| Embedding manifest/index | `data/embeddings/`                   | Có | Manifest trỏ về `data/chroma/` |
| Evaluation set           | `data/eval/`                         | Có | 10 câu hỏi sinh tự động |
| Baseline metrics         | `data/results/baseline_metrics.json` | Có | |
| Quality/freshness        | `data/quality/`                      | Có | Báo cáo GX và Freshness |
| Baseline report          | `data/reports/phase1_report.md`      | Có | Report sinh bằng code python |

### Baseline metrics

| Metric                 |       Giá trị | Diễn giải                             |
| ---------------------- | --------------: | --------------------------------------- |
| `retrieval_hit_rate` |     1.0 | Hệ thống vector tìm kiếm đúng 100% tài liệu liên quan đến câu hỏi. |
| `mean_token_f1`      |     0.4869 | Mức độ trùng lặp từ vựng giữa câu trả lời LLM và ground truth ở mức khá. |
| `judge_accuracy`     |     0.5 | 50% số câu hỏi được giám khảo công nhận là đúng chính xác ý nghĩa. |
| `mean_judge_score`   |     2.8 | Mức điểm đánh giá (trên thang 5) của giám khảo cho hệ thống RAG (ở mức khá). |
| Ragas, nếu có        | N/A | "Set RUN_RAGAS=1 to enable the slower Ragas pass." |

## 8. Data quality và freshness

### Quality checks

| Check        | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline      | Bằng chứng |
| ------------ | ----------------- | ------------------ | ----------------------- | ------------ |
| expect_table_row_count_to_be_between | Completeness | 1 đến 24 | Pass (24 rows) | `baseline_quality_report.json` |
| expect_column_values_to_not_be_null | Completeness | Not Null | Pass | `baseline_quality_report.json` |
| expect_column_values_to_be_unique | Uniqueness | Unique | Pass | `baseline_quality_report.json` |
| expect_column_value_lengths_to_be_between | Validity | Từ 50 - 5000 ký tự | Pass | `baseline_quality_report.json` |

### Freshness

| Thuộc tính               | Giá trị                           |
| -------------------------- | ----------------------------------- |
| Freshness được đo tại | Cleaned DataFrame            |
| Timestamp mới nhất       | 2026-09-15                         |
| Ngưỡng freshness         | 180 days                         |
| Trạng thái baseline      | Fresh               |
| Lý do                     | Bài cũ nhất xuất bản ngày 2026-04-01, hoàn toàn nằm trong ngưỡng 180 ngày nên `is_fresh` = True. |

## 9. Corruption scenarios và repair

| Corruption         | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair   |
| ------------------ | ---------- | ---------------------: | ------------------------ | --------------------- | -------------- |
| Mất thông tin quan trọng | Xóa/Làm null trường `paper_id`, `title` | Toàn bộ các dòng bị xóa | `expect_column_values_to_not_be_null` failed | Quality success trả về False (0.0) | Đọc lại từ raw snapshot |
| Đứt gãy độ dài nội dung | Rút ngắn `summary` dưới ngưỡng tối thiểu | Một số dòng | `expect_column_value_lengths_to_be_between` failed | Báo cáo bị đánh dấu Fail | Đọc lại từ raw snapshot |

Corruption log:

- Đường dẫn: `data/results/corruption_log.json`
- Trạng thái: Có
- Nhận xét: Log ghi nhận đầy đủ các field bị tác động bởi quá trình mô phỏng sự cố.

Giải thích cách repair đảm bảo dữ liệu được phục hồi từ nguồn đáng tin cậy thay vì chỉ che kết quả lỗi:

Kịch bản repair sử dụng luồng `repair_from_raw_snapshot`, nghĩa là hệ thống phớt lờ bảng corrupted_df mà đọc lại file `data/raw/crossref_records.json` (bản snapshot gốc bất biến) và chạy lại toàn bộ tiến trình Clean. Điều này giúp bảo toàn Data Lineage và nguyên tắc hàm Idempotent.

## 10. So sánh baseline, corrupted và repaired

| Metric/signal            | Baseline | Corrupted | Repaired | Thay đổi do corruption | Mức phục hồi | Nhận xét   |
| ------------------------ | -------: | --------: | -------: | -----------------------: | --------------: | ------------ |
| `retrieval_hit_rate`   |   1.0000 |    0.5000 |   1.0000 | Giảm mạnh 50% | Khôi phục 100% | RAG mất phương hướng do Vector Index không có data sạch. |
| `mean_token_f1`        |   0.4869 |    0.2165 |   0.4869 | Giảm mạnh | Khôi phục 100% | Trả lời sai do context sai. |
| `judge_accuracy`       |   0.5000 |    0.2000 |   0.5000 | Rớt 30% | Khôi phục 100% | Chất lượng câu trả lời bị hủy hoại. |
| `mean_judge_score`     |   2.8000 |    1.8000 |   2.8000 | Mất 1 điểm | Khôi phục 100% | Điểm giảm rõ rệt. |
| Quality checks pass/fail |   Pass |      Fail (0.0) |     Pass (1.0) | Hệ thống bắt được lỗi | Khôi phục 100% | GX hoạt động chính xác. |
| Freshness status         |   Pass |      Pass (1.0) |     Pass (1.0) | Không thay đổi | Khôi phục 100% | Corruption không ảnh hưởng tới tuổi bài báo. |

Nêu ít nhất hai kết luận có quan hệ nhân quả được hỗ trợ bởi artifacts:

1. **[Dữ liệu bị xóa Title/Summary] → [Quality Gate báo Fail] → [Retrieval hit_rate giảm 50%]**. Không có nội dung text hợp lệ dẫn đến ChromaDB index vector sai lệch, Agent bốc nhầm tài liệu.
2. **[Idempotent Repair reload từ Raw JSON] → [Quality Recovery Pass] → [Agent metric recovery 100%]**. Việc quay lại nguồn đáng tin cậy giúp khôi phục hoàn toàn chất lượng vector, đưa kết quả RAG trở lại chuẩn mực Baseline.

## 11. Vấn đề tích hợp quan trọng

Mô tả một vấn đề phát sinh khi ghép các module trong pipeline và cách nhóm xử lý:

- **Triệu chứng:** Gặp lỗi `FileNotFoundError` khi chạy `evaluate_pipeline` vì thiếu file `test_set.json` và lỗi `ValueError: run_date must be a valid datetime`.
- **Nguyên nhân:** Cờ `refresh_test_set` mặc định False khiến bước sinh file test bị nhảy cóc ở lần chạy đầu. Biến `run_date` bị gán bằng `None` khi gọi hàm tính độ trễ `age_days`.
- **Cách xử lý:** Cập nhật điều kiện `if settings.refresh_test_set or not settings.paths.eval_testset.exists():` và thay đổi `run_date=datetime.now(UTC)` trong `src/pipelines/phase1.py`.
- **Cách xác minh:** Chạy `python script/run_phase1.py`, console hiển thị đã tạo xong evaluation set và vượt qua luồng Clean thành công.

## 12. Giới hạn và hướng cải thiện

| Giới hạn hiện tại | Ảnh hưởng   | Hướng cải thiện có thể kiểm chứng |
| --------------------- | -------------- | ----------------------------------------- |
| Gom toàn bộ dữ liệu vào trường text duy nhất để nhúng Vector | LLM RAG đôi khi bị nhiễu thông tin khi tìm đáp án tác giả hay danh mục cụ thể. | Dùng Document Chunking nâng cao kết hợp tách Metadata Filtering (Vector filtering) trước khi query. |
| Prompt của LLM Judge quá đơn giản | Chấm điểm đôi lúc khắt khe vì đáp án của RAG tự nhiên sinh ra dài hơn ground truth (chỉ 1 câu) dẫn đến sai lệch F1. | Tinh chỉnh prompt Judge bằng Few-shot prompting hoặc đánh giá dựa trên Semantic Similarity. |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản dùng để nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
