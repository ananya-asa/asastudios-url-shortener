from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.url import URL
from app.api.schemas import ShortenRequest, ShortenResponse
from app.db.session import get_session
from app.services.shortener import encode_base62

router = APIRouter()


@router.post("/shorten")
def shorten_url(request: ShortenRequest, session: Session = Depends(get_session)):
    now = datetime.utcnow()

    existing = session.exec(
        select(URL).where(URL.long_url == request.long_url)
    ).first()

    if existing is not None:
        if existing.short_code is None:
            existing.short_code = encode_base62(existing.id)
            session.add(existing)
            session.commit()
        return ShortenResponse(
            short_url=f"https://asastudios.com/{existing.short_code}",
            expires_at=existing.expires_at,
        )

    new_url = URL(
        long_url=request.long_url,
        created_at=now,
        expires_at=now + timedelta(days=30),
    )

    session.add(new_url)
    session.commit()

    new_url.short_code = encode_base62(new_url.id)
    session.add(new_url)
    session.commit()

    return ShortenResponse(
        short_url=f"https://asastudios.com/{new_url.short_code}",
        expires_at=new_url.expires_at,
    )