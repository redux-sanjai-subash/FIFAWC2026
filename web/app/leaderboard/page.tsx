"use client";

import { useEffect, useState } from "react";
import Protected from "@/components/Protected";
import Loader from "@/components/Loader";
import { api } from "@/lib/api";
import type { LeaderboardData, LeaderboardRow } from "@/lib/types";

function LeaderboardInner() {
  const [data, setData] = useState<LeaderboardData | null>(null);

  useEffect(() => {
    api.leaderboard().then(setData);
  }, []);

  if (!data) return <Loader label="Tallying points" />;

  const isMe = (row: LeaderboardRow) => data.current_username === row.username;

  return (
    <div className="space-y-14">
      <header className="animate-fade-up">
        <span className="eyebrow">Standings</span>
        <h1 className="display mt-5 max-w-2xl text-balance text-4xl sm:text-5xl">
          Climb the leaderboard and <span className="gold-text">own the conversation.</span>
        </h1>
        <p className="mt-4 max-w-xl text-muted">
          Correct winner picks are worth {data.match_points} points. A correct Player
          of the Match is worth {data.potm_points} point{data.potm_points !== 1 ? "s" : ""}.
        </p>
      </header>

      {/* Podium — bare figures, no boxes */}
      {data.podium.length > 0 && (
        <section className="grid gap-10 border-y border-fg/10 py-10 sm:grid-cols-3">
          {data.podium.map((row, i) => (
            <div key={row.username} className={i === 0 ? "" : "sm:pl-10 sm:border-l sm:border-fg/10"}>
              <div className="flex items-baseline gap-3">
                <span className="display text-5xl text-muted/40">{i + 1}</span>
                <span className="text-2xl">{["🥇", "🥈", "🥉"][i]}</span>
              </div>
              <h2 className="display mt-3 text-2xl">{row.username}</h2>
              <p className="mt-1 text-sm text-muted">
                {row.favorite_team_flag ? `${row.favorite_team_flag} ` : ""}
                {row.favorite_team}
              </p>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="display text-3xl gold-text">{row.points}</span>
                <span className="text-xs uppercase tracking-luxe text-muted">pts</span>
              </div>
              <p className="mt-1 text-xs text-muted">{row.correct} winners · {row.potm_correct} POTM</p>
            </div>
          ))}
        </section>
      )}

      {/* Full standings — hairline rows */}
      <section>
        <div className="hidden grid-cols-[3rem_1fr_1fr_5rem_5rem_4rem] gap-4 border-b border-fg/10 pb-3 text-[0.62rem] uppercase tracking-luxe text-muted md:grid">
          <span>Rank</span>
          <span>Player</span>
          <span>Nation</span>
          <span className="text-right">Points</span>
          <span className="text-right">Winners</span>
          <span className="text-right">POTM</span>
        </div>
        <div className="divide-y divide-fg/10">
          {data.rows.length === 0 && (
            <p className="py-10 text-center text-muted">No scored results yet.</p>
          )}
          {data.rows.map((row) => (
            <div
              key={row.username}
              className={`grid grid-cols-2 items-center gap-x-4 gap-y-2 py-4 md:grid-cols-[3rem_1fr_1fr_5rem_5rem_4rem] ${
                isMe(row) ? "text-fg" : ""
              }`}
            >
              <span className={`display text-lg ${row.rank <= 3 ? "gold-text" : "text-muted"}`}>
                {row.rank}
              </span>
              <span className="flex items-center gap-2 font-medium">
                {row.username}
                {isMe(row) && (
                  <span className="chip border border-gold/40 text-[0.6rem] uppercase tracking-wide text-gold">You</span>
                )}
              </span>
              <span className="text-sm text-muted">
                {row.favorite_team_flag ? `${row.favorite_team_flag} ` : ""}
                {row.favorite_team}
              </span>
              <span className="text-right">
                <span className="md:hidden text-[0.6rem] uppercase tracking-luxe text-muted">Pts </span>
                <span className="display text-lg gold-text">{row.points}</span>
              </span>
              <span className="text-right text-sm text-muted">
                <span className="md:hidden text-[0.6rem] uppercase tracking-luxe">W </span>
                {row.correct}
              </span>
              <span className="text-right text-sm text-muted">
                <span className="md:hidden text-[0.6rem] uppercase tracking-luxe">POTM </span>
                {row.potm_correct}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default function LeaderboardPage() {
  return (
    <Protected>
      <LeaderboardInner />
    </Protected>
  );
}
