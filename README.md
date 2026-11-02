# ZEEVAN — Full-Stack Health Companion

Zeevan is a calm AI-powered health-awareness app. This repository is self-contained for local development on Windows and does **not** require Manus, OAuth, proprietary APIs, or paid AI services.

> Zeevan provides general health-awareness guidance, not a medical diagnosis. The local model is an educational pipeline demonstration, not a clinically validated diagnostic system.

## Publish with GitHub and Replit

The app is configured as one Replit web service: Vite builds the React app into `frontend/dist`, and FastAPI serves those files and handles `/api/*` from the same origin. The root `.replit` file contains the Replit build and start commands.

### 1. Create a GitHub repository

1. Sign in to GitHub and choose **New repository**.
2. Name it `zeevan` (or another name you prefer) and choose public or private.
3. Leave **Add a README**, **.gitignore**, and **license** unchecked. This folder already has project files and Git history will be created locally.
4. Create the empty repository and copy its HTTPS URL, such as `https://github.com/YOUR-USERNAME/zeevan.git`.

### 2. Push this project

Open PowerShell in this folder. If this is the first push from this computer, run:

```powershell
git init -b main
git add .
git status
git commit -m "Prepare Zeevan for Replit deployment"
git remote add origin https://github.com/YOUR-USERNAME/zeevan.git
git push -u origin main
```

Replace the URL with the one from your new repository. Check `git status` before committing: `.env` files, local databases, Python virtual environments, `node_modules`, and build output are excluded by `.gitignore`. The source symptom dataset and trained model are included because the app needs them to run.

For later changes, use `git add .`, `git commit -m "Describe the change"`, and `git push`.

### 3. Import the repository into Replit

1. In Replit, choose **Create App** or **Import from GitHub** and select the `zeevan` repository.
2. Wait for Replit to install the Node and Python system packages from `replit.nix`.
3. Add a PostgreSQL database using Replit's **Database** tool. Replit supplies `DATABASE_URL` to the app; publishing can use a separate production database.
4. Open **Secrets** and add `JWT_SECRET` with a long random value. Never put this value in a code file or GitHub. Keep `ACCESS_TOKEN_EXPIRE_MINUTES` at `1440` or set it as a secret if you want to change the session length.
5. Press **Run**. The `.replit` run command starts FastAPI on Replit's assigned port. Open the web preview and check that sign-in, symptom checks, and Health Journey work.

Replit documents importing GitHub projects and configuring the app with `.replit`/`replit.nix` files. See [Replit GitHub import and version control](https://docs.replit.com/replit-workspace/workspace-features/version-control) and [Replit project configuration](https://docs.replit.com/references/project-setup/configuration).

### 4. Publish and get the live URL

1. Open **Publish** in the Replit workspace.
2. Choose a public web deployment and review the build and run commands. They are already set in `.replit`.
3. Confirm the production database setting and add `JWT_SECRET` to the deployment's Secrets if Replit shows a separate deployment secrets panel.
4. Publish. Replit will show the public `*.replit.app` URL when the deployment finishes. Open it and check the same key flows.
5. Copy that URL to share the website. After future GitHub pushes, pull/sync the latest repository changes in Replit and republish.

Read [Replit's SQL database guide](https://docs.replit.com/references/data-and-storage/sql-database) and [production databases guide](https://docs.replit.com/references/data-and-storage/production-databases) before storing real user information. This project is an educational symptom guide, not a clinically validated diagnostic service.

## Architecture

```text
ZEEVAN/
├── frontend/                 # React + Vite frontend; runs with npm
│   ├── src/main.jsx          # Pages, navigation, symptom flow, local auth UI
│   ├── src/api.js            # All calls use VITE_API_URL
│   ├── .env.example
│   └── package.json
├── backend/                  # FastAPI + SQLAlchemy + JWT backend; runs with Python
│   ├── app/main.py           # REST API
│   ├── run.py                # Replit and production port-aware launcher
│   ├── app/auth.py           # Local PBKDF2 password hashing + JWT
│   ├── app/ai.py             # Local demo normalization, prediction, safety engine
│   ├── app/models.py         # PostgreSQL/SQLAlchemy tables and relationships
│   ├── requirements.txt
│   └── .env.example
├── data/
│   ├── raw/training_data.csv # public symptom-disease dataset copy
│   └── DATASET_CARD.md       # source and limitations
├── phases/                   # Phase 1, 2, and 3 implementation docs
├── backend/app/ml/           # preprocessing, training, evaluation, inference
├── reports/                  # generated model evaluation metrics
├── database/
│   ├── schema.sql            # Complete PostgreSQL schema
│   └── seed.sql              # Starter symptom data
├── docker-compose.yml        # PostgreSQL + backend one-command setup
├── .replit                   # Replit build, run, and web port settings
├── replit.nix                # Node and Python system packages for Replit
├── PROJECT_PHASES.md
└── README.md
```

## Three project phases

**Phase 1 — Product foundation** covers the frontend, FastAPI backend, PostgreSQL schema and seed data, local authentication, symptom workflow, Health Journey, and a local fallback engine. See [`phases/PHASE_1.md`](phases/PHASE_1.md).

**Phase 2 — Dataset and machine learning** uses the attributed public symptom-disease CSV in `data/raw/`. The pipeline cleans the raw headers, engineers a symptom-count feature, trains a Random Forest, evaluates accuracy and macro-F1, writes `reports/model_evaluation.json`, and saves `backend/app/ml/artifacts/symptom_model.joblib`. See [`phases/PHASE_2.md`](phases/PHASE_2.md).

**Phase 3 — Natural language and safety integration** extracts canonical symptoms from natural-language input, calls the trained model, runs an independent urgent-phrase safety engine, and returns a non-diagnostic Zeevan result. See [`phases/PHASE_3.md`](phases/PHASE_3.md).

## Prerequisites for Windows

Install:

- Node.js 20+ (includes npm): https://nodejs.org/
- Python 3.11+: https://www.python.org/downloads/windows/
- Docker Desktop: https://www.docker.com/products/docker-desktop/

During Python installation, enable **Add Python to PATH**.

## Option A — Recommended: PostgreSQL in Docker, frontend/backend local

Open PowerShell in the repository root:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env

docker compose up -d db

py -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn app.main:app --reload --port 8000
```

To retrain the local model after changing the dataset:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.ml.train
```

If PowerShell blocks activation, run once as the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Open a **second PowerShell** window:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints, normally `http://localhost:5173`.

## Option B — One-command Docker backend + database

This starts PostgreSQL and FastAPI together:

```powershell
docker compose up --build
```

Then run the frontend separately:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

The API is at `http://localhost:8000`; the frontend is at `http://localhost:5173`.

To stop containers:

```powershell
docker compose down
```

To remove the local database volume too:

```powershell
docker compose down -v
```

## Manual PostgreSQL instead of Docker

Create a PostgreSQL database named `zeevan`, then run `database/schema.sql` and `database/seed.sql` in pgAdmin or `psql`. Update `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://YOUR_USER:YOUR_PASSWORD@localhost:5432/zeevan
JWT_SECRET=use-a-long-random-development-secret
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Never commit `backend/.env` or `frontend/.env`. The repository only includes `.env.example` files.

## Local environment variables

Frontend (`frontend/.env`):

```env
VITE_API_URL=http://localhost:8000
```

Backend (`backend/.env`):

```env
DATABASE_URL=postgresql+psycopg2://zeevan:zeevan@localhost:5432/zeevan
JWT_SECRET=replace-with-a-long-random-local-secret
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## REST API

- `GET /api/health` — health check
- `GET /api/model` — trained model availability and metadata
- `GET /api/phases` — Phase 1–3 completion status
- `POST /api/auth/register` — create local account and return JWT
- `POST /api/auth/login` — sign in and return JWT
- `GET /api/auth/me` — return current user; requires Bearer token
- `POST /api/symptoms/check` — normalize symptoms, persist check, return follow-up questions
- `POST /api/symptoms/check/{id}/analyze` — run local demo analysis and persist result
- `POST /api/symptoms/{id}/save` — attach an anonymous check to the logged-in user's journey
- `GET /api/journeys` — retrieve the logged-in user's saved journey
- `POST /api/journeys/{id}/notes` — add a private journey note

Interactive API docs are available at `http://localhost:8000/docs` while the backend is running.

## Tests and verification

Backend API tests:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

Frontend build:

```powershell
cd frontend
npm install
npm run build
```

The frontend communicates with the backend exclusively through `src/api.js`, which reads `VITE_API_URL`. NLP, prediction, and safety run locally in Python. No external AI provider is needed.

The current holdout report shows 1.0 accuracy and 1.0 macro-F1 on 4,920 rows, but the source data contains repeated or near-duplicate symptom patterns. Treat that score as a pipeline check only, not evidence of real-world performance.

## Fresh-install checklist

1. Copy both `.env.example` files.
2. Start PostgreSQL (`docker compose up -d db`) or use a local PostgreSQL installation.
3. Install Python dependencies and start FastAPI on port 8000.
4. Install frontend dependencies and start Vite on port 5173.
5. Open Profile and register a local account.
6. Submit symptoms, answer follow-ups, view results, save to Health Journey, then reload Journey to retrieve persisted data.

## Safety and privacy

Zeevan's result language is deliberately non-diagnostic. Urgent symptom phrases are evaluated by a separate safety engine and produce an urgent-care notice. For real medical concerns, contact a qualified healthcare professional or local emergency services.
