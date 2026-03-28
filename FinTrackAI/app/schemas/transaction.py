from datetime import date, datetime
from datetime import date
from typing import Optional
from pydantic import BaseModel
from datetime import date
from typing import Optional

class TransactionCreate(BaseModel):
    amount: float
    description: str
    category: Optional[str] = None
    date: Optional[date] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: str | None
    date: date
    created_at: datetime

    class Config:
        from_attributes = True