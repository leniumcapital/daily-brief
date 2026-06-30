import type { BriefingItem } from "../types";
import { formatRelativeTime } from "../lib/dashboard";
import { Panel } from "./Panel";

interface FinanceNewsProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function FinanceNews({ items, isLoading }: FinanceNewsProps) {
  const [featured, ...rest] = items;

  return (
    <Panel
      title="Finance"
      accent="finance"
      className="min-h-[420px]"
      trailing={
        <span className="text-xs font-medium text-slate-400">
          {items.length} {items.length === 1 ? "story" : "stories"}
        </span>
      }
    >
      <div className="p-5">
        {isLoading && <p className="text-sm text-slate-400">Loading finance news...</p>}

        {!isLoading && items.length === 0 && (
          <p className="text-sm text-slate-500">No finance headlines yet.</p>
        )}

        {featured && (
          <article className="mb-4 rounded-xl border border-slate-100 bg-slate-50/50 p-5">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">
                {featured.source_name} · {formatRelativeTime(featured.published_at)}
              </span>
              <span className="rounded-lg bg-white px-2.5 py-1 text-xs font-bold text-slate-600 ring-1 ring-slate-200">
                {Math.round(featured.relevance_score * 100)}
              </span>
            </div>
            <h3 className="text-lg font-bold leading-snug text-ink">
              <a
                href={featured.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-markets"
              >
                {featured.headline}
              </a>
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">{featured.summary}</p>
          </article>
        )}

        {rest.length > 0 && (
          <div className="space-y-1 rounded-xl border border-slate-100">
            {rest.map((item) => (
              <a
                key={item.id}
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between border-b border-slate-100 px-4 py-3 last:border-0 hover:bg-slate-50"
              >
                <p className="truncate pr-3 text-sm font-medium text-ink">{item.headline}</p>
                <span className="shrink-0 text-xs text-slate-400">
                  {Math.round(item.relevance_score * 100)}
                </span>
              </a>
            ))}
          </div>
        )}
      </div>
    </Panel>
  );
}
