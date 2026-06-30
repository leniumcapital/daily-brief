import type { Dashboard } from "./types";

export async function fetchDashboard(): Promise<Dashboard> {
  const res = await fetch("/api/v1/dashboard", {
    headers: { "X-API-Key": "dev-key" },
  });
  if (!res.ok) throw new Error("Failed to load dashboard");
  return res.json();
}
