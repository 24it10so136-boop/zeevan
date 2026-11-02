# Zeevan

Zeevan is a symptom awareness web app. It uses a React frontend, a FastAPI backend, a trained model, and PostgreSQL for accounts and saved symptom journeys. Its predictions are educational and are not a medical diagnosis.

## What is in this repository

- `frontend/` — React + Vite user interface.
- `backend/` — FastAPI API, symptom analysis, authentication, and model inference.
- `backend/app/ml/artifacts/symptom_model.joblib` — trained model required by predictions.
- `data/raw/training_data.csv` — training data required by the model pipeline.
- `database/schema.sql` and `database/seed.sql` — PostgreSQL schema and starter data. The app also creates SQLAlchemy tables on startup.
- `.replit` and `replit.nix` — Replit run/build environment configuration.
- `docker-compose.yml` — local PostgreSQL and backend setup for development.

Local environment files, database files, caches, build output, and dependencies are excluded by `.gitignore`.

## Run locally

Requirements: Node.js 20+, Python 3.11+, and Docker Desktop.

1. Copy `backend/.env.example` to `backend/.env`, then set a private `JWT_SECRET` and your PostgreSQL `DATABASE_URL`.
2. Start PostgreSQL with `docker compose up -d db`.
3. Install backend packages: `pip install -r backend/requirements.txt`.
4. Start the API: `python backend/run.py`.
5. In another terminal, run `npm --prefix frontend install` and `npm --prefix frontend run dev`.
6. Open the Vite URL, normally `http://localhost:5173`.

## Database and deployment

The backend needs a persistent PostgreSQL database. In Replit, open the app's **Database** tool and create a PostgreSQL database, then add its connection URL as the `DATABASE_URL` secret. Add a strong random `JWT_SECRET` in **Secrets** as well. Keep both values out of GitHub. The app creates its tables from the SQLAlchemy models during startup; `database/schema.sql` and `database/seed.sql` are also available for manual setup.

The app is configured to run as one web service: Replit builds the frontend and FastAPI serves the built files and `/api` endpoints. Import this GitHub repository into Replit, set the two secrets, run it, and use **Publish** to create a public URL.

**Free-plan limitation:** Zeevan is full-stack; static hosting alone cannot run its API or database. Replit's static deployment serves frontend files, while a full-stack app requires a server deployment. Check the current Replit plan and publishing costs before publishing. Do not publish if Replit asks you to upgrade or enable paid usage and you want to stay strictly free.

## GitHub updates

After changing files locally:

```powershell
git add .
git commit -m "Describe the change"
git push
```

Then sync or pull the repository in Replit before running or publishing the updated version.

## Safety

The symptom results are educational and not clinically validated. Seek advice from a qualified healthcare professional for medical concerns.
