from pydantic import BaseModel

class DocumentUploadRequest(BaseModel):
    document_name: str
    department: str
    country: str