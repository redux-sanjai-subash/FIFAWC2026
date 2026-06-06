"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { useToast } from "@/components/ToastProvider";
import { api, ApiError } from "@/lib/api";
import type { Team } from "@/lib/types";
import { ArrowRight } from "@/components/Icons";

type Tab = "login" | "register";

export default function LandingPage() {
  const { user, loading, setUser } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  const [tab, setTab] = useState<Tab>("login");
  const [teams, setTeams] = useState<Team[]>([]);
  const [stats, setStats] = useState({ teams: 48, matches: 0, hosts: 3 });
  const [username, setUsername] = useState("");
  const [favoriteTeam, setFavoriteTeam] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [loading, user, router]);

  useEffect(() => {
    api.teams().then((d) => setTeams(d.teams)).catch(() => {});
    api.stats().then((d) => setStats(d.stats)).catch(() => {});
  }, []);

  const marquee = useMemo(() => teams.slice(0, 18), [teams]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return toast("Username is required.", "error");
    setBusy(true);
    try {
      const res =
        tab === "login"
          ? await api.login(username.trim())
          : await api.register(username.trim(), favoriteTeam || undefined);
      setUser(res.user);
      toast(tab === "login" ? "Welcome back." : "Profile created.", "success");
      router.push("/dashboard");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Something went wrong.";
      toast(msg, "error");
      if (err instanceof ApiError && err.status === 404) setTab("register");
      if (err instanceof ApiError && err.status === 409) setTab("login");
    } finally {
      setBusy(false);
    }
  };

  const figures = [
    { label: "Qualified nations", value: stats.teams },
    { label: "Fixtures", value: stats.matches },
    { label: "Host countries", value: stats.hosts },
  ];

  return (
    <div className="grid items-center gap-16 lg:grid-cols-[1.25fr_0.75fr] lg:gap-20">
      {/* Editorial hero — no box, type-led */}
      <section className="min-w-0 animate-fade-up">
        <span className="eyebrow">Redux · Invitational</span>
        <h1 className="display mt-6 text-balance text-5xl sm:text-6xl lg:text-7xl">
          Predict the tournament.
          <br />
          <span className="gold-text">Earn your place.</span>
        </h1>
        <p className="mt-7 max-w-lg text-lg leading-relaxed text-muted">
          A members-only prediction club by Redux. Call the winners, name the
          Player of the Match, and rise through a leaderboard worthy of the
          occasion.
        </p>

        <div className="mt-12 flex flex-wrap gap-x-12 gap-y-6">
          {figures.map((f) => (
            <div key={f.label}>
              <div className="display text-4xl gold-text">{f.value}</div>
              <div className="mt-1 text-[0.62rem] uppercase tracking-luxe text-muted">{f.label}</div>
            </div>
          ))}
        </div>

        {marquee.length > 0 && (
          <div className="mt-12 w-full overflow-hidden [mask-image:linear-gradient(90deg,transparent,#000_8%,#000_92%,transparent)]">
            <div className="flex w-max animate-marquee gap-6">
              {[...marquee, ...marquee].map((t, i) => (
                <span key={`${t.code}-${i}`} className="flex items-center gap-2 whitespace-nowrap text-sm text-muted">
                  <span className="text-base">{t.flag}</span> {t.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Auth — minimal, hairline framed */}
      <section className="min-w-0 animate-fade-up [animation-delay:120ms]">
        <div className="flex gap-8 border-b border-fg/10 pb-px">
          {(["login", "register"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`relative pb-3 text-sm font-medium capitalize transition ${
                tab === t ? "text-fg" : "text-muted hover:text-fg"
              }`}
            >
              {t}
              {tab === t && <span className="absolute -bottom-px left-0 h-px w-full bg-gold" />}
            </button>
          ))}
        </div>

        <div className="mt-8">
          <h2 className="display text-2xl">
            {tab === "login" ? "Return to your dashboard" : "Create your profile"}
          </h2>
          <p className="mt-2 text-sm text-muted">
            {tab === "login"
              ? "Enter your username to continue."
              : "Choose a username and your nation."}
          </p>
        </div>

        <form onSubmit={submit} className="mt-7 space-y-5">
          <div>
            <label className="field-label">Username</label>
            <input
              className="field"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={tab === "login" ? "Enter your username" : "Choose a username"}
              autoComplete="off"
            />
          </div>

          {tab === "register" && (
            <div className="animate-fade-in">
              <label className="field-label">Favorite team</label>
              <select className="field" value={favoriteTeam} onChange={(e) => setFavoriteTeam(e.target.value)}>
                <option value="">Select your nation</option>
                {teams.map((t) => (
                  <option key={t.code} value={t.name}>
                    {t.flag} {t.name} · {t.code}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button type="submit" disabled={busy} className="btn-gold w-full py-3">
            {busy ? "Please wait…" : tab === "login" ? "Enter the club" : "Create profile"}
            {!busy && <ArrowRight width={18} height={18} />}
          </button>
        </form>

        <p className="mt-6 text-sm text-muted">
          {tab === "login" ? "No profile yet? " : "Already a member? "}
          <button
            onClick={() => setTab(tab === "login" ? "register" : "login")}
            className="font-medium text-gold hover:underline"
          >
            {tab === "login" ? "Register" : "Log in"}
          </button>
        </p>
      </section>
    </div>
  );
}
