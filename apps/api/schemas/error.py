from pydantic import BaseModel


class ApiErrorResponse(BaseModel):
    error: str
    message: str
