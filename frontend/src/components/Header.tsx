interface HeaderProps {
  lastUpdated?: string;
  staleSources?: string[];
}

export function Header({ lastUpdated, staleSources = [] }: HeaderProps) {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between px-8 py-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-ink">Daily Brief</h1>
          <p className="mt-0.5 text-sm text-slate-500">{today}</p>
        </div>
        <div className="flex items-center gap-4">
          {staleSources.length > 0 && (
            <span className="rounded-full bg-amber-50 px-3.5 py-1.5 text-xs font-semibold text-amber-700 ring-1 ring-amber-200/60">
              {staleSources.length} source{staleSources.length > 1 ? "s" : ""} delayed
            </span>
          )}
          {lastUpdated && (
            <p className="text-xs font-medium text-slate-400">
              Updated{" "}
              {new Date(lastUpdated).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600 text-sm font-bold text-white">
            K
          </div>
        </div>
      </div>
    </header>
  );
}
