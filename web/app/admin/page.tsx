"use client";

import { useEffect, useMemo, useState } from "react";
import Protected from "@/components/Protected";
import Loader from "@/components/Loader";
import { api, ApiError } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import type { AdminData, Match } from "@/lib/types";
import { Plus, Refresh, Sparkle } from "@/components/Icons";

function AdminInner() {
  const { toast } = useToast();
  const [data, setData] = useState<AdminData | null>(null);
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [form, setForm] = useState({ team_a: "", team_b: "", stage: "", venue: "", kickoff_time: "" });

  const load = () => api.adminMatches().then(setData);
  useEffect(() => {
    load();
  }, []);

  const run = async (key: string, fn: () => Promise<{ ok: boolean; message: string }>) => {
    setBusy(key);
    try {
      const res = await fn();
      toast(res.message, res.ok ? "success" : "error");
      await load();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Action failed.", "error");
    } finally {
      setBusy(null);
    }
  };

  const addMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.team_a || !form.team_b || !form.kickoff_time) {
      return toast("Team A, Team B, and kickoff time are required.", "error");
    }
    await run("add", () => api.adminAddMatch(form));
    setForm({ team_a: "", team_b: "", stage: "", venue: "", kickoff_time: "" });
  };

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    if (!q) return data.matches;
    return data.matches.filter((m) =>
      `${m.id} ${m.team_a} ${m.team_b} ${m.stage} ${m.venue}`.toLowerCase().includes(q)
    );
  }, [data, search]);

  if (!data) return <Loader label="Loading control room" />;

  return (
    <div className="space-y-16">
      <div className="grid gap-12 items-start lg:grid-cols-[minmax(0,1.35fr)_minmax(340px,0.65fr)]">
        <div className="space-y-16">
          <header className="animate-fade-up">
            <span className="eyebrow">Admin</span>
            <h1 className="display mt-5 max-w-2xl text-balance text-4xl sm:text-5xl">
              Control fixtures, sync data, apply <span className="gold-text">overrides.</span>
            </h1>
          </header>

          <section className="self-start">
            <span className="eyebrow">Data sources</span>
            <h2 className="display mt-2 text-2xl">Seed or sync</h2>
            <p className="mt-2 text-sm text-muted">
              Bootstrap quickly, then refresh official fixtures when an API key is available.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button onClick={() => run("seed", api.adminSeed)} disabled={busy === "seed"} className="btn-gold">
                <Sparkle width={16} height={16} /> {busy === "seed" ? "Loading…" : "Load starter fixtures"}
              </button>
              <button onClick={() => run("sync", api.adminSync)} disabled={busy === "sync"} className="btn-line">
                <Refresh width={16} height={16} /> {busy === "sync" ? "Syncing…" : "Sync official fixtures"}
              </button>
            </div>
            <p className={`mt-5 text-sm ${data.api_enabled ? "text-emerald-500" : "text-muted"}`}>
              {data.api_enabled
                ? "football-data.org is configured — sync pulls World Cup data into SQLite."
                : "Set FOOTBALL_DATA_API_KEY to enable official sync. Starter fixtures still work."}
            </p>
          </section>
        </div>

        <section className="self-start">
          <span className="eyebrow">Manual fixture</span>
          <h2 className="display mt-2 text-2xl">Add a custom match</h2>
          <form onSubmit={addMatch} className="mt-6 grid gap-4 sm:grid-cols-2">
            {(["team_a", "team_b"] as const).map((key) => (
              <div key={key}>
                <label className="field-label">{key === "team_a" ? "Team A" : "Team B"}</label>
                <select
                  className="field"
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                >
                  <option value="">Choose {key === "team_a" ? "Team A" : "Team B"}</option>
                  {data.teams.map((t) => (
                    <option key={t.code} value={t.name}>
                      {t.flag} {t.name}
                    </option>
                  ))}
                </select>
              </div>
            ))}
            <div>
              <label className="field-label">Stage</label>
              <input className="field" value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value })} placeholder="e.g. Group A" />
            </div>
            <div>
              <label className="field-label">Venue</label>
              <input className="field" value={form.venue} onChange={(e) => setForm({ ...form, venue: e.target.value })} placeholder="e.g. Mexico City Stadium" />
            </div>
            <div className="sm:col-span-2">
              <label className="field-label">Kickoff time (IST)</label>
              <input
                className="field"
                type="datetime-local"
                value={form.kickoff_time}
                onChange={(e) => setForm({ ...form, kickoff_time: e.target.value })}
              />
            </div>
            <div className="sm:col-span-2">
              <button type="submit" disabled={busy === "add"} className="btn-gold">
                <Plus width={16} height={16} /> {busy === "add" ? "Adding…" : "Add match"}
              </button>
            </div>
          </form>
        </section>
      </div>

      {/* Overrides */}
      <section>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="eyebrow">Overrides</span>
            <h2 className="display mt-2 text-2xl">Results &amp; lock status</h2>
          </div>
          <span className="text-xs uppercase tracking-luxe text-muted">{data.matches.length} fixtures</span>
        </div>

        <input
          className="field mt-6"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by team, stage, venue, or match id"
        />

        <div className="mt-4 divide-y divide-fg/10 border-y border-fg/10">
          {filtered.map((m) => (
            <AdminMatchRow key={m.id} match={m} onSaved={load} setBusy={setBusy} busy={busy} toast={toast} />
          ))}
          {filtered.length === 0 && (
            <p className="py-10 text-center text-muted">No fixtures match your search.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function AdminMatchRow({
  match,
  onSaved,
  setBusy,
  busy,
  toast,
}: {
  match: Match;
  onSaved: () => Promise<void> | void;
  setBusy: (v: string | null) => void;
  busy: string | null;
  toast: (m: string, k?: "success" | "error" | "info") => void;
}) {
  const [winner, setWinner] = useState(match.winner ?? "");
  const [potmWinner, setPotmWinner] = useState(match.potm_winner ?? "");
  const [locked, setLocked] = useState(match.is_locked);
  const key = `match-${match.id}`;

  const save = async () => {
    setBusy(key);
    try {
      const res = await api.adminUpdateMatch(match.id, {
        winner: winner || null,
        potm_winner: potmWinner || null,
        is_locked: locked,
      });
      toast(res.message, "success");
      await onSaved();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Could not update match.", "error");
    } finally {
      setBusy(null);
    }
  };

  return (
    <details className="group py-4 [&_summary::-webkit-details-marker]:hidden">
      <summary className="flex cursor-pointer flex-wrap items-center justify-between gap-3">
        <div>
          <div className="font-medium">
            {match.team_a_flag} {match.team_a} <span className="text-muted">vs</span> {match.team_b_flag} {match.team_b}
          </div>
          <div className="mt-0.5 text-xs text-muted">
            {match.stage} · {match.kickoff_ist} · #{match.id}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <span className={match.is_locked ? "text-muted" : "text-emerald-500"}>
            {match.is_locked ? "Locked" : "Open"}
          </span>
          <span className="text-muted">{match.winner ? `· ${match.winner}` : "· No result"}</span>
        </div>
      </summary>

      <div className="mt-4 grid gap-3 sm:grid-cols-4 sm:items-end">
        <div>
          <label className="field-label">Winner</label>
          <select className="field" value={winner} onChange={(e) => setWinner(e.target.value)}>
            <option value="">No result yet</option>
            <option value={match.team_a}>{match.team_a}</option>
            <option value={match.team_b}>{match.team_b}</option>
            <option value="Draw">Draw</option>
          </select>
        </div>
        <div>
          <label className="field-label">Player of the Match</label>
          <input className="field" value={potmWinner} onChange={(e) => setPotmWinner(e.target.value)} placeholder="Official POTM" />
        </div>
        <div>
          <label className="field-label">Locked</label>
          <select className="field" value={locked ? "1" : "0"} onChange={(e) => setLocked(e.target.value === "1")}>
            <option value="0">No</option>
            <option value="1">Yes</option>
          </select>
        </div>
        <button onClick={save} disabled={busy === key} className="btn-gold">
          {busy === key ? "Saving…" : "Save"}
        </button>
      </div>
    </details>
  );
}

export default function AdminPage() {
  return (
    <Protected>
      <AdminInner />
    </Protected>
  );
}
