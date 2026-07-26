class EmbeddingService:
    def embed(self, chunks):
        print("Creating embeddings")
        return [
            f"Embedding({chunk})"
            for chunk in chunks
        ]