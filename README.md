# PlanIt (Flask API)

Backend for **PlanIt**, a personal planner that shows where your time goes. Users log events (study, hobby, sports, chores, miscellaneous) with a start and end time. The API returns the share of time spent per category for a day, week, month or year.

Built December 2023 – February 2024. Status: **prototype API**. There is no frontend in this repository (see [Status](#status)).

## API

| Method | Route | Body / params | Returns |
|---|---|---|---|
| POST | `/register` | `username`, `email`, `password` | Creates a user. Passwords are hashed with Werkzeug. |
| POST | `/login` | `username`, `password` | Checks credentials and opens a 30-minute session |
| POST | `/api/events` | `title`, `date`, `start_time`, `end_time`, `category` | Creates an event and computes its duration |
| GET | `/api/events/<YYYY-MM-DD>` | – | Events on that date |
| GET | `/api/events/summary` | `year`, `month`, `day`, `time_period` (1 = day, 2 = week, 3 = month, 4 = year) | Fraction of time per category, for example `{"study": 0.5, "hobby": 0.25, ...}` |
| GET | `/logout` | – | Ends the Flask-Login session |

Categories: `hobby`, `study`, `sports`, `chores`, `miscellaneous`.

## Stack

Flask · Flask-SQLAlchemy · Flask-Migrate · Flask-Login · Flask-CORS · PostgreSQL

```
run.py                 entry point
website/__init__.py    app factory and configuration (from environment variables)
website/models.py      User, Event, Session
website/routes.py      endpoints
```

## Running locally

```bash
python -m venv .venv && .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                 # set DATABASE_URL and SECRET_KEY
flask db init && flask db migrate && flask db upgrade
flask run                                            # http://127.0.0.1:5000
```

## Status

This is an early prototype, documented as-is:

- **Events aren't linked to users.** `owner` is never set, so summaries aggregate everyone's events.
- **Sessions aren't enforced.** Login stores a session row, but no endpoint checks it. `@login_required` sits above `@route`, where it has no effect, and `is_active` is defined outside the `Session` class.
- **Time format mismatch.** Duration is computed from `HH.MM.SS` strings, but `start_time` and `end_time` are `DateTime` columns.
- **The summary endpoint is a `GET` with a JSON body.** Week, month and year filters compare against strings, so `year` and `month` must be sent as strings.
- **Invalid categories return 201** instead of a 4xx error.
