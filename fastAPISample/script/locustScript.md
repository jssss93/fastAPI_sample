비동기
```
from locust import HttpUser, task, between
import gevent

class APITestUser(HttpUser):
    # 필요에 따라 주석 해제
    # wait_time = between(1, 3)
    
    @task
    def test_all_endpoints(self):
        # API 호출을 비동기로 실행하는 함수들
        def call_root():
            self.client.get("/root", name="Root Endpoint", headers={"accept": "application/json"})
            
        def call_users():
            self.client.get("/api/users/?skip=0&limit=100", name="Users Endpoint", headers={"accept": "application/json"})
            
        def call_items():
            self.client.get("/api/items/?skip=0&limit=100", name="Items Endpoint", headers={"accept": "application/json"})
        
        # 모든 호출을 비동기 태스크로 실행
        tasks = [
            gevent.spawn(call_root),
            gevent.spawn(call_users),
            gevent.spawn(call_items)
        ]
        
        # 모든 태스크가 완료될 때까지 대기
        gevent.joinall(tasks)

동기
```
from locust import HttpUser, task, between

class APITestUser(HttpUser):
    # 사용자 대기 시간 설정 (선택적)
    # wait_time = between(1, 3)
    
    @task
    def get_root(self):
        # 루트 엔드포인트 테스트
        self.client.get("/root", name="Root Endpoint", headers={"accept": "application/json"})
    
    @task
    def get_users(self):
        # 사용자 목록 엔드포인트 테스트
        self.client.get("/api/users/?skip=0&limit=100", name="Users Endpoint", headers={"accept": "application/json"})
    
    @task
    def get_items(self):
        # 아이템 목록 엔드포인트 테스트
        self.client.get("/api/items/?skip=0&limit=100", name="Items Endpoint", headers={"accept": "application/json"})
        

```
from locust import HttpUser, task, between
import time

class MainPageUser(HttpUser):
    #wait_time = between(3, 5)  # 사용자가 페이지 간 이동하는 평균 시간
    
    @task
    def load_main_page(self):
        # 메인 페이지 로드 시작 시간 기록
        start_time = time.time()

        # 병렬 요청 - 실제 브라우저 동작 시뮬레이션
        responses = {
            "get_items": self.client.get("/api/items/?skip=0&limit=100", name="API 1: getItems"),
            "get_users": self.client.get("/api/users/?skip=0&limit=100", name="API 2: getUsers"),
            "get_root": self.client.get("/root", name="API 3: getRoot")
        }
        
        # 전체 페이지 로드 시간 계산
        total_load_time = time.time() - start_time
        
        # 사용자 정의 메트릭으로 전체 페이지 로드 시간 기록
        self.environment.events.request.fire(
            request_type="PAGE",
            name="Main Page Complete Load",
            response_time=total_load_time * 1000,  # 밀리초로 변환
            response_length=0,
            exception=None,
        )
        
        # 모든 API 응답 검증
        for api_name, response in responses.items():
            if response.status_code != 200:
                self.environment.events.request.fire(
                    request_type="FAILED",
                    name=f"Main Page - {api_name} Failed",
                    response_time=0,
                    response_length=0,
                    exception=Exception(f"Status code: {response.status_code}"),
                )