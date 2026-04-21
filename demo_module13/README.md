# Demo Module 11

This is a short, one-hour teaching demo for Module 11.

The goal is to introduce the core Module 11 ideas before students work in the full `module11_is601` project:

- Pydantic schemas validate calculation input.
- SQLAlchemy models represent database-ready calculation objects.
- A `type` column acts as a discriminator for polymorphic inheritance.
- A factory method creates the correct subclass.
- Each subclass implements `get_result()` differently.
- FastAPI shows the flow in `/docs`, but this demo does not save to a database.

## Folder Structure

```text
demo_module 11/
├── app/
│   ├── models/
│   │   ├── base.py
│   │   ├── calculation.py
│   │   └── user.py
│   └── schemas/
│       └── calculation.py
├── tests/
│   ├── conftest.py
│   └── test_module11_demo.py
├── docker-compose.yml
├── main.py
├── requirements.txt
└── README.md
```

This mirrors the idea of the real Module 11 project while staying small enough
to use as a live lecture demo.

## Setup

From the projects folder:

```bash
cd "/home/dale/Desktop/IS601/projects/demo_module 11"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The FastAPI Demo

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

You should now see both:

```text
POST /users
POST /calculate
```

The user routes are intentionally simple and keep data in memory so you can
demonstrate model-to-route flow before introducing real database persistence.

Try this request body for `POST /users`:

```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "first_name": "Demo",
  "last_name": "User"
}
```

In Swagger UI, try:

```text
POST /calculate
```

With this request body:

```json
{
  "type": "addition",
  "inputs": [1, 2, 3],
  "user_id": "demo-user-1"
}
```

You should see a response like:

```json
{
  "type": "addition",
  "inputs": [1.0, 2.0, 3.0],
  "result": 6.0,
  "class_name": "Addition",
  "persisted": false
}
```

Try division by zero to show Pydantic validation:

```json
{
  "type": "division",
  "inputs": [100, 0],
  "user_id": "demo-user-1"
}
```

FastAPI should return a validation error.

## Run The Tests

```bash
pytest -v
```

The tests are intentionally small so students can read them as examples.

## Simple User Model

The demo now also includes a very small `User` model in `app/models/user.py`.

It is intentionally simple so you can introduce:

- a second SQLAlchemy model in the same project
- a shared `Base` class for multiple models
- the idea that calculations will eventually belong to users

The demo user model includes:

- `id`
- `username`
- `email`
- `first_name`
- `last_name`
- `created_at`

This keeps the lecture version lightweight before students move into the fuller
authentication and persistence work in Module 12.

## Run Postgres And pgAdmin With Docker Compose

For a simple database demo, start PostgreSQL and pgAdmin with:

```bash
docker compose up -d
```

This compose file starts:

- Postgres
- pgAdmin

You can stop it with:

```bash
docker compose down
```

If you also want to remove the Postgres volume:

```bash
docker compose down -v
```

### Postgres Connection Details

- database: `demo_module11`
- username: `postgres`
- password: `postgres`
- host port: `5434`

### pgAdmin Login

Open:

```text
http://127.0.0.1:5050
```

Use:

- email: `admin@example.com`
- password: `admin`

### pgAdmin Server Setup

Inside pgAdmin, add a new server with:

- Host name/address: `db`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Maintenance database: `demo_module11`

## Teaching Flow

1. Start with `app/schemas/calculation.py`.

Explain that schemas protect the application boundary. Bad data should fail before it reaches the model logic.

2. Move to `app/models/calculation.py`.

Explain that this is a SQLAlchemy model representing a row that could later be stored.

3. Point out the `type` column.

Explain that `type` is the discriminator column. It identifies whether a calculation is an addition, subtraction, multiplication, or division.

4. Show the subclasses.

All subclasses share `get_result()`, but each implements the calculation differently.

5. Move to `main.py`.

Explain that FastAPI receives the schema, creates a calculation object, calls `get_result()`, and returns a response.

6. Show the factory method.

Explain that `Calculation.create("addition", user_id, [1, 2, 3])` returns an `Addition` object.

7. End with the database boundary.

This demo does not persist anything. To store a calculation later, a route or service would need:

```python
db.add(calculation)
db.commit()
db.refresh(calculation)
```

## Suggested Class Exercise

Ask students to add a `Power` operation.

They should update:

- `CalculationType`
- The factory mapping
- Add a `Power` subclass
- Add one new demo input
- Add one new pytest test
