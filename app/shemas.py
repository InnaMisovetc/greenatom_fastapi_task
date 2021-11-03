from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Image(BaseModel):
    name: UUID
    created_at: datetime

    class Config:
        orm_mode = True
