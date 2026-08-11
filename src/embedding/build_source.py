import json
from pathlib import Path
import chromadb
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
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection("source_chunks")
    except Exception:
        pass
    collection = client.create_collection(
        name="source_chunks",
        metadata={"hnsw:space": "cosine"},
    )

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
            "text": content,
        })

    embeddings = embed_texts(documents)

    BATCH = 500
    for i in range(0, len(ids), BATCH):
        collection.add(
            ids=ids[i:i + BATCH],
            documents=documents[i:i + BATCH],
            embeddings=embeddings[i:i + BATCH],
            metadatas=metadatas[i:i + BATCH],
        )

if __name__ == "__main__":
    main()
