import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


from google import genai
from src.retrieval.query import answer

PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-flash-latest", "gemini-3.7-flash"]
_client = None
_system_prompt = None

def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        _client = genai.Client(api_key=api_key)
    return _client

def _get_system_prompt():
    global _system_prompt
    if _system_prompt is None:
        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            _system_prompt = f.read()
    return _system_prompt

def get_llm_response(query, context, need_web_search=False, history=None):
    client = _get_client()
    system_prompt = _get_system_prompt()

    history_str = ""
    if history:
        history_lines = []
        for msg in history:
            role_name = "Người dân" if msg.get("role") == "user" else "Chatbot"
            history_lines.append(f"{role_name}: {msg.get('text', '')}")
        if history_lines:
            history_str = "\n=== LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ ===\n" + "\n".join(history_lines) + "\n=================================\n"

    prompt = f"""{system_prompt}
{history_str}
=== TÀI LIỆU THAM KHẢO TỪ CSDL NỘI BỘ ===
{context}
=====================================

Câu hỏi hiện tại của người dân: "{query}"

LƯU Ý BẮT BUỘC KHI TRẢ LỜI:
- Bạn là Trợ lý Pháp lý của Công an xã An Viễn. Hãy xưng hô lịch sự, thân thiện (Công an xã An Viễn / Tôi và Anh/chị).
- Trả lời dựa trên tài liệu tham khảo ở trên.
- TUYỆT ĐỐI KHÔNG xuất ra các nhãn kỹ thuật thô như 'CLARIFYING_QUESTION_IF_MISSING:', 'HANDOFF_OR_EMERGENCY_RULE:', 'GUARDRAIL:', 'REQUIRED_ENTITIES:', '[matched: ...]'. Hãy diễn đạt nội dung một cách tự nhiên, mạch lạc, dễ hiểu.
"""

    if need_web_search:
        prompt_with_search = prompt + """
Một số phần của câu hỏi KHÔNG CÓ trong CSDL nội bộ.
Hãy sử dụng công cụ Search để tìm kiếm trên Internet phần thông tin còn thiếu.
Nhắc nhở người dân rằng thông tin từ Internet có thể khác thực tế tại địa phương.
"""
        config = genai.types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
        for model_name in FALLBACK_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_with_search,
                    config=config,
                )
                if response and response.text:
                    return response.text
            except Exception:
                # Fallback sang model khác hoặc chế độ prompt thường
                continue

    import time
    last_err = ""
    for model_name in FALLBACK_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_err = str(e)
                if any(k in last_err for k in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"]):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break  # thử model tiếp theo nếu lỗi không thể retry

    return f"Hệ thống đang bảo trì hoặc quá tải tạm thời (503/429), vui lòng thử lại sau giây lát. ({last_err[:100]})"

def process_query(user_input):
    ctx = answer(user_input)
    need_web_search = ctx.startswith("Xin lỗi, mình chưa tìm được thông tin")
    return get_llm_response(user_input, ctx, need_web_search=need_web_search)

def chat():
    while True:
        try:
            user_input = input("Người dân: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue
            reply = process_query(user_input)
            print(f"Chatbot:\n{reply}\n")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    chat()
