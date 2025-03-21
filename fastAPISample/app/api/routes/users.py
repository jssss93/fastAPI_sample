from fastapi import APIRouter, HTTPException, Path, status
from typing import List

from app.models.schemas import User, UserCreate, UserBase
from app.core.logger import CommonLogger
from app.api.deps import users_db

# 글로벌 변수
user_id_counter = 1
logger = CommonLogger()

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}},
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
@logger.log_execution_time
async def create_user(user: UserCreate):
    global user_id_counter

    logger.debug(f"Creating new user with username: {user.username}, email: {user.email}")

    # 이메일 중복 검사
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            logger.warning(f"Attempted to create user with duplicate email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # 새 사용자 생성
    from datetime import datetime
    new_user = User(
        id=user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=datetime.now()
    )

    # DB에 저장
    users_db[user_id_counter] = new_user
    user_id_counter += 1

    logger.info(f"User created: ID={new_user.id}, Username={new_user.username}")
    return new_user

@router.get("/", response_model=List[User])
@logger.log_execution_time
async def read_users(skip: int = 0, limit: int = 100):
    logger.debug(f"Fetching users with skip={skip}, limit={limit}")
    users = list(users_db.values())[skip:skip+limit]
    logger.debug(f"Retrieved {len(users)} users")
    return users

@router.get("/{user_id}", response_model=User)
@logger.log_execution_time
async def read_user(user_id: int = Path(..., gt=0)):
    logger.debug(f"Fetching user with ID: {user_id}")

    if user_id not in users_db:
        logger.warning(f"User not found: ID={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.debug(f"User found: ID={user_id}")
    return users_db[user_id]

# 추가 엔드포인트 (update, delete 등)은 필요에 따라 포함