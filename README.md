# Task API - SQLite CRUD

A simple REST API built with FastAPI and SQLite for managing to-do tasks.

## Technologies Used

- Python
- FastAPI
- SQLite
- Uvicorn

## Why SQLite?

SQLite was chosen because it is lightweight, easy to set up, and does not require a separate database server. It is suitable for a small CRUD application and stores the data in a local database file.

## Database

The SQLite database is stored in:

`tasks.db`

The database is automatically created when the application starts.

The `tasks` table contains:

- `id` - INTEGER PRIMARY KEY
- `title` - TEXT
- `done` - BOOLEAN

If the table is empty, the application automatically inserts three example tasks.

## How to Run the API

Open PowerShell in the project folder and run:

```bash
python -m uvicorn main:app --reload