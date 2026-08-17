from flask import Flask, render_template, request, Response, jsonify
import json
import sys
import os
import time
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generation.chatbot import get_llm_response
from src.generation.session_manager import session_manager
from src.retrieval.query import answer

app = Flask(__name__)

# ========================
# RATE LIMITER (key mặc định)
# ========================
_RATE_LIMIT_REQUESTS = 5   # request tối đa
_RATE_LIMIT_WINDOW  = 60   # trong 60 giây
_rate_log = defaultdict(list)

def _is_rate_limited(ip: str) -> bool:
    """Trả về True nếu IP này đã vượt rate limit (chỉ áp dụng khi dùng key mặc định)."""
    now = time.time()
    _rate_log[ip] = [t for t in _rate_log[ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_log[ip]) >= _RATE_LIMIT_REQUESTS:
        return True
    _rate_log[ip].append(now)
    return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session")
    user_api_key = data.get("api_key", "").strip()  # Key do người dùng cung cấp

    if not user_input:
        return Response("data: {}\n\n", mimetype="text/event-stream")

    # --- Rate limiting: chỉ áp dụng khi dùng key mặc định ---
    if not user_api_key:
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
        if _is_rate_limited(client_ip):
            def rate_limited_response():
                event_data = {
                    "status": "rate_limited",
                    "message": (
                        "Hệ thống đang quá tải, vui lòng chờ 1 phút rồi thử lại. "
                        "Hoặc nhập API Key riêng của anh/chị để tiếp tục ngay."
                    ),
                    "is_final": True,
                    "show_api_key_prompt": True
                }
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            return Response(rate_limited_response(), mimetype="text/event-stream")

    def generate():
        def send_event(status, message, is_final=False, extra=None):
            event_data = {"status": status, "message": message, "is_final": is_final}
            if extra:
                event_data.update(extra)
            return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        yield send_event("searching", "Đang tra cứu CSDL nội bộ...")
        ctx = answer(user_input)

        need_web_search = ctx.startswith("Xin lỗi, mình chưa tìm được thông tin")

        if need_web_search:
            yield send_event("web_search", "Không tìm thấy trong CSDL. Đang tra cứu Google...")
        else:
            yield send_event("found", "Đã tìm thấy tài liệu. Đang tổng hợp câu trả lời...")

        # Lấy lịch sử hội thoại trước đó của user
        history = session_manager.get_history(session_id)

        # Lưu câu hỏi của người dùng vào session
        session_manager.add_message(session_id, "user", user_input)

        # Gọi LLM — dùng key của user nếu có, ngược lại dùng key mặc định
        llm_reply = get_llm_response(
            query=user_input,
            context=ctx,
            need_web_search=need_web_search,
            history=history,
            api_key_override=user_api_key or None
        )

        # Lưu câu trả lời của bot vào session
        session_manager.add_message(session_id, "bot", llm_reply)

        yield send_event("done", llm_reply, is_final=True)

    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/chat/new", methods=["POST"])
def new_chat():
    """Archive session hiện tại (giữ lại) và trả về thông báo thành công."""
    data = request.json or {}
    old_session_id = data.get("session_id")
    if old_session_id:
        session_manager.archive_session(old_session_id)
    return jsonify({"status": "success", "message": "Đã lưu và tạo đoạn chat mới."})

@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """Liệt kê tất cả các phiên chat đã lưu."""
    sessions = session_manager.list_sessions()
    return jsonify({"sessions": sessions})

@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """Lấy toàn bộ tin nhắn của một session cụ thể để hiển thị lại trên UI."""
    messages = session_manager.get_full_messages(session_id)
    if not messages:
        return jsonify({"error": "Không tìm thấy phiên trò chuyện."}), 404
    return jsonify({"session_id": session_id, "messages": messages})

@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Xóa hẳn một session khi người dùng chọn xóa."""
    session_manager.delete_session(session_id)
    return jsonify({"status": "success", "message": "Đã xóa phiên trò chuyện."})

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Dang khoi dong va preload model...")
    from src.embedding.embedder import get_model
    get_model()  # Preload model vào RAM
    print(f"[*] Server chatbot san sang tai http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


