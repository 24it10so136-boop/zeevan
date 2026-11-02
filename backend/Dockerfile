FROM python:3.12-slim
WORKDIR /workspace/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY data/raw/training_data.csv /workspace/data/raw/training_data.csv
COPY reports/model_evaluation.json /workspace/reports/model_evaluation.json
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
