import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv(os.path.join(os.path.dirname(__file__), "src", "generation", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Đọc API key mặc định từ Streamlit Secrets hoặc .env
DEFAULT_API_KEY = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass
if not DEFAULT_API_KEY:
    DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

from src.generation.chatbot import get_llm_response
from src.retrieval.query import answer

# ========================
# CẤU HÌNH TRANG STREAMLIT
# ========================
st.set_page_config(
    page_title="Chatbot Hỗ Trợ Thủ Tục CA Xã An Viễn",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy biến giao diện CSS
st.markdown("""
<style>
    .main-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0b5394;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #475569;
        margin-bottom: 1rem;
    }
    .emergency-box {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #991b1b;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# RATE LIMITER (In-Memory)
# ========================
_RATE_LIMIT_REQUESTS = 5   # tối đa 5 req
_RATE_LIMIT_WINDOW = 60    # trong 60 giây

if "rate_log" not in st.session_state:
    st.session_state.rate_log = []

def is_rate_limited() -> bool:
    now = time.time()
    st.session_state.rate_log = [t for t in st.session_state.rate_log if now - t < _RATE_LIMIT_WINDOW]
    if len(st.session_state.rate_log) >= _RATE_LIMIT_REQUESTS:
        return True
    st.session_state.rate_log.append(now)
    return False

# ========================
# SESSION STATE (Lịch sử chat)
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Xin chào anh/chị! Tôi là hệ thống **Trợ lý Pháp lý của Công an xã An Viễn**. Anh/chị cần hỗ trợ thủ tục gì hôm nay?"
        }
    ]

if "llm_history" not in st.session_state:
    st.session_state.llm_history = []

# ========================
# SIDEBAR QUẢN LÝ
# ========================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Emblem_of_Vietnam.svg/200px-Emblem_of_Vietnam.svg.png", width=70)
    st.markdown("### 🛡️ CA XÃ AN VIÊN")
    st.caption("Trực ban 24/7: **02513.538.187**  \nĐịa chỉ: Ấp Phát Đạt, xã An Viễn")
    
    st.divider()

    st.markdown("#### 🔑 Cấu hình Gemini API Key")
    user_api_key = st.text_input(
        "API Key cá nhân (tùy chọn):",
        type="password",
        placeholder="Dán AIzaSy... (nếu có)",
        help="Nếu không nhập, hệ thống sẽ dùng Key mặc định (giới hạn 5 câu hỏi/phút)."
    )

    if user_api_key.strip():
        st.success("✅ Đang dùng: **Key cá nhân** (Không bị giới hạn lượt)")
    else:
        st.info("ℹ️ Đang dùng: **Key hệ thống** (Tối đa 5 lượt/phút)")

    st.markdown("""
    <small>
    💡 <i>Lấy API Key miễn phí tại:</i><br>
    👉 <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>
    </small>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("➕ Bắt đầu đoạn chat mới", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Đã bắt đầu đoạn chat mới. Anh/chị cần hỗ trợ thủ tục gì hôm nay?"
            }
        ]
        st.session_state.llm_history = []
        st.rerun()

    st.markdown("""
    ---
    **📞 Đường dây nóng:**
    - 🚨 **113**: An ninh trật tự
    - 🚒 **114**: Cháy nổ / Cứu nạn
    - 🚑 **115**: Cấp cứu y tế
    """)

# ========================
# KHUNG CHAT CHÍNH
# ========================
st.markdown('<div class="main-header">HỆ THỐNG HỖ TRỢ THỦ TỤC HÀNH CHÍNH & ANTT</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Công an xã An Viễn • Tư vấn trực tuyến 24/7</div>', unsafe_allow_html=True)

# Hiển thị toàn bộ tin nhắn đã có
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Xử lý khi người dùng gửi câu hỏi
user_input = st.chat_input("Nhập câu hỏi của anh/chị tại đây...")

if user_input:
    # 1. Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Kiểm tra Rate Limit nếu không dùng key riêng
    effective_api_key = user_api_key.strip()
    if not effective_api_key and is_rate_limited():
        warning_msg = (
            "⚠️ **Hệ thống đang quá tải**, vui lòng chờ 1 phút rồi thử lại.  \n"
            "Hoặc anh/chị có thể nhập **Gemini API Key riêng** ở thanh bên trái để tiếp tục nhắn tin không giới hạn."
        )
        st.session_state.messages.append({"role": "assistant", "content": warning_msg})
        with st.chat_message("assistant"):
            st.warning(warning_msg)
    else:
        # 3. Tiến hành xử lý RAG
        with st.chat_message("assistant"):
            with st.status("🔍 Đang xử lý câu hỏi...", expanded=True) as status_box:
                status_box.write("📚 Đang tra cứu cơ sở dữ liệu nội bộ...")
                ctx = answer(user_input)

                need_web_search = ctx.startswith("Xin lỗi, mình chưa tìm được thông tin")
                if need_web_search:
                    status_box.write("🌐 Không thấy trong CSDL nội bộ. Đang tra cứu thông tin trực tuyến...")
                else:
                    status_box.write("✅ Đã tìm thấy tài liệu quy định. Đang tổng hợp câu trả lời...")

                # Chuẩn bị lịch sử
                history_for_llm = st.session_state.llm_history

                # Lưu câu hỏi vào session history
                st.session_state.llm_history.append({"role": "user", "text": user_input})

                # Sinh phản hồi từ LLM
                response_text = get_llm_response(
                    query=user_input,
                    context=ctx,
                    need_web_search=need_web_search,
                    history=history_for_llm,
                    api_key_override=effective_api_key or None
                )

                # Cập nhật đường dẫn ảnh cục bộ nếu có
                if "/static/images/QR-dich-vu-cong.png" in response_text:
                    qr_local_url = "https://raw.githubusercontent.com/mizzhau/ChatBot-CA-AnVien/main/app/static/images/QR-dich-vu-cong.png"
                    response_text = response_text.replace("/static/images/QR-dich-vu-cong.png", qr_local_url)

                # Lưu câu trả lời của bot vào session history
                st.session_state.llm_history.append({"role": "bot", "text": response_text})
                status_box.update(label="✨ Đã hoàn thành!", state="complete", expanded=False)

            st.markdown(response_text, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
