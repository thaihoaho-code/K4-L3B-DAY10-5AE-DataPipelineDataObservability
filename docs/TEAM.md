# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `5AE`
- **Mã Nhóm / Lớp:** `K4-L3B-DAY10`
- **Tên Repository Nộp Bài:** `K4-L3B-DAY10-5AE-DataPipelineDataObservability`

---

## # Thành viên

| STT | Họ và tên | Branch | Vai trò | Folder/Files phụ trách |
|---:|---|---|---|---|
| 1 | Nguyễn Đình Lâm Phúc | `data-ingestion` | Data Ingestion | `src/ingestion/crossref.py`, `src/ingestion/cleaning.py` |
| 2 | Lê Minh Sang | `data-observability` | Data Observability | `src/observability/quality.py` |
| 3 | Nguyễn Việt Hoàng | `data-corruption` | Data Corruption & Repair | `src/ingestion/corruption.py`, `src/pipelines/corruption_flow.py` |
| 4 | Nguyễn Văn Hồng | `data-evaluation` | Evaluation & Reporting | `src/evaluation/testset.py`, `src/observability/reporting.py` |
| 5 | Hồ Thái Hòa | `data-orchestration` | Pipeline Orchestration (Team Lead) | `src/pipelines/phase1.py`, merge các branch khác |

---

## # Báo cáo cá nhân

### ## 1. Nguyễn Đình Lâm Phúc
- **Nhánh (Branch):** `data-ingestion`
- **Vai trò:** Phụ trách Data Ingestion (Thu thập và làm sạch).
- **Công việc chi tiết đã hoàn thành:**
  - Viết logic kéo dữ liệu từ API Crossref và lưu snapshot (`crossref.py`).
  - Viết module làm sạch dữ liệu thành DataFrame chuẩn (`cleaning.py`).

### ## 2. Lê Minh Sang
- **Nhánh (Branch):** `data-observability`
- **Vai trò:** Phụ trách Data Observability (Giám sát chất lượng).
- **Công việc chi tiết đã hoàn thành:**
  - Viết Great Expectations pipeline để đánh giá chất lượng các field, tính toán Freshness SLA (`quality.py`).

### ## 3. Nguyễn Việt Hoàng
- **Nhánh (Branch):** `data-corruption`
- **Vai trò:** Phụ trách Data Corruption & Repair.
- **Công việc chi tiết đã hoàn thành:**
  - Viết logic mô phỏng sự cố dữ liệu (Corruption) (`corruption.py`).
  - Cấu hình luồng thực thi vòng lặp hỏng/sửa lỗi (`corruption_flow.py`).

### ## 4. Nguyễn Văn Hồng
- **Nhánh (Branch):** `data-evaluation`
- **Vai trò:** Phụ trách Evaluation & Reporting.
- **Công việc chi tiết đã hoàn thành:**
  - Viết module tự động trích xuất và sinh bộ test set câu hỏi (`testset.py`).
  - Lập trình tạo file báo cáo Markdown tổng hợp (`reporting.py`).

### ## 5. Hồ Thái Hòa
- **Nhánh (Branch):** `data-orchestration`
- **Vai trò:** Trưởng nhóm / Pipeline Orchestration.
- **Công việc chi tiết đã hoàn thành:**
  - Xử lý cấu hình biến và ráp luồng `phase1.py`.
  - Tích hợp toàn bộ mã nguồn nhánh con (branches) của các thành viên thành luồng Pipeline hoàn chỉnh end-to-end.
