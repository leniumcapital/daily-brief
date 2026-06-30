import { useQuery } from "@tanstack/react-query";
import { fetchDashboard } from "./api";
import { Section } from "./components/Section";

export default function App() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Daily Brief</h1>
          <p className="text-sm text-gray-500">Your personalized news dashboard</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6">
        {isLoading && <p className="text-gray-500">Loading your briefing...</p>}
        {error && <p className="text-red-600">Failed to load briefing. Is the backend running?</p>}

        {data?.stale_sources && data.stale_sources.length > 0 && (
          <div className="mb-6 rounded-lg bg-orange-50 border border-orange-200 p-3 text-sm text-orange-800">
            Some sources may be outdated: {data.stale_sources.join(", ")}
          </div>
        )}

        {data?.sections.map((section) => (
          <Section key={section.category} section={section} />
        ))}

        {data?.twitter_section && <Section section={data.twitter_section} />}

        {data && (
          <p className="text-xs text-gray-400 text-center mt-8">
            Last updated {new Date(data.generated_at).toLocaleString()}
          </p>
        )}
      </main>
    </div>
  );
}
