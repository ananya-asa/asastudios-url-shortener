from sqlmodel import SQLModel
from datetime import datetime

class ShortenRequest(SQLModel):
    long_url: str

class ShortenResponse(SQLModel):
    short_url: str
    expires_at: datetime