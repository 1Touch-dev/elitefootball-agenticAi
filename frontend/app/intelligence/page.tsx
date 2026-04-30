import { api, TransferProbRow, ClubFitRow } from "@/lib/api";

export const metadata = { title: "Intelligence — Transfer & Club Fit" };

function ProbBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 70 ? "bg-red-500" : pct >= 45 ? "bg-amber-500" : pct >= 25 ? "bg-blue-500" : "bg-gray-400";
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 w-6">{label}</span>
      <div className="flex-1 bg-gray-700 rounded h-2">
        <div className={`h-2 rounded ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono w-10 text-right">{pct}%</span>
    </div>
  );
}

function CategoryBadge({ cat }: { cat: string }) {
  const map: Record<string, string> = {
    imminent: "bg-red-600 text-white",
    likely: "bg-amber-600 text-white",
    possible: "bg-blue-600 text-white",
    unlikely: "bg-gray-600 text-gray-200",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${map[cat] ?? "bg-gray-600"}`}>
      {cat.toUpperCase()}
    </span>
  );
}

export default async function IntelligencePage() {
  let transferRows: TransferProbRow[] = [];
  let clubFitRows: ClubFitRow[] = [];
  let errors: string[] = [];

  try {
    const tp = await api.transferProbability({ limit: 18 });
    transferRows = tp.items;
  } catch (e) {
    errors.push("Transfer probability unavailable — run pipeline first");
  }
  try {
    const cf = await api.clubFit();
    if ("items" in cf) clubFitRows = (cf as any).items;
  } catch (e) {
    errors.push("Club fit unavailable — run pipeline first");
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-3xl font-bold mb-1">Transfer Intelligence</h1>
      <p className="text-gray-400 mb-6 text-sm">
        Transfer probability model + club fit recommendations
      </p>

      {errors.map((e, i) => (
        <div key={i} className="bg-amber-900/40 border border-amber-700 rounded p-3 mb-4 text-sm text-amber-300">
          {e}
        </div>
      ))}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Transfer Probability */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-blue-300">Transfer Probability</h2>
          <div className="space-y-3">
            {transferRows.map((r) => (
              <div key={r.player_name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold">{r.player_name}</span>
                  <div className="flex items-center gap-2">
                    {r.age && <span className="text-xs text-gray-400">Age {r.age}</span>}
                    <CategoryBadge cat={r.transfer_category} />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <ProbBar value={r.transfer_probability_1y} label="1yr" />
                  <ProbBar value={r.transfer_probability_2y} label="2yr" />
                </div>
              </div>
            ))}
            {transferRows.length === 0 && !errors.length && (
              <p className="text-gray-500 italic">No transfer probability data available.</p>
            )}
          </div>
        </section>

        {/* Club Fit */}
        <section>
          <h2 className="text-xl font-semibold mb-4 text-emerald-300">Club Fit Recommendations</h2>
          <div className="space-y-3">
            {clubFitRows.slice(0, 12).map((r) => (
              <div key={r.player_name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">{r.player_name}</span>
                  {r.position && (
                    <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">
                      {r.position}
                    </span>
                  )}
                </div>
                <div className="space-y-1">
                  {(r.top_5_club_fits || []).slice(0, 3).map((fit) => (
                    <div key={fit.club} className="flex items-center justify-between text-sm">
                      <span className="capitalize text-gray-300">{fit.club}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-700 rounded h-1.5">
                          <div
                            className="h-1.5 rounded bg-emerald-500"
                            style={{ width: `${Math.round(fit.fit_score * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-gray-400 w-8 text-right">
                          {(fit.fit_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            {clubFitRows.length === 0 && !errors.length && (
              <p className="text-gray-500 italic">No club fit data available.</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
