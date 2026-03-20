from __future__ import annotations

import secrets
import string

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.link import Link

_ALPHABET = string.ascii_letters + string.digits
_SHORT_ID_LENGTH = 8


def _generate_short_id() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_SHORT_ID_LENGTH))


async def create_link(session: AsyncSession, original_url: str) -> Link:
    try:
        short_id = _generate_short_id()
        link = Link(short_id=short_id, original_url=original_url)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        logger.info(f"Created short link '{short_id}' for {original_url}")
        return link
    except Exception as exc:
        await session.rollback()
        logger.error(f"Failed to create link for {original_url}: {exc}")
        raise


async def get_link_by_short_id(session: AsyncSession, short_id: str) -> Link | None:
    try:
        result = await session.execute(select(Link).where(Link.short_id == short_id))
        return result.scalar_one_or_none()
    except Exception as exc:
        logger.error(f"Failed to fetch link '{short_id}': {exc}")
        raise


async def increment_clicks(session: AsyncSession, short_id: str) -> Link | None:
    try:
        result = await session.execute(select(Link).where(Link.short_id == short_id))
        link = result.scalar_one_or_none()
        if link is None:
            return None
        link.clicks += 1
        await session.commit()
        await session.refresh(link)
        logger.debug(f"Incremented clicks for '{short_id}': total={link.clicks}")
        return link
    except Exception as exc:
        await session.rollback()
        logger.error(f"Failed to increment clicks for '{short_id}': {exc}")
        raise
