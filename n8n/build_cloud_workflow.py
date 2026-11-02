import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dataset_path = root / "data" / "raw" / "training_data.csv"
workflow_path = Path(__file__).with_name("zeevan-ai-demo.workflow.json")
csv_text = dataset_path.read_text(encoding="utf-8-sig")
rows = list(csv.DictReader(csv_text.splitlines()))
columns = list(rows[0])
symptoms = [c for c in columns if c != "prognosis"]
classes = sorted({row["prognosis"].strip() for row in rows})

js = r'''// Self-contained educational demo. The CSV below is embedded at export time.
const csv = __CSV_DATA__;
const lines = csv.trim().split(/\r?\n/);
const headers = lines[0].split(',').map(s => s.trim());
const targetIndex = headers.indexOf('prognosis');
if (targetIndex < 0) throw new Error('Embedded data is missing the prognosis target column.');
const featureNames = headers.filter((_, i) => i !== targetIndex).map(s => s.replace(/^\"|\"$/g, '').trim());
const data = lines.slice(1).filter(Boolean).map(line => {
  const values = line.split(',');
  return { x: values.filter((_, i) => i !== targetIndex).map(v => Number(v) === 1 ? 1 : 0), y: values[targetIndex].trim() };
});
const labels = [...new Set(data.map(r => r.y))].sort();
if (!data.length) throw new Error('Embedded training data is empty.');

// Keep a deterministic, stratified last-20%-per-class holdout, like the project pipeline.
const byClass = new Map(labels.map(label => [label, data.filter(r => r.y === label)]));
const trainRows = [];
const testRows = [];
for (const label of labels) {
  const group = byClass.get(label);
  const cutoff = Math.max(1, Math.floor(group.length * 0.8));
  trainRows.push(...group.slice(0, cutoff));
  testRows.push(...group.slice(cutoff));
}
const priorCounts = Object.fromEntries(labels.map(label => [label, 0]));
const featureCounts = Object.fromEntries(labels.map(label => [label, Array(featureNames.length).fill(0)]));
for (const row of trainRows) {
  priorCounts[row.y]++;
  row.x.forEach((value, i) => { featureCounts[row.y][i] += value; });
}

// Train Bernoulli Naive Bayes with Laplace smoothing using only JavaScript built-ins.
const logPrior = {};
const logPresent = {};
const logAbsent = {};
for (const label of labels) {
  logPrior[label] = Math.log(priorCounts[label] / trainRows.length);
  logPresent[label] = [];
  logAbsent[label] = [];
  for (let i = 0; i < featureNames.length; i++) {
    const p = (featureCounts[label][i] + 1) / (priorCounts[label] + 2);
    logPresent[label][i] = Math.log(p);
    logAbsent[label][i] = Math.log(1 - p);
  }
}
function predict(x) {
  return labels.map(label => {
    let score = logPrior[label];
    for (let i = 0; i < featureNames.length; i++) score += x[i] ? logPresent[label][i] : logAbsent[label][i];
    return { label, score };
  }).sort((a, b) => b.score - a.score);
}

let correct = 0;
const confusion = new Map(labels.map(label => [label, new Map()]));
const holdoutPredictions = [];
for (const row of testRows) {
  const guess = predict(row.x)[0].label;
  holdoutPredictions.push({ actual: row.y, predicted: guess });
  if (guess === row.y) correct++;
  confusion.get(row.y).set(guess, (confusion.get(row.y).get(guess) || 0) + 1);
}
const accuracy = testRows.length ? correct / testRows.length : null;
const perClass = labels.map(label => {
  const tp = confusion.get(label).get(label) || 0;
  const actual = holdoutPredictions.filter(r => r.actual === label).length;
  const predicted = holdoutPredictions.filter(r => r.predicted === label).length;
  const precision = predicted ? tp / predicted : 0;
  const recall = actual ? tp / actual : 0;
  return { label, precision, recall, f1: precision + recall ? 2 * precision * recall / (precision + recall) : 0 };
});
const macro = key => perClass.reduce((s, row) => s + row[key], 0) / perClass.length;

// Example request demonstrates how feature strings become the model's candidate ranking.
const exampleSymptoms = ['high_fever', 'headache'];
const normalized = new Set(exampleSymptoms.map(s => s.toLowerCase().replace(/\s+/g, '_')));
const query = featureNames.map(name => normalized.has(name) ? 1 : 0);
const candidates = predict(query).slice(0, 5).map((r, i) => ({ rank: i + 1, dataset_label: r.label }));
const preview = data.slice(0, 5).map(row => ({
  symptoms_present: featureNames.filter((_, i) => row.x[i]).slice(0, 8),
  prognosis_label: row.y,
}));

return [{ json: {
  title: 'Zeevan self-contained model training and response demo',
  run_status: 'completed',
  data_source: 'data/raw/training_data.csv (embedded in this workflow at build time)',
  dataset: { rows: data.length, target_column: 'prognosis', classes: labels.length, symptom_features: featureNames.length, feature_names: featureNames, preview },
  training: {
    algorithm: 'Bernoulli Naive Bayes',
    implementation: 'JavaScript Code node; Laplace smoothing; no external packages or API calls',
    split: 'Deterministic stratified 80/20 per class',
    training_rows: trainRows.length,
    holdout_rows: testRows.length,
    steps: ['Read embedded labeled CSV', 'Convert each symptom column to a binary feature', 'Split rows by label into train and holdout subsets', 'Estimate class priors and symptom likelihoods with Laplace smoothing', 'Score each class for holdout rows', 'Rank classes for an example symptom request'],
    holdout_accuracy: accuracy,
    macro_precision: macro('precision'),
    macro_recall: macro('recall'),
    macro_f1: macro('f1'),
    warning: 'These are educational dataset metrics, not clinical accuracy. Repeated or near-duplicate records can inflate scores; this model is not medically validated.',
  },
  example_request: { symptoms: exampleSymptoms },
  example_response: { type: 'unvalidated dataset-label candidates, not a diagnosis', candidates },
  safety: 'Do not use this output to diagnose, choose medication, or delay professional care. Seek urgent care for severe or rapidly worsening symptoms.',
} }];'''.replace("__CSV_DATA__", json.dumps(csv_text, ensure_ascii=False))

workflow = {
    "name": "Zeevan AI Training and Response Demo (Cloud Ready)",
    "nodes": [
        {
            "parameters": {},
            "id": "a51f106b-4714-467d-b9c0-f7e28f2e3b08",
            "name": "Run Self-Contained Training Demo",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1.1,
            "position": [0, 0],
        },
        {
            "parameters": {"mode": "runOnceForAllItems", "jsCode": js},
            "id": "1fc1ee26-48aa-44ee-8303-2de7b560ab74",
            "name": "Train Model and Show Data and Response",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [260, 0],
        },
    ],
    "connections": {
        "Run Self-Contained Training Demo": {
            "main": [[{"node": "Train Model and Show Data and Response", "type": "main", "index": 0}]]
        }
    },
    "active": False,
    "settings": {"executionOrder": "v1"},
    "versionId": "848dd0af-1211-43fa-a09c-4c4c2bd8df44",
    "meta": {"templateCredsSetupCompleted": True},
    "tags": [],
}
workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {workflow_path} ({workflow_path.stat().st_size:,} bytes; {len(rows)} rows; {len(symptoms)} features; {len(classes)} labels)")
