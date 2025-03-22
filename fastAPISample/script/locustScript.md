```
from locust import HttpUser, task, between
import time

class MainPageUser(HttpUser):
    wait_time = between(3, 5)  # 사용자가 페이지 간 이동하는 평균 시간
    
    @task
    def load_main_page(self):
        # 메인 페이지 로드 시작 시간 기록
        start_time = time.time()
        
        # 병렬 요청 - 실제 브라우저 동작 시뮬레이션
        responses = {
            "user_profile": self.client.get("/api/user/profile", name="API 1: User Profile"),
            "notifications": self.client.get("/api/notifications", name="API 2: Notifications"),
            "content_feed": self.client.get("/api/content", name="API 3: Content Feed"),
            "recommendations": self.client.get("/api/recommendations", name="API 4: Recommendations"),
            "analytics": self.client.get("/api/analytics", name="API 5: Analytics"),
            "settings": self.client.get("/api/settings", name="API 6: Settings"),
            "search": self.client.get("/api/search/default", name="API 7: Search"),
            "messages": self.client.get("/api/messages/summary", name="API 8: Messages"),
            "categories": self.client.get("/api/categories", name="API 9: Categories"),
            "trending": self.client.get("/api/trending", name="API 10: Trending")
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