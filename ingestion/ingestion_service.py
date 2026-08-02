from ingestion.document_loader import DocumentLoader
from ingestion.cleaner import Cleaner
from ingestion.chunker import Chunker
from ingestion.embedding_service import EmbeddingService
from ingestion.metadata_builder import MetadataBuilder
from ingestion.vector_store import VectorStore
from services.logger import logger
from models.request_models import ApiResponse


class IngestionService:
    

      def __init__(
        self,
        loader,
        cleaner,
        chunker,
        embedding_service,
        metadata_builder,
        vector_store
      ):

        self.loader = loader
        self.cleaner = cleaner
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.metadata_builder = metadata_builder
        self.vector_store = vector_store

      def ingest(self, file_name):
        text=self.loader.load(file_name)
        logger.info("Load Run")
        clean_text=self.cleaner.clean(text)
        logger.info("clean text")
        chunks=self.chunker.chunk(clean_text)
        logger.info("create chunks")
        embeddings = self.embedding_service.embed(chunks)
        logger.info("embedding creation")
        metadata= self.metadata_builder.build(chunks)
        logger.info("metadata builder")
        self.vector_store.save(
             embeddings,
             metadata
        )
        logger.info("vector store run")
        return ApiResponse(
           success=True,
           message="Document ingested successfully.",
           data=None
          )