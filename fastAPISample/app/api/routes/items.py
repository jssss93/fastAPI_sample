from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import List

from app.models.schemas import Item, ItemCreate, ItemBase
from app.models.schemas import User
from app.core.logger import CommonLogger
from app.api.deps import get_current_user
import time

# 글로벌 변수
items_db = {}
item_id_counter = 1
logger = CommonLogger()

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Item not found"}},
)

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
@logger.log_execution_time
async def create_item(
        item: ItemCreate,
        current_user: User = Depends(get_current_user)
):
    global item_id_counter

    logger.debug(f"Creating new item for user ID: {current_user.id}")

    # 새 아이템 생성
    from datetime import datetime
    new_item = Item(
        id=item_id_counter,
        title=item.title,
        description=item.description,
        owner_id=current_user.id,
        created_at=datetime.now()
    )

    # DB에 저장
    items_db[item_id_counter] = new_item
    item_id_counter += 1

    logger.info(f"Item created: ID={new_item.id}, Title='{new_item.title[:20] if len(new_item.title) > 20 else new_item.title}', Owner={current_user.id}")
    return new_item

@router.get("/", response_model=List[Item])
@logger.log_execution_time
async def read_items(skip: int = 0, limit: int = 100):
    logger.debug(f"Fetching items with skip={skip}, limit={limit}")
    items = list(items_db.values())[skip:skip+limit]
    time.sleep(0.1)
    logger.debug(f"Retrieved {len(items)} items")
    return items

# 추가 엔드포인트 (상세 조회, 업데이트, 삭제 등)는 필요에 따라 포함