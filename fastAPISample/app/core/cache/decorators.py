# app/cache/decorators.py
from functools import wraps
from typing import Callable, TypeVar, Any, Optional

from app.core.cache.redis_cache import RedisCache

T = TypeVar('T')

def cached(expire: int = 60, prefix: Optional[str] = None):
    """
    함수 결과를 Redis에 캐싱하는 데코레이터

    Args:
        expire: 캐시 유효 시간(초), 기본값 60초
        prefix: 캐시 키 접두사, 없으면 함수명 사용
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_prefix = prefix or func.__name__
            cache_key = RedisCache.make_key(cache_prefix, *args, **kwargs)

            # 캐시에서 조회
            cached_result = await RedisCache.get(cache_key)
            print(cache_key)
            if cached_result is not None:
                return cached_result

            # 캐시 없으면 함수 실행
            result = await func(*args, **kwargs)

            # 결과 캐싱
            await RedisCache.set(cache_key, result, expire)

            return result
        return wrapper
    return decorator

# 좀 더 직관적인 이름의 함수 제공
def invalidate_cache(prefix: str, *args, **kwargs) -> Any:
    """특정 캐시 항목 무효화"""
    cache_key = RedisCache.make_key(prefix, *args, **kwargs)
    return RedisCache.delete(cache_key)

def invalidate_cache_pattern(pattern: str) -> Any:
    """패턴과 일치하는 모든 캐시 항목 무효화"""
    return RedisCache.delete_pattern(pattern)