// In server components, route directly to the backend; in client components, use the Next.js proxy.
// The Next.js proxy is at /api/[...path] and forwards to BACKEND_URL (env var, default port 9001).
const BASE_URL =
  typeof window === "undefined"
    ? (process.env.BACKEND_URL || "http://127.0.0.1:9001")
    : "";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  // Server components use BASE_URL directly; client components use Next.js /api proxy.
  const url = typeof window === "undefined" ? `${BASE_URL}${path}` : `/api${path}`;
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export interface HealthResponse { status: string }
export interface DashboardStatus { status: string; artifacts: Record<string, any>; sync: any; diagnostics: any }
export interface Player {
  player_name: string; preferred_name?: string; position?: string;
  current_club?: string; nationality?: string; date_of_birth?: string;
  features?: Record<string, any>; kpi?: Record<string, any>; valuation?: Record<string, any>;
}
export interface PlayerListResponse { count: number; items: Player[] }
export interface MatchStat {
  match_date?: string; club_name?: string; minutes?: number;
  goals?: number; assists?: number; shots?: number;
  yellow_cards?: number; red_cards?: number; source?: string;
}
export interface ValuationRow {
  player_name: string; position?: string; current_club?: string; competition?: string;
  valuation_score: number; valuation_tier: string;
  future_value?: { current: number; in_2yr: number; in_5yr: number; peak_window: string };
  components?: Record<string, number>; inputs?: Record<string, any>;
  model_version?: string;
}
export interface SimilarPlayer {
  player_name: string; position?: string; current_club?: string;
  similarity_score: number; trajectory?: string; valuation_score?: number;
  comp_classification?: string;
}
export interface CompareResponse {
  player_name: string; position?: string; role?: string;
  comparison_features?: Record<string, number>; similar_players: SimilarPlayer[];
}
export interface PathwayRow {
  player_name: string; position?: string; current_club?: string;
  development_stage?: string; trajectory?: string;
  age_league_percentile?: number; improvement_rate?: number;
  development_velocity?: number; best_pathway?: string[];
  success_probability?: number; minutes_growth?: { trend: string; delta: number };
}
export interface BenchmarkRow {
  club: string; development_score: number;
  reference_benchmarks?: Record<string, number>;
  live_metrics?: Record<string, any>; comparison_vs_idv?: Record<string, number>;
}
export interface AdvancedMetricsRow {
  player_name: string; xg_total?: number; xa_total?: number;
  xg_per_90?: number; xa_per_90?: number; xt_per_90?: number;
  epv_per_90?: number; obv_total?: number; progression_score?: number;
}
export interface UndervaluedRow extends ValuationRow {
  market_value_raw?: string; market_value_eur?: number; computed_value_eur?: number;
  potential_score?: number; value_gap_pct?: number | null; gap_type?: string;
}

export const api = {
  health: () => fetchAPI<HealthResponse>("/health"),
  dashboardStatus: () => fetchAPI<DashboardStatus>("/dashboard/status"),
  players: (params?: { name?: string; position?: string; limit?: number; offset?: number }) => {
    const q = new URLSearchParams();
    if (params?.name) q.set("name", params.name);
    if (params?.position) q.set("position", params.position);
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    return fetchAPI<PlayerListResponse>(`/players?${q}`);
  },
  playerStats: (name: string) => fetchAPI<{ player_name: string; count: number; items: MatchStat[] }>(`/players/${encodeURIComponent(name)}/stats`),
  valuation: (params?: { tier?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.tier) q.set("tier", params.tier);
    if (params?.limit) q.set("limit", String(params.limit || 50));
    return fetchAPI<{ count: number; items: ValuationRow[] }>(`/value?${q}`);
  },
  playerValuation: (name: string) => fetchAPI<ValuationRow>(`/value?player_name=${encodeURIComponent(name)}`),
  compare: (name: string) => fetchAPI<CompareResponse>(`/compare?player_name=${encodeURIComponent(name)}`),
  pathway: (name?: string) => name
    ? fetchAPI<PathwayRow>(`/pathway/${encodeURIComponent(name)}`)
    : fetchAPI<{ count: number; items: PathwayRow[] }>("/pathway"),
  benchmark: () => fetchAPI<{ count: number; items: BenchmarkRow[] }>("/benchmark"),
  advancedMetrics: (name?: string) => fetchAPI<{ count: number; items: AdvancedMetricsRow[] }>(
    name ? `/advanced-metrics?player_name=${encodeURIComponent(name)}` : "/advanced-metrics"
  ),
  undervalued: (params?: { min_gap_pct?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.min_gap_pct != null) q.set("min_gap_pct", String(params.min_gap_pct));
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: UndervaluedRow[] }>(`/undervalued?${q}`);
  },
  adminStatus: () => fetchAPI<any>("/admin/status"),
  adminRunPipeline: () => fetchAPI<any>("/admin/pipeline/run", { method: "POST" }),
};
