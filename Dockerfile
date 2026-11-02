FROM node:20-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend/app/ /app/backend/app/
COPY backend/run.py /app/backend/run.py
COPY data/raw/training_data.csv /app/data/raw/training_data.csv
COPY reports/model_evaluation.json /app/reports/model_evaluation.json
COPY --from=frontend-build /build/frontend/dist/ /app/frontend/dist/
EXPOSE 10000
CMD ["python", "backend/run.py"]
