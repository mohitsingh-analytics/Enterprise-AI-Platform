from pydantic import BaseModel
from typing import Any

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None

    