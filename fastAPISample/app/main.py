import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from app.core.config import get_settings
from app.core.logger import CommonLogger
from app.api.routes import users, items

# 설정 및 로거 설정
settings = get_settings()
logger = CommonLogger(
    logger_name=settings.APP_NAME,
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)

# Lifespan 컨텍스트 매니저 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행 (startup)
    logger.info("=== Application startup ===")
    logger.info("Initializing resources...")
    logger.info("=== Application startup completed===")
    # 애플리케이션 실행
    yield

    # 종료 시 실행 (shutdown)
    logger.info("Cleaning up resources...")
    logger.info("=== Application shutdown ===")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="A FastAPI application with structured logging",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import threading
    import asyncio
    import os

    # 고유 식별자 정보 수집
    thread_id = threading.get_ident()
    process_id = os.getpid()

    # 이벤트 루프 ID 가져오기
    try:
        loop = asyncio.get_running_loop()
        loop_id = id(loop)
    except RuntimeError:
        loop_id = "no_loop"

    # 요청 고유 ID 생성
    request_id = f"{threading.get_ident()}"
    start_time = time.time()

    # 기본 정보 추출
    path = request.url.path
    method = request.method

    # 쿼리 파라미터 추출
    query_params = dict(request.query_params)
    query_str = ""
    if query_params:
        query_str = f" Query Params: {query_params}"

    # 헤더 정보 추출 (선택적으로 필요한 헤더만)
    #headers = {}
    #if "user-agent" in request.headers:
    #    headers["user-agent"] = request.headers["user-agent"]
    #if "content-type" in request.headers:
    #    headers["content-type"] = request.headers["content-type"]

    #header_str = ""
    #if headers:
    #    header_str = f" Headers: {headers}"

    # 클라이언트 IP 추출
    client_host = request.client.host if request.client else "unknown"


    # 요청 로그 기록 (확장된 정보 포함)
    logger.info(f"Request started: {method} {path}{query_str} [ID: {request_id}] [LoopID: {loop_id}] [Client: {client_host}]")


    # 요청 로그 기록 (쿼리 파라미터 포함)
    #logger.info(f"Request started: {method} {path}{query_str} [ID: {request_id}]")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code

        # 응답 로그 기록 (쿼리 파라미터 포함)
        logger.info(f"Request completed: {method} {path}{query_str} [ID: {request_id}] - Status: {status_code} - {process_time:.2f}ms")
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.exception(f"Request failed: {method} {path}{query_str} [ID: {request_id}] - {process_time:.2f}ms - Error: {str(e)}")
        raise

# 루트 경로
@app.get("/")
@logger.log_execution_time
async def root():
    logger.debug("Root endpoint called")
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs_url": "/docs",
        "routes": {
            "users": "/users/",
            "items": "/items/"
        }
    }

@app.get("/root")
async def read_root():
    # 가능한 가장 간단한 응답
    return {"status": "ok"}

# 단순 JSON 객체 반환 (경로 매개변수 없음)
@app.get("/simple")
async def simple_response():
    return {"message": "Hello, World!"}

# 라우터 등록
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(items.router, prefix=settings.API_PREFIX)

# 애플리케이션 직접 실행 시
if __name__ == "__main__":
    import uvicorn
    import gunicorn
    logger.info(f"Starting {settings.APP_NAME}")


    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="debug",
        workers=3,
        loop="uvloop",
        timeout_keep_alive=10  # 연결 유지 타임아웃(초)
    )
    #uvicorn app.main:app --workers 3 --reload --log-level warning