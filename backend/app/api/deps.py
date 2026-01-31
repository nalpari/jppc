"""API dependencies."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user() -> dict:
    """Get current user (placeholder for future auth).

    Returns:
        User info dict. Currently returns a placeholder.
    """
    return {"id": 1, "name": "admin"}
