from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.link import ShortenRequest, ShortenResponse, StatsResponse
from app.database.dependencies import get_session
from app.services import link_service

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(
    body: ShortenRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ShortenResponse:
    link = await link_service.create_link(session, str(body.url))
    short_url = str(request.base_url) + link.short_id
    return ShortenResponse(
        short_id=link.short_id,
        short_url=short_url,
        original_url=link.original_url,
    )


@router.get("/stats/{short_id}", response_model=StatsResponse)
async def get_stats(
    short_id: str,
    session: AsyncSession = Depends(get_session),
) -> StatsResponse:
    link = await link_service.get_link_by_short_id(session, short_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return StatsResponse(
        short_id=link.short_id,
        original_url=link.original_url,
        clicks=link.clicks,
        created_at=link.created_at,
    )


@router.get("/{short_id}")
async def redirect_to_original(
    short_id: str,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    link = await link_service.increment_clicks(session, short_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=link.original_url, status_code=302)
