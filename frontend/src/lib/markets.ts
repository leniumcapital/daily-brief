import type { MarketsResponse } from "../types";

/** Fallback watchlist data when /markets API is unavailable */
export const FALLBACK_MARKETS: MarketsResponse = {
  updated_at: new Date().toISOString(),
  tickers: [
    {
      symbol: "SPY",
      name: "S&P 500",
      price: 541.28,
      change: 2.28,
      changePct: 0.42,
      history: [
        { time: "9a", value: 538 },
        { time: "10a", value: 539 },
        { time: "11a", value: 540 },
        { time: "12p", value: 539.5 },
        { time: "1p", value: 540.5 },
        { time: "2p", value: 541 },
        { time: "3p", value: 541.28 },
      ],
    },
    {
      symbol: "QQQ",
      name: "Nasdaq 100",
      price: 467.15,
      change: 2.83,
      changePct: 0.61,
      history: [
        { time: "9a", value: 463 },
        { time: "10a", value: 464 },
        { time: "11a", value: 465 },
        { time: "12p", value: 464.5 },
        { time: "1p", value: 466 },
        { time: "2p", value: 466.8 },
        { time: "3p", value: 467.15 },
      ],
    },
    {
      symbol: "BTC",
      name: "Bitcoin",
      price: 67420,
      change: -121,
      changePct: -0.18,
      history: [
        { time: "9a", value: 67800 },
        { time: "10a", value: 67650 },
        { time: "11a", value: 67500 },
        { time: "12p", value: 67600 },
        { time: "1p", value: 67480 },
        { time: "2p", value: 67450 },
        { time: "3p", value: 67420 },
      ],
    },
    {
      symbol: "10Y",
      name: "US 10Y Yield",
      price: 4.31,
      change: 0.03,
      changePct: 0.7,
      history: [
        { time: "9a", value: 4.28 },
        { time: "10a", value: 4.29 },
        { time: "11a", value: 4.3 },
        { time: "12p", value: 4.29 },
        { time: "1p", value: 4.3 },
        { time: "2p", value: 4.31 },
        { time: "3p", value: 4.31 },
      ],
    },
  ],
};
