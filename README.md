# Zeevan

Zeevan is a symptom awareness web app built with React, FastAPI, a trained model, and PostgreSQL. Its predictions are educational and are not a medical diagnosis.

## Repository contents

- `frontend/` — React + Vite interface.
- `backend/` — FastAPI API, authentication, symptom analysis, and model inference.
- `backend/app/ml/artifacts/symptom_model.joblib` and `data/raw/training_data.csv` — model files required at runtime.
- `database/schema.sql` and `database/seed.sql` — PostgreSQL schema and starter data.
- `Dockerfile` and `render.yaml` — production build and Render deployment configuration.
- `docker-compose.yml` and `backend/Dockerfile` — optional local development setup.

Local `.env` files, databases, dependency folders, and build output are excluded from Git.

## Deploy on Render with Neon PostgreSQL

1. Create a free PostgreSQL project at [Neon](https://neon.tech/). Copy its pooled connection string from the Neon dashboard. Keep the password private.
2. In Render, choose **New → Blueprint**, connect this GitHub repository, and select the branch `main`. Render reads `render.yaml` and uses the root `Dockerfile` to build the frontend and backend into one service.
3. When prompted, set `DATABASE_URL` to the Neon connection string. The blueprint generates `JWT_SECRET` automatically. Do not commit either value to GitHub.
4. Choose the **Free** web service plan and finish creating the Blueprint. After the build succeeds, Render displays the public `onrender.com` URL. Check `/api/health` on that URL.
5. The app creates its tables in PostgreSQL automatically at startup. `database/schema.sql` and `database/seed.sql` are available if you need to initialize tables manually; do not run schema creation twice if the app has already created them.

The free Render web service sleeps after 15 minutes without traffic, and its first request after sleeping can take about a minute. Its filesystem is temporary, so user records must stay in Neon, not SQLite or files. Neon free usage has limits; review its current limits and stay within them. Render's own free PostgreSQL expires after 30 days, so this setup uses Neon for the database.

This project is a demo, not a clinically validated medical service. Do not store real patient information in it.

## Run locally

Requirements: Node.js 20+, Python 3.11+, and Docker Desktop.

1. Copy `backend/.env.example` to `backend/.env`; set `DATABASE_URL` for local PostgreSQL and a private `JWT_SECRET`.
2. Start PostgreSQL: `docker compose up -d db`.
3. Install backend packages: `pip install -r backend/requirements.txt`.
4. Start the API: `python backend/run.py`.
5. In another terminal, run `npm --prefix frontend install` and `npm --prefix frontend run dev`.
6. Open the Vite URL, normally `http://localhost:5173`.

## Push later changes

```powershell
git add .
git commit -m "Describe the change"
git push
```

Render automatically redeploys after pushes to `main`.
