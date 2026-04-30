import { api, DecisionRow } from "@/lib/api";

export const metadata = { title: "Transfer Decisions — BUY / SELL / HOLD" };

const DECISION_STYLE: Record<string, { bg: string; border: string; badge: string; text: string }> = {
  BUY:  { bg: "bg-emerald-950/40",  border: "border-emerald-700/60", badge: "bg-emerald-600 text-white",  text: "text-emerald-400" },
  SELL: { bg: "bg-red-950/40",      border: "border-red-700/60",     badge: "bg-red-600 text-white",      text: "text-red-400"     },
  HOLD: { bg: "bg-slate-800/60",    border: "border-slate-600/60",   badge: "bg-slate-600 text-slate-200", text: "text-slate-300"  },
};

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-700 rounded h-1.5">
        <div className={`h-1.5 rounded ${color}`} style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <span className="text-xs font-mono text-slate-300 w-10 text-right">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}

function DecisionCard({ row }: { row: DecisionRow }) {
  const style = DECISION_STYLE[row.decision] ?? DECISION_STYLE.HOLD;
  const confPct = Math.round((row.decision_confidence ?? 0) * 100);

  return (
    <div className={`rounded-xl border p-5 ${style.bg} ${style.border}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-white text-lg">{row.player_name}</p>
          {row.age && <p className="text-slate-400 text-sm">Age {row.age}</p>}
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`px-3 py-1 rounded-full text-sm font-bold ${style.badge}`}>
            {row.decision}
          </span>
          <span className="text-xs text-slate-400">{confPct}% confidence</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <p className="text-xs text-slate-400 mb-1">Buy score</p>
          <ScoreBar value={row.buy_score} color="bg-emerald-500" />
        </div>
        <div>
          <p className="text-xs text-slate-400 mb-1">Sell score</p>
          <ScoreBar value={row.sell_score} color="bg-red-500" />
        </div>
      </div>

      {row.reasoning && row.reasoning.length > 0 && (
        <ul className="mt-2 space-y-1">
          {row.reasoning.slice(0, 3).map((r, i) => (
            <li key={i} className="text-xs text-slate-300 flex gap-1.5">
              <span className={`mt-0.5 ${style.text}`}>▸</span>
              {r}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default async function DecisionPage() {
  let rows: DecisionRow[] = [];
  let error: string | null = null;

  try {
    const res = await api.decisions({ limit: 18 });
    rows = res.items;
  } catch (e: any) {
    error = e.message;
  }

  const buys  = rows.filter(r => r.decision === "BUY");
  const sells = rows.filter(r => r.decision === "SELL");
  const holds = rows.filter(r => r.decision === "HOLD");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Transfer Decisions</h1>
        <p className="text-slate-400 text-sm mt-1">
          BUY / SELL / HOLD — weighted model (undervalued, potential, age risk, injury, market peak)
        </p>
      </div>

      {error && (
        <div className="bg-amber-900/30 border border-amber-700/50 text-amber-300 rounded-xl p-4 text-sm">
          {error} — run pipeline first.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-emerald-950/40 border border-emerald-700/50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">{buys.length}</p>
          <p className="text-sm text-slate-400 mt-1">BUY signals</p>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-slate-300">{holds.length}</p>
          <p className="text-sm text-slate-400 mt-1">HOLD signals</p>
        </div>
        <div className="bg-red-950/40 border border-red-700/50 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-red-400">{sells.length}</p>
          <p className="text-sm text-slate-400 mt-1">SELL signals</p>
        </div>
      </div>

      {buys.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wide mb-3">
            BUY Recommendations
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {buys.map(r => <DecisionCard key={r.player_name} row={r} />)}
          </div>
        </section>
      )}

      {holds.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
            HOLD
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {holds.map(r => <DecisionCard key={r.player_name} row={r} />)}
          </div>
        </section>
      )}

      {sells.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-red-400 uppercase tracking-wide mb-3">
            SELL Recommendations
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {sells.map(r => <DecisionCard key={r.player_name} row={r} />)}
          </div>
        </section>
      )}
    </div>
  );
}
