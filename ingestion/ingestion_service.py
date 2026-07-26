from ingestion.document_loader import DocumentLoader
from ingestion.cleaner import Cleaner
from ingestion.chunker import Chunker
from ingestion.embedding_service import EmbeddingService
from ingestion.metadata_builder import MetadataBuilder
from ingestion.vector_store import VectorStore



class IngestionService:
    def __init__(self, 
                 loader,
                   cleaner,
                     chunker,
                       embedding_service,
                         metadata_builder, 
                         vector_store
                         ):
        self.loader= DocumentLoader
        self.chunker = Chunker
        self.cleaner =Cleaner
        self.embedding_service =EmbeddingService
        self.metadata_builder= MetadataBuilder
        self.vector_store=VectorStore

    def ingest(self, file_name):
        text=self.loader.load(file_name)
        clean_text=self.cleaner.clean(text)
        chunks=self.chunker.chunk(clean_text)
        embeddings = self.embedding_service.embed(chunks)
        metadata= self.metadata_builder.build(chunks)
        self.vector_store.save(
             embeddings,
             metadata
        )
    
        return{
            "status": "Completed",
            
        }