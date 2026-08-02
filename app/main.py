from fastapi import FastAPI
from evaluation.evaluator import evaluate_run
from evaluation.evaluator import query_
from services.ai_service  import AIService
from services.evaluation_service import EvaluationService
from services.logger import LoggerService 
from app.dependencies import get_evaluation_service
from app.dependencies import get_ai_service
from app.dependencies import get_prompt_service
from app.dependencies import get_log_service
from app.dependencies import get_memory_service
from app.dependencies import get_ingestion_service
from app.dependencies import LoggerService
from services.PromptService import PromptService
from services.memory_service import MemoryService
from ingestion.ingestion_service import IngestionService
from app.models import EvaluationRequest
from app.models import ChatRequest
from app.models import DocLoad
from pydantic import BaseModel
from fastapi import Depends
import uuid
from app.middleware import RequestMiddleware
from app.exception_handler import global_exception_handler
from exceptions.exceptions import ValidationException
from fastapi.responses import JSONResponse



app = FastAPI()
app.add_middleware(RequestMiddleware)
app.add_exception_handler(
    Exception,
    global_exception_handler
    ) 


@app.get("/")
def home(logger: LoggerService = Depends(get_log_service)):
    logger.log_env_details()
    return {"message": "Enterprise AI Platform is running"}



@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):

    return JSONResponse(
        status_code=400, 
        content={
            "status":"FAILED",
            "message":str(exc)
        }
    )   
@app.post("/documents/upload")
def uploaddocs(
    request: DocLoad,
    ingest_service: IngestionService=Depends(get_ingestion_service)):
    result = ingest_service.ingest(request.docname)
    return result
    

@app.get("/health")
def health():
    return {
            "status":"healthy",
            "version":"1.0", 
            "llm":"Azure OpenAI"
            }





@app.post("/query")
def query(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
    memory_service: MemoryService=Depends(get_memory_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    logger: LoggerService = Depends(get_log_service)
):
    session_id = "session_1"
    
    prompt = prompt_service.build_prompt(request.query,request.context, request.prompt_type)
    conv_history=memory_service.get_history(session_id)
    response_query = memory_service.add_message(session_id, ai_service.ask_claude(prompt,request.context, conv_history),request.query, request.context)

    return response_query

@app.post("/evaluate")
def evaluate(request:EvaluationRequest, service: EvaluationService= Depends(get_evaluation_service)):
    logger = LoggerService()
    logger.log_query("API Evaluation Called")
    return service.evaluate(request.faithfulness, request.latency, request.cost) 
    
