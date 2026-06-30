import type { BriefingSection } from "../types";
import { NewsCard } from "./NewsCard";

export function Section({ section }: { section: BriefingSection }) {
  if (section.items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-lg font-bold text-gray-800 border-b border-gray-200 pb-2">
        {section.label}
      </h2>
      <div className="grid gap-3">
        {section.items.map((item) => (
          <NewsCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
