# Cobalt Lab — Ryan Vo

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


AI-powered job application evaluation framework. Evaluates job-posting fit for a candidate profile using a deterministic, multi-dimensional scoring engine.

## Quick Start

### Local Development

**Backend**

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Run tests
PYTHONPATH=backend .venv/bin/python -m pytest tests/ -v

# Start server
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173
npm test          # run frontend tests
npm run build     # production build
```

**Docker (one command)**

```bash
docker compose up --build
# Frontend: http://localhost
# Backend API: http://localhost:8000
```

## API Overview

| Method   | Endpoint                    | Description                         |
|----------|-----------------------------|-------------------------------------|
| GET      | `/api/health`               | Health check                        |
| PUT      | `/api/v1/profiles/default`  | Create or update the default profile|
| GET      | `/api/v1/profiles/default`  | Retrieve the default profile        |
| POST     | `/api/v1/jobs`              | Create a job posting                |
| GET      | `/api/v1/jobs`              | List all jobs                       |
| GET      | `/api/v1/jobs/{id}`         | Get a job by ID                     |
| POST     | `/api/v1/evaluations`       | Evaluate a job against the profile  |
| GET      | `/api/v1/evaluations`       | List evaluations (optional `job_id`)|
| GET      | `/api/v1/ranking`           | Ranked jobs by fit score            |

API documentation is available at `/docs` (Swagger UI) and `/redoc`.

## Scoring Engine

The `ScoringEngine` evaluates a job posting against a candidate profile across five dimensions:

| Dimension      | Weight | Algorithm                                          |
|----------------|--------|----------------------------------------------------|
| Skills match   | 0.40   | Jaccard similarity of normalized skill sets         |
| Experience     | 0.20   | Level ordinal comparison (entry → lead)            |
| Location       | 0.15   | Location keyword + remote affinity matching        |
| Role type      | 0.15   | Job title keyword overlap with preferred roles     |
| Dealbreakers   | 0.10   | Binary: 0.0 if any dealbreaker keyword is found     |

**Overall score** = Σ(dimension_score × weight)

The engine is fully deterministic and runs offline — no LLM API key required.

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app, route registration
│   ├── config.py        # Pydantic settings
│   ├── database.py      # SQLAlchemy engine, session, base
│   ├── schemas.py       # Pydantic request/response models
│   ├── models/          # SQLAlchemy ORM models
│   ├── core/            # Domain engine (scoring, text utils)
│   ├── api/             # HTTP route handlers
│   ├── services/        # Business logic orchestration
│   └── tests/           # Test suite
├── requirements.txt
└── Dockerfile

frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile
├── nginx.conf
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/client.ts    # Typed fetch client
    ├── types.ts         # Shared TypeScript types
    ├── components/      # Reusable UI components
    └── pages/           # Route-level page components
```

## Configuration

Environment variables (see `.env.example`):

| Variable       | Default                    | Description                    |
|----------------|----------------------------|--------------------------------|
| `DATABASE_URL` | `sqlite:///./app.db`       | Database connection string   |
| `HOST`         | `0.0.0.0`                  | Bind address                   |
| `PORT`         | `8000`                     | Bind port                      |
| `LOG_LEVEL`    | `info`                     | Logging verbosity              |
| `VITE_API_URL` | `http://127.0.0.1:8000`    | Frontend API base URL (Vite → browser) |

## Testing

```bash
# Backend
PYTHONPATH=backend .venv/bin/python -m pytest backend/tests -v

# Frontend
cd frontend && npm test
```

## License

MIT
Maintainer: Ryan Vo <ryandtvo@gmail.com>
