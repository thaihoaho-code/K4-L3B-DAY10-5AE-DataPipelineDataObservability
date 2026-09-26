# Member Role Report — Day 10: Data Pipeline & Data Observability
## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | [Nguyễn Đình Lâm Phúc]             |
| MSSV               | [2A202602986]                     |
| Khóa/Lớp         | [K4]              |
| Tên nhóm         | [5AE]     |
| Vai trò chính    | [Data Ingestion]                 |
| Repository         | [https://github.com/thaihoaho-code/K4-L3B-DAY10-5AE-DataPipelineDataObservability] |
| Ngày hoàn thành | [2026-09-26]               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Thu thập và bóc tách metadata Crossref | `crossref.py`: `parse_crossref_payload()`, `fetch_source_records()` | `Settings` gồm query, filter, số lượng bài | `crossref_response.json`, `crossref_records.json` và danh sách `PaperRecord` | Hoàn thành; đã kiểm tra parse và giả lập lỗi mạng, 429/503, JSON lỗi để xác minh fallback. |
| Nạp lại dữ liệu thô từ snapshot | `crossref.py`: `load_raw_records()` | `crossref_records.json` | Danh sách `PaperRecord` cho cleaning | Hoàn thành; đã kiểm tra nạp snapshot và chuyển tiếp sang cleaning thành công 24 dòng. |
| Làm sạch dữ liệu và chuẩn bị văn bản cho embedding | `cleaning.py`: `build_clean_dataframe()` | Danh sách `PaperRecord` và thời điểm chạy `run_date` | `pandas.DataFrame` chuẩn hóa khoảng trắng, Unicode, ngày tháng; loại dòng không hợp lệ và trùng `paper_id`. | Hoàn thành; đã kiểm tra 24 records mẫu, trùng ID, ngày lỗi, múi giờ và đầu vào rỗng. |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Debug lỗi hiển thị tiếng Việt | Lệnh kiểm tra luồng nạp snapshot → cleaning trong PowerShell | Xác định lỗi `UnicodeEncodeError` khi in kết quả; bổ sung tùy chọn `python -X utf8 -c` và chạy lại thành công, nhận thông báo: `Tín hiệu hoàn thành: Clean thành công 24 dòng`. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Thu thập metadata Crossref, bóc tách trường dữ liệu, loại thẻ HTML/XML và lưu raw artifacts | `crossref.py`: `parse_crossref_payload()`, `fetch_source_records()` | `crossref_response.json` chứa phản hồi API nguyên bản; `crossref_records.json` chứa danh sách metadata theo cấu trúc `PaperRecord`. Có retry và fallback sang snapshot khi API lỗi. | Đã đối chiếu kết quả parse với 24 records mẫu; kiểm tra API giả lập thành công, timeout, HTTP 429/503 và JSON lỗi; xác nhận fallback không ghi đè snapshot. |
| Nạp snapshot, làm sạch metadata, khử trùng ID và tạo ngữ cảnh embedding | `crossref.py`: `load_raw_records()`; `cleaning.py`: `build_clean_dataframe()` | DataFrame chuẩn hóa văn bản và ngày tháng; `paper_id` không trùng lặp. | Chạy lệnh để kiểm tra luồng nạp → clean; đã kiểm tra thêm trường hợp trùng ID, ngày không hợp lệ, múi giờ và danh sách rỗng. |

Output cụ thể đã xác minh là DataFrame gồm **24 dòng** từ snapshot `data/raw/crossref_records.json`. Mỗi dòng có `text_for_embedding` gồm năm phần: `Title`, `Authors`, `Published`, `Categories`, `Summary`. DataFrame được trả về cho pipeline sử dụng; hàm cleaning không tự ghi file CSV/JSON.


## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Phần Data Ingestion của tôi chuyển metadata Crossref thành dữ liệu có cấu trúc để các bước kiểm tra chất lượng và tạo embedding sử dụng. Dữ liệu đầu vào có thể chứa thẻ XML trong abstract, khoảng trắng thừa, trường thiếu, ngày tháng khác định dạng hoặc DOI trùng nhau. Ngoài ra, API có thể lỗi mạng hoặc giới hạn lượt gọi, nên cần snapshot để bài lab tiếp tục chạy khi nguồn trực tuyến không khả dụng.

### Cách triển khai

1. Gửi yêu cầu đến Crossref với `query`, `filter`, `rows` lấy từ `Settings`. Với lỗi kết nối, timeout hoặc HTTP 429/500/502/503/504, thử tối đa ba lần, chờ lần lượt 1 và 2 giây giữa các lần thử. Nếu vẫn lỗi, đọc snapshot hiện có; nếu snapshot cũng thiếu hoặc không hợp lệ thì báo lỗi rõ ràng.
2. Duyệt `message.items`, lấy DOI làm `paper_id`, tiêu đề, abstract, tác giả, lĩnh vực, ngày và URL. Loại thẻ HTML/XML, giải mã HTML entities và chuẩn hóa khoảng trắng. Bỏ bản ghi thiếu DOI hoặc tiêu đề; ngày chỉ có năm/tháng được bổ sung tháng/ngày mặc định là 1.
3. Khi API thành công, lưu nguyên `response.content` vào `data/raw/crossref_response.json`; lưu danh sách `PaperRecord` đã chuyển đổi vào `data/raw/crossref_records.json`. Khi fallback, giữ nguyên snapshot nguồn. `load_raw_records()` đọc file records bằng UTF-8 có hỗ trợ BOM và chuyển từng đối tượng JSON thành `PaperRecord`.
4. Cleaning chuẩn hóa Unicode NFC, khoảng trắng và danh sách tác giả/lĩnh vực; chuyển ngày về UTC và xuất dạng `YYYY-MM-DD`. Loại dòng thiếu ID, title, summary hoặc ngày xuất bản không hợp lệ; nếu `updated` không hợp lệ thì dùng `published`. Khử trùng `paper_id`, giữ dòng hợp lệ đầu tiên.
5. Tính `age_days = (run_date - published).days` sau khi chuẩn hóa ngày xuất bản về đầu ngày UTC. Tạo các cột ghép, độ dài summary và `text_for_embedding` theo thứ tự Title → Authors → Published → Categories → Summary. Sắp xếp ngày xuất bản giảm dần, sau đó theo ID. Hàm trả DataFrame và không sửa danh sách đầu vào.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input | `Settings` chứa query/filter/số lượng và đường dẫn; payload Crossref hoặc snapshot; cleaning nhận `list[PaperRecord]` và `run_date` hợp lệ. `run_date` không có múi giờ được hiểu là UTC. |
| Output | Hai raw artifacts; danh sách `PaperRecord`; DataFrame giữ metadata cùng `age_days`, `authors_joined`, `categories_joined`, `summary_chars`, `text_for_embedding`. Ngày là chuỗi ISO, `paper_id` duy nhất. |
| Module phụ thuộc | `src/core/config.py` cung cấp cấu hình/đường dẫn; Requests gọi API; pandas xử lý bảng và ngày. |
| Module sử dụng output | `src/pipelines/phase1.py` tích hợp baseline; `src/observability/quality.py` kiểm tra chất lượng; `src/retrieval/index.py` tạo index; `src/evaluation/testset.py` tạo bộ câu hỏi; `src/pipelines/corruption_flow.py` nạp raw và clean lại để repair. |
| Điều kiện lỗi cần xử lý | Mạng/HTTP lỗi; JSON hoặc cấu trúc payload sai; snapshot thiếu; records không đúng cấu trúc; ngày không hợp lệ. Không trả dữ liệu giả khi cả API và snapshot đều không dùng được. |

### Cách xác minh

```powershell
python -X utf8 -c "from datetime import datetime, timezone; from core.config import load_settings; from ingestion.crossref import load_raw_records; from ingestion.cleaning import build_clean_dataframe; s=load_settings(); df=build_clean_dataframe(load_raw_records(s.paths.raw_records_json), datetime.now(timezone.utc)); assert df['paper_id'].is_unique; assert {'age_days', 'text_for_embedding'}.issubset(df.columns); print(f'Tín hiệu hoàn thành: Clean thành công {len(df)} dòng')"
```

- **Kết quả mong đợi:** Nạp được snapshot, tạo DataFrame sạch với ID duy nhất và đủ cột phục vụ embedding.
- **Kết quả thực tế:** `Tín hiệu hoàn thành: Clean thành công 24 dòng`; các assertion đều đạt.
- **Artifact/log:** Đầu vào là `data/raw/crossref_records.json`; kết quả kiểm tra được in ở terminal. Lệnh này không ghi file dữ liệu sạch và không chạy evaluation toàn pipeline.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Việc phụ thuộc hoàn toàn vào API khiến bước ingestion có thể dừng bài lab khi mạng lỗi hoặc bị giới hạn lượt gọi.
- **Các phương án đã cân nhắc:** Chỉ dùng API và dừng khi lỗi; luôn đọc snapshot offline; hoặc gọi API với retry có giới hạn rồi fallback snapshot.
- **Phương án đã chọn:** Retry tối đa ba lần cho các lỗi tạm thời, sau đó đọc snapshot có sẵn. Chỉ ghi phản hồi API mới sau khi JSON đã được parse thành công.
- **Lý do:** Cách này cho phép lấy dữ liệu mới khi nguồn hoạt động, đồng thời duy trì khả năng chạy lab khi nguồn gián đoạn. Đổi lại, dữ liệu fallback có thể cũ nên vẫn cần kiểm tra freshness. Snapshot tại đường dẫn hiện tại sẽ bị thay thế khi fetch thành công, chưa phải kho lưu lịch sử từng lần chạy.
- **Bằng chứng quyết định phù hợp:** Kiểm tra API giả lập timeout, 429 và 503 đều retry rồi đọc được 24 records mẫu; snapshot giữ nguyên byte khi fallback. Kiểm tra JSON lỗi cũng dùng snapshot; khi không có snapshot hợp lệ, hàm báo `RuntimeError`.

## 6. Một lỗi hoặc blocker đã xử lý

### Lỗi encoding khi in kết quả tiếng Việt trên Windows

- **Triệu chứng/lỗi nguyên văn:** Sau khi nạp snapshot và cleaning, lệnh kiểm tra dừng ở `print(...)` với lỗi `UnicodeEncodeError: 'charmap' codec can't encode character '\u1ec7' in position 6: character maps to <undefined>`. Traceback đi qua `encodings/cp1258.py`.
- **Lệnh hoặc bước tái hiện:** Chạy lệnh ở mục 4 bằng `python -c` thay cho `python -X utf8 -c` trong môi trường Windows có encoding đầu ra CP1258. Lệnh in chuỗi `Tín hiệu hoàn thành: Clean thành công ... dòng` gây lỗi tại ký tự `ệ` (U+1EC7) trong từ `hiệu`. Lỗi phụ thuộc encoding đầu ra của môi trường; terminal đã dùng UTF-8 có thể không gặp lỗi này.
- **Nguyên nhân gốc:** Python giữ chuỗi dưới dạng Unicode nhưng cần mã hóa chuỗi khi ghi ra `stdout`. Trong lần kiểm tra bị lỗi, đầu ra dùng CP1258 và không mã hóa trực tiếp được ký tự U+1EC7 ở dạng đang có. Vì vậy, xử lý dữ liệu đã hoàn tất nhưng bước in thông báo thất bại. Đây là lỗi encoding của đầu ra, không phải JSON bị mất dữ liệu hay hàm cleaning trả kết quả sai.
- **Cách xử lý:** Bật UTF-8 mode cho tiến trình bằng tùy chọn `python -X utf8 -c`. Giữ nguyên dữ liệu và thông báo tiếng Việt, không dùng cách bỏ qua ký tự lỗi vì có thể làm mất nội dung log.
- **Cách xác minh sau khi sửa:** Chạy lại nguyên luồng nạp snapshot → cleaning với `-X utf8` như mục 4. Lệnh kết thúc thành công và in `Tín hiệu hoàn thành: Clean thành công 24 dòng`; các assertion kiểm tra ID duy nhất và sự tồn tại của `age_days`, `text_for_embedding` đều đạt. Bằng chứng là kết quả terminal trong lần kiểm tra, không có file log riêng được lưu.
- **Điều học được:** Encoding của file đầu vào và encoding của terminal là hai cấu hình độc lập. Đọc JSON bằng UTF-8 thành công chưa bảo đảm in tiếng Việt thành công. Khi debug cần xác định lỗi nằm ở bước đọc, xử lý hay xuất kết quả; với lỗi này, thay đổi cấu hình đầu ra là đủ, không cần sửa thuật toán cleaning.

## 7. Hiểu biết về luồng end-to-end

1. **Từ Crossref đến vector index:** API trả JSON, ingestion lưu bản raw và bóc tách thành `PaperRecord`. Cleaning tạo DataFrame và `text_for_embedding`. Pipeline của nhóm lưu dữ liệu sạch, dùng mô hình embedding mã hóa văn bản thành vector và đưa vector cùng metadata vào ChromaDB. Phần tôi trực tiếp thực hiện kết thúc ở DataFrame đầu vào cho các bước sau.
2. **Evaluation và ground truth:** Mỗi câu hỏi có câu trả lời tham chiếu và `ground_truth_doc_ids`. Retrieval được tính là hit khi ít nhất một ID truy xuất trùng ID tham chiếu. Token F1 đo mức trùng từ giữa câu trả lời và ground truth; judge đánh giá độ đúng và cho điểm. Tìm đúng tài liệu chưa bảo đảm trả lời đúng.
3. **Quality và freshness:** Quality kiểm tra cấu trúc/nội dung như ID không null, không trùng và độ dài summary. Freshness dùng `age_days` để đếm dòng quá hạn rồi so tỷ lệ với ngưỡng cho phép. Trong artifact hiện có, ngưỡng tuổi là 180 ngày và tỷ lệ stale tối đa là 25%, nên có dòng cũ vẫn có thể đạt freshness tổng thể.
4. **Giữ cùng test set:** Cùng câu hỏi và ground truth giúp so sánh ba trạng thái trên một đầu vào đánh giá cố định. Nếu đổi test set, khó tách tác động của corruption khỏi khác biệt về độ khó câu hỏi. Để tái lập đầy đủ còn cần cố định cấu hình mô hình, snapshot và thời điểm chạy.
5. **Xác nhận repair:** Đối chiếu dữ liệu repaired với nguồn raw, kiểm tra lại ID/summary/freshness, xây lại index và đánh giá trên cùng test set. Các file `data/clean/papers_clean_repaired.json`, `data/quality/repaired_quality_report.json`, `data/quality/repaired_freshness_report.json` và `data/results/repaired_metrics.json` cung cấp bằng chứng. Metrics trở về baseline là phục hồi mức ban đầu, không có nghĩa chất lượng trả lời đã hoàn hảo.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | 1.0 | 0.5 | 1.0 | Tỷ lệ tìm đúng tài liệu giảm từ 10/10 xuống 5/10 câu, sau đó phục hồi. |
| `mean_token_f1` | 0.4869 | 0.2165 | 0.4869 | Mức trùng từ với câu trả lời tham chiếu giảm ở dữ liệu corrupted. |
| `judge_accuracy` | 0.5 | 0.2 | 0.5 | Số câu được judge đánh giá đúng giảm từ 5/10 xuống 2/10. |
| `mean_judge_score` | 2.8 | 1.8 | 2.8 | Điểm trung bình trên thang 1–5 phục hồi về baseline. |
| Quality checks | Pass, 5/5 | Fail, 3/5 | Pass, 5/5 | Corrupted không đạt kiểm tra ID duy nhất và độ dài summary. |
| Freshness status | Pass, 0/24 stale | Pass, 2/20 stale | Pass, 0/24 stale | Corrupted có 10% dòng quá 180 ngày, vẫn dưới ngưỡng 25%. |

Số liệu được đối chiếu từ các artifact tích hợp của nhóm: `data/results/{baseline,corrupted,repaired}_metrics.json`, `data/quality/{baseline,corrupted,repaired}_quality_report.json`, `data/quality/freshness_report.json`, `data/quality/corrupted_freshness_report.json` và `data/quality/repaired_freshness_report.json`. Các metrics evaluation dùng 10 mẫu, làm tròn bốn chữ số khi cần. Đây là kết quả nhóm đã lưu, không phải một lần chạy toàn pipeline do tôi thực hiện trong bước viết báo cáo. Ragas đang được bỏ qua theo trường `ragas.skipped`.

### Kết luận từ số liệu

1. **Corruption → tín hiệu dữ liệu → chất lượng agent:** `data/results/corruption_log.json` ghi nhận bỏ 5 bài mới nhất, làm rỗng 2 summary, thêm nhiễu vào 2 summary, cắt 2 title, làm cũ ngày của 2 bài và thêm 1 dòng trùng. Dữ liệu còn 20 dòng với 19 ID duy nhất; quality không đạt và có 2 dòng stale. Các metrics corrupted được lưu cho thấy hit rate giảm từ 1.0 xuống 0.5 và token F1 từ 0.4869 xuống 0.2165. Các thay đổi được áp dụng đồng thời nên chưa thể quy toàn bộ mức giảm cho một loại lỗi riêng.
2. **Repair → tín hiệu phục hồi → metrics phục hồi:** Module repair của nhóm nạp raw bằng `load_raw_records()`, chạy lại `build_clean_dataframe()` rồi tạo lại index. Artifact repaired có 24 dòng, quality đạt 5/5 và không có dòng stale. Bốn metrics evaluation được lưu đều bằng baseline. Phần đóng góp của tôi là cung cấp raw records và hàm nạp/cleaning có thể tái sử dụng cho bước phục hồi.

**Corruption có bằng chứng ảnh hưởng trực tiếp rõ nhất:** Việc bỏ tài liệu nguồn làm truy vấn không còn tìm được bài cần thiết. Ví dụ, `eval_001` trong `baseline_answers.json` tìm được DOI `10.21203/rs.3.rs-10489777/v1`; DOI này nằm trong danh sách bị xóa của corruption log. Ở `corrupted_answers.json`, ID đó không xuất hiện trong kết quả truy xuất và câu trả lời rỗng; ở `repaired_answers.json`, tài liệu được tìm lại. Đây là bằng chứng cho một câu hỏi cụ thể, chưa phải phép đo tách riêng tác động của cả sáu kịch bản.

**Kết quả khác với kỳ vọng ban đầu:** Freshness của corrupted vẫn Pass dù đã có ngày bị làm cũ. Đối chiếu `corrupted_freshness_report.json` cho thấy `stale_rows=2`, `total_rows=20`, `stale_ratio=0.1` và `max_stale_ratio=0.25`; vì vậy kết quả đúng với ngưỡng cấu hình. Điều này cho thấy cần đọc cả số dòng và tỷ lệ stale, không chỉ cờ `is_fresh`.

Một giới hạn khi đối chiếu là các artifact chưa có `run_id` chung; thời điểm kiểm tra GX trong báo cáo corrupted và repaired khác nhau. Vì vậy, các số liệu trên mô tả kết quả đang lưu trong workspace, chưa chứng minh tất cả artifact thuộc cùng một lần chạy đồng bộ.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Data pipeline cần đầu vào/đầu ra rõ ràng:** JSON gốc, `PaperRecord` và DataFrame sạch có vai trò khác nhau. Lưu raw giúp truy vết và chạy lại cleaning; chỉ một hàm nạp snapshot chưa triển khai cũng có thể chặn cả luồng tích hợp.
2. **Dữ liệu sạch cần được đo bằng nhiều tín hiệu:** Loại trùng ID và chuẩn hóa ngày giúp các bước sau hoạt động ổn định, nhưng còn phải kiểm tra độ đầy đủ, độ dài văn bản và freshness. Một trạng thái Pass chỉ có ý nghĩa trong phạm vi các điều kiện và ngưỡng đang áp dụng.
3. **Chất lượng dữ liệu ảnh hưởng trực tiếp đến RAG:** Tài liệu bị mất hoặc summary thiếu làm giảm ngữ cảnh cho retrieval và trả lời. Chuỗi `text_for_embedding` nhất quán giúp pipeline dùng đúng metadata; kết quả nhóm cũng cho thấy tìm đúng tài liệu 100% chưa đồng nghĩa câu trả lời đúng 100%.

### Nếu có thêm thời gian

Tôi sẽ bổ sung phiên bản snapshot theo từng lần fetch, kèm manifest chứa `run_id`, thời điểm UTC, query/filter, nguồn API hay fallback, số records và SHA-256 của file raw. Mỗi artifact clean/quality/evaluation sẽ tham chiếu cùng `run_id` để xác định đúng nguồn dữ liệu. Cải thiện này giải quyết hạn chế snapshot hiện bị ghi đè khi fetch thành công và hỗ trợ đối chiếu các kết quả thuộc cùng lần chạy.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x]Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** [Nguyễn Đình Lâm Phúc]
**Ngày xác nhận:** [2026-09-26]
