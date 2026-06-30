import type { BriefingItem, BriefingSection, Dashboard } from "../types";

export function getSection(dashboard: Dashboard | undefined, category: string): BriefingItem[] {
  if (!dashboard) return [];
  const section = dashboard.sections.find((s: BriefingSection) => s.category === category);
  return section?.items ?? [];
}

export function getTwitterItems(dashboard: Dashboard | undefined): BriefingItem[] {
  return dashboard?.twitter_section?.items ?? [];
}

export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function sectionLabel(section: BriefingSection): string {
  return section.label;
}
