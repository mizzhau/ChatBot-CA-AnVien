import sys
import json
from pathlib import Path
import chromadb
from src.embedding.embedder import embed_texts

DB_DIR = Path(__file__).parent.parent.parent / "data" / "vectorstore"
SOURCE_REGISTRY_PATH = Path(__file__).parent.parent.parent / "data" / "chunks" / "id_source.json"

def _load_source_registry():
    with open(SOURCE_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_source_registry = _load_source_registry()

def get_website_links(source_ids_str: str) -> str:
    if not source_ids_str:
        return ""
    try:
        src_ids = json.loads(source_ids_str) if isinstance(source_ids_str, str) else source_ids_str
    except (json.JSONDecodeError, TypeError):
        return ""
    links = []
    for sid in src_ids:
        entry = _source_registry.get(sid)
        if entry and entry.get("url"):
            links.append(f"- {entry['title']}: {entry['url']}")
    if not links:
        return ""
    return "\n🔗 Link website:\n" + "\n".join(links)

SIM_THRESHOLD_KB = 0.45
SIM_THRESHOLD_SOURCE = 0.20

EMERGENCY_NOTE = (
    "\n\n Nếu tình huống đang nguy hiểm/khẩn cấp: gọi 113 (an ninh trật tự), "
    "114 (cháy nổ/cứu nạn cứu hộ), 115 (cấp cứu y tế)."
)

def is_fallback_chunk(meta: dict) -> bool:
    return meta.get("intent_code", "").endswith("_FALLBACK_LIEN_QUAN")

def search_kb(query: str, top_k: int = 8):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection("kb_chunks")
    q_emb = embed_texts([query])[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)

    best_by_chunk = {}
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        sim = 1 - dist
        cid = meta["chunk_id"]
        if cid not in best_by_chunk or sim > best_by_chunk[cid]["sim"]:
            best_by_chunk[cid] = {"sim": sim, "meta": meta, "matched_variant": doc}

    ranked = sorted(best_by_chunk.values(), key=lambda x: x["sim"], reverse=True)
    return ranked

def search_sources(query: str, top_k: int = 5):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_collection("source_chunks")
    q_emb = embed_texts([query])[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)

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
        out.append(meta["canonical_answer"])
        if meta.get("clarifying_question_if_missing"):
            out.append(f"\n(Nếu thiếu thông tin, hỏi lại: {meta['clarifying_question_if_missing']})")
        if meta.get("legal_basis"):
            out.append(f"\nCăn cứ: {meta['legal_basis']}")
        website_links = get_website_links(meta.get("source_ids", ""))
        if website_links:
            out.append(website_links)
        out.append(f"\n[matched: {meta['chunk_id']} | sim={top['sim']:.3f} | "
                    f"qua biến thể: \"{top['matched_variant']}\"]")
        result = "\n".join(out)
        if meta.get("module", "").startswith(("E", "F")):
            result += EMERGENCY_NOTE
        return result

    src_results = search_sources(query)
    if src_results and src_results[0]["sim"] >= SIM_THRESHOLD_SOURCE:
        top = src_results[0]["meta"]
        return (
            f"(Không tìm thấy KB_CHUNK khớp tốt — trích từ nguồn gốc để tham khảo, "
            f"cần cán bộ xác nhận thêm)\n\n"
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
