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
    retry: false,
  });

  const financeItems = getSection(dashboard.data, "finance_markets");
  const startupItems = getSection(dashboard.data, "technology_startups");
  const twitterItems = getTwitterItems(dashboard.data);

  return (
    <div className="min-h-screen bg-[#f4f6f9]">
      <Header
        lastUpdated={dashboard.data?.generated_at}
        staleSources={dashboard.data?.stale_sources}
      />

      {dashboard.error && (
        <div className="mx-auto max-w-[1440px] px-8 pt-4">
          <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            Could not reach the API — make sure the backend is running on port 8000.
          </p>
        </div>
      )}

      <div className="mx-auto max-w-[1440px] space-y-5 px-8 py-6">
        {/* Top row: 3 columns matching mockup */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          <TwitterTracker items={twitterItems} isLoading={dashboard.isLoading} />
          <FinanceNews items={financeItems} isLoading={dashboard.isLoading} />
          <MarketsPanel
            tickers={markets.data?.tickers ?? []}
            isLoading={markets.isLoading}
          />
        </div>

        {/* Bottom row: full-width startup section */}
        <StartupFunding items={startupItems} isLoading={dashboard.isLoading} />
      </div>
    </div>
  );
}
