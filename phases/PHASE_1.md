# Phase 1 — Product foundation

## Delivered

- Separated React/Vite frontend and FastAPI backend
- PostgreSQL schema, relationships, indexes, and seed data
- Local JWT authentication with PBKDF2 password hashing
- Symptom submission and three follow-up questions
- Local demo analysis and safety engine
- Health Journey persistence and retrieval
- Docker Compose for PostgreSQL + backend

## Acceptance checks

- `GET /api/health` returns `status=ok`
- Register, login, and `GET /api/auth/me` work with Bearer JWT
- `/api/symptoms/check` returns a persisted check and follow-ups
- `/api/symptoms/check/{id}/analyze` returns results
- `/api/symptoms/{id}/save` and `/api/journeys` persist/retrieve journey data
