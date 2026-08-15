import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


from google import genai
from src.retrieval.query import answer

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
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

def get_llm_response(query, context, need_web_search=False):
    client = _get_client()
    system_prompt = _get_system_prompt()

    prompt = f"""{system_prompt}

=== TÀI LIỆU THAM KHẢO TỪ CSDL NỘI BỘ ===
{context}
=====================================

Câu hỏi của người dân: "{query}"

Hãy trả lời dựa trên tài liệu nội bộ ở trên. Bỏ qua mọi thông tin kỹ thuật như [matched: ...] hoặc [sim=...].
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
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt_with_search,
                config=config,
            )
            return response.text
        except Exception:
            # Fallback nếu Google Search tool gặp sự cố hoặc giới hạn quota
            pass

    import time
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < 2:
                    time.sleep(3)
                    continue
            return f"Lỗi khi gọi LLM: {str(e)}"
    return "Hệ thống đang bận, vui lòng thử lại sau giây lát."

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
