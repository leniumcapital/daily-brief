import { Area, AreaChart, ResponsiveContainer, YAxis } from "recharts";
import type { MarketTicker } from "../types";
import { Panel } from "./Panel";

interface MarketsPanelProps {
  tickers: MarketTicker[];
  isLoading?: boolean;
}

function TickerChart({ ticker }: { ticker: MarketTicker }) {
  const isUp = ticker.changePct >= 0;
  const stroke = isUp ? "#059669" : "#dc2626";
  const displayPrice =
    ticker.price >= 1000
      ? ticker.price.toLocaleString(undefined, { maximumFractionDigits: 0 })
      : ticker.price.toFixed(2);

  return (
    <div className="rounded-xl border border-slate-100 bg-white p-3.5">
      <div className="mb-2 flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {ticker.symbol}
          </p>
          <p className="text-xs font-medium text-slate-500">{ticker.name}</p>
        </div>
        <div className="text-right">
          <p className="text-base font-bold tabular-nums text-ink">{displayPrice}</p>
          <p className={`text-xs font-bold tabular-nums ${isUp ? "text-finance" : "text-red-500"}`}>
            {isUp ? "+" : ""}
            {ticker.changePct.toFixed(2)}%
          </p>
        </div>
      </div>
      <div className="h-14 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={ticker.history} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`g-${ticker.symbol}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={stroke} stopOpacity={0.25} />
                <stop offset="100%" stopColor={stroke} stopOpacity={0} />
              </linearGradient>
            </defs>
            <YAxis domain={["dataMin", "dataMax"]} hide />
            <Area
              type="monotone"
              dataKey="value"
              stroke={stroke}
              strokeWidth={2}
              fill={`url(#g-${ticker.symbol})`}
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
    <Panel
      title="Your Markets"
      subtitle="Tailored to your watchlist"
      accent="markets"
      className="min-h-[420px]"
    >
      <div className="grid grid-cols-2 gap-3 p-5">
        {isLoading &&
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-[120px] animate-pulse rounded-xl bg-slate-100" />
          ))}
        {!isLoading && tickers.map((ticker) => <TickerChart key={ticker.symbol} ticker={ticker} />)}
      </div>
    </Panel>
  );
}
