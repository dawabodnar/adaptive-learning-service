# locustfile.py
from locust import HttpUser, task, between
import random

class StudentUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    session_id = None

    def on_start(self):
        # Логін
        response = self.client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        
        # Старт сесії — головний endpoint з Knapsack
        if self.token:
            resp = self.client.post(
                "/sessions/start",
                json={"time_budget_seconds": 1800},
                headers=self.auth_headers(),
                name="/sessions/start"
            )
            if resp.status_code == 201:
                self.session_id = resp.json().get("session_id")

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def get_history(self):
        """Перегляд історії сесій — найчастіший запит."""
        self.client.get(
            "/sessions/my-history",
            headers=self.auth_headers(),
            name="/sessions/my-history"
        )

    @task(2)
    def get_suggested_budget(self):
        """Запит рекомендованого бюджету часу."""
        self.client.get(
            "/sessions/suggested-budget",
            headers=self.auth_headers(),
            name="/sessions/suggested-budget"
        )

    @task(1)
    def get_session_stats(self):
        """Статистика сесії."""
        if self.session_id:
            self.client.get(
                f"/sessions/{self.session_id}/stats",
                headers=self.auth_headers(),
                name="/sessions/{id}/stats"
            )