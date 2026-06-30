import type { Dashboard, MarketsResponse } from "./types";
import { FALLBACK_MARKETS } from "./lib/markets";

const headers = { "X-API-Key": "dev-key" };

export async function fetchDashboard(): Promise<Dashboard> {
  const res = await fetch("/api/v1/dashboard", { headers });
  if (!res.ok) throw new Error("Failed to load dashboard");
  return res.json();
}

export async function fetchMarkets(): Promise<MarketsResponse> {
  try {
    const res = await fetch("/api/v1/markets", { headers });
    if (!res.ok) return FALLBACK_MARKETS;
    return res.json();
  } catch {
    return FALLBACK_MARKETS;
  }
}
