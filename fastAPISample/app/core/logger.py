import logging
import threading
import time
import os
import asyncio
from functools import wraps
from logging.handlers import RotatingFileHandler

class CommonLogger:
    """
    시간 및 스레드 정보를 포함하는 공통 로그 클래스
    """

    # 로그 레벨 상수
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # 싱글톤 인스턴스
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CommonLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, logger_name='app', log_level=logging.INFO, log_format=None, log_file=None, max_file_size=10*1024*1024, backup_count=5):
        # 이미 초기화되었으면 다시 초기화하지 않음
        if self._initialized:
            return

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)

        # 핸들러가 이미 있으면 중복 방지를 위해 모두 제거
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 기본 로그 포맷
        if log_format is None:
            log_format = '[%(asctime)s.%(msecs)03d] [%(thread)d:%(threadName)s] [%(levelname)s] %(message)s'

        # 날짜 포맷
        date_format = '%Y-%m-%d %H:%M:%S'

        # 로그 포맷터 설정
        formatter = logging.Formatter(log_format, date_format)

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 파일 핸들러 추가 (지정된 경우)
        if log_file:
            # 로그 디렉터리 생성
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 회전 파일 핸들러 추가
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self._initialized = True

    # 로깅 메소드들
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def log_execution_time(self, func=None, level=logging.INFO):
        """
        함수 실행 시간을 로깅하는 데코레이터
        Python 3.12와 Pydantic v2 환경에 최적화
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 비동기 함수용 래퍼
                start_time = time.time()
                thread_info = f"{threading.get_ident()}:{threading.current_thread().name}"

                try:
                    result = await func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000  # 밀리초로 변환

                    self.logger.log(
                        level,
                        f"Function '{func.__name__}' executed in {execution_time:.2f}ms [Thread: {thread_info}]"
                    )
                    return result
                except Exception as e:
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000  # 밀리초로 변환

                    self.logger.exception(
                        f"Error in function '{func.__name__}' after {execution_time:.2f}ms [Thread: {thread_info}]: {str(e)}"
                    )
                    raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 동기 함수용 래퍼
                start_time = time.time()
                thread_info = f"{threading.get_ident()}:{threading.current_thread().name}"

                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000  # 밀리초로 변환

                    self.logger.log(
                        level,
                        f"Function '{func.__name__}' executed in {execution_time:.2f}ms [Thread: {thread_info}]"
                    )
                    return result
                except Exception as e:
                    end_time = time.time()
                    execution_time = (end_time - start_time) * 1000  # 밀리초로 변환

                    self.logger.exception(
                        f"Error in function '{func.__name__}' after {execution_time:.2f}ms [Thread: {thread_info}]: {str(e)}"
                    )
                    raise

            # 함수가 비동기인지 확인하여 적절한 래퍼 반환
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        if func is None:
            return decorator
        return decorator(func)