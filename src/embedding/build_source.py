import json
from pathlib import Path
import chromadb
try:
    from src.embedding.embedder import embed_texts
except ImportError:
    from embedder import embed_texts

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "chunks"
DB_DIR = Path(__file__).parent.parent.parent / "data" / "vectorstore"

def load_sources():
    rows = []
    with open(DATA_DIR / "source.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def main():
    rows = load_sources()
    
    # Deduplicate rows by chunk_id
    unique_rows = {}
    for row in rows:
        unique_rows[row.get("chunk_id", "")] = row
    rows = list(unique_rows.values())

    ids, documents, metadatas = [], [], []
    for row in rows:
        cid = row.get("chunk_id", "")
        chuong_title = row.get("chuong_title") or ""
        dieu_title = row.get("dieu_title") or ""
        content = row.get("content") or ""
        
        heading_parts = []
        if chuong_title: heading_parts.append(chuong_title)
        if dieu_title: heading_parts.append(dieu_title)
        heading = " - ".join(heading_parts)
        
        text_to_embed = f"{heading}\n{content}".strip()
        ids.append(cid)
        documents.append(text_to_embed)
        metadatas.append({
            "source_id": row.get("source_id", ""),
            "chunk_id": cid,
            "heading": heading,
            "name": row.get("source_title", ""),
            "url": row.get("source_url", ""),
            "content_type": row.get("content_type", ""),
            "doc_quality": row.get("doc_quality", "text"),
            "text": content,
        })

    print(f"Embedding {len(documents)} source chunks...")
    embeddings = embed_texts(documents)

    print("Saving embeddings to ChromaDB...")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection("source_chunks")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name="source_chunks",
        metadata={"hnsw:space": "cosine"},
    )

    BATCH = 500
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            documents=documents[i:i + BATCH],
            embeddings=embeddings[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )
    print("Done building source_chunks vector store.")

if __name__ == "__main__":
    main()
