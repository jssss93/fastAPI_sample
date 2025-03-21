from fastapi import Depends, HTTPException, status, Query
from typing import Dict, Any

# 임시 인메모리 데이터베이스
users_db: Dict[int, Any] = {}

async def get_current_user(user_id: int = Query(..., description="Current user ID")):
    from app.core.logger import CommonLogger
    logger = CommonLogger()

    if user_id not in users_db:
        logger.warning(f"Unauthorized access attempt with user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return users_db[user_id]