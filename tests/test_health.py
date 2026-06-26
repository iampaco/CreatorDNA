from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_health_liveness(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("apps.api.routers.health._check_workers")
@patch("apps.api.routers.health._check_redis")
@patch("apps.api.routers.health._check_postgres")
def test_ready_all_ok(
    mock_pg: MagicMock,
    mock_redis: MagicMock,
    mock_workers: MagicMock,
    client: TestClient,
) -> None:
    mock_pg.return_value = (True, "ok")
    mock_redis.return_value = (True, "ok")
    mock_workers.return_value = (True, "1 worker(s)")
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@patch("apps.api.routers.health._check_workers")
@patch("apps.api.routers.health._check_redis")
@patch("apps.api.routers.health._check_postgres")
def test_ready_fails_when_postgres_down(
    mock_pg: MagicMock,
    mock_redis: MagicMock,
    mock_workers: MagicMock,
    client: TestClient,
) -> None:
    mock_pg.return_value = (False, "connection refused")
    mock_redis.return_value = (True, "ok")
    mock_workers.return_value = (True, "1 worker(s)")
    response = client.get("/ready")
    assert response.status_code == 503
