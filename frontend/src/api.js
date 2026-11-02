// Production serves the frontend and API from one origin. Vite proxies /api
// to FastAPI during local development, so a relative URL works in both places.
const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export async function api(path, options = {}) {
  const token = localStorage.getItem("zeevan_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.message || "Something went wrong. Please try again.");
  return payload;
}

export function apiUrl() { return API_URL; }
