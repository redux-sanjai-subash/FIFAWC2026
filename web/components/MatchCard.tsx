"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useToast } from "./ToastProvider";
import Countdown from "./Countdown";
import type { Match } from "@/lib/types";
import { Check, Clock, Lock, ShieldCheck } from "./Icons";

export default function MatchCard({
  match,
  onSaved,
}: {
  match: Match;
  onSaved?: (savedCount: number) => void;
}) {
  const { toast } = useToast();
  const [winner, setWinner] = useState<string | null>(null);
  const [potm, setPotm] = useState("");
  const [picked, setPicked] = useState(match.already_picked);
  const [savedWinner, setSavedWinner] = useState<string | null>(match.prediction);
  const [savedPotm, setSavedPotm] = useState<string | null>(match.potm_prediction);
  const [busy, setBusy] = useState(false);

  const choices = [
    { value: match.team_a, label: match.team_a, flag: match.team_a_flag },
    { value: "Draw", label: "Draw", flag: "🤝" },
    { value: match.team_b, label: match.team_b, flag: match.team_b_flag },
  ];

  const save = async () => {
    if (!winner) return toast("Pick a winner first.", "error");
    if (!potm.trim()) return toast("Choose a Player of the Match.", "error");
    setBusy(true);
    try {
      const res = await api.savePrediction(match.id, winner, potm.trim());
      setSavedWinner(res.prediction);
      setSavedPotm(res.potm_prediction);
      setPicked(true);
      toast("Pick locked in — it's final.", "success");
      onSaved?.(res.saved_count);
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Could not save this pick.", "error");
    } finally {
      setBusy(false);
    }
  };

  const result = (team: string | null) =>
    match.winner && team ? (match.winner === team ? "hit" : "miss") : null;

  return (
    <article className="py-7">
      {/* Top row: stage + status */}
      <div className="flex items-center justify-between gap-3">
        <span className="text-[0.62rem] font-semibold uppercase tracking-luxe text-gold">{match.stage}</span>
        <div className="flex items-center gap-3 text-xs text-muted">
          {match.winner && (
            <span className="chip text-gold">
              <Check width={12} height={12} /> {match.winner}
            </span>
          )}
          {match.can_pick && !picked && (
            <span className="flex items-center gap-1.5 text-muted">
              <Clock width={13} height={13} />
              <Countdown target={match.lock_time} prefix="closes in" expired="closing" />
            </span>
          )}
          {picked && (
            <span className="flex items-center gap-1.5 text-gold">
              <Lock width={13} height={13} /> Locked
            </span>
          )}
          {!picked && !match.can_pick && !match.winner && (
            <span className="text-muted">Picks closed</span>
          )}
        </div>
      </div>

      {/* Teams */}
      <div className="mt-5 flex items-center gap-4">
        <div className="flex flex-1 items-center gap-3">
          <span className="text-3xl">{match.team_a_flag}</span>
          <div>
            <div className="display text-xl">{match.team_a}</div>
            <div className="text-[0.6rem] uppercase tracking-[0.2em] text-muted">{match.team_a_code || "—"}</div>
          </div>
        </div>
        <span className="font-serif text-sm italic text-muted">vs</span>
        <div className="flex flex-1 items-center justify-end gap-3 text-right">
          <div>
            <div className="display text-xl">{match.team_b}</div>
            <div className="text-[0.6rem] uppercase tracking-[0.2em] text-muted">{match.team_b_code || "—"}</div>
          </div>
          <span className="text-3xl">{match.team_b_flag}</span>
        </div>
      </div>

      <div className="mt-3 text-xs text-muted">
        {match.venue} · {match.kickoff_ist}
      </div>

      {/* Pick area */}
      {match.can_pick && !picked ? (
        <div className="mt-6 space-y-4">
          <div className="flex flex-wrap gap-2">
            {choices.map((c) => {
              const active = winner === c.value;
              return (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => setWinner(c.value)}
                  className={`chip border transition ${
                    active
                      ? "border-gold bg-gold text-bg"
                      : "border-fg/12 text-fg/80 hover:border-fg/30"
                  }`}
                >
                  <span>{c.flag}</span> {c.label}
                </button>
              );
            })}
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="field-label">Player of the Match</label>
              <input
                className="field"
                list={`potm-${match.id}`}
                value={potm}
                onChange={(e) => setPotm(e.target.value)}
                placeholder="Type or select a player"
              />
              <datalist id={`potm-${match.id}`}>
                {match.potm_options.map((p) => (
                  <option key={p} value={p} />
                ))}
              </datalist>
            </div>
            <button onClick={save} disabled={busy} className="btn-gold whitespace-nowrap">
              {busy ? "Locking…" : "Lock in pick"}
            </button>
          </div>
          <p className="flex items-center gap-1.5 text-xs text-muted">
            <ShieldCheck width={13} height={13} /> Your pick is final and can't be changed once locked.
          </p>
        </div>
      ) : picked ? (
        <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          <span className="flex items-center gap-2">
            <span className="text-muted">Winner</span>
            <span className="font-medium">{savedWinner}</span>
            {result(savedWinner) === "hit" && <span className="text-emerald-500">✓</span>}
            {result(savedWinner) === "miss" && <span className="text-rose-500">✗</span>}
          </span>
          {savedPotm && (
            <span className="flex items-center gap-2">
              <span className="text-muted">POTM</span>
              <span className="font-medium">{savedPotm}</span>
            </span>
          )}
        </div>
      ) : (
        <div className="mt-5 text-sm text-muted">
          Picks for this fixture have closed.
        </div>
      )}
    </article>
  );
}
