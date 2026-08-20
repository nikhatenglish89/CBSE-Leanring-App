# EduSphere CBSE

> Working name — placeholder, configurable via env/config, not hardcoded (see `docs/ARCHITECTURE.md` §2).

An original, India-focused online learning platform for CBSE students (primarily classes
6–12), covering video lessons, study material, live classes, an online test engine, Q&A,
subscriptions, and an AI learning assistant — built for students, parents, teachers, and
administrators on an API-first architecture designed to scale from thousands of concurrent
users toward millions over time.

## Status

**Architecture phase — implementation not yet started.**

This repository currently contains the proposed system architecture, database design, API
conventions, and project folder skeleton. Per the project's own development methodology,
implementation begins only after this architecture is explicitly reviewed and approved.

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

_TODO — pending Phase 1 implementation (auth, users, roles, permissions foundation)._

## License / Content Notice

Seed and demo educational content in this repository is original and fictional. This
project does not include or reproduce copyrighted NCERT/CBSE textbook content.
