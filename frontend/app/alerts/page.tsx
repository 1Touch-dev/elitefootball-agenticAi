import { api, AlertRow } from "@/lib/api";

export const metadata = { title: "Alerts — IDV Intelligence" };

const SEVERITY_STYLE: Record<string, string> = {
  critical: "border-red-500 bg-red-950/40",
  high: "border-amber-500 bg-amber-950/40",
  medium: "border-blue-500 bg-blue-950/40",
  low: "border-gray-600 bg-gray-800/40",
};

const SEVERITY_BADGE: Record<string, string> = {
  critical: "bg-red-600 text-white",
  high: "bg-amber-600 text-white",
  medium: "bg-blue-600 text-white",
  low: "bg-gray-600 text-gray-200",
};

const TYPE_ICON: Record<string, string> = {
  UNDERVALUED: "💰",
  BREAKOUT: "🚀",
  DECLINE: "📉",
};

function SummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className={`bg-gray-800 rounded-lg p-4 border ${color}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-400 mt-1">{label}</div>
    </div>
  );
}

export default async function AlertsPage() {
  let alerts: AlertRow[] = [];
  let summary: any = {};
  let error = "";

  try {
    const data = await api.alerts({ limit: 50 });
    alerts = data.items;
    summary = data.summary;
  } catch (e) {
    error = "Alerts unavailable — run pipeline first";
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-3xl font-bold mb-1">Player Alerts</h1>
      <p className="text-gray-400 mb-6 text-sm">
        Undervalued opportunities, breakout signals, and decline warnings
      </p>

      {error && (
        <div className="bg-amber-900/40 border border-amber-700 rounded p-3 mb-6 text-sm text-amber-300">
          {error}
        </div>
      )}

      {summary && Object.keys(summary).length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <SummaryCard label="Total Alerts" value={summary.total ?? 0} color="border-gray-600" />
          <SummaryCard label="Critical" value={summary.critical ?? 0} color="border-red-600" />
          <SummaryCard label="High" value={summary.high ?? 0} color="border-amber-600" />
          <SummaryCard label="Undervalued" value={summary.undervalued ?? 0} color="border-emerald-600" />
          <SummaryCard label="Breakout" value={summary.breakout ?? 0} color="border-blue-600" />
          <SummaryCard label="Decline" value={summary.decline ?? 0} color="border-purple-600" />
        </div>
      )}

      <div className="space-y-3">
        {alerts.map((alert, i) => (
          <div
            key={i}
            className={`rounded-lg p-4 border ${SEVERITY_STYLE[alert.severity] ?? "border-gray-600 bg-gray-800"}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{TYPE_ICON[alert.alert_type] ?? "⚠️"}</span>
                <div>
                  <div className="font-semibold text-lg">{alert.player_name}</div>
                  <div className="text-sm text-gray-300 mt-0.5">{alert.trigger_reason}</div>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${SEVERITY_BADGE[alert.severity]}`}>
                  {alert.severity.toUpperCase()}
                </span>
                <span className="text-xs text-gray-400">{alert.alert_type}</span>
              </div>
            </div>

            {alert.supporting_metrics && Object.keys(alert.supporting_metrics).length > 0 && (
              <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(alert.supporting_metrics)
                  .filter(([, v]) => v != null && v !== false)
                  .slice(0, 6)
                  .map(([k, v]) => (
                    <div key={k} className="bg-black/20 rounded p-2">
                      <div className="text-xs text-gray-400">{k.replace(/_/g, " ")}</div>
                      <div className="text-sm font-mono font-semibold mt-0.5">
                        {typeof v === "number"
                          ? k.includes("eur")
                            ? `€${(v as number).toLocaleString()}`
                            : k.includes("prob") || k.includes("pct") || k.includes("score")
                            ? (v as number).toFixed(2)
                            : String(v)
                          : String(v)}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        ))}

        {alerts.length === 0 && !error && (
          <div className="text-center text-gray-500 py-16 italic">
            No alerts at this time. Run the pipeline to generate analysis.
          </div>
        )}
      </div>
    </main>
  );
}
