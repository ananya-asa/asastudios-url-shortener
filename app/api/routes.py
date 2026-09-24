from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, func, select


from fastapi import Request

from app.models.url import URL
from app.models.click import Click
from app.api.schemas import ClickDay, ShortenRequest, ShortenResponse, StatsResponse
from app.db.session import get_session
from app.services.shortener import encode_base62
from app.core import limiter


router = APIRouter()


@router.post("/shorten")
@limiter.limit("5/minute")
def shorten_url(request: Request,body: ShortenRequest, session: Session = Depends(get_session)):
    now = datetime.utcnow()
    long_url = str(body.long_url)

    existing = session.exec(
        select(URL).where(URL.long_url == long_url)
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
        long_url=long_url,
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
@limiter.limit("100/minute")
def redirect_to_long_url(request: Request, short_code: str, session: Session=Depends(get_session)):
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



@router.get("/{short_code}/stats")
@limiter.limit("15/minute")
def get_short_code_stats(request: Request, short_code: str, session: Session=Depends(get_session)):
    short_code_entry=session.exec(
        select(URL).where(URL.short_code==short_code)).first()
    
    if short_code_entry is None:
        raise HTTPException(status_code=404, detail="ShortCODE NOT FOUND")
    if short_code_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="ShortCODE EXPIRED")
    
    stats = session.exec(
        select(func.date(Click.clicked_at), func.count())
        .where(Click.short_code == short_code)
        .group_by(func.date(Click.clicked_at))
    ).all()

    return StatsResponse(
        total_clicks=sum(count for _, count in stats),
        clicks_per_day=[ClickDay(date=str(date)[:10], count=count) for date, count in stats]
    )