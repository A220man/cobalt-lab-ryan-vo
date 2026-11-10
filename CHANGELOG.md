# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

### Added

**Backend**
- Batch job evaluation endpoint: `POST /api/v1/evaluations/batch` evaluates all "new" jobs against the default profile (or a specific profile) in a single operation
- Ranking filter: `GET /api/v1/ranking?min_score=X` returns only jobs meeting the minimum score threshold
- CSV export endpoint: `GET /api/v1/ranking/export` downloads ranked jobs as CSV with all dimension scores, skill overlap, and explanations
- `RankingExportQuery` schema with `min_score` and `limit` parameters
- `BatchEvaluationRequest` and `BatchEvaluationResponse` schemas
- `EvaluationService.evaluate_all_new_jobs()` method for batch processing
- `min_score` parameter to `EvaluationService.get_ranking()`

**Tests**
- 8 new backend integration tests covering batch evaluation, min_score filtering, and CSV export
- Total: 82 backend tests (unit + integration) — all passing
- 15 frontend tests (component) — all passing

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Fixed

- **Scoring**: Dealbreaker keyword matching now uses word-boundary regex
  `(?<!\w)...(?!\w)` to prevent false positives where a dealbreaker
  appears as a substring of a longer word (e.g., "on-call" matching
  inside "on-callback"). Added `_keyword_hits` helper function and
  test `test_word_boundary_no_false_positive`.

### Tests

- 74 backend tests (unit + integration) — all passing
- 15 frontend tests (component) — all passing
## 1.1.0 — work-in-progress checkpoint

### Changed

- **Frontend**: `EvaluationResult` component now displays dimension scores in a fixed order (skills, experience, location, role_type, dealbreakers) matching the scoring engine design, instead of sorting by score value. This makes it easier to compare evaluations side-by-side.
- **Tests**: Added 2 new tests for `EvaluationResult` verifying fixed dimension order and proper omission of missing dimensions.

### Tests

- 73 backend tests (unit + integration) — all passing
- 15 frontend tests (component) — all passing (2 new tests added)

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

# CHANGELOG

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-10-16

### Added

**Backend**
- FastAPI application with health check endpoint (`GET /api/health`)
- SQLite database via SQLAlchemy 2.0 with declarative models
  (`Profile`, `JobPosting`, `EvaluationResult`)
- Pydantic schemas for all request/response models
- ScoringEngine with 5-dimension weighted scoring:
  - Skills match (Jaccard similarity, weight 0.40)
  - Experience level (ordinal comparison, weight 0.20)
  - Location affinity (weight 0.15)
  - Role type (title keyword overlap, weight 0.15)
  - Dealbreakers (binary, weight 0.10)
- Text processing utilities: normalization, BOM stripping, skill extraction
  with word-boundary matching, experience-level detection, slug generation
  with Unicode transliteration
- REST API endpoints:
  - `PUT /api/v1/profiles/default` — upsert default profile
  - `GET /api/v1/profiles/default` — retrieve default profile
  - `POST /api/v1/jobs` — create job posting (auto-extracts skills)
  - `GET /api/v1/jobs` — list jobs
  - `GET /api/v1/jobs/{id}` — get job by ID
  - `POST /api/v1/evaluations` — evaluate a job against profile
  - `GET /api/v1/evaluations` — list evaluations
  - `GET /api/v1/ranking` — rank evaluated jobs by score
- Pydantic-settings configuration with environment variable support
- CORS middleware for local development

**Frontend**
- React 18 + TypeScript + Vite build system
- Typed API client (`src/api/client.ts`) with shared types (`src/types.ts`)
- Components:
  - `ProfileForm` — candidate profile setup/edit form
  - `JobForm` — job posting creation form
  - `EvaluationResult` — score display with per-dimension breakdown
- Pages:
  - `Dashboard` — job list, evaluation, and ranking view
  - `ProfilePage` — profile management
- Vitest + React Testing Library test suite
- Responsive CSS design

**Infrastructure**
- Multi-stage Dockerfile for backend (`backend/Dockerfile`)
- Multi-stage Dockerfile for frontend (`frontend/Dockerfile`)
- Nginx configuration for frontend static serving and API proxying
- Docker Compose for local development (`compose.yaml`)
- Root `.dockerignore` for optimized build contexts

### Tests

- 73 backend tests (unit + integration) — all passing
- 13 frontend tests (component) — all passing
- Coverage includes: scoring engine, text utilities, all API endpoints,
  form rendering/submission, evaluation display

### Fixed

- `normalize_text` now strips BOM (U+FEFF) from input
- `extract_skills` uses word-boundary matching to prevent false positives
  (e.g., "r" matching inside "recognizable")
- Experience level extraction: `principal` is checked before `lead` so
  "Principal Architect" correctly returns `principal`, not `lead`
- API routes mounted under `/api/v1/` prefix for versioned access
- Slugify Unicode handling: "Café" → "cafe" (correct decomposition)
