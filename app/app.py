from flask import Flask, render_template, request, Response
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.generation.chatbot import get_llm_response
from src.retrieval.query import answer

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

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

        llm_reply = get_llm_response(user_input, ctx, need_web_search=need_web_search)

        yield send_event("done", llm_reply, is_final=True)

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
