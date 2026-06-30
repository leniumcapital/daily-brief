import type { BriefingItem } from "../types";
import { formatRelativeTime } from "../lib/dashboard";
import { Panel } from "./Panel";

interface StartupFundingProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function StartupFunding({ items, isLoading }: StartupFundingProps) {
  return (
    <Panel
      title="Startup & Funding"
      accent="startup"
      trailing={
        <span className="rounded-full bg-violet-50 px-3 py-1 text-xs font-bold text-startup ring-1 ring-violet-100">
          VC · Rounds · Tech
        </span>
      }
    >
      <div className="grid gap-0 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse border-b border-r border-slate-100 bg-slate-50" />
          ))}

        {!isLoading && items.length === 0 && (
          <p className="col-span-full p-8 text-center text-sm text-slate-500">
            No startup funding news yet.
          </p>
        )}

        {items.map((item) => (
          <article
            key={item.id}
            className="border-b border-r border-slate-100 p-5 transition-colors hover:bg-violet-50/30 lg:[&:nth-child(3n)]:border-r-0"
          >
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500">
                {item.source_name} · {formatRelativeTime(item.published_at)}
              </span>
              <span className="rounded-md bg-violet-50 px-2 py-0.5 text-xs font-bold text-startup">
                {Math.round(item.relevance_score * 100)}
              </span>
            </div>
            <h3 className="font-bold leading-snug text-ink">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-startup"
              >
                {item.headline}
              </a>
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600 line-clamp-3">{item.summary}</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}
