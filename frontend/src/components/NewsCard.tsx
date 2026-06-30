import type { BriefingItem } from "./types";

const contentTypeBadge: Record<string, string> = {
  reporting: "bg-blue-100 text-blue-800",
  opinion: "bg-purple-100 text-purple-800",
  analysis: "bg-indigo-100 text-indigo-800",
  social: "bg-sky-100 text-sky-800",
};

export function NewsCard({ item }: { item: BriefingItem }) {
  return (
    <article className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-gray-900 leading-snug">
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
            {item.headline}
          </a>
        </h3>
        <span className="shrink-0 text-xs font-medium text-gray-500">
          {Math.round(item.relevance_score * 100)}%
        </span>
      </div>

      <p className="mt-2 text-sm text-gray-600 leading-relaxed">{item.summary}</p>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
        <span className="font-medium text-gray-700">{item.source_name}</span>
        <span className={`rounded px-1.5 py-0.5 ${contentTypeBadge[item.content_type]}`}>
          {item.content_type}
        </span>
        {item.is_developing && (
          <span className="rounded bg-amber-100 px-1.5 py-0.5 text-amber-800">Developing</span>
        )}
        {item.is_serendipity && (
          <span className="rounded bg-green-100 px-1.5 py-0.5 text-green-800">Worth a look</span>
        )}
        {item.fetch_status === "stale" && (
          <span className="rounded bg-orange-100 px-1.5 py-0.5 text-orange-800">Possibly stale</span>
        )}
        <time className="ml-auto text-gray-400">
          {new Date(item.published_at).toLocaleString()}
        </time>
      </div>
    </article>
  );
}
