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
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-ink">Daily Brief</h1>
          <p className="text-sm text-slate-500">{today}</p>
        </div>
        <div className="flex items-center gap-4">
          {staleSources.length > 0 && (
            <span className="hidden rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 sm:inline">
              {staleSources.length} source{staleSources.length > 1 ? "s" : ""} delayed
            </span>
          )}
          {lastUpdated && (
            <p className="text-xs text-slate-400">
              Updated {new Date(lastUpdated).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          )}
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-sm font-bold text-white">
            K
          </div>
        </div>
      </div>
    </header>
  );
}
