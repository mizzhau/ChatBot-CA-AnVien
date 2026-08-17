import sys
import json
import logging
from pathlib import Path
import chromadb
from src.embedding.embedder import embed_texts

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).parent.parent.parent / "data" / "vectorstore"
SOURCE_REGISTRY_PATH = Path(__file__).parent.parent.parent / "data" / "chunks" / "id_source.json"

def _load_source_registry():
    with open(SOURCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_source_registry = _load_source_registry()

def get_website_links(source_ids_val) -> str:
    if not source_ids_val:
        return ""
    src_ids = []
    if isinstance(source_ids_val, list):
        src_ids = source_ids_val
    elif isinstance(source_ids_val, str):
        source_ids_val = source_ids_val.strip()
        if source_ids_val.startswith("["):
            try:
                parsed = json.loads(source_ids_val)
                if isinstance(parsed, list):
                    src_ids = parsed
            except Exception:
                src_ids = [s.strip() for s in source_ids_val.split("|") if s.strip()]
        else:
            src_ids = [s.strip() for s in source_ids_val.split("|") if s.strip()]
    
    links = []
    for sid in src_ids:
        entry = _source_registry.get(sid)
        if entry and entry.get("url"):
            links.append(f"- {entry['title']}: {entry['url']}")
    if not links:
        return ""
    return "\n🔗 Link website:\n" + "\n".join(links)

SIM_THRESHOLD_KB = 0.35
SIM_THRESHOLD_SOURCE = 0.20

EMERGENCY_NOTE = (
    "\n\n🚨 Nếu tình huống đang nguy hiểm/khẩn cấp: gọi 113 (an ninh trật tự), "
    "114 (cháy nổ/cứu nạn cứu hộ), 115 (cấp cứu y tế)."
)

def is_fallback_chunk(meta: dict) -> bool:
    return meta.get("intent_code", "").endswith("_FALLBACK_LIEN_QUAN")

def search_kb(query: str, top_k: int = 12):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection("kb_chunks")
    q_emb = embed_texts([query])[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)

    if not res or not res.get("documents") or not res["documents"] or not res["documents"][0]:
        return []

    best_by_chunk = {}
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        sim = 1 - dist
        cid = meta.get("chunk_id", "")
        if cid not in best_by_chunk or sim > best_by_chunk[cid]["sim"]:
            best_by_chunk[cid] = {"sim": sim, "meta": meta, "matched_variant": doc}

    ranked = sorted(best_by_chunk.values(), key=lambda x: x["sim"], reverse=True)
    return ranked

def search_sources(query: str, top_k: int = 8):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection("source_chunks")
    q_emb = embed_texts([query])[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)

    if not res or not res.get("metadatas") or not res["metadatas"] or not res["metadatas"][0]:
        return []

    results = []
    for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
        results.append({"sim": 1 - dist, "meta": meta})
    return results

def pick_kb_match(kb_results):
    if not kb_results:
        return None, False

    specific = [r for r in kb_results if not is_fallback_chunk(r["meta"])]
    fallback = [r for r in kb_results if is_fallback_chunk(r["meta"])]

    best_specific = specific[0] if specific else None
    best_fallback = fallback[0] if fallback else None

    if best_specific and best_specific["sim"] >= SIM_THRESHOLD_KB:
        return best_specific, False
    if best_fallback and best_fallback["sim"] >= SIM_THRESHOLD_KB:
        return best_fallback, True
    return None, False

def answer(query: str) -> str:
    kb_results = search_kb(query)
    top, used_fallback = pick_kb_match(kb_results)
    if top is not None:
        meta = top["meta"]
        out = []

        # 1. Câu trả lời chính — sạch, không kèm nhãn kỹ thuật
        out.append(meta["canonical_answer"])

        # 2. Gợi ý hỏi lại — diễn đạt tự nhiên
        if meta.get("clarifying_question_if_missing"):
            out.append(f"\nGợi ý câu hỏi làm rõ: {meta['clarifying_question_if_missing']}")

        # 3. Hướng dẫn chuyển tiếp — diễn đạt tự nhiên
        if meta.get("handoff_or_emergency_rule"):
            out.append(f"\nLưu ý chuyển tiếp: {meta['handoff_or_emergency_rule']}")

        # 4. Căn cứ pháp lý
        if meta.get("legal_basis"):
            out.append(f"\nCăn cứ pháp lý: {meta['legal_basis']}")

        # 5. Guardrail (quy tắc an toàn cho LLM tuân thủ)
        if meta.get("guardrail"):
            out.append(f"\nQuy tắc an toàn: {meta['guardrail']}")

        # 6. Link website
        website_links = get_website_links(meta.get("source_ids", ""))
        if website_links:
            out.append(website_links)

        # 7. Debug info — CHỈ log, KHÔNG đưa vào context cho LLM
        logger.info(f"[KB-MATCH] chunk={meta['chunk_id']} | sim={top['sim']:.3f} | "
                    f"variant=\"{top['matched_variant']}\"")

        result = "\n".join(out)
        if meta.get("module", "").startswith(("E", "F")):
            result += EMERGENCY_NOTE
        return result

    src_results = search_sources(query)
    if src_results and src_results[0]["sim"] >= SIM_THRESHOLD_SOURCE:
        top = src_results[0]["meta"]
        ocr_warning = ""
        if top.get("doc_quality") in ("ocr", "mixed"):
            ocr_warning = (
                "\n⚠ Lưu ý: Thông tin trích từ tài liệu scan (OCR), "
                "có thể chưa chính xác 100%.\n"
            )
        return (
            f"(Không tìm thấy KB_CHUNK khớp tốt — trích từ nguồn gốc để tham khảo, "
            f"cần cán bộ xác nhận thêm)\n{ocr_warning}\n"
            f"{top['heading']}\n{top['text'][:500]}...\n\n"
            f"Nguồn: {top['name']} ({top['url']})"
        )

    return (
        "Xin lỗi, mình chưa tìm được thông tin phù hợp cho câu hỏi này trong cơ sở dữ liệu. "
        "Anh/chị vui lòng liên hệ cán bộ phụ trách hoặc số trực ban Công an phường để được "
        "hỗ trợ trực tiếp." + EMERGENCY_NOTE
    )

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "tôi mới chuyển về phường muốn nhập hộ khẩu thì làm sao"
    print(f"Câu hỏi: {q}\n")
    print(answer(q))
