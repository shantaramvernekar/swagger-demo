from typing import List, Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    id: int = Field(..., example=1, description="Unique item ID")
    name: str = Field(..., min_length=1, max_length=100, example="Widget")
    price: float = Field(..., ge=0, example=12.99)
    tags: List[str] = Field(default_factory=list, example=["new", "sale"])


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Widget")
    price: float = Field(..., ge=0, example=12.99)
    tags: Optional[List[str]] = Field(default=None, example=["new"])

