# RAG Chatbot - Công An Phường

Dự án này là hệ thống Hỏi đáp (Chatbot) Hỗ trợ Thông tin Thủ tục Hành chính, An ninh Trật tự dành cho Công an Phường/Xã tại Việt Nam. Chatbot ứng dụng **RAG** với các tính năng:
- **Phân tích truy vấn:** Chia nhỏ câu hỏi phức tạp đa ý định thành các truy vấn đơn giản.
- **Truy xuất vector đa tầng:** Ưu tiên trả kết quả từ cơ sở tri thức hỏi đáp (Q&A KB). Nếu không đủ độ tin cậy, tự động tra cứu trong văn bản pháp luật gốc.
- **Grader tự động:** Đánh giá độ tin cậy của tài liệu truy xuất để quyết định có nên sử dụng hay không.
- **Giao diện realtime:** Trả về kết quả dưới dạng Server-Sent Events giúp hiển thị trực quan các bước suy nghĩ của chatbot.

## Phạm vi thông tin hỗ trợ

1. **Thủ tục Cư trú:** Hướng dẫn đăng ký thường trú, tạm trú, khai báo tạm vắng, thông báo lưu trú, xóa/điều chỉnh và xác nhận thông tin cư trú.
2. **Căn cước & Định danh điện tử (VNeID):** Thủ tục cấp, đổi, cấp lại thẻ căn cước (cho người dưới 14 tuổi và từ 14 tuổi trở lên); đăng ký, kích hoạt tài khoản định danh VNeID (Mức 1, Mức 2) và tích hợp giấy tờ.
3. **Dịch vụ công trực tuyến:** Hướng dẫn nộp hồ sơ, tra cứu tiến độ giải quyết và thanh toán lệ phí trực tuyến trên Cổng Dịch vụ công Quốc gia & Cổng Dịch vụ công Bộ Công an.
4. **Đăng ký xe & Giấy phép lái xe (GPLX):** Cấp, thu hồi đăng ký xe, biển số xe cơ giới; cấp, đổi, cấp lại Giấy phép lái xe và Giấy phép lái xe quốc tế.
5. **An ninh trật tự & Phản ánh của người dân:** Tiếp nhận tố giác, tin báo về tội phạm; phản ánh các vi phạm ANTT (trộm cắp, gây rối, tụ tập đua xe, cho vay nặng lãi...) và hướng dẫn gọi số khẩn cấp 113.
6. **Phòng cháy chữa cháy & Cứu nạn cứu hộ (PCCC & CNCH):** Quy định an toàn PCCC cho hộ gia đình và cơ sở kinh doanh, cảnh báo xử phạt vi phạm và hướng dẫn gọi số khẩn cấp 114.
7. **Ngành nghề kinh doanh có điều kiện về ANTT:** Hướng dẫn thủ tục cấp Giấy chứng nhận đủ điều kiện về ANTT, quy định con dấu, pháo và trách nhiệm của cơ sở kinh doanh (khách sạn, nhà nghỉ, karaoke, cầm đồ...).
8. **Tuyên truyền phòng chống tội phạm:** Cảnh báo các thủ đoạn lừa đảo mới trên không gian mạng; khuyến cáo bảo mật OTP, tài khoản ngân hàng và thông tin cá nhân.
9. **Thông tin địa phương & Lịch làm việc:** Địa chỉ trụ sở Công an phường/xã, số điện thoại trực ban 24/7, lịch tiếp công dân, cán bộ phụ trách địa bàn và các kênh truyền thông chính thức.

## Cấu trúc thư mục

```
├── app/
│   ├── templates/
│   │   └── index.html               # Giao diện Chatbot web
│   └── app.py                       # Flask server
├── data/
│   ├── chunks/
│   │   ├── kb_chunks.jsonl          # Các câu hỏi & trả lời chuẩn hóa
│   │   └── source.jsonl             # Dữ liệu chia nhỏ từ văn bản luật gốc
│   └── vectorstore/                 # Cơ sở dữ liệu Chroma
├── src/
│   ├── embedding/
│   │   ├── embedder.py              # Logic load model Embedding tiếng Việt
│   │   ├── build_kb.py              # Nhúng kb_chunks vào Chroma DB
│   │   └── build_source.py          # Nhúng source.jsonl vào Chroma DB
│   ├── retrieval/
│   │   └── query.py                 # Hàm truy xuất dữ liệu từ Chroma DB
│   └── generation/
│       ├── .env                     # File chứa API Key
│       └── chatbot.py               # Logic LLM chính
├── requirements.txt
└── README.md
```

## Yêu cầu cài đặt

1. Cài đặt Python 3.9+
2. Khởi tạo virtual environment và cài đặt thư viện:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Thêm API Key của Google Gemini:
Bạn cần mở file `src/generation/.env` và thêm:
```env
GEMINI_API_KEY=your_api_key_here
```

## Hướng dẫn sử dụng

### 1. Xây dựng Cơ sở dữ liệu Vector ChromaDB
Chạy 1 lần các lệnh sau để đọc dữ liệu từ `data/chunks/` và nhúng vào `data/vectorstore/`:
```bash
python src/embedding/build_kb.py
python src/embedding/build_source.py
```

### 2. Khởi chạy Web Server
```bash
python app/app.py
```
Truy cập: `http://127.0.0.1:5000` trên trình duyệt để sử dụng chatbot.

### 3. Sử dụng trực tiếp trên Terminal (Cách 2)
```bash
python src/generation/chatbot.py
```
