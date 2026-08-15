import json
from pathlib import Path
import chromadb
try:
    from src.embedding.embedder import embed_texts
except ImportError:
    from embedder import embed_texts

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "chunks"
DB_DIR = Path(__file__).parent.parent.parent / "data" / "vectorstore"

def load_kb_chunks():
    chunks = []
    with open(DATA_DIR / "kb_chunks.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks

def flatten_metadata(chunk: dict) -> dict:
    meta = {}
    for k, v in chunk.items():
        if isinstance(v, list):
            meta[k] = " | ".join(str(x) for x in v)
        elif v is None:
            meta[k] = ""
        else:
            meta[k] = v
    return meta

def main():
    chunks = load_kb_chunks()

    # Deduplicate chunks by chunk_id
    unique_chunks = {}
    for chunk in chunks:
        unique_chunks[chunk.get("chunk_id", "")] = chunk
    chunks = list(unique_chunks.values())

    ids, documents, metadatas = [], [], []
    for chunk in chunks:
        variants = list(chunk["question_variants"])
        if "retrieval_title" in chunk:
            variants.append(chunk["retrieval_title"])

        meta = flatten_metadata(chunk)
        for i, variant in enumerate(variants):
            ids.append(f"{chunk['chunk_id']}::v{i}")
            documents.append(variant)
            metadatas.append(meta)

    print(f"Embedding {len(documents)} KB question variants...")
    embeddings = embed_texts(documents)

    print("Saving KB embeddings to ChromaDB...")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection("kb_chunks")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name="kb_chunks",
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
    print("Done building kb_chunks vector store.")

if __name__ == "__main__":
    main()
