import { api, ScoutReportRow } from "@/lib/api";

export const metadata = { title: "Scout Reports" };

const DECISION_BADGE: Record<string, string> = {
  BUY:  "bg-emerald-600 text-white",
  SELL: "bg-red-600 text-white",
  HOLD: "bg-slate-600 text-slate-200",
};

function formatEur(v?: number) {
  if (!v) return "—";
  if (v >= 1_000_000) return `€${(v / 1_000_000).toFixed(1)}M`;
  return `€${Math.round(v / 1000)}K`;
}

function ReportCard({ row }: { row: ScoutReportRow }) {
  const m = row.key_metrics;
  const lines = (row.report_text || "").split("\n").filter(l => l.trim());

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-slate-700">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-white font-semibold text-lg">{row.player_name}</p>
            <div className="flex gap-3 mt-1 text-xs text-slate-400">
              {m.age && <span>Age {m.age}</span>}
              {m.trajectory && <span className="capitalize">{m.trajectory}</span>}
              {m.best_fit_club && <span>{m.best_fit_club}</span>}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${DECISION_BADGE[row.decision] ?? DECISION_BADGE.HOLD}`}>
              {row.decision}
            </span>
            <span className="text-xs text-slate-500 capitalize">{row.report_source}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-4">
          {m.valuation_score != null && (
            <div className="bg-slate-700/50 rounded-lg p-2 text-center">
              <p className="text-xs text-slate-400">Valuation</p>
              <p className="text-white font-bold">{m.valuation_score.toFixed(0)}</p>
            </div>
          )}
          {m.kpi_score != null && (
            <div className="bg-slate-700/50 rounded-lg p-2 text-center">
              <p className="text-xs text-slate-400">KPI</p>
              <p className="text-white font-bold">{m.kpi_score.toFixed(1)}</p>
            </div>
          )}
          {m.blended_value_eur != null && (
            <div className="bg-slate-700/50 rounded-lg p-2 text-center">
              <p className="text-xs text-slate-400">Est. Value</p>
              <p className="text-white font-bold">{formatEur(m.blended_value_eur)}</p>
            </div>
          )}
        </div>
      </div>

      {/* Report text */}
      <div className="p-5">
        <div className="text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap max-h-64 overflow-y-auto bg-slate-900/50 rounded-lg p-3">
          {lines.map((line, i) => {
            const isHeader = /^\d+\.\s/.test(line) || line.startsWith("===") || line.startsWith("SCOUT REPORT");
            return (
              <div key={i} className={isHeader ? "text-blue-300 font-semibold mt-2" : ""}>
                {line}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default async function ScoutReportPage() {
  let rows: ScoutReportRow[] = [];
  let error: string | null = null;

  try {
    const res = await api.scoutReports({ limit: 18 });
    rows = res.items;
  } catch (e: any) {
    error = e.message;
  }

  const buys  = rows.filter(r => r.decision === "BUY");
  const holds = rows.filter(r => r.decision === "HOLD");
  const sells = rows.filter(r => r.decision === "SELL");
  const ordered = [...buys, ...holds, ...sells];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Scout Reports</h1>
        <p className="text-slate-400 text-sm mt-1">
          AI-generated scouting assessments with BUY/SELL/HOLD recommendations
        </p>
      </div>

      {error && (
        <div className="bg-amber-900/30 border border-amber-700/50 text-amber-300 rounded-xl p-4 text-sm">
          {error} — run pipeline first.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "BUY", count: buys.length, color: "text-emerald-400" },
          { label: "HOLD", count: holds.length, color: "text-slate-300" },
          { label: "SELL", count: sells.length, color: "text-red-400" },
        ].map(({ label, count, color }) => (
          <div key={label} className="bg-slate-800 border border-slate-700 rounded-xl p-4 text-center">
            <p className={`text-3xl font-bold ${color}`}>{count}</p>
            <p className="text-sm text-slate-400 mt-1">{label} reports</p>
          </div>
        ))}
      </div>

      {ordered.length === 0 && !error && (
        <p className="text-slate-500 text-center py-12">No scout reports — run pipeline first.</p>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {ordered.map(r => <ReportCard key={r.player_name} row={r} />)}
      </div>
    </div>
  );
}
