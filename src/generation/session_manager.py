import time
from typing import List, Dict, Any

class SessionManager:
    """
    Quản lý phiên hội thoại (In-Memory Session Manager) cho từng người dùng.
    Mỗi session lưu danh sách các message: [{"role": "user"|"bot", "text": "..."}]
    Session cũ được lưu lại (archive) khi người dùng tạo đoạn chat mới,
    cho phép quay lại xem hoặc tiếp tục cuộc trò chuyện cũ.
    """
    def __init__(self, max_history_turns: int = 5, session_ttl_hours: int = 72, max_archived_sessions: int = 20):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.max_history_turns = max_history_turns
        self.session_ttl_seconds = session_ttl_hours * 3600
        self.max_archived_sessions = max_archived_sessions

    def _cleanup_expired_sessions(self):
        now = time.time()
        expired_ids = [
            sid for sid, data in self.sessions.items()
            if now - data.get("last_active", 0) > self.session_ttl_seconds
        ]
        for sid in expired_ids:
            self.sessions.pop(sid, None)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        if not session_id:
            return []
        self._cleanup_expired_sessions()
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get("messages", [])

    def get_full_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Trả về toàn bộ tin nhắn của session (dùng để hiển thị lại trên UI)."""
        if not session_id:
            return []
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get("all_messages", session.get("messages", []))

    def add_message(self, session_id: str, role: str, text: str):
        if not session_id or not text:
            return
        self._cleanup_expired_sessions()
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "all_messages": [],
                "last_active": time.time(),
                "created_at": time.time(),
                "title": ""
            }

        session = self.sessions[session_id]
        session["last_active"] = time.time()

        msg = {"role": role, "text": text}
        session["all_messages"].append(msg)
        session["messages"].append(msg)

        # Tự động đặt tiêu đề session từ câu hỏi đầu tiên của người dùng
        if not session["title"] and role == "user":
            session["title"] = text[:60] + ("..." if len(text) > 60 else "")

        # Giữ lại số lượt hội thoại gần nhất cho context gửi LLM
        max_messages = self.max_history_turns * 2
        if len(session["messages"]) > max_messages:
            session["messages"] = session["messages"][-max_messages:]

    def archive_session(self, session_id: str):
        """
        Lưu trữ (archive) session hiện tại — KHÔNG xóa.
        Session được đánh dấu archived và vẫn truy xuất được.
        """
        if session_id in self.sessions:
            self.sessions[session_id]["archived"] = True
            self.sessions[session_id]["archived_at"] = time.time()

        # Giới hạn số lượng session archived để tránh tràn bộ nhớ
        archived = [
            (sid, data) for sid, data in self.sessions.items()
            if data.get("archived", False)
        ]
        if len(archived) > self.max_archived_sessions:
            # Xóa session cũ nhất
            archived.sort(key=lambda x: x[1].get("created_at", 0))
            for sid, _ in archived[:len(archived) - self.max_archived_sessions]:
                self.sessions.pop(sid, None)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Liệt kê tất cả sessions có tin nhắn (cả active và archived)."""
        self._cleanup_expired_sessions()
        result = []
        for sid, data in self.sessions.items():
            if not data.get("all_messages") and not data.get("messages"):
                continue
            msgs = data.get("all_messages", data.get("messages", []))
            result.append({
                "session_id": sid,
                "title": data.get("title", "Cuộc trò chuyện"),
                "message_count": len(msgs),
                "created_at": data.get("created_at", 0),
                "last_active": data.get("last_active", 0),
                "archived": data.get("archived", False)
            })
        # Sắp xếp theo thời gian hoạt động gần nhất
        result.sort(key=lambda x: x["last_active"], reverse=True)
        return result

    def delete_session(self, session_id: str):
        """Xóa hẳn một session (chỉ khi người dùng yêu cầu xóa thật sự)."""
        self.sessions.pop(session_id, None)

# Global singleton
session_manager = SessionManager()
