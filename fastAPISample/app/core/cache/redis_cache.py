# app/cache/redis_cache.py
import redis.asyncio as redis
import pickle
import json
import hashlib
from typing import Any, Optional, Callable, TypeVar, Dict

from app.core.config import REDIS_URL

# Redis 클라이언트 인스턴스
redis_client = redis.from_url(REDIS_URL, decode_responses=False)

# 타입 힌트를 위한 제네릭 타입
T = TypeVar('T')

class RedisCache:
    """Redis 기반 캐시 관리 클래스"""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        value = await redis_client.get(key)
        if value:
            try:
                return pickle.loads(value)
            except Exception as e:
                print(f"캐시 역직렬화 오류: {e}")
        return None

    @staticmethod
    async def set(key: str, value: Any, expire: int = 60) -> bool:
        """캐시에 값 저장하기"""
        try:
            pickled_value = pickle.dumps(value)
            await redis_client.setex(key, expire, pickled_value)
            return True
        except Exception as e:
            print(f"캐시 저장 오류: {e}")
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """캐시 삭제하기"""
        return await redis_client.delete(key) > 0

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """패턴과 일치하는 캐시 모두 삭제하기"""
        cursor = 0
        deleted = 0

        while True:
            cursor, keys = await redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                deleted += await redis_client.delete(*keys)
            if cursor == 0:
                break

        return deleted

    @staticmethod
    def make_key(prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성 헬퍼 함수"""
        key_parts = [prefix]

        # args 처리
        for arg in args:
            key_parts.append(str(arg))
        print(key_parts)
        # kwargs 처리 (정렬하여 일관성 유지)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                key_parts.append(f"{k}={v}")


        return ":".join(key_parts)
        #MD5 해시 사용
        #return f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"