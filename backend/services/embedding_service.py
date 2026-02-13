from sentence_transformers import SentenceTransformer

# Load model ONCE at server startup
model = SentenceTransformer("all-MiniLM-L6-v2")

class EmbeddingService:
    def embed_texts(self, texts):
        return model.encode(texts, convert_to_numpy=True)
