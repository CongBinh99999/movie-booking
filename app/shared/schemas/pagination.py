from math import ceil
from pydantic import BaseModel, Field, computed_field
from typing import TypeVar, Generic

T = TypeVar('T')


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page-1) * self.size


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int

    @computed_field
    @property
    def pages(self) -> int:
        return ceil(self.total / self.size) if self.size > 0 else 0

    
    @computed_field
    @property
    def has_next(self) -> bool: 
        return self.page < self.pages


    @computed_field
    @property
    def has_prev(self) -> bool: 
        return self.page > 1 

    
    
