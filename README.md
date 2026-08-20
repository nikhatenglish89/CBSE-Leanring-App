# EduSphere CBSE

> Working name — placeholder, configurable via env/config, not hardcoded (see `docs/ARCHITECTURE.md` §2).

An original, India-focused online learning platform for CBSE students (primarily classes
6–12), covering video lessons, study material, live classes, an online test engine, Q&A,
subscriptions, and an AI learning assistant — built for students, parents, teachers, and
administrators on an API-first architecture designed to scale from thousands of concurrent
users toward millions over time.

## Status

**Phase 2 complete: Authentication, Users, Roles & Permissions.**

Register/login/refresh/logout work end-to-end against a real FastAPI backend with RBAC
enforced server-side (`require_permission(...)`), backed by a SQLAlchemy schema and Alembic
migration. The React frontend has a working login/register flow, a protected route example,
and the shared design-system primitives. See `docs/ARCHITECTURE.md` §12 for the full 12-phase
roadmap — Phase 3 (Classes/Subjects/Courses/Chapters/Lessons) is next.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture, tech stack, module
  dependency diagram, frontend/backend/API/security/deployment design, and the 12-phase
  development roadmap.
- [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md) — full entity-relationship diagram
  and schema design rationale.
- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) — API conventions, response
  envelope, and endpoint reference.

## Repository Layout

```
cbse-learning-platform/
├── frontend/        # React + TypeScript + Vite SPA
├── backend/          # FastAPI modular monolith (app/modules/*)
├── database/           # Alembic migrations, seed scripts, ERD assets
├── docs/                 # Architecture & design documentation
├── deployment/             # Dockerfiles, docker-compose, infra config
├── scripts/                  # Dev/setup/seed helper scripts
└── tests/                      # Backend + frontend test suites
```

See `docs/ARCHITECTURE.md` §5 for the fully expanded folder structure.

## Getting Started

### Backend

Local dev runs against SQLite with zero external services (no Docker/Postgres required); set
`DATABASE_URL` to a Postgres URL to run against Postgres instead — the schema is
Postgres-compatible.

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
alembic upgrade head
python ../scripts/seed_dev_data.py   # creates roles/permissions + 5 demo accounts
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`. Demo accounts (dev only — see `scripts/seed_dev_data.py`):
`admin@edusphere.dev` / `teacher@edusphere.dev` / `student@edusphere.dev` /
`parent@edusphere.dev` / `support@edusphere.dev`, all with password `DevPass123!`.

Run tests: `pytest` (from `backend/`, venv active).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` (defaults to `http://localhost:8000/api/v1`) if the backend runs
elsewhere.

### Docker (full stack, requires Docker)

```bash
cp .env.example .env   # fill in real values
docker compose -f deployment/docker-compose.yml up --build
```

## License / Content Notice

Seed and demo educational content in this repository is original and fictional. This
project does not include or reproduce copyrighted NCERT/CBSE textbook content.
