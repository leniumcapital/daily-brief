export interface BriefingItem {
  id: number;
  headline: string;
  summary: string;
  source_name: string;
  source_type: string;
  category: string;
  content_type: "reporting" | "opinion" | "analysis" | "social";
  relevance_score: number;
  is_developing: boolean;
  is_serendipity: boolean;
  published_at: string;
  url: string;
  fetch_status: "ok" | "stale" | "error";
}

export interface BriefingSection {
  category: string;
  label: string;
  items: BriefingItem[];
}

export interface Dashboard {
  generated_at: string;
  sections: BriefingSection[];
  twitter_section: BriefingSection | null;
  stale_sources: string[];
}

export interface MarketPoint {
  time: string;
  value: number;
}

export interface MarketTicker {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePct: number;
  history: MarketPoint[];
}

export interface MarketsResponse {
  tickers: MarketTicker[];
  updated_at: string;
}
