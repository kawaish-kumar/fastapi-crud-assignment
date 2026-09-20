from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import sqlite3

DATABASE = "tasks.db"

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A SQLite CRUD API for managing to-do tasks."
)


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if count == 0:
        conn.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Test with Swagger UI", 1),
            ]
        )

    conn.commit()
    conn.close()


init_database()


def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": message}
    )


async def get_json_body(request: Request):
    try:
        data = await request.json()
    except Exception:
        return None, error_response(
            "Request body must be valid JSON", 400
        )

    if not isinstance(data, dict):
        return None, error_response(
            "Request body must be a JSON object", 400
        )

    return data, None


def row_to_task(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


@app.get("/", summary="Show API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check server health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    conn = get_connection()

    rows = conn.execute(
        "SELECT id, title, done FROM tasks ORDER BY id"
    ).fetchall()

    conn.close()

    return [row_to_task(row) for row in rows]


@app.get(
    "/tasks/{task_id}",
    summary="Get one task",
    responses={404: {"description": "Task not found"}}
)
def get_task(task_id: int):
    conn = get_connection()

    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return error_response(
            f"Task {task_id} not found", 404
        )

    return row_to_task(row)


@app.post(
    "/tasks",
    status_code=201,
    summary="Create a new task",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {
                                "type": "string",
                                "example": "SQLite Assignment"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def create_task(request: Request):
    data, error = await get_json_body(request)

    if error:
        return error

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return error_response(
            "Title is required and cannot be empty", 400
        )

    conn = get_connection()

    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title.strip(), 0)
    )

    task_id = cursor.lastrowid

    conn.commit()

    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    return row_to_task(row)


@app.put(
    "/tasks/{task_id}",
    summary="Update a task",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "example": "Updated Task"
                            },
                            "done": {
                                "type": "boolean",
                                "example": True
                            }
                        }
                    }
                }
            }
        }
    }
)
async def update_task(task_id: int, request: Request):
    data, error = await get_json_body(request)

    if error:
        return error

    if not data or not any(
        key in data for key in ("title", "done")
    ):
        return error_response(
            "Provide at least one field to update: title or done",
            400
        )

    if "title" in data:
        if (
            not isinstance(data["title"], str)
            or not data["title"].strip()
        ):
            return error_response(
                "Title cannot be empty", 400
            )

    if "done" in data and not isinstance(data["done"], bool):
        return error_response(
            "Done must be true or false", 400
        )

    conn = get_connection()

    existing = conn.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return error_response(
            f"Task {task_id} not found", 404
        )

    if "title" in data and "done" in data:
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, done = ?
            WHERE id = ?
            """,
            (
                data["title"].strip(),
                int(data["done"]),
                task_id
            )
        )

    elif "title" in data:
        conn.execute(
            "UPDATE tasks SET title = ? WHERE id = ?",
            (data["title"].strip(), task_id)
        )

    elif "done" in data:
        conn.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (int(data["done"]), task_id)
        )

    conn.commit()

    row = conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    return row_to_task(row)


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task"
)
def delete_task(task_id: int):
    conn = get_connection()

    existing = conn.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return error_response(
            f"Task {task_id} not found", 404
        )

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return Response(status_code=204)