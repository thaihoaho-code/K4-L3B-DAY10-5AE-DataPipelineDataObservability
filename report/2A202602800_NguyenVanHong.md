# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Văn Hồng |
| MSSV | 2A202602800 |
| Khóa/Lớp | K4-L3B-DAY10 |
| Tên nhóm | 5AE |
| Vai trò chính | Evaluation & Reporting |
| Repository | `K4-L3B-DAY10-5AE-DataPipelineDataObservability` |
| Nhánh làm việc | `data-evaluation` |
| Ngày hoàn thành báo cáo | 2026-09-26 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Evaluation set | `src/evaluation/testset.py` — `build_test_set` | Cleaned `DataFrame` có `paper_id`, `title`, `summary`, `authors`, `categories`, `published` | 10 test cases và `data/eval/test_set.json` | Đã hoàn thiện implementation; chờ tích hợp pipeline |
| Markdown reporting | `src/observability/reporting.py` — `generate_phase1_report`, `generate_corruption_report` | Source summary, metrics, quality/freshness dicts | `data/reports/phase1_report.md` và `data/reports/corruption_report.md` | Đã hoàn thiện implementation; chờ tích hợp pipeline |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Rà soát contract tích hợp | `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `src/observability/quality.py` | Giữ nguyên signature skeleton và xác định input/output cần truyền cho reporting |
| Rà soát artifact path | `src/core/config.py` | Dùng các path đã cấu hình như `eval_testset`, `baseline_report` và `comparison_report`; không hard-code đường dẫn local |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Sinh evaluation set từ cleaned DataFrame | `src/evaluation/testset.py:build_test_set` | Kiểm tra cột bắt buộc, yêu cầu tối thiểu 10 documents, sinh đúng 10 case qua 4 loại `summary`, `authors`, `date`, `categories` | `python -m py_compile src/evaluation/testset.py`; rà soát schema trong code |
| Chuẩn hóa ground truth | `src/evaluation/testset.py` | `summary` lấy câu đầu; list/string được chuyển thành text; `published` hỗ trợ string/datetime; DOI được giữ trong `ground_truth_doc_ids` | Rà soát `_as_text`, `_first_sentence`, `_date_text` |
| Sinh phase 1 Markdown report | `src/observability/reporting.py:generate_phase1_report` | Render source summary, metrics, quality và freshness nếu được truyền vào; tạo thư mục cha và ghi UTF-8 | `python -m py_compile src/observability/reporting.py`; rà soát `_write_report` |
| Sinh corruption comparison report | `src/observability/reporting.py:generate_corruption_report` | Render bảng `Metric | Baseline | Corrupted | Repaired`; render quality/freshness theo dữ liệu signature hiện có | Rà soát `_metrics_table`, `_comparison_table`; giữ nguyên API skeleton |

### Output cụ thể

Các module đã sẵn sàng tạo các artifact sau khi orchestration truyền dữ liệu thực:

- `data/eval/test_set.json`: evaluation set gồm 10 câu hỏi.
- `data/reports/phase1_report.md`: báo cáo baseline phase.
- `data/reports/corruption_report.md`: báo cáo so sánh ba trạng thái theo metrics.

Hiện tại không tạo artifact hoặc số liệu giả. Các file `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py` và `src/observability/quality.py` trong working tree vẫn còn skeleton nên chưa thể xác minh end-to-end.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline cần một evaluation set cố định để đo retrieval và answer quality trên cùng một tập câu hỏi. Sau đó, các kết quả baseline, corrupted và repaired cần được chuyển thành Markdown dễ đọc để nhóm đối chiếu artifact và metrics mà không làm thay đổi dữ liệu gốc.

### Cách triển khai

#### Evaluation set

`build_test_set` thực hiện các bước:

1. Kiểm tra DataFrame có đủ sáu cột theo clean-data contract.
2. Từ chối DataFrame có ít hơn 10 documents vì đề bài yêu cầu đúng 10 test cases.
3. Lấy 10 dòng đầu theo thứ tự hiện có để tạo kết quả deterministic, không random và không mock data.
4. Luân phiên bốn loại câu hỏi `summary`, `authors`, `date`, `categories`.
5. Tạo các field `id`, `question_type`, `question`, `ground_truth`, `ground_truth_doc_ids`.
6. Ghi JSON UTF-8 với indent dễ đọc và tự tạo thư mục cha.

#### Reporting

`reporting.py` chỉ render dữ liệu đã được truyền vào:

- Không gọi Crossref, ChromaDB, Great Expectations hoặc LLM.
- Không tự tính lại metrics.
- Không hard-code kết quả thực nghiệm.
- Render được scalar và dict/list lồng nhau.
- Escape ký tự `|` và xuống dòng trong Markdown table.
- Giữ nguyên chữ ký hàm hiện có để tránh làm hỏng merge với orchestration.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input của `build_test_set` | `pd.DataFrame` sạch với `paper_id`, `title`, `summary`, `authors`, `categories`, `published`; `output_path` |
| Output của `build_test_set` | `list[dict[str, Any]]` gồm 10 test cases; đồng thời ghi JSON tại `output_path` |
| Input của `generate_phase1_report` | `report_path`, `source_summary`, `metrics`, `quality`, `freshness` |
| Input của `generate_corruption_report` | `report_path`, baseline/corrupted/repaired metrics, corrupted/repaired quality và freshness |
| Output của reporting | Không return dữ liệu; ghi Markdown UTF-8 tại `report_path` |
| Module phụ thuộc | Cleaned DataFrame, evaluation metrics, quality/freshness results và paths trong `core.config` |
| Module sử dụng output | `phase1.py`, `corruption_flow.py` và các artifact báo cáo |
| Điều kiện lỗi cần xử lý | Thiếu cột hoặc ít hơn 10 documents; dữ liệu ngày không parse được; report path chưa tồn tại; dict thiếu key |

### Cách xác minh

```bash
python -m py_compile src/evaluation/testset.py src/observability/reporting.py
git diff --check
```

- **Kết quả mong đợi:** Hai module hợp lệ về cú pháp, không có lỗi whitespace trong diff.
- **Kết quả thực tế:** `py_compile` đạt và `git diff --check` đạt trong phạm vi phần việc hiện tại.
- **Artifact/log:** Các artifact JSON/Markdown sẽ được sinh khi pipeline tích hợp truyền dữ liệu thực; chưa tạo artifact giả trong giai đoạn phát triển module.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Báo cáo corruption cần bảng so sánh ba trạng thái, nhưng signature skeleton chỉ nhận baseline cho metrics; quality và freshness chỉ có corrupted/repaired.
- **Các phương án đã cân nhắc:**
  1. Tự đọc thêm file baseline hoặc tự gọi quality module trong `reporting.py`.
  2. Đổi signature để nhận thêm `baseline_quality` và `baseline_freshness`.
  3. Giữ nguyên signature và chỉ render đúng dữ liệu được truyền vào.
- **Phương án đã chọn:** Giữ nguyên API hiện có; render đủ ba trạng thái cho metrics và render `Corrupted | Repaired` cho quality/freshness.
- **Lý do:** Không tạo coupling với filesystem hoặc Great Expectations, không tự tính dữ liệu ngoài input, và tránh làm hỏng lời gọi từ `corruption_flow.py` khi các branch được merge. Nếu nhóm muốn so sánh quality/freshness đủ ba trạng thái, cần thống nhất contract mới trước khi sửa signature.
- **Bằng chứng quyết định phù hợp:** Signature trong `src/observability/reporting.py` hiện không có `baseline_quality` và `baseline_freshness`; `src/core/config.py` cung cấp path artifact nhưng không phải input trực tiếp của renderer.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Các hàm trong `testset.py` và `reporting.py` ban đầu là `NotImplementedError`.
- **Lệnh hoặc bước tái hiện:** Đọc skeleton và kiểm tra compile trước khi implementation.
- **Nguyên nhân gốc:** Starter lab để trống phần evaluation/reporting cho sinh viên hoàn thiện; pipeline orchestration chưa kết nối các module.
- **Cách xử lý:** Implement generator cho evaluation JSON và Markdown renderer, giữ nguyên signature, bổ sung tạo thư mục cha và encoding UTF-8.
- **Cách xác minh sau khi sửa:**

  ```bash
  python -m py_compile src/evaluation/testset.py src/observability/reporting.py
  git diff --check
  ```

- **Điều học được:** Cần thống nhất schema và artifact path trước khi các branch chạy song song; renderer chỉ nên trình bày kết quả, không tự truy cập nguồn dữ liệu hoặc tự tính lại metrics.

### Blocker còn lại

- **Phạm vi bị ảnh hưởng:** Chạy end-to-end và tạo metrics/report artifact thực tế.
- **Những gì đã loại trừ:** Không dùng mock DataFrame, không tạo số liệu giả, không gọi API, ChromaDB hoặc Great Expectations để giả lập kết quả.
- **Bước tiếp theo:** Sau khi các branch hoàn thiện `quality.py`, `phase1.py` và `corruption_flow.py`, chạy hai lệnh pipeline trong `report/README.md`, sau đó đối chiếu metrics và report với JSON artifact.

## 7. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   `crossref.py` lấy và parse raw records thành `PaperRecord`; `cleaning.py` chuyển chúng thành cleaned DataFrame, chuẩn hóa các field và tạo `text_for_embedding`; module retrieval dùng cleaned documents để tạo embeddings và nạp vào ChromaDB. `testset.py` tạo evaluation set từ cleaned DataFrame trước bước đánh giá.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Mỗi test case có câu hỏi, ground truth và `ground_truth_doc_ids` lấy từ `paper_id`. `metrics.py` kiểm tra document ID được truy hồi có nằm trong danh sách ground truth hay không để tính `retrieval_hit_rate`, đồng thời so sánh câu trả lời với ground truth để tính token F1 và judge metrics.

3. **Quality checks khác freshness monitoring ở điểm nào?**
   Quality checks kiểm tra tính hợp lệ của schema và dữ liệu, chẳng hạn `paper_id` không null/unique, title không null và summary hợp lệ. Freshness monitoring tập trung vào độ mới của `published`, số dòng stale và trạng thái có còn trong ngưỡng freshness SLA hay không.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Cùng evaluation set giúp thay đổi metrics phản ánh tác động của corruption/repair thay vì thay đổi do câu hỏi hoặc ground truth khác nhau. Đây là điều kiện cần để so sánh ba trạng thái có ý nghĩa.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   Cần kiểm tra repaired dataset được tạo lại từ raw source, quality/freshness trở về trạng thái hợp lệ hơn, và các metrics như `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score` phục hồi so với corrupted state. Kết luận cuối cùng phải dựa trên JSON artifacts và comparison report thực tế.

## 8. Phân tích kết quả

### Metrics chính

Do các module orchestration, quality và corruption flow chưa hoàn tất trong working tree, hiện chưa có số liệu thực tế để điền. Không ghi số giả vào báo cáo.

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | N/A | N/A | N/A | Sẽ lấy từ các file `*_metrics.json` sau khi pipeline chạy |
| `mean_token_f1` | N/A | N/A | N/A | Sẽ đối chiếu trên cùng evaluation set |
| `judge_accuracy` | N/A | N/A | N/A | Phụ thuộc kết quả evaluate thực tế |
| `mean_judge_score` | N/A | N/A | N/A | Không tự suy diễn khi chưa có artifact |
| Quality checks | Chưa có | Chưa có | Chưa có | `quality.py` chưa sinh report trong working tree hiện tại |
| Freshness status | Chưa có | Chưa có | Chưa có | Chưa chạy freshness report thực tế |

### Kết luận từ số liệu

Chưa thể kết luận định lượng về mức suy giảm hoặc phục hồi vì chưa có output mới từ baseline/corruption flow. Sau khi tích hợp cần điền hai chuỗi bằng artifact thực tế:

1. Corruption/data change → quality hoặc freshness signal thay đổi → retrieval/answer metric thay đổi.
2. Repair action → quality hoặc freshness signal phục hồi → agent metric phục hồi hoặc ghi rõ lý do chưa phục hồi.

Corruption ảnh hưởng rõ nhất và kết quả khác kỳ vọng chỉ được xác định sau khi có `corruption_log.json`, `corrupted_metrics.json`, `repaired_metrics.json` và các quality/freshness reports.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Evaluation set phải ổn định, có document ID rõ ràng và được dùng lại giữa baseline, corrupted và repaired.
2. Reporting nên là lớp trình bày thuần túy; việc tính quality, freshness và metrics phải thuộc module chuyên trách để tránh sai lệch kết quả.
3. Một comparison report chỉ có giá trị khi số liệu được sinh từ cùng cấu hình, cùng test set và có artifact để truy nguyên.

### Nếu có thêm thời gian

Sau khi pipeline hoàn thiện, có thể bổ sung kiểm tra tự động cho schema của test set và report contract, đồng thời thêm baseline quality/freshness vào API của `generate_corruption_report` nếu nhóm thống nhất cần bảng ba trạng thái cho mọi signal. Thay đổi đó phải được cập nhật đồng thời trong `corruption_flow.py` để không phá compatibility.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Văn Hồng
**Ngày xác nhận:** 2026-09-26