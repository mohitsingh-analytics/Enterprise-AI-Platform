from services.evaluation_service import EvaluationService
from services.ai_service import AIService
from services.PromptService import PromptService
from services.logger import LoggerService
from services.memory_service import MemoryService
from ingestion.vector_store import VectorStore
from ingestion.chunker import Chunker
from ingestion.cleaner import Cleaner
from ingestion.document_loader import DocumentLoader
from ingestion.embedding_service import EmbeddingService
from ingestion.metadata_builder import MetadataBuilder
from ingestion.ingestion_service import IngestionService

from app.config import settings
from fastapi import Depends
memory_service = MemoryService()
def get_settings(): 
    return settings

def get_ai_service(settings=Depends(get_settings)):
    return AIService(settings)


def get_evaluation_service(settings=Depends(get_settings)):
    return EvaluationService(settings)

def get_prompt_service():
    return PromptService()

def get_log_service(settings=Depends(get_settings)):
    return LoggerService(settings)

def get_memory_service():
    return memory_service


def get_document_loader():
    return DocumentLoader()
def get_cleaner():
    return Cleaner()
def get_chunker():
    return Chunker()
def get_embedding_service():
    return EmbeddingService()
def get_metadata_builder():
    return MetadataBuilder()
def get_vector_store():
    return VectorStore()

def get_ingestion_service(
    loader=Depends(get_document_loader),
    cleaner=Depends(get_cleaner),
    chunker=Depends(get_chunker),
    embedding=Depends(get_embedding_service),
    metadata=Depends(get_metadata_builder),
    vector_store=Depends(get_vector_store),
):
    return IngestionService(
        loader,
        cleaner,
        chunker,
        embedding,
        metadata,
        vector_store,
    )