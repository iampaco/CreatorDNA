import os

import pytest
from fastapi.testclient import TestClient

from apps.api.config import get_settings
from apps.api.main import app


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_client() -> TestClient:
    monkeypatch_key = os.environ.get("API_SECRET_KEY", "test-secret-key")
    os.environ["API_SECRET_KEY"] = monkeypatch_key
    os.environ["AUTH_REQUIRED"] = "true"
    get_settings.cache_clear()
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {monkeypatch_key}"})
    return client
