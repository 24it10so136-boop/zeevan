# Zeevan n8n AI training and response demo (Cloud Ready)

This workflow is self-contained for n8n Cloud. It does not call `localhost`, your local FastAPI service, or any other external service. The source CSV (`data/raw/training_data.csv`) is embedded in the JSON at build time, so importing the JSON transfers the demonstration data with it.

## Import and run

1. In n8n Cloud, choose **Workflows → Import from File** and select `zeevan-ai-demo.workflow.json`.
2. Open the imported workflow and click **Execute workflow** (or the manual trigger).
3. Select **Train Model and Show Data and Response** in the execution view to inspect the output JSON: source data preview, row/class/feature counts, training steps, holdout metrics, and ranked candidate labels for an example query (`high_fever`, `headache`).

No credentials, localhost URL changes, Docker, backend server, or environment variables are required.

## What it demonstrates

The Code node runs a small Bernoulli Naive Bayes implementation in JavaScript with Laplace smoothing. It uses a deterministic per-class 80/20 training/holdout split, reports accuracy and macro precision/recall/F1, then scores an example symptom vector and returns the top five dataset labels. This makes the data-to-model-to-response path visible in a single n8n execution.

## Limitations and safety

This is an educational demonstration, not a clinical model or medical advice. The source dataset contains repeated or near-duplicate patterns, which can inflate holdout scores. Returned labels are unvalidated dataset candidates, not diagnoses. It does not recommend medicines. Do not use the output to make health decisions or delay medical care.

The workflow embeds the dataset directly, so rebuild the JSON after changing the source CSV. From the project root, run `backend\\venv\\Scripts\\python.exe n8n\\build_cloud_workflow.py`.
