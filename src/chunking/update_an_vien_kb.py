import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KB_PATH = REPO_ROOT / "data" / "chunks" / "kb_chunks.jsonl"

def update_kb():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    # Filter out custom chunks if re-running
    base_chunks = [c for c in chunks if not c.get("chunk_id", "").startswith("CAP-UPDATE-")]

    updated_chunks = []
    for c in base_chunks:
        cid = c.get("chunk_id", "")

        if cid == "CAP-I-079-I_DIA_CHI_CONG_AN_PHUONG":
            c["canonical_answer"] = (
                "Trụ sở Công an xã An Viễn (An Viên) tọa lạc tại: Ấp Phát Đạt, xã An Viễn, thành phố Đồng Nai (tỉnh Đồng Nai).\n"
                "Thời gian tiếp công dân giải quyết thủ tục hành chính:\n"
                "- Buổi sáng: 07h00 - 11h30\n"
                "- Buổi chiều: 13h30 - 17h00 (từ thứ 2 đến thứ 6).\n"
                "Tiếp nhận tin báo, vụ việc an ninh trật tự: 24/7 tất cả các ngày trong tuần (kể cả Lễ, Tết)."
            )
            c["question_variants"].extend([
                "Địa chỉ Công an xã An Viên ở đâu?",
                "Địa chỉ Công an xã An Viễn ở đâu?",
                "Trụ sở Công an xã An Viên nằm ở đâu?",
                "Công an xã An Viên ở ấp nào?",
                "Địa chỉ công an an viên",
                "dia chi cong an xa an vien",
                "ca xa an vien o dau",
                "tru so ca an vien o dau",
                "cong an an vien nam o dau"
            ])
            c["source_ids"] = ["SRC-UPDATE-01", "SRC-AV-01", "SRC-I-01"]

        elif cid == "CAP-I-080-I_SO_DIEN_THOAI_TRUC_BAN":
            c["canonical_answer"] = (
                "Số điện thoại trực ban chính thức của Công an xã An Viễn (An Viên): 02513.538.187 (tiếp nhận 24/7).\n\n"
                "Danh bạ Ban Chỉ huy và cán bộ phụ trách Công an xã An Viễn:\n"
                "1. Thượng tá Trần Thị Minh Huệ - Trưởng Công an xã (Phụ trách chung): 0908.304.266\n"
                "2. Trung tá Nguyễn Viết Cường – Phó Trưởng Công an xã (Tổ Tổng hợp): 0915.559.645\n"
                "3. Trung tá Hoàng Chiến Thắng – Phó Trưởng Công an xã (Tổ Trật tự): 0909.542.599\n"
                "4. Trung tá Nguyễn Văn Viên – Phó Trưởng Công an xã (Tổ Phòng chống tội phạm): 0989.325.325\n"
                "5. Trung tá Phạm Tiến Dũng – Phó Trưởng Công an xã (Tổ An ninh): 0914.728.779\n"
                "6. Thiếu tá Nguyễn Thế Lam – Phó Trưởng Công an xã (Tổ Khu vực): 0983.137.968\n"
                "7. Đại úy Nguyễn Văn Định – Cảnh sát khu vực ấp An Phú: 0903.060.308\n"
                "8. Thượng úy Hà Văn Bằng – Cảnh sát khu vực ấp An Phú: 0372.170.117\n"
                "9. Đại úy Phạm Lê Minh – Cảnh sát khu vực ấp Phát Đạt: 0973.520.521\n"
                "10. Thiếu tá Vũ Văn Mong – Cảnh sát khu vực ấp Hưng Thịnh: 0937.813.979\n"
                "11. Đại úy Bùi Thị Thương – Cán bộ tiếp nhận cư trú & dữ liệu dân cư: 0789.310.928\n"
                "12. Đại úy Lê Đình Quý – Cán bộ tiếp nhận cư trú & dữ liệu dân cư: 0783.404.383\n"
                "13. Đại úy Trần Hữu Trang – Cán bộ đăng ký xe: 0908.066.600\n"
                "14. Trung tá Lê Văn Phong – Cán bộ PCCC: 0918.550.798\n"
                "15. Trung tá Bùi Phương Định – Cán bộ tạm trú người nước ngoài: 0913.399.438\n"
                "16. Thượng úy Phạm Xuân Sang – Cán bộ tuyển sinh & nghĩa vụ CAND: 0989.327.407"
            )
            c["question_variants"].extend([
                "số điện thoại công an xã an viên là số mấy",
                "số điện thoại công an xã an viên",
                "số điện thoại công an xã an viễn",
                "sđt công an xã an viên",
                "sdt ca xa an vien",
                "cho tôi số điện thoại công an xã an viên",
                "số trực ban công an xã an viên",
                "số điện thoại trực ban công an an viên",
                "so dien thoai cong an xa an vien la so may",
                "danh bạ số điện thoại công an xã an viên",
                "danh sách số điện thoại cán bộ công an xã an viên",
                "so dien thoai ca xa an vien",
                "sdt truc ban an vien",
                "sdt ca xa an vien so may",
                "sdt truc ban ca xa an vien"
            ])
            c["source_ids"] = ["SRC-UPDATE-01", "SRC-AV-01", "SRC-I-01"]

        elif cid == "CAP-I-081-I_GIO_LAM_VIEC":
            c["canonical_answer"] = (
                "Thời gian làm việc giải quyết thủ tục hành chính tại Công an xã An Viễn (An Viên):\n"
                "- Buổi sáng: Từ 07h00 đến 11h30\n"
                "- Buổi chiều: Từ 13h30 đến 17h00\n"
                "(Làm việc từ thứ 2 đến thứ 6 hàng tuần, thứ 7 và Chủ nhật nghỉ giải quyết TTHC).\n"
                "Riêng công tác tiếp nhận tin báo, tố giác tội phạm và tình hình an ninh trật tự: Phục vụ 24/7 tất cả các ngày trong tuần (kể cả thứ 7, Chủ nhật, Lễ, Tết)."
            )
            c["question_variants"].extend([
                "Giờ làm việc của Công an xã An Viên",
                "Công an xã An Viên làm việc từ mấy giờ đến mấy giờ",
                "Công an xã An Viễn có làm việc thứ 7 không",
                "Lịch làm việc của công an an viên",
                "ca xa an vien co lam t7 ko",
                "cong an xa an vien co lam thu 7 ko",
                "gio lam viec ca an vien",
                "ca an vien tiep dan luc nao"
            ])
            c["source_ids"] = ["SRC-UPDATE-01", "SRC-AV-01", "SRC-I-01"]

        elif cid == "CAP-I-082-I_LICH_TIEP_DAN":
            c["canonical_answer"] = (
                "Lịch tiếp công dân của Công an xã An Viễn (An Viên):\n"
                "- Công an xã duy trì mô hình “Buổi sáng với Nhân dân” vào các buổi sáng trong giờ hành chính tất cả các ngày làm việc trong tuần (từ thứ 2 đến thứ 6).\n"
                "- Đồng chí Thượng tá Trần Thị Minh Huệ - Trưởng Công an xã (SĐT: 0908.304.266) trực tiếp tiếp công dân vào lúc 08h00 thứ 5 hằng tuần tại trụ sở Công an xã (Ấp Phát Đạt, xã An Viễn)."
            )
            c["question_variants"].extend([
                "Lịch tiếp dân của Công an xã An Viên",
                "Lịch tiếp công dân của Trưởng Công an xã An Viên",
                "Trưởng Công an xã An Viễn tiếp dân vào thứ mấy",
                "Buổi sáng với nhân dân công an an viên",
                "truong ca tiep dan thu may",
                "truong cong an xa an vien tiep dan khi nao",
                "lich tiep dan ca an vien",
                "truong ca an vien tiep dan luc nao"
            ])
            c["source_ids"] = ["SRC-UPDATE-01", "SRC-AV-01", "SRC-I-01"]

        elif cid == "CAP-I-083-I_CAN_BO_PHU_TRACH_LINH_VUC":
            c["canonical_answer"] = (
                "Danh bạ cán bộ phụ trách các lĩnh vực cụ thể tại Công an xã An Viễn (An Viên):\n\n"
                "1. Ban Chỉ huy Công an xã:\n"
                "- Thượng tá Trần Thị Minh Huệ - Trưởng Công an xã (Phụ trách chung): 0908.304.266\n"
                "- Trung tá Nguyễn Viết Cường – Phó Trưởng Công an xã (Tổ Tổng hợp): 0915.559.645\n"
                "- Trung tá Hoàng Chiến Thắng – Phó Trưởng Công an xã (Tổ Trật tự): 0909.542.599\n"
                "- Trung tá Nguyễn Văn Viên – Phó Trưởng Công an xã (Tổ PCTP): 0989.325.325\n"
                "- Trung tá Phạm Tiến Dũng – Phó Trưởng Công an xã (Tổ An ninh): 0914.728.779\n"
                "- Thiếu tá Nguyễn Thế Lam – Phó Trưởng Công an xã (Tổ Khu vực): 0983.137.968\n\n"
                "2. Cảnh sát khu vực phụ trách các ấp:\n"
                "- Ấp An Phú: Đại úy Nguyễn Văn Định (0903.060.308) và Thượng úy Hà Văn Bằng (0372.170.117)\n"
                "- Ấp Phát Đạt: Đại úy Phạm Lê Minh (0973.520.521)\n"
                "- Ấp Hưng Thịnh: Thiếu tá Vũ Văn Mong (0937.813.979)\n\n"
                "3. Cán bộ phụ trách nghiệp vụ & TTHC:\n"
                "- Cán bộ đăng ký xe: Đại úy Trần Hữu Trang (0908.066.600)\n"
                "- Cán bộ cư trú & Dữ liệu dân cư: Đại úy Bùi Thị Thương (0789.310.928) và Đại úy Lê Đình Quý (0783.404.383)\n"
                "- Cán bộ phòng cháy chữa cháy (PCCC): Trung tá Lê Văn Phong (0918.550.798)\n"
                "- Cán bộ tạm trú người nước ngoài: Trung tá Bùi Phương Định (0913.399.438)\n"
                "- Cán bộ tuyển sinh CAND & Nghĩa vụ CAND: Thượng úy Phạm Xuân Sang (0989.327.407)"
            )
            c["question_variants"].extend([
                "Ai là cán bộ đăng ký xe công an xã an viên?",
                "Cảnh sát khu vực ấp An Phú công an an viên là ai số điện thoại nào?",
                "Cảnh sát khu vực ấp Phát Đạt là ai?",
                "Cảnh sát khu vực ấp Hưng Thịnh là ai?",
                "Ai phụ trách làm hộ khẩu cư trú ở công an an viên?",
                "Ai phụ trách phòng cháy chữa cháy ở công an an viên?",
                "Trưởng công an xã an viên là ai số mấy?",
                "Danh bạ cán bộ công an xã an viên",
                "sdt can bo dang ki xe an vien la ai zay",
                "sdt can bo dang ky xe an vien",
                "can bo dang ki xe xa an vien sdt may",
                "sdt dang ky xe cong an an vien",
                "ai dang ky xe o ca an vien",
                "cho hoi cskv ap hung thinh la a nao, co sdt ko",
                "cskv ap an phu la ai",
                "cskv ap phat dat sdt",
                "cskv ap hung thinh sdt",
                "so dt can bo dang ki xe an vien"
            ])
            c["source_ids"] = ["SRC-UPDATE-01", "SRC-AV-01", "SRC-I-01"]

        updated_chunks.append(c)

    # Dedicated KB chunks
    extra_chunks = [
        {
            "chunk_id": "CAP-UPDATE-001-NGHIA_VU_CAND",
            "module": "UPDATE - Tuyển Chọn Nghĩa Vụ CAND",
            "intent_code": "UPDATE_NGHIA_VU_CAND",
            "retrieval_title": "Tuyển chọn công dân thực hiện nghĩa vụ tham gia Công an nhân dân tại xã An Viễn",
            "last_verified": "2026-08-01",
            "question_variants": [
                "Thủ tục tuyển nghĩa vụ công an nhân dân tại xã An Viên",
                "Tuyển chọn công dân thực hiện nghĩa vụ tham gia CAND xã An Viễn",
                "Đi nghĩa vụ công an cần tiêu chuẩn gì ở An Viên",
                "Độ tuổi đi nghĩa vụ công an nhân dân",
                "Tiêu chuẩn sức khỏe đi nghĩa vụ công an",
                "Hồ sơ đăng ký nghĩa vụ CAND gồm những gì",
                "Ai phụ trách tuyển nghĩa vụ CAND công an xã an viên",
                "em sinh 2003 can 2 do co di nghia vu cong an an vien dc ko",
                "can 2 do co di nghia vu cong an dc ko",
                "can thi co di nghia vu cand duoc khong",
                "tieu chuan di nghia vu cong an an vien",
                "ho so di nghia vu ca xa an vien"
            ],
            "canonical_answer": (
                "Thông tin tuyển chọn công dân thực hiện nghĩa vụ tham gia CAND tại xã An Viễn:\n"
                "1. Độ tuổi: Từ đủ 18 đến hết 25 tuổi (công dân đã tốt nghiệp CĐ/ĐH được tạm hoãn gọi nhập ngũ thì tuyển chọn đến hết 27 tuổi).\n"
                "2. Tiêu chuẩn sức khỏe: Phân loại sức khỏe loại 1, 2, 3; Nam cao từ 1m64 trở lên, nặng từ 47kg trở lên; Nữ cao từ 1m58 trở lên, nặng từ 45kg trở lên; Tật khúc xạ mắt không quá 3 đi-ốp (cận 2 độ vẫn đủ điều kiện nếu cam kết điều trị khi có yêu cầu).\n"
                "3. Thời gian thực hiện: 24 tháng.\n"
                "4. Hồ sơ dự tuyển: Tờ khai đăng ký (Mẫu NĐ 184/2025/NĐ-CP), Giấy đăng ký NVQS, bản sao Giấy khai sinh, bằng cấp THPT/CĐ/ĐH, CCCD, 04 ảnh 3x4.\n"
                "5. Cán bộ phụ trách: Thượng úy Phạm Xuân Sang (SĐT: 0989.327.407) - Công an xã An Viễn."
            ),
            "required_entities": "họ tên, độ tuổi, trình độ học vấn, tình trạng sức khỏe",
            "clarifying_question_if_missing": "Anh/chị vui lòng cho biết năm sinh, trình độ học vấn và chiều cao cân nặng để được tư vấn điều kiện cụ thể ạ.",
            "handoff_or_emergency_rule": "Liên hệ Thượng úy Phạm Xuân Sang - 0989.327.407 để được hướng dẫn nộp hồ sơ trực tiếp.",
            "legal_basis": "Nghị định 70/2019/NĐ-CP; Thông tư 62/2023/TT-BCA; Thông tư 131/2025/TT-BCA; Nghị định 184/2025/NĐ-CP.",
            "group_legal_basis": "Văn bản quy định về tuyển chọn thực hiện nghĩa vụ tham gia CAND.",
            "guardrail": "Hướng dẫn đúng tiêu chuẩn độ tuổi, sức khỏe, không kết luận thay Hội đồng khám tuyển.",
            "source_ids": ["SRC-UPDATE-01"],
            "tags": ["nghia-vu-cand", "tuyen-chon-cong-an", "an-vien", "suc-khoe-nghia-vu"]
        },
        {
            "chunk_id": "CAP-UPDATE-002-TUYEN_SINH_CAND",
            "module": "UPDATE - Tuyển Sinh Các Trường CAND",
            "intent_code": "UPDATE_TUYEN_SINH_CAND",
            "retrieval_title": "Tuyển sinh các trường Công an nhân dân tại xã An Viễn",
            "last_verified": "2026-08-01",
            "question_variants": [
                "Thông tin tuyển sinh các trường công an nhân dân tại xã An Viên",
                "Đăng ký thi đại học công an tại xã An Viễn",
                "Hồ sơ đăng ký sơ tuyển công an nhân dân",
                "Tuyển sinh văn bằng 2 công an nhân dân",
                "Tiêu chuẩn chiều cao học lực thi trường công an",
                "Địa điểm đăng ký thi trường công an xã an viên",
                "hoc xong dh muon thi vb2 cong an o an vien thi nop ho so the nao",
                "thi vb2 cong an nop ho so o dau an vien",
                "hoc dai hoc xong thi van bang 2 cong an duoc khong",
                "tuyen sinh vb2 cong an an vien"
            ],
            "canonical_answer": (
                "Thông tin tuyển sinh các trường CAND tại Công an xã An Viễn:\n"
                "1. Đối tượng: Chiến sĩ nghĩa vụ xuất ngũ trong vòng 12 tháng hoặc công dân thường trú tại xã An Viễn (không quá 22 tuổi, dân tộc thiểu số không quá 25 tuổi). Đối với Văn bằng 2 (VB2CA): Tuyển công dân đã tốt nghiệp đại học trở lên.\n"
                "2. Hệ đào tạo: Đại học chính quy tuyển mới, Văn bằng 2 (VB2CA), Trung cấp chính quy (T08, T10).\n"
                "3. Tiêu chuẩn: Học lực THPT Khá trở lên; Từng môn trong tổ hợp đạt từ 7.0 điểm trở lên (người dân tộc thiểu số từ 6.5 trở lên); Nam cao 164-195cm, Nữ cao 158-180cm; Cận/viễn không quá 3 đi-ốp.\n"
                "4. Hồ sơ khi đến đăng ký: CCCD, Giấy khai sinh, Học bạ THPT, Bằng tốt nghiệp THPT/Đại học (hoặc Quyết định xuất ngũ).\n"
                "5. Địa điểm & Liên hệ: Trụ sở Công an xã An Viễn (Ấp Phát Đạt, xã An Viễn) - SĐT: 02513.538.187 hoặc 0989.327.407 (Thượng úy Phạm Xuân Sang).\n"
                "6. Lộ trình thi máy tính: Triển khai thi trên máy tính cho Văn bằng 2 từ năm 2026; thí điểm đại học chính quy từ 2027 và toàn diện từ 2028."
            ),
            "required_entities": "năm sinh, hệ đào tạo muốn thi (Đại học/VB2/Trung cấp), học lực THPT, chiều cao",
            "clarifying_question_if_missing": "Anh/chị muốn đăng ký dự tuyển hệ Đại học chính quy mới tốt nghiệp THPT, Văn bằng 2 hay Trung cấp CAND ạ?",
            "handoff_or_emergency_rule": "Đến trực tiếp Công an xã An Viễn gặp Thượng úy Phạm Xuân Sang (0989.327.407) để nhận hồ sơ sơ tuyển.",
            "legal_basis": "Hướng dẫn tuyển sinh CAND hằng năm của Bộ Công an.",
            "group_legal_basis": "Quy chế tuyển sinh các trường Công an nhân dân.",
            "guardrail": "Cung cấp đúng đối tượng, tiêu chuẩn sơ tuyển; thông báo chủ trương thi trên máy tính.",
            "source_ids": ["SRC-UPDATE-01"],
            "tags": ["tuyen-sinh-cand", "dai-hoc-cong-an", "van-bang-2-cong-an", "an-vien"]
        }
    ]

    updated_chunks.extend(extra_chunks)

    with open(KB_PATH, "w", encoding="utf-8") as f:
        for c in updated_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"Successfully updated {len(updated_chunks)} KB chunks!")

if __name__ == "__main__":
    update_kb()
