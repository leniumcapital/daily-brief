import type { BriefingItem } from "../types";
import { formatRelativeTime } from "../lib/dashboard";

const PLACEHOLDER_ACCOUNTS = ["@elonmusk", "@fintech", "@markets", "@a16z", "@naval"];

interface TwitterTrackerProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function TwitterTracker({ items, isLoading }: TwitterTrackerProps) {
  return (
    <aside className="card flex h-full flex-col overflow-hidden">
      <div className="border-b border-slate-100 bg-gradient-to-r from-sky-50 to-white px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-twitter/10 text-twitter">
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          </div>
          <div>
            <h2 className="text-sm font-bold text-ink">X Tracker</h2>
            <p className="text-xs text-slate-500">Accounts & keywords you follow</p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {PLACEHOLDER_ACCOUNTS.map((handle) => (
            <span
              key={handle}
              className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200"
            >
              {handle}
            </span>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <p className="p-5 text-sm text-slate-400">Loading feed...</p>
        )}
        {!isLoading && items.length === 0 && (
          <div className="p-5 text-center">
            <p className="text-sm text-slate-500">No posts yet</p>
            <p className="mt-1 text-xs text-slate-400">
              Add X API key in .env to enable live tracking
            </p>
          </div>
        )}
        <ul className="divide-y divide-slate-100">
          {items.map((item) => (
            <li key={item.id}>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block px-5 py-4 transition-colors hover:bg-sky-50/50"
              >
                <p className="text-sm font-medium leading-snug text-ink line-clamp-3">
                  {item.headline}
                </p>
                <p className="mt-2 text-xs text-slate-400">{formatRelativeTime(item.published_at)}</p>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
