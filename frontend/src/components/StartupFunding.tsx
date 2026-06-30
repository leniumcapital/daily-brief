import type { BriefingItem } from "../types";
import { NewsCard } from "./NewsCard";

interface StartupFundingProps {
  items: BriefingItem[];
  isLoading?: boolean;
}

export function StartupFunding({ items, isLoading }: StartupFundingProps) {
  return (
    <section className="card overflow-hidden">
      <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-startup" />
          <h2 className="section-title text-startup">Startup & Funding</h2>
        </div>
        <span className="rounded-full bg-startup/10 px-3 py-1 text-xs font-semibold text-startup">
          VC · Rounds · Tech
        </span>
      </header>

      <div className="grid gap-0 md:grid-cols-2 lg:grid-cols-3">
        {isLoading && (
          <p className="col-span-full p-6 text-sm text-slate-400">Loading startup news...</p>
        )}
        {!isLoading && items.length === 0 && (
          <p className="col-span-full p-6 text-sm text-slate-500">
            No startup funding news yet — check back after the next refresh.
          </p>
        )}
        {items.map((item) => (
          <div key={item.id} className="border-b border-r border-slate-100 md:[&:nth-child(3n)]:border-r-0">
            <NewsCard item={item} accent="startup" />
          </div>
        ))}
      </div>
    </section>
  );
}
