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
  transferProbability: (params?: { min_prob?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.min_prob != null) q.set("min_prob", String(params.min_prob));
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: TransferProbRow[] }>(`/transfer-probability?${q}`);
  },
  clubFit: (playerName?: string) => playerName
    ? fetchAPI<ClubFitRow>(`/club-fit/${encodeURIComponent(playerName)}`)
    : fetchAPI<{ count: number; items: ClubFitRow[] }>("/club-fit"),
  marketValue: (params?: { player_name?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.player_name) q.set("player_name", params.player_name);
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: MarketValueRow[] }>(`/market-value?${q}`);
  },
  clusters: () => fetchAPI<{ players: ClusterRow[]; centroids: any[] }>("/clusters"),
  alerts: (params?: { alert_type?: string; severity?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.alert_type) q.set("alert_type", params.alert_type);
    if (params?.severity) q.set("severity", params.severity);
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ summary: any; count: number; items: AlertRow[] }>(`/alerts?${q}`);
  },
  featureStore: (params?: { player_name?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.player_name) q.set("player_name", params.player_name);
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: any[] }>(`/feature-store?${q}`);
  },
  adminStatus: () => fetchAPI<any>("/admin/status"),
  adminRunPipeline: () => fetchAPI<any>("/admin/pipeline/run", { method: "POST" }),
  adminDiscover: (leagueKeys?: string[]) => fetchAPI<any>("/admin/discover", {
    method: "POST",
    body: JSON.stringify(leagueKeys || null),
  }),
  decisions: (params?: { decision_type?: string; min_confidence?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.decision_type) q.set("decision_type", params.decision_type);
    if (params?.min_confidence != null) q.set("min_confidence", String(params.min_confidence));
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: DecisionRow[] }>(`/decision?${q}`);
  },
  decision: (playerName: string) => fetchAPI<DecisionRow>(`/decision/${encodeURIComponent(playerName)}`),
  simulations: (params?: { limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: SimulationRow[] }>(`/simulation?${q}`);
  },
  simulation: (playerName: string) => fetchAPI<SimulationRow>(`/simulation/${encodeURIComponent(playerName)}`),
  scoutReports: (params?: { decision?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.decision) q.set("decision", params.decision);
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: ScoutReportRow[] }>(`/scout-report?${q}`);
  },
  scoutReport: (playerName: string) => fetchAPI<ScoutReportRow>(`/scout-report/${encodeURIComponent(playerName)}`),
  playerGraph: () => fetchAPI<any>("/player-graph"),
  pathwayLearning: (params?: { limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.limit) q.set("limit", String(params.limit));
    return fetchAPI<{ count: number; items: PathwayLearningRow[] }>(`/pathway-learning?${q}`);
  },
  shortlist: (params: { position?: string; age_max?: number; market_value_max?: number; league_level?: string }) =>
    fetchAPI<any[]>("/shortlist", { method: "POST", body: JSON.stringify(params) }),
  playerProfile: (slug: string) => fetchAPI<any>(`/player/${encodeURIComponent(slug)}`),
  decisionEngine: (slug: string) => fetchAPI<any>(`/player/${encodeURIComponent(slug)}/decision`),
  comparePlayers: (players: string[]) => fetchAPI<any>("/compare", { method: "POST", body: JSON.stringify({ players }) }),
  alertsPanel: () => fetchAPI<any[]>("/alerts"),
  clubFitEngine: (club: string, player_slug: string) => fetchAPI<any>("/club-fit", { method: "POST", body: JSON.stringify({ club, player_slug }) }),
  reportGenerator: (player_slug: string) => fetchAPI<any>("/report", { method: "POST", body: JSON.stringify({ player_slug }) }),
  saveShortlist: (data: { name?: string; filters?: any; players: string[]; notes?: string }) =>
    fetchAPI<any>("/shortlist/save", { method: "POST", body: JSON.stringify(data) }),
  listSavedShortlists: () => fetchAPI<any[]>("/shortlist/saved"),
  deleteSavedShortlist: (id: string) => fetchAPI<any>(`/shortlist/${encodeURIComponent(id)}`, { method: "DELETE" }),
};

export interface TransferProbRow {
  player_name: string; age?: number;
  transfer_probability_1y: number; transfer_probability_2y: number;
  transfer_category: string;
  features?: Record<string, number>;
}
export interface ClubFitRow {
  player_name: string; age?: number; position?: string;
  best_fit_club?: string; best_fit_score?: number;
  top_5_club_fits: Array<{ club: string; fit_score: number; components: Record<string, number> }>;
}
export interface MarketValueRow {
  player_name: string; predicted_value_eur: number; blended_value_eur: number;
  market_value_eur_raw?: number; value_confidence: number;
  components?: { base_value_eur: number; performance_factor: number; age_factor: number; demand_factor: number };
}
export interface ClusterRow {
  player_name: string; cluster_id: number; cluster_label: string;
  feature_vector?: number[];
}
export interface AlertRow {
  alert_type: string; severity: string; player_name: string;
  trigger_reason: string; supporting_metrics: Record<string, any>;
}
export interface DecisionRow {
  player_name: string; age?: number; decision: "BUY" | "SELL" | "HOLD";
  decision_confidence: number; buy_score: number; sell_score: number;
  reasoning: string[];
  buy_components: Record<string, number>;
  sell_components: Record<string, number>;
  supporting_data: Record<string, any>;
}
export interface SimulationRow {
  player_name: string; age?: number; current_league?: string;
  current_kpi?: number; current_valuation_score?: number; trajectory?: string;
  best_projection: { target_league?: string; projected_kpi?: number; projected_value_eur?: number; minutes_probability?: number; simulation_confidence?: number };
  league_simulations: Array<{ target_league: string; projected_kpi: number; projected_value_eur: number; minutes_probability: number; adaptation_months: number; simulation_confidence: number; factors: Record<string, number> }>;
}
export interface ScoutReportRow {
  player_name: string; decision: string; report_text: string; report_source: string;
  key_metrics: { age?: number; valuation_score?: number; kpi_score?: number; blended_value_eur?: number; risk_score?: number; trajectory?: string; best_fit_club?: string };
}
export interface PathwayLearningRow {
  player_name: string; age?: number; current_league?: string;
  trajectory?: string; top_destinations: Array<{ destination: string; success_probability: number }>;
  best_destination?: string; best_success_probability?: number;
}
