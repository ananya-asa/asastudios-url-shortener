from sqlmodel import SQLModel, Field
from datetime import datetime


class URL(SQLModel, table=True):
    __tablename__ = "urls"
    
    id: int | None = Field(default=None, primary_key=True)
    short_code: str | None = Field(default=None, nullable=True, index=True, unique=True, max_length=10)
    long_url: str = Field(index=True, unique=True, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime