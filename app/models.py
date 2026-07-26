from pydantic import BaseModel


class EvaluationRequest(BaseModel):

    faithfulness: float

    latency: float

    cost: float
    

    

class UserContext(BaseModel):
    user_id: str
    country: str
    language: str
    Age: str


class ChatRequest(BaseModel):

    query: str
    context: str
    prompt_type: str

   
