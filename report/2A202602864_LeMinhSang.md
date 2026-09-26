# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác. Thay nội dung trong dấu `[ ]` và xóa các dòng hướng dẫn không cần thiết trước khi nộp.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Lê Minh Sang             |
| MSSV               | 2A202602864                |
| Khóa/Lớp         | K4-L3B-DAY10              |
| Tên nhóm         | 5AE                        |
| Vai trò chính    | Data Observability         |
| Repository         | https://github.com/thaihoaho-code/K4-L3B-DAY10-5AE-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Data Quality Checks (Great Expectations Quality Gate) | `src/observability/quality.py`: `run_data_quality_checks()`, `_quality_report_path()` | Cleaned `pandas.DataFrame` từ cleaning, đối tượng `Settings`, chuỗi tên báo cáo `report_name` | File JSON báo cáo chất lượng (`baseline_quality_report.json`, `corrupted_quality_report.json`, `repaired_quality_report.json`) tại `data/quality/` | Hoàn thành; kiểm định 5 expectations và tích hợp kiểm tra kết hợp cùng Freshness SLA. |
| Freshness Monitoring & SLA Reporting | `src/observability/quality.py`: `_freshness_metrics()`, `build_freshness_report()` | Cleaned `pandas.DataFrame` chứa cột `published` và `age_days`, đối tượng `Settings` (ngưỡng 180 ngày), `report_path` | Báo cáo Freshness JSON (`freshness_report.json`, `corrupted_freshness_report.json`, `repaired_freshness_report.json`) tại `data/quality/` | Hoàn thành; đo lường số dòng stale, tỷ lệ stale_ratio, fail-closed khi thiếu hoặc sai age_days. |

Chỉ nhận ownership cho phần bạn trực tiếp thực hiện. Liên hệ rõ phần việc của bạn với đầu vào, đầu ra và các thành viên phụ thuộc vào phần đó.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Tích hợp và chuẩn hóa contract cột ngày tháng (`published`, `age_days`) cho SLA Freshness | Hồ Thái Hòa (`src/pipelines/phase1.py`) và Nguyễn Đình Lâm Phúc (`src/ingestion/cleaning.py`) | Thống nhất format `published` UTC datetime và `run_date` hợp lệ để `age_days` không bị null/NaN; giúp `_freshness_metrics()` tính toán chính xác, loại bỏ lỗi `ValueError: run_date must be a valid datetime` và đưa `invalid_age_rows` về 0. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Xây dựng Quality Gate bằng Great Expectations 1.x kiểm tra schema, tính toàn vẹn và độ dài văn bản | `src/observability/quality.py`: `run_data_quality_checks()`; artifacts: `data/quality/*_quality_report.json` | 5 expectations kiểm định toàn vẹn: 5/5 pass ở baseline/repaired (success: true), phát hiện chính xác 2 vi phạm ở corrupted (ID trùng lặp và summary rỗng, gx_success: false). | Chạy `python script/run_phase1.py` và `python script/run_corruption_flow.py`; đối chiếu kết quả trong `data/quality/`. |
| Thiết lập hệ thống giám sát độ tươi mới dữ liệu (Data Freshness Monitoring & SLA) | `src/observability/quality.py`: `_freshness_metrics()`, `build_freshness_report()`; artifacts: `data/quality/*freshness_report.json` | Xác định số dòng stale so với ngưỡng 180 ngày; baseline/repaired có 0 dòng stale (stale_ratio 0.0), corrupted có 2 dòng stale (stale_ratio 0.1 <= max_stale_ratio 0.25). | Kiểm tra trường `freshness` trong `baseline_quality_report.json` và artifact `data/quality/freshness_report.json`; xác nhận `is_fresh: true`. |

Nêu một output cụ thể mà phần việc của bạn tạo ra hoặc giúp xác minh:

Báo cáo chất lượng `data/quality/baseline_quality_report.json` và `data/quality/freshness_report.json`. Báo cáo xác minh toàn diện 24 records của dataset sạch: 100% đạt 5/5 expectations của Great Expectations (row count từ 1 đến 24, `paper_id` và `title` không null, `paper_id` duy nhất, độ dài `summary` từ 50 đến 5000 ký tự) và đạt Freshness SLA với 0 dòng stale (tuổi bài báo từ 11 đến 178 ngày, đều nằm trong ngưỡng 180 ngày), trả về `success: true`. Khi kích hoạt luồng corrupted, `corrupted_quality_report.json` lập tức kích hoạt còi báo động (`success: false`, `gx_success: false`) với 2 vi phạm cụ thể, đóng vai trò chốt chặn bảo vệ vector database.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong kiến trúc Data Pipeline phục vụ RAG Agent, nếu dữ liệu nguồn bị lỗi (thiếu định danh, trùng lặp ID, tiêu đề rỗng, tóm tắt bị cắt cụt hoặc thông tin quá cũ quá hạn) lọt vào Vector Database (ChromaDB), toàn bộ hệ thống downstream sẽ bị suy thoái: vector embedding sai lệch, truy xuất sai tài liệu, LLM sinh ảo giác và lãng phí chi phí API. Module Data Observability do tôi phụ trách giải quyết 3 bài toán trọng tâm:
1. Thiết lập chốt chặn chất lượng (Quality Gate) tự động bằng Great Expectations 1.x nhằm kiểm định tính toàn vẹn (completeness), tính duy nhất (uniqueness) và tính hợp lệ (validity) của DataFrame sau cleaning trước khi nhúng vector.
2. Giám sát độ tươi mới của dữ liệu (Data Freshness Monitoring) nhằm bảo đảm tài liệu khoa học đáp ứng SLA quy định (không quá 180 ngày tính từ ngày xuất bản đến thời điểm chạy `run_date`).
3. Chuẩn hóa và lưu trữ báo cáo Observability dưới dạng JSON tĩnh (`data/quality/`) để các module Orchestration, Reporting và kịch bản Corruption/Repair có căn cứ định lượng đưa ra quyết định vận hành và phục hồi.

### Cách triển khai

1. Khởi tạo runtime Great Expectations 1.x ở chế độ Ephemeral Context (`gx.get_context(mode="ephemeral")`) để kiểm định in-memory gọn nhẹ, không sinh file rác cấu hình hệ thống. Đăng ký Pandas datasource (`papers_source`), thêm DataFrame asset (`papers_asset`) và tạo batch definition gắn trực tiếp với DataFrame cần kiểm định.
2. Xây dựng Expectation Suite gồm 5 quy tắc cốt lõi:
   - `ExpectTableRowCountToBeBetween(min_value=1, max_value=settings.max_results)`: Đảm bảo số lượng bản ghi nằm trong giới hạn 1 đến 24 dòng.
   - `ExpectColumnValuesToNotBeNull(column="paper_id")`: Đảm bảo mọi bài báo đều có định danh DOI.
   - `ExpectColumnValuesToBeUnique(column="paper_id")`: Đảm bảo không có bản ghi trùng lặp ID gây nhiễu vector index.
   - `ExpectColumnValuesToNotBeNull(column="title")`: Đảm bảo tiêu đề bài báo không được phép rỗng.
   - `ExpectColumnValueLengthsToBeBetween(column="summary", min_value=50, max_value=5000)`: Đảm bảo tóm tắt có độ dài hợp lý để tạo ngữ cảnh vector embedding có nghĩa, chặn các đoạn tóm tắt rỗng hoặc quá ngắn.
3. Tính toán và đánh giá Freshness SLA theo quy tắc Fail-closed:
   - Chuyển đổi cột `published` sang UTC datetime để xác định ngày xuất bản mới nhất (`latest_published`) và cũ nhất (`oldest_published`).
   - Đọc cột `age_days`, đếm số dòng có tuổi vượt ngưỡng quy định (`freshness_threshold_days = 180`) để tính `stale_rows` và `stale_ratio = stale_rows / total_rows`.
   - Cơ chế "Fail-closed": Nếu DataFrame rỗng hoặc có bất kỳ dòng nào không xác định được `age_days` (`invalid_age_rows > 0`), hệ thống coi như vi phạm SLA (`is_fresh = False`). Dữ liệu chỉ được công nhận là fresh khi `stale_ratio <= 0.25` (tỷ lệ bài quá hạn tối đa 25%).
4. Đóng gói kết quả và kết hợp tín hiệu: Hàm `run_data_quality_checks()` kết hợp cả hai điều kiện: `success = gx_success and freshness["is_fresh"]`. Toàn bộ payload gồm thống kê, kết quả chi tiết từng expectation và chỉ số freshness được xuất ra file JSON thông qua tiện ích `write_json()`. Đồng thời áp dụng lazy import cho Great Expectations để tối ưu hiệu năng khi chỉ gọi báo cáo Freshness độc lập.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | `pandas.DataFrame` sạch từ bước cleaning (chứa các cột: `paper_id`, `title`, `summary`, `published`, `age_days`), đối tượng `Settings` từ `src/core/config.py`, và chuỗi định danh `report_name` (`"baseline"`, `"corrupted"`, hoặc `"repaired"`). |
| Output                         | Báo cáo chất lượng JSON tại `data/quality/{report_name}_quality_report.json` và báo cáo freshness JSON tại `data/quality/{report_name}_freshness_report.json`; hàm trả về dictionary chứa `report_name`, cờ `success`, `gx_success`, `freshness_success`, metrics `freshness`, `statistics`, và danh sách `results` chi tiết. |
| Module phụ thuộc             | `src/core/config.py` (cấu hình đường dẫn, ngưỡng SLA), `src/core/utils.py` (`write_json`), thư viện `great_expectations` (GX 1.x) và `pandas`. |
| Module sử dụng output        | `src/pipelines/phase1.py` (kiểm tra gate baseline), `src/pipelines/corruption_flow.py` (kiểm tra gate corrupted và repaired), `src/observability/reporting.py` (tổng hợp báo cáo Markdown cho người dùng). |
| Điều kiện lỗi cần xử lý | Cột `age_days` hoặc `published` bị thiếu/chứa NaN; DataFrame rỗng; tên `report_name` chứa ký tự đặc biệt (chuẩn hóa qua Regex `_quality_report_path`); `summary` bị rỗng hoặc quá ngắn/dài; `paper_id` bị trùng lặp hoặc null. |

### Cách xác minh

```bash
python -c "from core.config import load_settings; from ingestion.crossref import load_raw_records; from ingestion.cleaning import build_clean_dataframe; from observability.quality import run_data_quality_checks, build_freshness_report; from datetime import datetime, timezone; s=load_settings(); df=build_clean_dataframe(load_raw_records(s.paths.raw_records_json), datetime.now(timezone.utc)); qr=run_data_quality_checks(df, s, 'baseline'); fr=build_freshness_report(df, s, s.paths.quality_dir / 'freshness_report.json'); print(f'Quality Success: {qr[\"success\"]}, GX Success: {qr[\"gx_success\"]}, Freshness: {fr[\"is_fresh\"]}, Total Rows: {fr[\"total_rows\"]}')"
```

- **Kết quả mong đợi:** Kiểm tra thành công 5/5 expectations của Great Expectations và xác nhận Freshness SLA trên DataFrame sạch gồm 24 dòng; xuất các file `baseline_quality_report.json` và `freshness_report.json` với `success: True`.
- **Kết quả thực tế:** `Quality Success: True, GX Success: True, Freshness: True, Total Rows: 24`; toàn bộ 5/5 expectation đạt 100%, 0 dòng stale.
- **Artifact/log:** `data/quality/baseline_quality_report.json` và `data/quality/freshness_report.json`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương thức triển khai Great Expectations 1.x: Khởi tạo project tĩnh trên filesystem với cấu trúc thư mục cấu hình YAML (`great_expectations/`) hay sử dụng Ephemeral Context (in-memory runtime) kết hợp API Fluent.
- **Các phương án đã cân nhắc:**
  1. Phương án 1: Dùng filesystem store truyền thống (`gx.init()`), lưu expectation suite và validation result vào các file YAML/JSON tĩnh trong thư mục dự án.
  2. Phương án 2: Dùng Ephemeral Data Context (`gx.get_context(mode="ephemeral")`) cùng API Fluent của GX 1.x để định nghĩa datasource, asset, batch và suite trực tiếp trong bộ nhớ khi chạy code, sau đó chủ động trích xuất payload và ghi ra file JSON chuẩn hóa theo đường dẫn cấu hình trong `Settings`.
- **Phương án đã chọn:** Phương án 2 (Ephemeral Data Context kết hợp API Fluent GX 1.x).
- **Lý do:** Trade-off giữa độ phức tạp quản lý cấu hình và tính Reproducibility / Lightweight: Ephemeral mode giúp pipeline chạy độc lập, idempotent, loại bỏ nguy cơ xung đột file cấu hình YAML hoặc lỗi đường dẫn tuyệt đối khi chuyển đổi môi trường giữa các thành viên. Đồng thời, cho phép kiểm soát hoàn toàn schema và vị trí lưu trữ artifact JSON tại `data/quality/`.
- **Bằng chứng quyết định phù hợp:** Pipeline chạy trơn tru qua cả 3 trạng thái baseline, corrupted, repaired mà không cần file cấu hình `great_expectations.yml`; các báo cáo `baseline_quality_report.json`, `corrupted_quality_report.json`, `repaired_quality_report.json` được tạo ra đầy đủ, rõ ràng và nhất quán.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Khi chạy kiểm tra Freshness trong pipeline ban đầu, `freshness_report.json` trả về `"is_fresh": false` và `"invalid_age_rows": 24` dù các bài báo đều mới xuất bản trong năm 2026. Khi kiểm tra console xuất hiện ngoại lệ: `ValueError: run_date must be a valid datetime` phát sinh từ `src/ingestion/cleaning.py`.
- **Lệnh hoặc bước tái hiện:** `python script/run_phase1.py` khi hàm `main()` trong `src/pipelines/phase1.py` truyền giá trị `run_date=None` vào hàm `build_clean_dataframe()`.
- **Nguyên nhân gốc:** Module Cleaning cần tham số `run_date` hợp lệ (dạng UTC datetime) để tính toán độ trễ ngày xuất bản `age_days = (run_date - published).days`. Khi `run_date` bị gán `None`, cột `age_days` không được tính toán (hoặc mang giá trị NaN). Trong `src/observability/quality.py`, hàm `_freshness_metrics()` áp dụng cơ chế "Fail-closed": bất kỳ dòng nào thiếu hoặc có `age_days` không hợp lệ (`invalid_age_rows > 0`) đều làm điều kiện `invalid_age_rows == 0` bị vi phạm, khiến `is_fresh` bị đánh rớt thành `False`.
- **Cách xử lý:** Thống nhất contract giữa các module: yêu cầu Orchestration (`phase1.py`) truyền `run_date=datetime.now(UTC)` vào `build_clean_dataframe()`. Đồng thời trong `quality.py`, áp dụng `pd.to_numeric(df["age_days"], errors="coerce")` và `pd.to_datetime(df["published"], errors="coerce", utc=True)` để bắt lỗi ép kiểu an toàn và ghi nhận minh bạch số dòng không hợp lệ.
- **Cách xác minh sau khi sửa:** Chạy lại `python script/run_phase1.py`. Báo cáo `data/quality/freshness_report.json` và `baseline_quality_report.json` ghi nhận: `"invalid_age_rows": 0`, `"stale_rows": 0`, `"total_rows": 24`, `"is_fresh": true`, `"success": true`.
- **Điều học được:** Cơ chế "Fail-closed" là nguyên tắc sống còn trong Data Observability để tránh việc lọt dữ liệu lỗi mà hệ thống vẫn báo xanh. Tuy nhiên, contract dữ liệu giữa các module (đặc biệt là kiểu datetime có timezone) cần được quy định rõ ràng và kiểm tra ngay từ bước tích hợp đầu tiên.

Nếu chưa xử lý xong:

- **Phạm vi bị ảnh hưởng:** Không có (vấn đề đã được xử lý triệt để, không còn blocker).
- **Những gì đã loại trừ:** Đã loại trừ giả thuyết lỗi do logic nội tại của thư viện Great Expectations; xác định nguyên nhân cốt lõi là sự sai lệch contract tham số `run_date` giữa Orchestrator và hàm Cleaning.
- **Bước tiếp theo:** Đã hoàn thành xác minh và kiểm chứng hoạt động ổn định trên cả 3 kịch bản: baseline, corrupted và repaired.

## 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của bạn:

1. Dữ liệu đi từ Crossref đến vector index như thế nào?
2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?
3. Quality checks khác freshness monitoring ở điểm nào trong bài lab?
4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?
5. Repair được xem là thành công dựa trên artifact và metric nào?

**Câu trả lời:**

1. **Dữ liệu đi từ Crossref đến vector index:** Dữ liệu thô từ Crossref API được tải về và lưu thành raw JSON (`crossref_records.json`). Module Cleaning loại bỏ HTML/XML, chuẩn hóa Unicode/ngày tháng sang UTC, khử trùng `paper_id`, tính toán `age_days`, và tạo chuỗi `text_for_embedding` (ghép Title, Authors, Published, Categories, Summary). Module Observability chạy kiểm định Great Expectations và Freshness SLA trên DataFrame sạch. Khi Quality Gate đạt chuẩn (Pass), dữ liệu được đưa vào mô hình `sentence-transformers/all-MiniLM-L6-v2` để sinh vector embeddings và lưu trữ vào ChromaDB (`data/chroma/`).
2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality:** Bộ evaluation gồm 10 câu hỏi (`data/eval/test_set.json`) với ground truth và `ground_truth_doc_ids` (DOI của bài báo nguồn). Khi Agent truy vấn, hệ thống lấy `top_k=4` tài liệu liên quan từ ChromaDB: nếu có chứa `ground_truth_doc_ids`, hệ thống ghi nhận 1 hit (đo `retrieval_hit_rate`). Sau đó, câu trả lời do LLM sinh ra từ context được so khớp với ground truth bằng token overlap (đo `mean_token_f1`) và được LLM Judge chấm điểm độ chính xác ngữ nghĩa trên thang điểm 1–5 (đo `judge_accuracy` và `mean_judge_score`).
3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab:** Quality checks (Great Expectations) tập trung vào tính đúng đắn cấu trúc và nội dung tĩnh của dữ liệu (Completeness, Uniqueness, Validity như ID không null, ID duy nhất, summary từ 50 đến 5000 ký tự). Freshness monitoring tập trung vào chiều thời gian (Timeliness / Currency), theo dõi xem dữ liệu có bị cũ quá hạn SLA (180 ngày) so với thời điểm chạy pipeline hay không và áp dụng cơ chế fail-closed khi thiếu thông tin ngày tháng.
4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired:** Giữ nguyên test set là nguyên tắc biến kiểm soát (Control variable) bắt buộc trong phương pháp luận thực nghiệm. Nếu thay đổi câu hỏi giữa các pha, sự thay đổi của các chỉ số hiệu năng (hit rate, F1, judge score) có thể xuất phát từ độ khó ngẫu nhiên của câu hỏi mới thay vì phản ánh sự thay đổi chất lượng dữ liệu. Giữ cố định test set giúp cô lập biến số duy nhất là chất lượng của dataset (sạch, hỏng, hay đã phục hồi).
5. **Repair được xem là thành công dựa trên artifact và metric nào:** Repair được xem là thành công khi: (1) Báo cáo observability `repaired_quality_report.json` và `repaired_freshness_report.json` đạt `success: true`, 5/5 expectation pass 100%, 0 dòng stale; (2) Dataset `papers_clean_repaired.json` phục hồi đầy đủ 24 bản ghi sạch khớp với raw snapshot; (3) Toàn bộ metrics đánh giá trong `repaired_metrics.json` phục hồi hoàn toàn về mức Baseline (`retrieval_hit_rate` = 1.0, `mean_token_f1` = 0.4869, `judge_accuracy` = 0.5, `mean_judge_score` = 2.8).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |      1.0 |       0.5 |      1.0 | Dữ liệu bị hỏng làm giảm 50% khả năng truy xuất đúng tài liệu; sau khi repair từ snapshot, hit rate phục hồi hoàn toàn về 1.0 (100%). |
| `mean_token_f1`      |   0.4869 |    0.2165 |   0.4869 | Độ trùng lặp từ vựng sụt giảm hơn 55% do LLM nhận context sai/thiếu; sau repair khôi phục 100% về mức baseline. |
| `judge_accuracy`     |      0.5 |       0.2 |      0.5 | Tỷ lệ câu trả lời được LLM Judge công nhận đúng rơi từ 5/10 xuống 2/10 câu do mất ngữ cảnh; sau repair phục hồi về 5/10. |
| `mean_judge_score`   |      2.8 |       1.8 |      2.8 | Điểm đánh giá trung bình tụt mất 1.0 điểm (trên thang 5) ở tập corrupted; sau repair phục hồi hoàn toàn về 2.8. |
| Quality checks         |     Pass | Fail (0.0)| Pass (1.0)| Quality Gate Great Expectations bắt chính xác 2 vi phạm (ID trùng lặp và summary rỗng); sau repair 5/5 expectation pass 100%. |
| Freshness status       |     Pass |      Pass |      Pass | Corrupted có 2 dòng stale (10%), vẫn dưới ngưỡng cho phép 25% nên cờ is_fresh vẫn đạt; sau repair không còn dòng stale nào. |

### Kết luận từ số liệu

Hoàn thành hai chuỗi nguyên nhân–bằng chứng sau:

1. [Xóa bỏ 5 bài viết, làm rỗng 2 summary, nhân bản 1 ID và làm cũ ngày xuất bản] → [Quality Gate Great Expectations báo Fail (3/5 expectation đạt, gx_success: false, vi phạm ID unique và summary length); Freshness ghi nhận 2 dòng stale (stale_ratio = 0.1)] → [ChromaDB index bị thiếu và sai dữ liệu khiến retrieval_hit_rate giảm 50% (từ 1.0 xuống 0.5), mean_token_f1 giảm từ 0.4869 xuống 0.2165, mean_judge_score rơi từ 2.8 xuống 1.8].
2. [Hành động Idempotent Repair bằng cách nạp lại dữ liệu gốc từ snapshot raw `crossref_records.json` và chạy lại luồng clean chuẩn] → [Báo cáo Quality Gate và Freshness khôi phục hoàn toàn (5/5 expectation pass, success: true, 0 dòng stale, is_fresh: true)] → [Toàn bộ metrics của RAG Agent phục hồi 100% về trạng thái Baseline: retrieval_hit_rate đạt 1.0, mean_token_f1 đạt 0.4869, judge_accuracy đạt 0.5, mean_judge_score đạt 2.8].

Corruption nào ảnh hưởng rõ nhất và vì sao?

Dạng corruption ảnh hưởng nghiêm trọng nhất là **việc xóa bỏ hoàn toàn các bài viết (`drop_recent`) và làm rỗng trường `summary` (`empty_summary`)**. Trong kiến trúc RAG, `summary` là thành phần nội dung chiếm tỷ trọng ngữ nghĩa lớn nhất trong chuỗi `text_for_embedding`. Khi bài viết bị xóa khỏi dataset, ChromaDB hoàn toàn không có tài liệu nguồn để truy xuất (dẫn đến `retrieval_hit_rate` sụt giảm thẳng 50%). Khi `summary` bị xóa rỗng, vector embedding trở nên vô nghĩa, khiến LLM nhận context rỗng và phải trả lời "Tôi không tìm thấy thông tin", trực tiếp kéo sụt `judge_accuracy` từ 50% xuống 20%. Artifact `corrupted_quality_report.json` đã chỉ rõ 2 dòng vi phạm độ dài summary tối thiểu (< 50 ký tự), chứng minh Quality Gate đã phát hiện chính xác nguồn cơn gây suy giảm hiệu năng Agent.

Kết quả nào khác với kỳ vọng ban đầu?

Kết quả Freshness của tập Corrupted vẫn trả về `is_fresh: true` (Pass) dù trong kịch bản đã cố tình làm cũ ngày xuất bản của 2 bài viết (`data/results/corruption_log.json` ghi nhận làm cũ 2 bài về ngày 2025-09-26). Ban đầu tôi kỳ vọng Freshness Gate sẽ báo lỗi đỏ (Fail). Tuy nhiên khi kiểm tra chi tiết `data/quality/corrupted_freshness_report.json`, số dòng stale thực tế là 2 trên tổng số 20 dòng, tương ứng `stale_ratio = 0.1` (10%). Trong cấu hình hệ thống, ngưỡng tối đa cho phép là `_FRESHNESS_MAX_STALE_RATIO = 0.25` (25%). Do 10% < 25% nên hệ thống vẫn đánh giá đạt SLA. Điều này cho thấy hệ thống Data Observability cần phân biệt giữa "tín hiệu cảnh báo suy thoái" (stale ratio tăng từ 0% lên 10%) và "chốt chặn cứng" (hard failure khi vượt 25%). Kỹ sư observability không thể chỉ nhìn cờ boolean `is_fresh` mà phải theo dõi các metric định lượng chi tiết như `stale_rows` và `stale_ratio`.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data pipeline cần nguyên tắc Idempotency và Data Lineage:** Dữ liệu thô (Raw Snapshot) phải được bảo toàn bất biến (immutable). Khi xảy ra sự cố dữ liệu ở các tầng downstream, phương pháp phục hồi duy nhất an toàn và tin cậy là replay pipeline từ snapshot nguồn sạch, thay vì cố gắng sửa chữa cục bộ trên dữ liệu đã bị biến dạng.
2. **Data Observability phải là hệ thống giám sát đa chiều (Multi-dimensional Quality Gate):** Cần kết hợp cả kiểm tra cấu trúc/schema tĩnh (Completeness, Uniqueness, Validity bằng Great Expectations) lẫn giám sát thuộc tính động theo thời gian (Freshness SLA với cơ chế fail-closed). Việc tách biệt các lớp kiểm tra và xuất báo cáo JSON chuẩn hóa giúp hệ thống dễ dàng tích hợp vào luồng tự động hóa.
3. **Chất lượng dữ liệu quyết định trần hiệu năng của RAG Agent ("Garbage in, Garbage out"):** Chỉ cần 2 dòng summary rỗng và một vài record bị mất đã đủ làm bốc hơi 50% hit rate và 60% độ chính xác của LLM Judge. Ngay cả khi retrieval hit rate đạt 100% ở baseline, điểm judge vẫn chỉ đạt 2.8/5.0, cho thấy chất lượng RAG còn phụ thuộc rất lớn vào cách cấu trúc văn bản đưa vào embedding (`text_for_embedding`).

### Nếu có thêm thời gian

Nếu có thêm thời gian, tôi sẽ triển khai module **Data Quality Profiling tự động kết hợp Semantic Drift Monitoring cho Vector Embeddings**:
- Bổ sung bước đo lường khoảng cách cosine trung bình giữa các vector embedding mới và vector baseline nhằm phát hiện sớm sự trôi dạt ngữ nghĩa (semantic drift) trước khi ghi vào ChromaDB.
- Xây dựng dashboard Data Quality Score tổng hợp (thang điểm 0–100%) và tích hợp webhook cảnh báo tự động (qua Slack/Discord) ngay khi có expectation bị vi phạm hoặc khi `stale_ratio > 0`.
- Cách đo lường: Thực hiện inject nhiễu ngữ nghĩa có chủ đích vào văn bản bài báo và kiểm tra xem hệ thống có phát hiện và kích hoạt cảnh báo bất thường trong vòng dưới 1 giây hay không, giảm thời gian phát hiện sự cố (MTTD) ngay tại cổng Ingestion.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Lê Minh Sang
**Ngày xác nhận:** 2026-09-26
