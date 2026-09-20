from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models.url import URL
from app.models.click import Click
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

# Get Shortcode

@router.get("/{short_code}")
def redirect_to_long_url(short_code: str, session: Session=Depends(get_session)):
    short_code_entry=session.exec(
        select(URL).where(URL.short_code==short_code)).first()

    if short_code_entry is None:
        raise HTTPException(status_code=404, detail="ShortCODE NOT FOUND")
    if short_code_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="ShortCODE EXPIRED")
    
        # Record the click
    new_click=Click(
        short_code=short_code,
        clicked_at=datetime.utcnow()
        )
    session.add(new_click)
    session.commit()
    return RedirectResponse(url=short_code_entry.long_url,status_code=302)
