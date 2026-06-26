from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.stub.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="workers.tasks.stub.record_dead_letter")
def record_dead_letter(
    *,
    task_name: str,
    task_id: str | None,
    args: list,
    kwargs: dict,
    error: str,
) -> dict:
    return {
        "task_name": task_name,
        "task_id": task_id,
        "args": args,
        "kwargs": kwargs,
        "error": error,
        "status": "dead_letter",
    }
