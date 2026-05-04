import { api } from "@/lib/api";
import { StatusDot, StatCard, Card } from "@/components/ui";
import Link from "next/link";

async function getDashboardData() {
  try {
    const [health, status] = await Promise.all([api.health(), api.dashboardStatus()]);
    return { health, status, error: null };
  } catch (e: any) {
    return { health: null, status: null, error: e.message };
  }
}

export default async function DashboardPage() {
  const { health, status, error } = await getDashboardData();

  const artifacts = status?.artifacts || {};
  const artifactList = Object.entries(artifacts);
  const readyCount = artifactList.filter(([, v]: any) => v.state === "ready").length;
  const totalCount = artifactList.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Football Intelligence Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Independiente del Valle · Player Analysis Platform</p>
        </div>
        <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2">
          <StatusDot status={status?.status} />
          <span className="text-sm text-slate-300 capitalize">{status?.status || "Unknown"}</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700/50 text-red-300 rounded-xl p-4 text-sm">
          Backend unavailable: {error}. Make sure the API is running at port 9001.
        </div>
      )}

      {/* System stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="API Status" value={health?.status === "ok" ? "Online" : "Offline"} color={health?.status === "ok" ? "green" : "red"} />
        <StatCard label="Artifacts Ready" value={`${readyCount} / ${totalCount}`} color="blue" />
        <StatCard label="Last Sync" value={status?.sync?.last_successful_sync_at ? new Date(status.sync.last_successful_sync_at).toLocaleString() : "—"} color="slate" />
        <StatCard label="System" value={status?.status ? status.status.toUpperCase() : "—"} color={status?.status === "ready" ? "green" : "yellow"} />
      </div>

      {/* Quick navigation */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { href: "/scout", icon: "✨", title: "AI Recruitment Workflow", desc: "Advanced shortlist, analyze, and decisions" },
          { href: "/players", icon: "👤", title: "Players", desc: "Browse IDV squad profiles and stats" },
          { href: "/valuation", icon: "💰", title: "Valuation", desc: "Player value scores and projections" },
          { href: "/undervalued", icon: "🔍", title: "Undervalued", desc: "Players priced below model estimate" },
          { href: "/market-value", icon: "💶", title: "Market Value", desc: "€ predictions: base × perf × age × demand" },
          { href: "/intelligence", icon: "🧠", title: "Intelligence", desc: "Transfer probability + club fit rankings" },
          { href: "/alerts", icon: "🚨", title: "Alerts", desc: "Breakout, undervalued, and decline signals" },
          { href: "/decision", icon: "🎯", title: "Decisions", desc: "BUY / SELL / HOLD with full reasoning" },
          { href: "/simulation", icon: "🔬", title: "Simulation", desc: "Projected performance in any league" },
          { href: "/scout-report", icon: "📋", title: "Scout Reports", desc: "AI-generated scouting assessments" },
          { href: "/compare", icon: "⚖️", title: "Compare", desc: "Role-aware similarity engine" },
          { href: "/pathway", icon: "🛤️", title: "Pathway", desc: "Development trajectory and career paths" },
          { href: "/benchmark", icon: "🏆", title: "Benchmark", desc: "IDV vs Benfica vs Ajax vs Salzburg" },
          { href: "/admin", icon: "⚙️", title: "Admin", desc: "Pipeline control and data validation" },
        ].map(({ href, icon, title, desc }) => (
          <Link key={href} href={href}
            className="bg-slate-800 border border-slate-700 hover:border-blue-600 hover:bg-slate-700/60 rounded-xl p-5 transition-all group">
            <div className="text-2xl mb-2">{icon}</div>
            <h3 className="font-semibold text-white group-hover:text-blue-400 transition-colors">{title}</h3>
            <p className="text-slate-400 text-sm mt-1">{desc}</p>
          </Link>
        ))}
      </div>

      {/* Artifact status table */}
      {artifactList.length > 0 && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">Artifact Status</h2>
          <div className="space-y-2">
            {artifactList.map(([name, art]: any) => (
              <div key={name} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                <div className="flex items-center gap-2">
                  <StatusDot status={art.state} />
                  <span className="text-slate-200 text-sm font-medium">{name}</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span>{art.row_count ?? 0} rows</span>
                  <span className="capitalize">{art.state}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {status?.diagnostics?.recommended_action && (
        <div className="bg-blue-900/20 border border-blue-700/30 text-blue-300 rounded-xl p-4 text-sm">
          💡 {status.diagnostics.recommended_action}
        </div>
      )}
    </div>
  );
}
