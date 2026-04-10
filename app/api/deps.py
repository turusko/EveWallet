from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


DBSession = Session


def get_current_user(x_user_id: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(User.id == x_user_id)) if x_user_id else None
    if not user:
        # MVP single-user bootstrap behavior
        user = db.scalar(select(User))
    if not user:
        raise HTTPException(status_code=401, detail="No user context. complete /auth/login first")
    return user
