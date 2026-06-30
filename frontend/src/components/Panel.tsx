import type { ReactNode } from "react";

type Accent = "finance" | "markets" | "startup" | "twitter";

const accentDot: Record<Accent, string> = {
  finance: "bg-finance",
  markets: "bg-markets",
  startup: "bg-startup",
  twitter: "bg-twitter",
};

const accentTitle: Record<Accent, string> = {
  finance: "text-finance",
  markets: "text-markets",
  startup: "text-startup",
  twitter: "text-twitter",
};

interface PanelProps {
  title: string;
  subtitle?: string;
  accent?: Accent;
  trailing?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Panel({ title, subtitle, accent, trailing, children, className = "" }: PanelProps) {
  return (
    <section className={`card flex flex-col overflow-hidden ${className}`}>
      <header className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div className="flex items-center gap-2.5">
          {accent && <div className={`h-2 w-2 rounded-full ${accentDot[accent]}`} />}
          <div>
            <h2 className={`text-xs font-bold uppercase tracking-widest ${accent ? accentTitle[accent] : "text-slate-500"}`}>
              {title}
            </h2>
            {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
          </div>
        </div>
        {trailing}
      </header>
      <div className="flex-1">{children}</div>
    </section>
  );
}
