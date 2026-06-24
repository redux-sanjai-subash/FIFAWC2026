export interface User {
  id: number;
  username: string;
  favorite_team: string | null;
  favorite_team_flag: string | null;
  favorite_team_code: string | null;
}

export interface Team {
  name: string;
  code: string;
  flag: string;
  confederation: string;
}

export interface Match {
  id: number;
  team_a: string;
  team_b: string;
  team_a_flag: string;
  team_b_flag: string;
  team_a_code: string;
  team_b_code: string;
  stage: string;
  venue: string;
  kickoff_time: string; // UTC ISO instant (for countdowns)
  kickoff_ist: string; // preformatted IST display string
  lock_time: string; // UTC ISO instant when picks close (kickoff + 15m)
  winner: string | null;
  potm_winner: string | null;
  is_locked: boolean;
  visible: boolean;
  selection_closed: boolean;
  already_picked: boolean;
  can_pick: boolean;
  prediction: string | null;
  potm_prediction: string | null;
  potm_options: string[];
  lock_extension_minutes?: number;
  reopen_picks?: boolean;
}

export interface DashboardData {
  open_matches: Match[];
  locked_matches: Match[];
  next_unlock: { unlock_time: string; count: number } | null;
  counts: { picks: number; open: number; upcoming: number; total: number };
  stats: { teams: number; matches: number; hosts: number };
}

export interface LeaderboardRow {
  rank: number;
  username: string;
  favorite_team: string;
  favorite_team_flag: string | null;
  points: number;
  correct: number;
  potm_correct: number;
  scored_matches: number;
}

export interface LeaderboardData {
  rows: LeaderboardRow[];
  podium: LeaderboardRow[];
  match_points: number;
  potm_points: number;
  current_username: string | null;
}

export interface Scorer {
  rank: number;
  name: string;
  team: string;
  team_flag: string | null;
  position: string;
  goals: number;
  assists: number;
  penalties: number;
}

export interface ScorersData {
  scorers: Scorer[];
  api_enabled: boolean;
  api_status: string | null;
}

export interface AdminData {
  matches: Match[];
  api_enabled: boolean;
  teams: Team[];
}
