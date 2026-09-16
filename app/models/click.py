from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, ForeignKey
from datetime import datetime

class Click(SQLModel, table=True):
    __tablename__ = "clicks"

    id: int | None = Field(default=None, primary_key=True)
    short_code: str = Field(sa_column=Column(String, ForeignKey("urls.short_code", ondelete="CASCADE"), index=True))
    clicked_at: datetime = Field(default_factory=datetime.utcnow)
    