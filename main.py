from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A simple in-memory CRUD API for managing to-do tasks."
)

# In-memory "database"
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test with Swagger UI", "done": True},
]


def find_task(task_id: int):
    """Return a task by id, or None if it does not exist."""
    return next((task for task in tasks if task["id"] == task_id), None)


def error_response(message: str, status_code: int):
    """Return errors in the assignment's required JSON format."""
    return JSONResponse(
        status_code=status_code,
        content={"error": message}
    )


async def get_json_body(request: Request):
    """Read JSON safely and return (data, error_response)."""
    try:
        data = await request.json()
    except Exception:
        return None, error_response("Request body must be valid JSON", 400)

    if not isinstance(data, dict):
        return None, error_response("Request body must be a JSON object", 400)

    return data, None


@app.get("/", summary="Show API information")
def root():
    """Return basic information about this API."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check server health")
def health():
    """Return a simple health-check response."""
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    """Return every task stored in memory."""
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    """Return one task by id, or 404 if it does not exist."""
    task = find_task(task_id)

    if task is None:
        return error_response(f"Task {task_id} not found", 404)

    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(request: Request):
    """Create a task. A non-empty title is required."""
    data, error = await get_json_body(request)
    if error:
        return error

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return error_response("Title is required and cannot be empty", 400)

    next_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", summary="Update a task")
async def update_task(task_id: int, request: Request):
    """Update a task's title and/or done value."""
    task = find_task(task_id)

    if task is None:
        return error_response(f"Task {task_id} not found", 404)

    data, error = await get_json_body(request)
    if error:
        return error

    if not data or not any(key in data for key in ("title", "done")):
        return error_response(
            "Provide at least one field to update: title or done",
            400
        )

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return error_response("Title cannot be empty", 400)

    if "done" in data and not isinstance(data["done"], bool):
        return error_response("Done must be true or false", 400)

    if "title" in data:
        task["title"] = data["title"].strip()

    if "done" in data:
        task["done"] = data["done"]

    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """Delete a task by id and return 204 No Content."""
    task = find_task(task_id)

    if task is None:
        return error_response(f"Task {task_id} not found", 404)

    tasks.remove(task)
    return Response(status_code=204)
