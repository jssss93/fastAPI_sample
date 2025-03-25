import os
from pydantic_settings import BaseSettings
from functools import lru_cache

# Redis 설정
REDIS_URL = os.getenv("REDIS_URL", "redis://:0l7idGeXJu@localhost:6379/0")

# 캐시 설정
DEFAULT_CACHE_TTL = int(os.getenv("DEFAULT_CACHE_TTL", "300"))  # 기본 5분
USER_CACHE_TTL = int(os.getenv("USER_CACHE_TTL", "600"))  # 사용자 캐시 10분

class Settings(BaseSettings):
    # 애플리케이션 정보
    APP_NAME: str = "FastAPI Example"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # 로깅 설정
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/app.log"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 3000

    # 기타 설정
    RELOAD: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 환경 변수에서 값을 가져오는 로직
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.LOG_FILE = os.getenv("LOG_FILE", self.LOG_FILE)
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", str(self.PORT)))
        self.RELOAD = os.getenv("RELOAD", "True").lower() == "true"

@lru_cache()
def get_settings():
    return Settings()