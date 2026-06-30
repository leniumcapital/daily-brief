import { useQuery } from "@tanstack/react-query";
import { fetchDashboard, fetchMarkets } from "./api";
import { getSection, getTwitterItems } from "./lib/dashboard";
import { Header } from "./components/Header";
import { TwitterTracker } from "./components/TwitterTracker";
import { FinanceNews } from "./components/FinanceNews";
import { MarketsPanel } from "./components/MarketsPanel";
import { StartupFunding } from "./components/StartupFunding";

export default function App() {
  const dashboard = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
    refetchInterval: (query) => {
      const empty =
        query.state.data &&
        query.state.data.sections.length === 0 &&
        !query.state.data.twitter_section;
      return empty ? 5000 : 60000;
    },
  });

  const markets = useQuery({
    queryKey: ["markets"],
    queryFn: fetchMarkets,
    refetchInterval: 60000,
  });

  const financeItems = getSection(dashboard.data, "finance_markets");
  const startupItems = getSection(dashboard.data, "technology_startups");
  const twitterItems = getTwitterItems(dashboard.data);

  return (
    <div className="min-h-screen bg-surface">
      <Header
        lastUpdated={dashboard.data?.generated_at}
        staleSources={dashboard.data?.stale_sources}
      />

      {dashboard.error && (
        <div className="mx-auto max-w-[1600px] px-6 pt-4">
          <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Could not reach the API — make sure the backend is running on port 8000.
          </p>
        </div>
      )}

      <main className="mx-auto grid max-w-[1600px] grid-cols-1 gap-5 px-6 py-6 lg:grid-cols-[320px_1fr]">
        {/* Left: Twitter tracker */}
        <div className="lg:sticky lg:top-[73px] lg:h-[calc(100vh-97px)]">
          <TwitterTracker items={twitterItems} isLoading={dashboard.isLoading} />
        </div>

        {/* Right: Finance, Markets, Startups */}
        <div className="flex min-w-0 flex-col gap-5">
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <FinanceNews items={financeItems} isLoading={dashboard.isLoading} />
            <MarketsPanel
              tickers={markets.data?.tickers ?? []}
              isLoading={markets.isLoading}
            />
          </div>

          <StartupFunding items={startupItems} isLoading={dashboard.isLoading} />
        </div>
      </main>
    </div>
  );
}
