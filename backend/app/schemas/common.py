"""Common schemas."""
from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        return self.skip + self.limit < self.total


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None


class SuccessResponse(BaseModel):
    message: str
    data: dict | None = None
