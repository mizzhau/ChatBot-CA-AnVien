from typing import List

_MODEL = None
_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"

def get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL

def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_model()
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return vectors.tolist()
