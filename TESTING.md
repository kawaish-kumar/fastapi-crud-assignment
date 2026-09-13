# API Testing

The Task API was tested using FastAPI Swagger UI.

## Tests Completed

- GET `/tasks` returned status 200.
- POST `/tasks` created a task with status 201.
- PUT `/tasks/{id}` updated a task with status 200.
- DELETE `/tasks/{id}` deleted a task with status 204.
- GET `/tasks/{id}` retrieved a specific task.
- Unknown task IDs return 404 errors.
- Invalid request data returns 400 errors.

All main CRUD operations were tested successfully.