"use client";

import { useEffect, useState } from "react";
import Protected from "@/components/Protected";
import Loader from "@/components/Loader";
import { api } from "@/lib/api";
import type { ScorersData } from "@/lib/types";

function GoldenBootInner() {
  const [data, setData] = useState<ScorersData | null>(null);

  useEffect(() => {
    api.scorers().then(setData);
  }, []);

  if (!data) return <Loader label="Loading scorers" />;

  const live = data.api_enabled && !data.api_status;
  const status = live ? "Auto-updating" : data.api_enabled ? "Data unavailable" : "API key needed";

  return (
    <div className="space-y-12">
      <header className="flex flex-wrap items-end justify-between gap-6 animate-fade-up">
        <div>
          <span className="eyebrow">Golden Boot</span>
          <h1 className="display mt-5 max-w-lg text-balance text-4xl sm:text-5xl">
            The race for the <span className="gold-text">Golden Boot.</span>
          </h1>
          <p className="mt-4 max-w-lg text-muted">
            Live tournament top scorers. Match picks live on your dashboard.
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          {live && <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />}
          <span className={live ? "text-emerald-500" : "text-muted"}>{status}</span>
        </div>
      </header>

      {data.scorers.length > 0 ? (
        <div className="divide-y divide-fg/10 border-y border-fg/10">
          {data.scorers.map((s) => (
            <div key={`${s.rank}-${s.name}`} className="flex items-center gap-5 py-4">
              <span className={`display w-8 text-2xl ${s.rank === 1 ? "gold-text" : "text-muted/50"}`}>
                {s.rank}
              </span>
              <div className="min-w-0 flex-1">
                <div className="truncate font-medium">{s.name}</div>
                <div className="text-xs text-muted">
                  {s.team_flag ? `${s.team_flag} ` : ""}
                  {s.team} · {s.position}
                </div>
              </div>
              <div className="text-right">
                <span className="display text-2xl gold-text">{s.goals}</span>
                <span className="ml-1.5 text-[0.6rem] uppercase tracking-luxe text-muted">goals</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="border-y border-fg/10 py-16 text-center">
          <h3 className="display text-2xl">No scorer table yet</h3>
          <p className="mx-auto mt-3 max-w-md text-sm text-muted">
            {data.api_status
              ? data.api_status
              : data.api_enabled
              ? "The scorer feed is connected, but scorer data is not available yet."
              : "Add FOOTBALL_DATA_API_KEY to enable automatic scorer updates."}
          </p>
        </div>
      )}
    </div>
  );
}

export default function GoldenBootPage() {
  return (
    <Protected>
      <GoldenBootInner />
    </Protected>
  );
}
