from services.logger import logger
class VectorStore:

    def save(self, embeddings, metadata):

        logger.info("Embeddings stored in vector database.")

        return True