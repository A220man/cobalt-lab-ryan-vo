# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

job-evaluation

## Roadmap

### skeleton — FastAPI backend + Vite/React frontend skeleton

Status: done

Acceptance:
- FastAPI app starts with /api/health returning 200
- React dev server starts and renders the dashboard
- SQLite database initializes with job/profile/evaluation tables

Implementation: `backend/app/main.py`, `backend/app/database.py`, `backend/app/config.py`, `frontend/package.json`, `frontend/src/main.tsx`

Tests: `backend/tests/test_app.py::test_health`

### job-evaluation — Job fit evaluation engine with multi-dimensional scoring

Status: done

Acceptance:
- Create and retrieve a candidate profile via API
- Submit a job posting with title, company, description, requirements via API
- POST /api/v1/evaluations returns an overall fit score with per-dimension breakdown and dealbreaker hits
- GET /api/v1/ranking returns jobs sorted by evaluation score
- Scoring engine is deterministic and tested independently

Implementation: `backend/app/core/scoring.py`, `backend/app/core/text.py`, `backend/app/models/profile.py`, `backend/app/models/job.py`, `backend/app/models/evaluation.py`, `backend/app/schemas.py`, `backend/app/api/profiles.py`, `backend/app/api/jobs.py`, `backend/app/api/evaluations.py`, `backend/app/services/evaluation_service.py`, `frontend/src/api/client.ts`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/ProfilePage.tsx`, `frontend/src/components/ProfileForm.tsx`, `frontend/src/components/JobForm.tsx`, `frontend/src/components/EvaluationResult.tsx`, `frontend/src/types.ts`, `backend/Dockerfile`, `frontend/Dockerfile`, `compose.yaml`

Tests: `backend/tests/test_scoring.py`, `backend/tests/test_jobs_api.py`, `backend/tests/test_profiles_api.py`, `backend/tests/test_evaluations_api.py`, `backend/tests/test_text.py`, `backend/tests/test_app.py`, `frontend/src/__tests__/Dashboard.test.tsx`, `frontend/src/__tests__/ProfileForm.test.tsx`, `frontend/src/__tests__/EvaluationResult.test.tsx`

### job-ranking — Batch job ranking with shortlist and filtering

Status: planned

Acceptance:
- Import multiple job postings
- Rank all jobs against the default profile in a single operation
- Filter by minimum score threshold
- Export ranked results as CSV

### application-tracking — Application status tracking with state machine

Status: planned

Acceptance:
- Jobs transition through new -> scored -> expired / fetch_failed states
- Expired jobs (deadline passed) are distinguished from fetch_failed jobs
- fetch_failed jobs remain eligible for retry
- Step 5 report lists unassessed fetch_failed jobs separately

### auth-sso — Keycloak OIDC authentication with SAML brokering

Status: planned

Acceptance:
- SPA PKCE login flow completes with state + nonce + PKCE
- Tokens validated via issuer/audience claims
- Role-based authorization on all data endpoints
- Local demo mode refuses to start in production

### llm-enrichment — Optional LLM-powered fit explanations (advisory only)

Status: planned

Acceptance:
- LLM_API_KEY is the only LLM credential variable
- OpenAI-compatible, Anthropic, and Gemini adapters via httpx
- Offline mode works without any LLM key
- Provider errors are redacted, never fabricated
- Explanations labeled advisory and grounded in evaluation records

