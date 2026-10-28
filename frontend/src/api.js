const BASE = (import.meta.env.VITE_API_URL || "").trim().replace(/\/+$/, "");

async function get(path, params = {}) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== "")
  );
  const res = await fetch(`${BASE}/api${path}?${qs}`);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export const api = {
  series: (p) => get("/series", p),
  metrics: (p) => get("/metrics", p),
  byHorizon: () => get("/metrics/by-horizon"),
  decision: (p) => get("/decision", p),
};
