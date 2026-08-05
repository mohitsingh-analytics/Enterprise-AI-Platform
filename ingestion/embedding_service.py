from services.logger import logger
class EmbeddingService:
    def embed(self, chunks):
        logger.info(f"Creating embeddings for {len(chunks)} chunks")
        return [
            f"Embedding({chunk})"
            for chunk in chunks
        ]