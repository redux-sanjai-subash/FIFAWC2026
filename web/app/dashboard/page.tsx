"use client";

import { useEffect, useState } from "react";
import Protected from "@/components/Protected";
import Loader from "@/components/Loader";
import MatchCard from "@/components/MatchCard";
import Countdown from "@/components/Countdown";
import { api } from "@/lib/api";
import type { DashboardData } from "@/lib/types";
import { useAuth } from "@/components/AuthProvider";

function DashboardInner() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [picks, setPicks] = useState(0);

  useEffect(() => {
    api.dashboard().then((d) => {
      setData(d);
      setPicks(d.counts.picks);
    });
  }, []);

  if (!data) return <Loader label="Loading fixtures" />;

  const figures = [
    { label: "Your picks", value: picks },
    { label: "Open now", value: data.counts.open },
    { label: "Upcoming", value: data.counts.upcoming },
  ];

  return (
    <div className="space-y-16">
      {/* Header */}
      <header className="animate-fade-up">
        <span className="eyebrow">Redux</span>
        <h1 className="display mt-5 max-w-2xl text-balance text-4xl sm:text-5xl">
          Welcome back, <span className="gold-text">{user?.username}</span>.
        </h1>
        <p className="mt-4 max-w-xl text-muted">
          Voting opens 1 day before kickoff. Lock your winner and Player of the
          Match — picks close 15 minutes after kickoff, and once made they're final.
        </p>
        <div className="mt-10 flex flex-wrap gap-x-12 gap-y-5">
          {figures.map((f) => (
            <div key={f.label}>
              <div className="display text-3xl gold-text">{f.value}</div>
              <div className="mt-1 text-[0.6rem] uppercase tracking-luxe text-muted">{f.label}</div>
            </div>
          ))}
        </div>
      </header>

      {/* Open for picks */}
      <section>
        <SectionHead eyebrow="Open now" title="Make your picks" />
        {data.open_matches.length ? (
          <div className="mt-4 divide-y divide-fg/10 border-y border-fg/10">
            {data.open_matches.map((m) => (
              <MatchCard key={m.id} match={m} onSaved={setPicks} />
            ))}
          </div>
        ) : (
          <NextUnlock data={data} />
        )}
      </section>

      {/* Locked / your picks */}
      {data.locked_matches.length > 0 && (
        <section>
          <SectionHead eyebrow="In play & closed" title="Locked fixtures" />
          <div className="mt-4 divide-y divide-fg/10 border-y border-fg/10">
            {data.locked_matches.map((m) => (
              <MatchCard key={m.id} match={m} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function NextUnlock({ data }: { data: DashboardData }) {
  if (!data.next_unlock) {
    return (
      <p className="mt-6 text-muted">No fixtures are open right now. Check back soon.</p>
    );
  }
  return (
    <div className="mt-6 flex flex-col items-start gap-3 border-y border-fg/10 py-12">
      <span className="text-[0.62rem] uppercase tracking-luxe text-muted">
        {data.next_unlock.count} fixture{data.next_unlock.count !== 1 ? "s" : ""} ahead
      </span>
      <div className="display text-3xl sm:text-4xl">
        Next fixture unlocks in{" "}
        <span className="gold-text">
          <Countdown target={data.next_unlock.unlock_time} expired="moments" />
        </span>
      </div>
      <p className="max-w-md text-sm text-muted">
        Fixtures appear here 24 hours before kickoff so the picks stay fair for everyone.
      </p>
    </div>
  );
}

function SectionHead({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div>
      <span className="eyebrow">{eyebrow}</span>
      <h2 className="display mt-2 text-2xl sm:text-3xl">{title}</h2>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Protected>
      <DashboardInner />
    </Protected>
  );
}
