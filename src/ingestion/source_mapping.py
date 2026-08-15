"""
Ánh xạ file trong new_docs/ → Source ID + metadata.

Quy tắc:
  - Ưu tiên .docx hơn .pdf khi trùng nội dung (dedup).
  - Bỏ qua .pptx (tạm thời).
  - Relative path tính từ new_docs/.
"""

NEW_SOURCES: dict[str, dict] = {
    # ── Root-level files ──────────────────────────────────────────────
    "1 CÁC THỦ TỤC HÀNH CHÍNH.docx": {
        "source_id": "SRC-TTHC-01",
        "title": "Các thủ tục hành chính tổng hợp",
        "module": "MULTI",
        "url": "",
        "scope": "Tổng hợp các TTHC liên quan đến Công an phường: cư trú, căn cước, đăng ký xe, ANTT.",
        "doc_quality": "text",
    },
    "Hướng dẫn Chatbox về Đăng ký xe.docx": {
        "source_id": "SRC-D-05",
        "title": "Hướng dẫn Chatbot về Đăng ký xe",
        "module": "D",
        "url": "",
        "scope": "Hướng dẫn chi tiết đăng ký xe dành cho chatbot, bổ sung module D.",
        "doc_quality": "text",
    },
    "NoiDungChatBox- CA AnVien.docx": {
        "source_id": "SRC-AV-01",
        "title": "Nội dung ChatBot – Công an An Viên",
        "module": "MULTI",
        "url": "",
        "scope": "Nội dung chatbot tùy biến cho Công an An Viên, bao gồm nhiều module.",
        "doc_quality": "text",
    },
    "tài liệu cập nhật chatbox AI.docx": {
        "source_id": "SRC-UPDATE-01",
        "title": "Tài liệu cập nhật Chatbot AI",
        "module": "MULTI",
        "url": "",
        "scope": "Cập nhật nội dung mới cho chatbot AI, bổ sung nhiều module.",
        "doc_quality": "text",
    },
    "thủ tục trích lục hộ tịch.docx": {
        "source_id": "SRC-TTHC-02",
        "title": "Thủ tục trích lục hộ tịch",
        "module": "MULTI",
        "url": "",
        "scope": "Hướng dẫn thủ tục trích lục hộ tịch, có chứa QR code dịch vụ công.",
        "doc_quality": "text",
    },
    "Huongdandangnhap-PCCC_CNCH.docx": {
        "source_id": "SRC-F-37",
        "title": "Hướng dẫn đăng nhập PCCC và CNCH",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn người dân đăng nhập, nộp hồ sơ PCCC, có chứa QR code dịch vụ công.",
        "doc_quality": "text",
    },

    # ── PCCC — Docx / Doc (text-based) ────────────────────────────────
    "10 hướng dẫn về PCCC/6. Luật PCCC và CNCH 2025.docx": {
        "source_id": "SRC-F-05",
        "title": "Luật Phòng cháy, chữa cháy và cứu nạn, cứu hộ số 55/2024/QH15 (bản docx)",
        "module": "F",
        "url": "https://vanban.chinhphu.vn/?docid=212483&pageid=27160",
        "scope": "Luật PCCC & CNCH – bản text đầy đủ, chunk theo Điều.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/6. nghi-dinh-105;2025.docx": {
        "source_id": "SRC-F-06",
        "title": "Nghị định 105/2025/NĐ-CP quy định chi tiết Luật PCCC & CNCH (bản docx)",
        "module": "F",
        "url": "https://vanban.chinhphu.vn/?classid=1&docid=213702&pageid=27160&typegroupid=4",
        "scope": "NĐ 105/2025 quy định chi tiết thi hành Luật PCCC & CNCH.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/7. Nghị-định-69-2026-NĐ-CP.docx": {
        "source_id": "SRC-F-07",
        "title": "Nghị định 69/2026/NĐ-CP",
        "module": "F",
        "url": "",
        "scope": "Nghị định 69/2026 liên quan PCCC & CNCH.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/11. Thông-tư-36-2025-TT-BCA.docx": {
        "source_id": "SRC-F-08",
        "title": "Thông tư 36/2025/TT-BCA",
        "module": "F",
        "url": "",
        "scope": "Thông tư 36/2025 của Bộ Công an hướng dẫn Luật PCCC & CNCH.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/2. QCVN 10;2025; BCA.docx": {
        "source_id": "SRC-F-09",
        "title": "QCVN 10:2025/BCA – Quy chuẩn kỹ thuật quốc gia về PCCC",
        "module": "F",
        "url": "",
        "scope": "Quy chuẩn kỹ thuật quốc gia về PCCC do BCA ban hành.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/9. QCVN 6;2022.BXD.docx": {
        "source_id": "SRC-F-10",
        "title": "QCVN 06:2022/BXD – Quy chuẩn kỹ thuật quốc gia về an toàn cháy cho nhà và công trình",
        "module": "F",
        "url": "",
        "scope": "Quy chuẩn an toàn cháy cho nhà và công trình xây dựng.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/3. 06_2022_TT-BXD_544059.doc": {
        "source_id": "SRC-F-11",
        "title": "Thông tư 06/2022/TT-BXD",
        "module": "F",
        "url": "",
        "scope": "Thông tư Bộ Xây dựng về an toàn cháy.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/4. Bảng đối chiếu cảu hệ thống chữa cháy tự động.docx": {
        "source_id": "SRC-F-12",
        "title": "Bảng đối chiếu hệ thống chữa cháy tự động",
        "module": "F",
        "url": "",
        "scope": "Bảng so sánh đối chiếu các hệ thống chữa cháy tự động.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/5. Bảng đối chiếu của hệ thống báo cháy.docx": {
        "source_id": "SRC-F-13",
        "title": "Bảng đối chiếu hệ thống báo cháy",
        "module": "F",
        "url": "",
        "scope": "Bảng so sánh đối chiếu các hệ thống báo cháy.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/8. CÁC ĐIỂM MỚI CỦA LUẬT PCCC VÀ CNCH SỐ 55; NGHỊ ĐỊNH 105 VÀ THÔNG TƯ 36.docx": {
        "source_id": "SRC-F-14",
        "title": "Các điểm mới của Luật PCCC & CNCH số 55, Nghị định 105 và Thông tư 36",
        "module": "F",
        "url": "",
        "scope": "Tổng hợp các điểm mới, thay đổi quan trọng trong Luật PCCC, NĐ 105, TT 36.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/10.tcvn7435-1-2004.doc": {
        "source_id": "SRC-F-15",
        "title": "TCVN 7435-1:2004 – Phòng cháy chữa cháy",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn Việt Nam 7435-1:2004 về PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/Kỹ năng PCCC hộ gia đình/Kỹ năng PCCC.docx": {
        "source_id": "SRC-F-16",
        "title": "Kỹ năng PCCC hộ gia đình",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn kỹ năng PCCC cơ bản cho hộ gia đình.",
        "doc_quality": "text",
    },

    # ── PCCC — PDF text-based (không trùng .docx) ─────────────────────
    "10 hướng dẫn về PCCC/106-npcp.signed.pdf": {
        "source_id": "SRC-F-17",
        "title": "Nghị định 106/2025/NĐ-CP về xử phạt vi phạm PCCC & CNCH",
        "module": "F",
        "url": "https://vanban.chinhphu.vn/?docid=213672&pageid=27160",
        "scope": "Xử phạt vi phạm hành chính trong lĩnh vực PCCC & CNCH.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/118.signed.pdf": {
        "source_id": "SRC-F-18",
        "title": "Văn bản pháp luật 118 (ký số)",
        "module": "F",
        "url": "",
        "scope": "Văn bản ký số liên quan PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/TCVN 3890 - 2023 (1).pdf": {
        "source_id": "SRC-F-19",
        "title": "TCVN 3890:2023 – Phương tiện PCCC cho nhà và công trình",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn trang bị phương tiện PCCC cho nhà và công trình.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/TCVN 7568 5.2025 Báo cháy mới chuẩn.pdf": {
        "source_id": "SRC-F-20",
        "title": "TCVN 7568-5:2025 – Hệ thống báo cháy",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn hệ thống báo cháy phiên bản mới 2025.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/TCVN_5507_2002-1.pdf": {
        "source_id": "SRC-F-21",
        "title": "TCVN 5507:2002 – Yêu cầu an toàn PCCC",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn yêu cầu an toàn PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/tieu-chuan-tcvn-13456-2022-phong-chay-chua-chay-phuong-tien-chieu-sang-su-co-va-chi-dan-thoat-nan-yeu-cau-thiet-ke-lap-dat.pdf": {
        "source_id": "SRC-F-22",
        "title": "TCVN 13456:2022 – Phương tiện chiếu sáng sự cố và chỉ dẫn thoát nạn",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn thiết kế lắp đặt phương tiện chiếu sáng sự cố, chỉ dẫn thoát nạn.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/-Phu luc III. Hướng dẫn chữa cháy tự động.pdf": {
        "source_id": "SRC-F-23",
        "title": "Phụ lục III – Hướng dẫn hệ thống chữa cháy tự động",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn kỹ thuật hệ thống chữa cháy tự động.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/Phu luc IV. Hướng dẫn chiếu sáng sự cố và chỉ dẫn thoát nạn.pdf": {
        "source_id": "SRC-F-24",
        "title": "Phụ lục IV – Hướng dẫn chiếu sáng sự cố và chỉ dẫn thoát nạn",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn chiếu sáng sự cố và chỉ dẫn thoát nạn theo quy chuẩn.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/-Phu luc V. Hướng dẫn hệ thống điện PCCC.pdf": {
        "source_id": "SRC-F-25",
        "title": "Phụ lục V – Hướng dẫn hệ thống điện PCCC",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn kỹ thuật hệ thống điện PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/Phụ lục I. Đối chiếu trách nhiệm người đứng đầu cơ sở (1).pdf": {
        "source_id": "SRC-F-26",
        "title": "Phụ lục I – Đối chiếu trách nhiệm người đứng đầu cơ sở",
        "module": "F",
        "url": "",
        "scope": "Bảng đối chiếu trách nhiệm PCCC của người đứng đầu cơ sở.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/1. CV 2283.PC07.PC ngày 15.12.2025 về TLG và ĐCCCC.pdf": {
        "source_id": "SRC-F-27",
        "title": "Công văn 2283/PC07 ngày 15/12/2025 về tổ liên gia và PCCC",
        "module": "F",
        "url": "",
        "scope": "Công văn hướng dẫn về tổ liên gia và đội chữa cháy cơ sở.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/1715.CAT-PC07.pdf": {
        "source_id": "SRC-F-28",
        "title": "Công văn 1715/CAT-PC07",
        "module": "F",
        "url": "",
        "scope": "Công văn Công an tỉnh – Phòng Cảnh sát PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/1640-29.01-UBND tỉnh chỉ đạo an toàn PCCC năm 2026.pdf": {
        "source_id": "SRC-F-29",
        "title": "Văn bản 1640 UBND tỉnh chỉ đạo an toàn PCCC năm 2026",
        "module": "F",
        "url": "",
        "scope": "UBND tỉnh chỉ đạo đảm bảo an toàn PCCC năm 2026.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/609 ngày 01.8.25 VB HD của CAT-PC07.PDF": {
        "source_id": "SRC-F-30",
        "title": "Văn bản 609 ngày 01/8/2025 – Hướng dẫn CAT-PC07",
        "module": "F",
        "url": "",
        "scope": "Văn bản hướng dẫn của Công an tỉnh – Phòng PC07.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/QĐ ban hành quy trình nội bộ, quy trình điện tử-hoàn chỉnh.pdf": {
        "source_id": "SRC-F-31",
        "title": "Quyết định ban hành quy trình nội bộ, quy trình điện tử PCCC",
        "module": "F",
        "url": "",
        "scope": "Quy trình nội bộ và quy trình điện tử giải quyết TTHC lĩnh vực PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/QĐ công bố TTHC-hoàn chỉnh.pdf": {
        "source_id": "SRC-F-32",
        "title": "Quyết định công bố TTHC lĩnh vực PCCC",
        "module": "F",
        "url": "",
        "scope": "Công bố danh mục TTHC lĩnh vực PCCC & CNCH.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/Kế hoạch kiểm tra PCCC năm 2026.pdf": {
        "source_id": "SRC-F-33",
        "title": "Kế hoạch kiểm tra PCCC năm 2026",
        "module": "F",
        "url": "",
        "scope": "Kế hoạch kiểm tra an toàn PCCC trên địa bàn năm 2026.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/cv 1267 hướng dẫn xây dựng mô hình to lien gia pccc.pdf": {
        "source_id": "SRC-F-34",
        "title": "Công văn 1267 hướng dẫn xây dựng mô hình tổ liên gia PCCC",
        "module": "F",
        "url": "",
        "scope": "Hướng dẫn xây dựng mô hình tổ liên gia an toàn PCCC.",
        "doc_quality": "text",
    },
    "10 hướng dẫn về PCCC/QCVN 01 2020 - Xăng dầu - xăng dầu.pdf": {
        "source_id": "SRC-F-35",
        "title": "QCVN 01:2020 – Quy chuẩn kỹ thuật quốc gia về xăng dầu",
        "module": "F",
        "url": "",
        "scope": "Quy chuẩn an toàn PCCC đối với cửa hàng kinh doanh xăng dầu.",
        "doc_quality": "text",
    },

    # ── PCCC — PDF scan (cần OCR) ──────────────────────────────────────
    "10 hướng dẫn về PCCC/TCVN 5738 scan.pdf": {
        "source_id": "SRC-F-36",
        "title": "TCVN 5738 – Hệ thống báo cháy tự động (bản scan)",
        "module": "F",
        "url": "",
        "scope": "Tiêu chuẩn hệ thống báo cháy tự động – yêu cầu kỹ thuật.",
        "doc_quality": "ocr",
    },
}

# ── Files to SKIP (duplicates hoặc .pptx) ─────────────────────────────
SKIP_FILES: dict[str, str] = {
    # .pptx — tạm loại
    "thủ tục trích lục hộ tịch.pptx":
        "PPTX tạm loại theo yêu cầu (~508 MB).",
    "10 hướng dẫn về PCCC/HƯỚNG DẪN PHIÊU_Update.pptx":
        "PPTX tạm loại theo yêu cầu.",

    # Duplicate PDFs — ưu tiên bản .docx
    "10 hướng dẫn về PCCC/105-ndcp.signed.pdf":
        "Trùng NĐ 105/2025 → ưu tiên SRC-F-06 (.docx).",
    "10 hướng dẫn về PCCC/88qh.signed.pdf":
        "Trùng Luật 55/2024 → ưu tiên SRC-F-05 (.docx).",
    "10 hướng dẫn về PCCC/88qh.signed (1).pdf":
        "Bản copy trùng 88qh.signed.pdf.",
    "10 hướng dẫn về PCCC/69_2026_ND-CP.pdf":
        "Trùng NĐ 69/2026 → ưu tiên SRC-F-07 (.docx).",
    "10 hướng dẫn về PCCC/QCVN 10-2025.pdf":
        "Trùng QCVN 10:2025 → ưu tiên SRC-F-09 (.docx).",
    "10 hướng dẫn về PCCC/Quy-chuẩn-Việt-Nam-QCVN-10-2025-BCA.pdf":
        "Trùng QCVN 10:2025 → ưu tiên SRC-F-09 (.docx).",
    "10 hướng dẫn về PCCC/Double-L-QCVN-06_2022-SUA-DOI-1_2023_BXD.pdf":
        "Trùng QCVN 06:2022 → ưu tiên SRC-F-10 (.docx).",
}
