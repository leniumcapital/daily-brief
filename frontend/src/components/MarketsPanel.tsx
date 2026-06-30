import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  YAxis,
} from "recharts";
import type { MarketTicker } from "../types";

interface MarketsPanelProps {
  tickers: MarketTicker[];
  isLoading?: boolean;
}

function TickerChart({ ticker }: { ticker: MarketTicker }) {
  const isUp = ticker.changePct >= 0;
  const color = isUp ? "#059669" : "#dc2626";

  return (
    <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-4 transition-shadow hover:shadow-card">
      <div className="mb-3 flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {ticker.symbol}
          </p>
          <p className="text-sm font-medium text-slate-600">{ticker.name}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold tabular-nums text-ink">
            {ticker.price.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
          <p
            className={`text-xs font-semibold tabular-nums ${isUp ? "text-finance" : "text-red-600"}`}
          >
            {isUp ? "+" : ""}
            {ticker.changePct.toFixed(2)}%
          </p>
        </div>
      </div>
      <div className="h-16 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={ticker.history} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`grad-${ticker.symbol}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <YAxis domain={["dataMin", "dataMax"]} hide />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "1px solid #e2e8f0",
                fontSize: "12px",
              }}
              formatter={(value: number) => [value.toFixed(2), ""]}
              labelFormatter={() => ""}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              fill={`url(#grad-${ticker.symbol})`}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function MarketsPanel({ tickers, isLoading }: MarketsPanelProps) {
  return (
    <section className="card overflow-hidden">
      <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-markets" />
          <h2 className="section-title text-markets">Your Markets</h2>
        </div>
        <span className="text-xs text-slate-400">Tailored to your watchlist</span>
      </header>

      <div className="grid grid-cols-2 gap-3 p-4 lg:grid-cols-2 xl:grid-cols-4">
        {isLoading &&
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-100" />
          ))}
        {!isLoading &&
          tickers.map((ticker) => <TickerChart key={ticker.symbol} ticker={ticker} />)}
      </div>
    </section>
  );
}
