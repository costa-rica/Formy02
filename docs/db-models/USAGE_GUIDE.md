---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Database Usage Guide

Startup order is:

1. `configure_logging()`
2. `check_database()`
3. `create_db_and_tables()`

`check_database()` first executes `SELECT 1` against PostgreSQL, then creates SQLModel metadata if the connection is healthy. Startup raises on database failure.

The engine URL is built from environment variables:

```python
postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
```

FastAPI routes use the `get_session()` dependency:

```python
def get_session():
    with Session(engine) as session:
        yield session
```

Example SQLModel query:

```python
questions = db.exec(select(Question).where(Question.is_active == True)).all()
```

Example insert:

```python
person = SurveyedPerson(name="Ada")
db.add(person)
db.commit()
db.refresh(person)
```

The restore route intentionally uses `require_admin_for_restore`, which opens and closes its own session before `pg_restore` runs so the application does not hold ORM locks during restore.
