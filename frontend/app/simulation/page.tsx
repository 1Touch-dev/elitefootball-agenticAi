import { api, SimulationRow } from "@/lib/api";

export const metadata = { title: "Player Simulation — League Projections" };

function formatEur(v?: number) {
  if (!v) return "—";
  if (v >= 1_000_000) return `€${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `€${(v / 1_000).toFixed(0)}K`;
  return `€${v}`;
}

const PRESTIGE_COLOR = (p: number) =>
  p >= 0.88 ? "text-amber-400" : p >= 0.70 ? "text-blue-400" : "text-slate-300";

function SimCard({ row }: { row: SimulationRow }) {
  const best = row.best_projection;
  const top = (row.league_simulations || []).slice(0, 5);

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-white">{row.player_name}</p>
          <p className="text-xs text-slate-400">
            Age {row.age ?? "?"} · {row.current_league ?? "unknown league"} · {row.trajectory ?? "stable"}
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-300">Current KPI</p>
          <p className="text-xl font-bold text-white">{row.current_kpi?.toFixed(1) ?? "—"}</p>
        </div>
      </div>

      {best?.target_league && (
        <div className="bg-blue-950/40 border border-blue-700/40 rounded-lg p-3 mb-3">
          <p className="text-xs text-blue-300 font-semibold uppercase mb-1">Best projection</p>
          <p className="text-sm text-white font-medium">{best.target_league}</p>
          <div className="flex gap-4 mt-1 text-xs text-slate-300">
            <span>KPI: <strong className="text-white">{best.projected_kpi?.toFixed(1)}</strong></span>
            <span>Value: <strong className="text-white">{formatEur(best.projected_value_eur)}</strong></span>
            <span>Minutes prob: <strong className="text-white">{Math.round((best.minutes_probability ?? 0) * 100)}%</strong></span>
          </div>
        </div>
      )}

      <div className="space-y-1.5">
        {top.map(sim => (
          <div key={sim.target_league} className="flex items-center justify-between py-1 border-b border-slate-700/40 last:border-0">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-medium ${PRESTIGE_COLOR(sim.factors?.target_league_prestige ?? 0)}`}>
                {sim.target_league}
              </span>
              <span className="text-xs text-slate-500">
                +{sim.adaptation_months}mo adapt
              </span>
            </div>
            <div className="flex gap-4 text-xs font-mono text-right">
              <span className="text-slate-400">KPI {sim.projected_kpi?.toFixed(1)}</span>
              <span className="text-slate-300">{formatEur(sim.projected_value_eur)}</span>
              <span className="text-slate-500">{Math.round((sim.minutes_probability ?? 0) * 100)}%min</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default async function SimulationPage() {
  let rows: SimulationRow[] = [];
  let error: string | null = null;

  try {
    const res = await api.simulations({ limit: 18 });
    rows = res.items;
  } catch (e: any) {
    error = e.message;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Player Simulation</h1>
        <p className="text-slate-400 text-sm mt-1">
          Projected KPI, value, and minutes probability for each player in different leagues
        </p>
      </div>

      {error && (
        <div className="bg-amber-900/30 border border-amber-700/50 text-amber-300 rounded-xl p-4 text-sm">
          {error} — run pipeline first.
        </div>
      )}

      <div className="text-xs text-slate-500 bg-slate-800/50 border border-slate-700 rounded-lg p-3">
        <strong className="text-slate-300">How it works:</strong> Current KPI and valuation are adjusted by league difficulty,
        tactical fit, minutes probability, and trajectory momentum. Adaptation months estimates time to reach projected peak.
      </div>

      {rows.length === 0 && !error && (
        <p className="text-slate-500 text-center py-12">No simulation data — run pipeline first.</p>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        {rows.map(r => <SimCard key={r.player_name} row={r} />)}
      </div>
    </div>
  );
}
