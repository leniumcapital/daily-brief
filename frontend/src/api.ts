import type { Dashboard, MarketsResponse } from "./types";

const headers = { "X-API-Key": "dev-key" };

export async function fetchDashboard(): Promise<Dashboard> {
  const res = await fetch("/api/v1/dashboard", { headers });
  if (!res.ok) throw new Error("Failed to load dashboard");
  return res.json();
}

export async function fetchMarkets(): Promise<MarketsResponse> {
  const res = await fetch("/api/v1/markets", { headers });
  if (!res.ok) throw new Error("Failed to load markets");
  return res.json();
}
