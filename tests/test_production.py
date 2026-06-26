from fastapi.testclient import TestClient


def test_dead_letter_task_registered() -> None:
    from workers.tasks.stub import record_dead_letter

    result = record_dead_letter.run(
        task_name="workers.tasks.analyze_video.analyze_video_task",
        task_id="task-123",
        args=["task-123"],
        kwargs={},
        error="boom",
    )
    assert result["status"] == "dead_letter"
    assert result["task_id"] == "task-123"


def test_request_id_header(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-test-1"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "req-test-1"
