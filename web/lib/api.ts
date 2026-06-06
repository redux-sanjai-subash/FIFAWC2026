import type {
  AdminData,
  DashboardData,
  LeaderboardData,
  Match,
  ScorersData,
  Team,
  User,
} from "./types";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api${path}`, {
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  let payload: any = null;
  try {
    payload = await res.json();
  } catch {
    /* non-JSON response */
  }

  if (!res.ok) {
    const message = payload?.message || `Request failed (${res.status})`;
    throw new ApiError(message, res.status);
  }
  return payload as T;
}

const post = (path: string, body?: unknown) =>
  request(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });

export const api = {
  me: () => request<{ user: User | null }>("/auth/me"),
  login: (username: string) =>
    post("/auth/login", { username }) as Promise<{ ok: boolean; user: User }>,
  register: (username: string, favorite_team?: string) =>
    post("/auth/register", { username, favorite_team }) as Promise<{ ok: boolean; user: User }>,
  logout: () => post("/auth/logout"),

  teams: () => request<{ teams: Team[] }>("/teams"),
  stats: () => request<{ stats: DashboardData["stats"] }>("/stats"),

  dashboard: () => request<DashboardData>("/dashboard"),
  savePrediction: (matchId: number, prediction: string, potm_prediction: string) =>
    post(`/predictions/${matchId}`, { prediction, potm_prediction }) as Promise<{
      ok: boolean;
      prediction: string;
      potm_prediction: string;
      saved_count: number;
      message: string;
    }>,

  leaderboard: () => request<LeaderboardData>("/leaderboard"),
  scorers: () => request<ScorersData>("/scorers"),

  adminMatches: () => request<AdminData>("/admin/matches"),
  adminAddMatch: (body: {
    team_a: string;
    team_b: string;
    stage: string;
    venue: string;
    kickoff_time: string;
  }) => post("/admin/matches", body) as Promise<{ ok: boolean; message: string; match: Match }>,
  adminUpdateMatch: (
    matchId: number,
    body: { winner: string | null; potm_winner: string | null; is_locked: boolean }
  ) =>
    request(`/admin/matches/${matchId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }) as Promise<{ ok: boolean; message: string; match: Match }>,
  adminSeed: () => post("/admin/seed") as Promise<{ ok: boolean; message: string }>,
  adminSync: () => post("/admin/sync") as Promise<{ ok: boolean; message: string }>,
};
