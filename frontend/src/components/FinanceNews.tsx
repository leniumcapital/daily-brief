import type { BriefingItem } from "../types";
import { NewsCard } from "./NewsCard";

interface FinanceNewsProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function FinanceNews({ items, isLoading }: FinanceNewsProps) {
  const [featured, ...rest] = items;

  return (
    <section className="card flex flex-col overflow-hidden">
      <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-finance" />
          <h2 className="section-title text-finance">Finance</h2>
        </div>
        <span className="text-xs text-slate-400">{items.length} stories</span>
      </header>

      <div className="flex-1 overflow-y-auto p-2">
        {isLoading && <p className="p-4 text-sm text-slate-400">Loading finance news...</p>}
        {!isLoading && items.length === 0 && (
          <p className="p-4 text-sm text-slate-500">No finance headlines yet.</p>
        )}
        {featured && (
          <div className="mb-2">
            <NewsCard item={featured} variant="featured" accent="finance" />
          </div>
        )}
        <div className="divide-y divide-slate-100 rounded-xl border border-slate-100">
          {rest.map((item) => (
            <NewsCard key={item.id} item={item} variant="compact" accent="finance" />
          ))}
        </div>
      </div>
    </section>
  );
}
