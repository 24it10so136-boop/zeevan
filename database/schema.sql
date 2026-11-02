CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(200) NOT NULL,
  email VARCHAR(320) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  date_of_birth VARCHAR(32),
  gender VARCHAR(32),
  preferred_language VARCHAR(32) NOT NULL DEFAULT 'English',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS symptoms (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) UNIQUE NOT NULL,
  category VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS symptom_checks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
  initial_description TEXT NOT NULL,
  normalized_symptoms TEXT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  follow_up_answers TEXT,
  result_json TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS symptom_check_symptoms (
  id SERIAL PRIMARY KEY,
  symptom_check_id INTEGER NOT NULL REFERENCES symptom_checks(id) ON DELETE CASCADE,
  symptom_id INTEGER NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
  severity VARCHAR(32),
  duration VARCHAR(64),
  UNIQUE(symptom_check_id, symptom_id)
);

CREATE TABLE IF NOT EXISTS follow_up_questions (
  id SERIAL PRIMARY KEY,
  symptom_check_id INTEGER NOT NULL REFERENCES symptom_checks(id) ON DELETE CASCADE,
  question_key VARCHAR(80) NOT NULL,
  question_text TEXT NOT NULL,
  options_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS follow_up_answers (
  id SERIAL PRIMARY KEY,
  follow_up_question_id INTEGER NOT NULL REFERENCES follow_up_questions(id) ON DELETE CASCADE,
  answer VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS health_journey_notes (
  id SERIAL PRIMARY KEY,
  symptom_check_id INTEGER NOT NULL REFERENCES symptom_checks(id) ON DELETE CASCADE,
  note TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS symptom_checks_user_id_idx ON symptom_checks(user_id);
CREATE INDEX IF NOT EXISTS symptom_checks_created_at_idx ON symptom_checks(created_at DESC);
