# 🛡️ Chatbot RAG — Trợ Lý Ảo Thông Tin Hành Chính & ANTT Công An Phường / Xã

Hệ thống Hỏi đáp (Chatbot) thông minh hỗ trợ tư vấn thủ tục hành chính, an ninh trật tự, phòng cháy chữa cháy và thông tin liên hệ cho **Công an phường / xã** (được tối ưu hóa dữ liệu thực tế cho địa bàn **Công an xã An Viễn**).

Ứng dụng kiến trúc **Retrieval-Augmented Generation (RAG)** đa tầng kết hợp mô hình ngôn ngữ lớn **Google Gemini** và cơ sở dữ liệu vector **ChromaDB**.

---

## 🌟 Tính năng nổi bật

- **Truy xuất vector đa tầng (Multi-tier Retrieval):**
  - **Tầng 1 (Q&A Knowledge Base):** Ưu tiên truy xuất nhanh từ bộ câu hỏi - trả lời chuẩn hóa (`kb_chunks`) với độ chính xác cao và câu hỏi làm rõ (`clarifying_question`).
  - **Tầng 2 (Văn bản pháp luật gốc):** Tự động tìm kiếm trong hơn 900+ đoạn văn bản luật, nghị định, thông tư, quy chuẩn và tiêu chuẩn quốc gia (`source_chunks`) khi câu hỏi chuyên sâu hoặc chưa có trong KB.
- **Xử lý linh hoạt câu hỏi tự nhiên:**
  - Nhận diện tốt các trường hợp **gõ tắt, teen code, không dấu, sai lỗi chính tả** (ví dụ: *cskv, ca xa, sdt, t7, vb2, dh, dang ki xe...*).
  - Phân loại chính xác các tình huống khẩn cấp (trộm cắp, cháy nổ, xô xát) để ưu tiên hướng dẫn gọi ngay **113 / 114 / 115**.
- **Tích hợp Dịch vụ công & QR Code:**
  - Tự động cung cấp đường dẫn chính thống (`dichvucong.gov.vn`, `dichvucong.bocongan.gov.vn`, `vanban.chinhphu.vn`) kèm ảnh mã QR để người dân quét thao tác trực tuyến.
- **Giao diện Web Realtime (Server-Sent Events):**
  - Hiển thị trực quan trạng thái từng bước: *Đang tra cứu CSDL nội bộ → Đã tìm thấy tài liệu → Đang tổng hợp câu trả lời*.

---

## 📋 Phạm vi nghiệp vụ hỗ trợ

1. **Module A — Thủ tục Cư trú:** Đăng ký thường trú, tạm trú, khai báo tạm vắng, thông báo lưu trú, điều chỉnh thông tin cư trú (Luật Cư trú 68/2020, NĐ 154/2024, TT 66/2023, TT 53/2025).
2. **Module B — Căn cước & Định danh VNeID:** Cấp mới/cấp đổi thẻ căn cước (dưới 14 tuổi và từ đủ 14 tuổi), kích hoạt tài khoản VNeID Mức 1/Mức 2, tích hợp giấy tờ (Luật Căn cước 26/2023).
3. **Module C — Dịch vụ công trực tuyến:** Hướng dẫn nộp hồ sơ, tra cứu tiến độ, thanh toán phí/lệ phí trên Cổng DVC Quốc gia & Cổng DVC Bộ Công an.
4. **Module D — Đăng ký xe & GPLX:** Đăng ký xe lần đầu, sang tên, cấp đổi/thu hồi biển số định danh, đổi và cấp lại giấy phép lái xe.
5. **Module E — An ninh trật tự & Khẩn cấp:** Tiếp nhận tố giác tội phạm, báo tin an ninh trật tự, hướng dẫn an toàn và liên hệ khẩn cấp 113.
6. **Module F — Phòng cháy chữa cháy & Cứu nạn cứu hộ (PCCC & CNCH):** Quy định an toàn nhà ở, nhà trọ, cơ sở kinh doanh theo Luật PCCC 55/2024, NĐ 105/2025, NĐ 106/2025 (xử phạt), QCVN 06:2022, QCVN 10:2025, TCVN 3890; gọi khẩn cấp 114.
7. **Module G — Ngành nghề kinh doanh có điều kiện về ANTT:** Giấy chứng nhận đủ điều kiện ANTT, con dấu, cơ sở lưu trú, cầm đồ, karaoke.
8. **Module H — Tuyên truyền phòng chống tội phạm:** Cảnh báo thủ đoạn lừa đảo mạng, bảo mật OTP, tài khoản ngân hàng.
9. **Module I & AV — Thông tin liên hệ & Công an xã An Viễn:**
   - **Số điện thoại trực ban 24/7:** `02513.538.187`
   - **Địa chỉ trụ sở:** Ấp Phát Đạt, xã An Viễn, thành phố Đồng Nai, tỉnh Đồng Nai.
   - **Lịch tiếp dân:** Mô hình “Buổi sáng với Nhân dân” (sáng T2 - T6); Trưởng Công an xã tiếp dân vào 08h00 thứ 5 hằng tuần.
   - **Danh bạ 16 cán bộ Ban chỉ huy, Cảnh sát khu vực (ấp An Phú, Phát Đạt, Hưng Thịnh) & Cán bộ phụ trách từng mảng.**
   - **Tuyển chọn nghĩa vụ tham gia CAND & Tuyển sinh các trường CAND (Văn bằng 2, Đại học chính quy).**

---

## 🗂️ Cấu trúc thư mục

```
├── app/
│   ├── static/
│   │   └── images/
│   │       └── QR-dich-vu-cong.png   # Ảnh mã QR Cổng Dịch vụ công
│   ├── templates/
│   │   └── index.html               # Giao diện Chatbot web thời gian thực
│   └── app.py                       # Server Flask + Server-Sent Events (SSE)
├── data/
│   └── vectorstore/                 # CSDL Vector ChromaDB
├── src/
│   ├── chunking/
│   │   ├── chunker.py               # Chia nhỏ tài liệu luật và quy chuẩn
│   │   └── update_an_vien_kb.py     # Cập nhật dữ liệu tri thức Công an xã An Viễn
│   ├── embedding/
│   │   ├── embedder.py              # Load mô hình Sentence-Transformers tiếng Việt
│   │   ├── build_kb.py              # Nhúng tập tri thức kb_chunks vào ChromaDB
│   │   └── build_source.py          # Nhúng văn bản luật source_chunks vào ChromaDB
│   ├── generation/
│   │   ├── .env                     # File cấu hình GEMINI_API_KEY
│   │   ├── system_prompt.md         # Quy tắc & hướng dẫn trả lời của Chatbot
│   │   └── chatbot.py               # Logic gọi Google Gemini API + xử lý ngữ cảnh RAG
│   ├── ingestion/
│   │   ├── converter.py             # Chuyển đổi .docx/.doc/.pdf sang Markdown
│   │   ├── ocr_processor.py         # Xử lý PDF scan bằng PyMuPDF & Tesseract OCR
│   │   ├── source_mapping.py        # Mapping metadata danh mục tài liệu
│   │   └── run_ingestion.py         # Pipeline nạp dữ liệu đầu vào
│   ├── retrieval/
│   │   └── query.py                 # Thuật toán tìm kiếm & phân loại kết quả RAG
├── requirements.txt                 # Danh sách thư viện phụ thuộc
├── run_pipeline.py                  # Script chạy toàn bộ pipeline tự động
├── .gitignore                       # Cấu hình bỏ qua tài liệu thô & chỉ giữ vectorstore
└── README.md
```

---

## ⚙️ Cài đặt & Cấu hình

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên.
- Git.

### 2. Cài đặt môi trường
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo (Windows PowerShell):
.venv\Scripts\activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 3. Cấu hình API Key
Tạo hoặc mở file `src/generation/.env` và cấu hình:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```

---

## 🚀 Hướng dẫn vận hành

### Cách 1: Khởi chạy Giao diện Web (Khuyên dùng)
```bash
python app/app.py
```
Mở trình duyệt truy cập: **`http://127.0.0.1:5000`** để sử dụng giao diện chat trực quan.

### Cách 2: Chat trực tiếp qua Terminal CLI
```bash
python src/generation/chatbot.py
```