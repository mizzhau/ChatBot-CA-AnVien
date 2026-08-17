import sys
import os
import re
import time
import random
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from google import genai
from src.retrieval.query import answer

logger = logging.getLogger(__name__)

PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
# Fallback chain: model chính → lite (nhẹ, ít bị rate limit) → flash-latest
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite", "gemini-flash-latest"]
_client = None
_system_prompt = None

# Các nhãn kỹ thuật cần loại bỏ khỏi output LLM (phòng ngừa)
_TECHNICAL_LABELS = re.compile(
    r'(?:^|\n)\s*\*?\*?\s*'
    r'(?:CLARIFYING_QUESTION_IF_MISSING|HANDOFF_OR_EMERGENCY_RULE|'
    r'GUARDRAIL|REQUIRED_ENTITIES|CANONICAL_ANSWER|'
    r'LEGAL_BASIS|GROUP_LEGAL_BASIS|INTENT_CODE|RETRIEVAL_TITLE)'
    r'\s*:?\s*',
    re.IGNORECASE
)
_MATCHED_DEBUG = re.compile(r'\[matched:.*?\]', re.IGNORECASE)


def _sanitize_response(text: str) -> str:
    """Loại bỏ các nhãn kỹ thuật còn sót trong output LLM (lớp phòng ngừa cuối)."""
    if not text:
        return text
    # Xóa debug tag [matched: ...]
    text = _MATCHED_DEBUG.sub('', text)
    # Xóa nhãn kỹ thuật thô
    text = _TECHNICAL_LABELS.sub('\n', text)
    # Dọn dẹp khoảng trắng thừa
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

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

def _call_gemini_with_retry(client, model_list, contents, config=None, max_attempts=3):
    """
    Gọi Gemini API với exponential backoff + jitter, thử qua danh sách model fallback.
    Trả về response.text hoặc raise Exception nếu tất cả đều thất bại.
    """
    last_err = ""
    retryable_keywords = ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "DEADLINE_EXCEEDED"]

    for model_name in model_list:
        for attempt in range(max_attempts):
            try:
                kwargs = {"model": model_name, "contents": contents}
                if config:
                    kwargs["config"] = config
                response = client.models.generate_content(**kwargs)
                if response and response.text:
                    return response.text
                # Response rỗng — thử lại
                logger.warning(f"[RETRY] Model {model_name} trả response rỗng (attempt {attempt+1})")
            except Exception as e:
                last_err = str(e)
                logger.warning(f"[RETRY] Model {model_name} lỗi (attempt {attempt+1}): {last_err[:120]}")
                if any(k in last_err for k in retryable_keywords):
                    # Exponential backoff: 1s, 2s, 4s + jitter ngẫu nhiên
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"[RETRY] Chờ {delay:.1f}s trước khi thử lại...")
                    time.sleep(delay)
                    continue
                # Lỗi không thể retry (ví dụ: invalid API key) → thử model tiếp
                break

    return None, last_err


def get_llm_response(query, context, need_web_search=False, history=None, api_key_override=None):
    # Nếu user cung cấp key riêng → tạo client riêng với key của họ (quota độc lập)
    if api_key_override:
        client = genai.Client(api_key=api_key_override)
        logger.info("[API-KEY] Dùng key do người dùng cung cấp.")
    else:
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
- TUYỆT ĐỐI KHÔNG được xuất ra bất kỳ nhãn kỹ thuật nào. Tất cả nội dung phải được diễn đạt tự nhiên, mạch lạc, dễ hiểu cho người dân.
- Phần "Gợi ý câu hỏi làm rõ" trong tài liệu: hãy biến nó thành câu hỏi tự nhiên nếu thấy cần thiết, hoặc bỏ qua nếu câu hỏi đã rõ ràng.
- Phần "Lưu ý chuyển tiếp" trong tài liệu: hãy diễn đạt thành lời khuyên tự nhiên cho người dân.
- Phần "Quy tắc an toàn" trong tài liệu: tuân thủ nhưng KHÔNG hiển thị cho người dân.
"""

    # --- Thử web search nếu cần ---
    if need_web_search:
        prompt_with_search = prompt + """
Một số phần của câu hỏi KHÔNG CÓ trong CSDL nội bộ.
Hãy sử dụng công cụ Search để tìm kiếm trên Internet phần thông tin còn thiếu.
Nhắc nhở người dân rằng thông tin từ Internet có thể khác thực tế tại địa phương.
"""
        config = genai.types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
        result = _call_gemini_with_retry(client, FALLBACK_MODELS, prompt_with_search, config=config)
        if isinstance(result, str):
            return _sanitize_response(result)

    # --- Gọi LLM thường ---
    result = _call_gemini_with_retry(client, FALLBACK_MODELS, prompt)
    if isinstance(result, str):
        return _sanitize_response(result)

    # Tất cả đều thất bại
    _, last_err = result if isinstance(result, tuple) else ("", "Unknown error")
    return ("Hệ thống đang bận, vui lòng thử lại sau giây lát. "
            "Nếu cần hỗ trợ gấp, anh/chị vui lòng gọi trực tiếp đến "
            "số trực ban Công an xã An Viễn.")

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
