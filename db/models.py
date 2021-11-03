import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.database import Base


class ImageModel(Base):
    __tablename__ = "inbox"
    request_code = Column(UUID(as_uuid=True))
    name = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
