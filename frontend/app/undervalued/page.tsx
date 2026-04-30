import { api } from "@/lib/api";
import { TierBadge, ScoreBar, EmptyState } from "@/components/ui";
import Link from "next/link";

function fmt(val: number | null | undefined): string {
  if (val == null) return "—";
  if (val >= 1_000_000) return `€${(val / 1_000_000).toFixed(1)}m`;
  if (val >= 1_000) return `€${(val / 1_000).toFixed(0)}k`;
  return `€${val}`;
}

export default async function UndervaluedPage() {
  let rows: any[] = [];
  let total = 0;
  let error: string | null = null;

  try {
    const res = await api.undervalued({ min_gap_pct: 0, limit: 50 });
    rows = res.items;
    total = res.count;
  } catch (e: any) {
    error = e.message;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Undervalued Players</h1>
        <p className="text-slate-400 text-sm mt-1">
          Players where our model estimates a higher value than the current market price · {total} flagged
        </p>
      </div>

      {error && <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">{error}</div>}
      {rows.length === 0 && !error && <EmptyState message="No undervalued players found. Run the pipeline first." />}

      <div className="space-y-3">
        {rows.map((row, i) => {
          const gapPct = row.value_gap_pct;
          const isNoMarketData = row.gap_type === "no_market_data_high_score";
          return (
            <Link
              key={row.player_name}
              href={`/players/${encodeURIComponent(row.player_name)}`}
              className="bg-slate-800 border border-slate-700 hover:border-emerald-600/50 rounded-xl p-4 flex items-start gap-4 transition-all group"
            >
              <span className="text-slate-500 text-sm w-8 text-right flex-shrink-0 pt-1">#{i + 1}</span>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-white group-hover:text-emerald-400 transition-colors">
                    {row.player_name}
                  </span>
                  <TierBadge tier={row.valuation_tier} />
                  {isNoMarketData && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-900/40 border border-yellow-700/50 text-yellow-400">
                      No market data
                    </span>
                  )}
                </div>
                <p className="text-slate-400 text-xs mt-0.5">
                  {row.position || "—"} · {row.current_club || "—"}
                </p>

                <div className="mt-2 flex gap-4 flex-wrap text-xs">
                  <span className="text-slate-400">
                    Model score: <span className="text-white font-medium">{row.valuation_score?.toFixed(1)}</span>
                  </span>
                  {row.potential_score != null && (
                    <span className="text-slate-400">
                      Potential: <span className="text-purple-400 font-medium">{row.potential_score?.toFixed(1)}</span>
                    </span>
                  )}
                  {row.market_value_raw && (
                    <span className="text-slate-400">
                      Market: <span className="text-slate-300 font-medium">{row.market_value_raw}</span>
                    </span>
                  )}
                  {row.computed_value_eur != null && (
                    <span className="text-slate-400">
                      Computed: <span className="text-emerald-400 font-medium">{fmt(row.computed_value_eur)}</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="flex-shrink-0 text-right">
                {gapPct != null ? (
                  <div>
                    <p className="text-xs text-slate-500 mb-0.5">Undervaluation</p>
                    <p className="text-xl font-bold text-emerald-400">+{gapPct.toFixed(0)}%</p>
                  </div>
                ) : (
                  <div className="w-24">
                    <p className="text-xs text-slate-500 mb-1">Model Score</p>
                    <ScoreBar value={row.valuation_score || 0} color="#34d399" />
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </div>

      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-sm text-slate-400">
        <p className="font-medium text-slate-300 mb-2">How undervaluation is calculated</p>
        <p className="text-xs">
          Computed value = (valuation_score − 40) × €500k. Players are flagged when computed value exceeds
          market price by 25%+. Players without Transfermarkt market data are shown separately if their
          model score is ≥60.
        </p>
      </div>
    </div>
  );
}
