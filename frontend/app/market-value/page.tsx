import { api, MarketValueRow } from "@/lib/api";

export const metadata = { title: "Market Value — IDV Intelligence" };

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? "bg-emerald-500" : pct >= 60 ? "bg-blue-500" : "bg-amber-500";
  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="flex-1 bg-gray-700 rounded h-1.5">
        <div className={`h-1.5 rounded ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-gray-400 w-8 text-right">{pct}%</span>
    </div>
  );
}

function formatEur(val: number | undefined | null): string {
  if (val == null) return "—";
  if (val >= 1_000_000) return `€${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `€${(val / 1_000).toFixed(0)}K`;
  return `€${val.toFixed(0)}`;
}

export default async function MarketValuePage() {
  let rows: MarketValueRow[] = [];
  let error = "";

  try {
    const data = await api.marketValue({ limit: 18 });
    rows = data.items;
  } catch (e) {
    error = "Market value data unavailable — run pipeline first";
  }

  const totalBlended = rows.reduce((s, r) => s + (r.blended_value_eur || 0), 0);

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-3xl font-bold mb-1">Market Value Model</h1>
      <p className="text-gray-400 mb-1 text-sm">
        Predicted € values: base_league × performance × age × demand
      </p>
      {rows.length > 0 && (
        <p className="text-emerald-400 text-sm font-semibold mb-6">
          Squad total estimated value: {formatEur(totalBlended)}
        </p>
      )}

      {error && (
        <div className="bg-amber-900/40 border border-amber-700 rounded p-3 mb-6 text-sm text-amber-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {rows.map((r) => (
          <div key={r.player_name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-semibold">{r.player_name}</div>
                <div className="text-xs text-gray-400 mt-0.5">confidence</div>
                <ConfidenceBar value={r.value_confidence} />
              </div>
              <div className="text-right">
                <div className="text-xl font-bold text-emerald-400">
                  {formatEur(r.blended_value_eur)}
                </div>
                <div className="text-xs text-gray-400">blended</div>
              </div>
            </div>

            <div className="border-t border-gray-700 pt-3 grid grid-cols-2 gap-2 text-xs">
              <div>
                <div className="text-gray-400">Model prediction</div>
                <div className="font-mono font-semibold mt-0.5">{formatEur(r.predicted_value_eur)}</div>
              </div>
              {r.market_value_eur_raw != null && (
                <div>
                  <div className="text-gray-400">Market (TM)</div>
                  <div className="font-mono font-semibold mt-0.5">{formatEur(r.market_value_eur_raw)}</div>
                </div>
              )}
            </div>

            {r.components && (
              <div className="mt-3 pt-3 border-t border-gray-700 grid grid-cols-2 gap-1 text-xs text-gray-400">
                <div>Base: {formatEur(r.components.base_value_eur)}</div>
                <div>Perf ×{r.components.performance_factor?.toFixed(2)}</div>
                <div>Age ×{r.components.age_factor?.toFixed(2)}</div>
                <div>Demand ×{r.components.demand_factor?.toFixed(2)}</div>
              </div>
            )}
          </div>
        ))}
      </div>

      {rows.length === 0 && !error && (
        <p className="text-gray-500 italic text-center py-16">No market value data. Run pipeline first.</p>
      )}
    </main>
  );
}
