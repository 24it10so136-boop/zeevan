INSERT INTO symptoms (name, category) VALUES
  ('headache', 'pain'),
  ('fever', 'systemic'),
  ('nausea', 'digestive'),
  ('fatigue', 'energy'),
  ('cold symptoms', 'respiratory'),
  ('pain', 'pain'),
  ('breathing problem', 'respiratory')
ON CONFLICT (name) DO NOTHING;

-- Demo accounts are intentionally not seeded with passwords.
-- Register through POST /api/auth/register or the Profile page.
