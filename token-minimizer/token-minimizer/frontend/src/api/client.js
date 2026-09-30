const BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const getHealth = () => request("/health");

export const getModels = () => request("/models");

export const countTokens = (text) =>
  request("/count", { method: "POST", body: JSON.stringify({ text }) });

export const compressText = (text, model) =>
  request("/compress", {
    method: "POST",
    body: JSON.stringify({ text, model }),
  });
