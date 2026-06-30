import type { BriefingItem } from "../types";
import { formatRelativeTime } from "../lib/dashboard";
import { Panel } from "./Panel";

const TRACKED_ACCOUNTS = ["@elonmusk", "@fintech", "@markets", "@a16z", "@naval"];

interface TwitterTrackerProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function TwitterTracker({ items, isLoading }: TwitterTrackerProps) {
  return (
    <Panel
      title="X Tracker"
      subtitle="Accounts & keywords you follow"
      accent="twitter"
      className="min-h-[420px]"
    >
      <div className="flex flex-col p-5">
        <div className="mb-4 flex flex-wrap gap-2">
          {TRACKED_ACCOUNTS.map((handle) => (
            <span
              key={handle}
              className="rounded-full bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-600 ring-1 ring-slate-200"
            >
              {handle}
            </span>
          ))}
        </div>

        {isLoading && <p className="text-sm text-slate-400">Loading feed...</p>}

        {!isLoading && items.length === 0 && (
          <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/80 px-4 py-10 text-center">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-sky-100 text-sky-600">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-600">No posts yet</p>
            <p className="mt-1.5 max-w-[200px] text-xs leading-relaxed text-slate-400">
              Add your X API key in .env to enable live tracking
            </p>
          </div>
        )}

        <ul className="-mx-5 mt-2 divide-y divide-slate-100 border-t border-slate-100">
          {items.map((item) => (
            <li key={item.id}>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block px-5 py-3.5 transition-colors hover:bg-sky-50/60"
              >
                <p className="text-sm font-medium leading-snug text-ink line-clamp-2">
                  {item.headline}
                </p>
                <p className="mt-1.5 text-xs text-slate-400">
                  {formatRelativeTime(item.published_at)}
                </p>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </Panel>
  );
}
