from flask import Flask, render_template, request, Response, jsonify
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generation.chatbot import get_llm_response
from src.generation.session_manager import session_manager
from src.retrieval.query import answer

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session")

    if not user_input:
        return Response("data: {}\n\n", mimetype="text/event-stream")

    def generate():
        def send_event(status, message, is_final=False):
            event_data = {
                "status": status,
                "message": message,
                "is_final": is_final
            }
            return f"data: {json.dumps(event_data)}\n\n"

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

        # Gọi LLM sinh phản hồi với ngữ cảnh đa lượt
        llm_reply = get_llm_response(
            query=user_input,
            context=ctx,
            need_web_search=need_web_search,
            history=history
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
    app.run(host="127.0.0.1", port=5000, debug=True)

