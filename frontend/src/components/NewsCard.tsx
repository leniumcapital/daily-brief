import type { BriefingItem } from "../types";
import { formatRelativeTime } from "../lib/dashboard";

interface NewsCardProps {
  item: BriefingItem;
  variant?: "default" | "compact" | "featured";
  accent?: "finance" | "startup" | "default";
}

const accentBorder = {
  finance: "border-l-finance",
  startup: "border-l-startup",
  default: "border-l-accent",
};

export function NewsCard({ item, variant = "default", accent = "default" }: NewsCardProps) {
  const isCompact = variant === "compact";
  const isFeatured = variant === "featured";

  return (
    <article
      className={`group border-l-2 ${accentBorder[accent]} bg-white transition-all hover:bg-slate-50/80 ${
        isFeatured ? "rounded-xl p-5 shadow-card" : isCompact ? "px-4 py-3" : "rounded-xl p-4"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2 text-xs text-slate-400">
            <span className="font-medium text-slate-500">{item.source_name}</span>
            <span>·</span>
            <time>{formatRelativeTime(item.published_at)}</time>
            {item.is_developing && (
              <span className="rounded-full bg-amber-50 px-2 py-0.5 text-amber-700">Live</span>
            )}
          </div>
          <h3
            className={`font-semibold leading-snug text-ink group-hover:text-accent ${
              isFeatured ? "text-lg" : isCompact ? "text-sm" : "text-base"
            }`}
          >
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.headline}
            </a>
          </h3>
          {!isCompact && (
            <p className={`mt-2 text-slate-600 ${isFeatured ? "text-sm leading-relaxed" : "text-sm line-clamp-2"}`}>
              {item.summary}
            </p>
          )}
        </div>
        <span className="shrink-0 rounded-lg bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
          {Math.round(item.relevance_score * 100)}
        </span>
      </div>
    </article>
  );
}
