from pydantic import BaseModel
from typing import Any
from time import datetime

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None
    errors: list | None = None
    request_id: str | None = None
    timestamp: datetime | None = None

    