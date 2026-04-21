from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ItemRead(BaseModel):
    id: str
    name: str
    description: Optional[str] = None