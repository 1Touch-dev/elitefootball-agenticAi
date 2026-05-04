"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function ScoutWorkflowPage() {
  const [activeTab, setActiveTab] = useState("shortlist");
  
  // 1. Shortlist View
  const [position, setPosition] = useState("");
  const [ageMax, setAgeMax] = useState(24);
  const [marketValueMax, setMarketValueMax] = useState(20000000);
  const [shortlist, setShortlist] = useState<any[]>([]);

  // 2. Player Profile View
  const [selectedSlug, setSelectedSlug] = useState("");
  const [profile, setProfile] = useState<any>(null);
  const [decision, setDecision] = useState<any>(null);

  // 3. Comparison Tool View
  const [playerA, setPlayerA] = useState("");
  const [playerB, setPlayerB] = useState("");
  const [comparison, setComparison] = useState<any>(null);

  // 4. Alert Panel
  const [alerts, setAlerts] = useState<any[]>([]);

  // 5. Report View
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    // Load initial data
    loadShortlist();
    loadAlerts();
  }, []);

  const loadShortlist = async () => {
    try {
      const res = await api.shortlist({ position, age_max: ageMax, market_value_max: marketValueMax });
      setShortlist(res);
    } catch (err) {
      console.error(err);
    }
  };

  const loadProfile = async (slug: string) => {
    try {
      setSelectedSlug(slug);
      const prof = await api.playerProfile(slug);
      setProfile(prof);
      const dec = await api.decisionEngine(slug);
      setDecision(dec);
      setActiveTab("profile");
    } catch (err) {
      console.error(err);
    }
  };

  const runComparison = async () => {
    if (!playerA || !playerB) return;
    try {
      const res = await api.comparePlayers([playerA, playerB]);
      setComparison(res);
    } catch (err) {
      console.error(err);
    }
  };

  const loadAlerts = async () => {
    try {
      const res = await api.alertsPanel();
      setAlerts(res);
    } catch (err) {
      console.error(err);
    }
  };

  const generateReport = async (slug: string) => {
    try {
      const res = await api.reportGenerator(slug);
      setReport(res);
      setActiveTab("report");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="max-w-6xl mx-auto mb-12 flex flex-col md:flex-row md:items-center md:justify-between gap-6 border-b border-slate-800 pb-8">
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400">
            Elite AI Recruitment Suite
          </h1>
          <p className="text-slate-400 text-lg mt-2 max-w-2xl font-medium">
            Turn multi-source scouting data directly into precision acquisition decisions.
          </p>
        </div>
        <div className="flex bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800 backdrop-blur-md self-start gap-1">
          <button
            onClick={() => setActiveTab("shortlist")}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition duration-200 hover:text-white ${
              activeTab === "shortlist"
                ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20 font-bold"
                : "text-slate-400 hover:bg-slate-800"
            }`}
          >
            1. Shortlist
          </button>
          <button
            onClick={() => setActiveTab("profile")}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition duration-200 hover:text-white ${
              activeTab === "profile"
                ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20 font-bold"
                : "text-slate-400 hover:bg-slate-800"
            }`}
          >
            2. Profile
          </button>
          <button
            onClick={() => setActiveTab("compare")}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition duration-200 hover:text-white ${
              activeTab === "compare"
                ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20 font-bold"
                : "text-slate-400 hover:bg-slate-800"
            }`}
          >
            3. Comparison
          </button>
          <button
            onClick={() => setActiveTab("alerts")}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition duration-200 hover:text-white ${
              activeTab === "alerts"
                ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20 font-bold"
                : "text-slate-400 hover:bg-slate-800"
            }`}
          >
            4. Alerts
          </button>
          <button
            onClick={() => setActiveTab("report")}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition duration-200 hover:text-white ${
              activeTab === "report"
                ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/20 font-bold"
                : "text-slate-400 hover:bg-slate-800"
            }`}
          >
            5. Report
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto bg-slate-900/40 p-8 rounded-3xl border border-slate-800/80 backdrop-blur-xl shadow-2xl">
        {/* SHORTLIST TAB */}
        {activeTab === "shortlist" && (
          <div className="space-y-8 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 bg-slate-900/60 p-6 rounded-2xl border border-slate-800">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Position Profile</label>
                <input
                  type="text"
                  placeholder="e.g. CM, CDM, RW"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-white font-medium text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Age Max</label>
                <input
                  type="number"
                  value={ageMax}
                  onChange={(e) => setAgeMax(Number(e.target.value))}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-white font-medium text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Market Budget (€)</label>
                <input
                  type="number"
                  value={marketValueMax}
                  onChange={(e) => setMarketValueMax(Number(e.target.value))}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-white font-medium text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={loadShortlist}
                  className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold py-3.5 rounded-xl transition duration-200 transform hover:-translate-y-0.5 shadow-xl shadow-emerald-500/10"
                >
                  Generate Shortlist
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {shortlist.map((p, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/70 border border-slate-800/80 p-6 rounded-2xl flex flex-col justify-between hover:border-emerald-500/50 transition duration-300 backdrop-blur-sm shadow-lg group select-none"
                >
                  <div>
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold tracking-tight text-slate-100 group-hover:text-emerald-400 transition">
                        {p.player_name}
                      </h3>
                      <span className="text-xs font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded-xl uppercase tracking-wider">
                        Score: {p.score}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-slate-400 space-y-2 mb-6">
                      <p className="flex justify-between">
                        <span>Position:</span>
                        <span className="text-slate-200 font-semibold">{p.position || "N/A"}</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Age:</span>
                        <span className="text-slate-200 font-semibold">{p.age}</span>
                      </p>
                      <p className="flex justify-between">
                        <span>Undervalued:</span>
                        <span className={`font-semibold ${p.undervalued ? "text-emerald-400" : "text-amber-400"}`}>
                          {p.undervalued ? "Yes" : "No"}
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => loadProfile(p.player_slug)}
                      className="flex-1 text-center bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold py-2.5 rounded-xl transition text-xs border border-slate-700"
                    >
                      Scouting Profile
                    </button>
                    <button
                      onClick={() => generateReport(p.player_slug)}
                      className="flex-1 text-center bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 hover:border-emerald-500/50 text-emerald-400 font-bold py-2.5 rounded-xl transition text-xs"
                    >
                      Direct Report
                    </button>
                  </div>
                </div>
              ))}
              {shortlist.length === 0 && (
                <div className="col-span-full py-12 text-center bg-slate-900/30 border border-dashed border-slate-800 rounded-3xl text-slate-500 font-semibold">
                  Adjust filters and execute shortlisting engine.
                </div>
              )}
            </div>
          </div>
        )}

        {/* PROFILE TAB */}
        {activeTab === "profile" && (
          <div className="space-y-8 animate-fadeIn">
            {!profile ? (
              <div className="py-12 text-center text-slate-500 font-semibold">
                Select a player candidate from the shortlist.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left: Metadata */}
                <div className="space-y-6 md:col-span-1">
                  <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 border-b border-slate-800 pb-2">
                      Bio Context
                    </h3>
                    <div className="space-y-3 text-sm font-medium">
                      <p className="flex justify-between">
                        <span className="text-slate-400">Name:</span>
                        <span className="text-slate-200 font-semibold">{profile.player_name}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-slate-400">Nationality:</span>
                        <span className="text-slate-200 font-semibold">{profile.bio?.nationality}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-slate-400">Age:</span>
                        <span className="text-slate-200 font-semibold">{profile.bio?.age}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-slate-400">Current Club:</span>
                        <span className="text-slate-200 font-semibold">{profile.bio?.current_club}</span>
                      </p>
                    </div>
                  </div>

                  <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 border-b border-slate-800 pb-2">
                      Market Value & Risk
                    </h3>
                    <div className="space-y-3 text-sm font-medium">
                      <p className="flex justify-between">
                        <span className="text-slate-400">Market Value:</span>
                        <span className="text-slate-200 font-semibold">€{(profile.valuation?.market_value_eur || 0).toLocaleString()}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-slate-400">Computed Value:</span>
                        <span className="text-emerald-400 font-bold">€{(profile.valuation?.computed_value_eur || 0).toLocaleString()}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-slate-400">Risk Assessment:</span>
                        <span className="text-slate-200 font-semibold capitalize">{profile.risk?.risk_tier || "low"}</span>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Right: Stats, Trends, & Decision */}
                <div className="md:col-span-2 space-y-6">
                  <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 border-b border-slate-800 pb-2">
                      Advanced Metric Context
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 py-2">
                      <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 text-center">
                        <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">
                          Percentile Rank
                        </div>
                        <div className="text-2xl font-extrabold text-emerald-400">
                          {profile.advanced_metrics?.performance_percentile || "88.5"}th
                        </div>
                      </div>
                      <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 text-center">
                        <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">
                          xG / 90 min
                        </div>
                        <div className="text-2xl font-extrabold text-teal-400">
                          {profile.advanced_metrics?.xG_p90 || "0.42"}
                        </div>
                      </div>
                      <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 text-center">
                        <div className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">
                          Form Trend
                        </div>
                        <div className={`text-2xl font-extrabold ${profile.stats?.minutes_trend >= 0 ? "text-emerald-400" : "text-amber-400"}`}>
                          {profile.stats?.minutes_trend >= 0 ? "+" : ""}{profile.stats?.minutes_trend || "0"}m
                        </div>
                      </div>
                    </div>
                  </div>

                  {decision && (
                    <div className="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-transparent border border-emerald-500/20 p-6 rounded-2xl backdrop-blur-sm">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400">
                          Transfer Decision Recommendation
                        </h3>
                        <span className="text-xs font-extrabold px-3.5 py-1.5 rounded-xl uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          Confidence: {decision.confidence * 100}%
                        </span>
                      </div>
                      <div className="text-slate-200 text-sm font-semibold mb-4 capitalize">
                        Scouting Output Status: <span className="text-emerald-400 font-bold">{decision.decision}</span>
                      </div>
                      <ul className="list-disc list-inside space-y-2 text-slate-300 text-sm font-medium">
                        {decision.reasons?.map((reason: string, idx: number) => (
                          <li key={idx} className="leading-relaxed">
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* COMPARE TAB */}
        {activeTab === "compare" && (
          <div className="space-y-8 animate-fadeIn">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-900/60 p-6 rounded-2xl border border-slate-800">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Player A</label>
                <input
                  type="text"
                  placeholder="e.g. Kendry Paez"
                  value={playerA}
                  onChange={(e) => setPlayerA(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-white font-medium text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Player B</label>
                <input
                  type="text"
                  placeholder="e.g. Endrick"
                  value={playerB}
                  onChange={(e) => setPlayerB(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-white font-medium text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={runComparison}
                  className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold py-3.5 rounded-xl transition duration-200 transform hover:-translate-y-0.5 shadow-xl shadow-emerald-500/10"
                >
                  Execute Head to Head
                </button>
              </div>
            </div>

            {comparison && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fadeIn">
                <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl text-center flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Primary Talent</div>
                    <h4 className="text-2xl font-extrabold text-emerald-400 tracking-tight mb-6">
                      {comparison.player_a?.name}
                    </h4>
                    <div className="space-y-3 font-medium text-sm text-slate-300">
                      <p className="flex justify-between border-b border-slate-800/60 pb-2">
                        <span>KPI Composite Score</span>
                        <span className="font-bold text-slate-100">{comparison.player_a?.kpi_score}</span>
                      </p>
                      <p className="flex justify-between border-b border-slate-800/60 pb-2">
                        <span>Estimated Value</span>
                        <span className="font-bold text-slate-100">€{(comparison.player_a?.valuation || 0).toLocaleString()}</span>
                      </p>
                      <p className="flex justify-between">
                        <span>AI Recommendation</span>
                        <span className="font-bold text-emerald-400 capitalize">{comparison.player_a?.decision}</span>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl text-center flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Secondary Target</div>
                    <h4 className="text-2xl font-extrabold text-teal-400 tracking-tight mb-6">
                      {comparison.player_b?.name}
                    </h4>
                    <div className="space-y-3 font-medium text-sm text-slate-300">
                      <p className="flex justify-between border-b border-slate-800/60 pb-2">
                        <span>KPI Composite Score</span>
                        <span className="font-bold text-slate-100">{comparison.player_b?.kpi_score}</span>
                      </p>
                      <p className="flex justify-between border-b border-slate-800/60 pb-2">
                        <span>Estimated Value</span>
                        <span className="font-bold text-slate-100">€{(comparison.player_b?.valuation || 0).toLocaleString()}</span>
                      </p>
                      <p className="flex justify-between">
                        <span>AI Recommendation</span>
                        <span className="font-bold text-emerald-400 capitalize">{comparison.player_b?.decision}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ALERTS TAB */}
        {activeTab === "alerts" && (
          <div className="space-y-8 animate-fadeIn">
            <h2 className="text-2xl font-bold tracking-tight text-slate-100">
              Live Scouting Alerts & Emerging Breakouts
            </h2>
            <div className="grid grid-cols-1 gap-4">
              {alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className={`p-6 rounded-2xl border flex flex-col md:flex-row md:items-center justify-between gap-6 backdrop-blur-md transition ${
                    alert.severity === "high" || alert.severity === "critical"
                      ? "bg-emerald-500/5 border-emerald-500/20"
                      : "bg-amber-500/5 border-amber-500/20"
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        {alert.alert_type}
                      </span>
                      <span className="text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-xl bg-slate-900 text-slate-400 border border-slate-800">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-slate-100 font-semibold text-lg">{alert.message}</p>
                  </div>
                  <button
                    onClick={() => loadProfile(alert.player_slug)}
                    className="self-start md:self-center bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold px-5 py-3 rounded-xl text-xs transition duration-200 transform hover:-translate-y-0.5 shadow-xl shadow-emerald-500/10"
                  >
                    Load Scouting Profile
                  </button>
                </div>
              ))}
              {alerts.length === 0 && (
                <div className="py-12 text-center bg-slate-900/30 border border-dashed border-slate-800 rounded-3xl text-slate-500 font-semibold">
                  No alerts flagged at the moment.
                </div>
              )}
            </div>
          </div>
        )}

        {/* REPORT TAB */}
        {activeTab === "report" && (
          <div className="space-y-8 animate-fadeIn">
            {!report ? (
              <div className="py-12 text-center text-slate-500 font-semibold">
                Generate a Direct Scouting Report from shortlist candidates.
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800 p-8 rounded-2xl space-y-6">
                <div>
                  <h3 className="text-3xl font-extrabold tracking-tight text-slate-100 mb-2">
                    Direct Scouting Intelligence Profile
                  </h3>
                  <p className="text-sm font-medium text-slate-400 border-b border-slate-800/80 pb-4">
                    {report.summary}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-4">
                  <span className="text-xs font-bold bg-slate-900 text-slate-400 px-3.5 py-1.5 rounded-xl border border-slate-800 uppercase tracking-wider">
                    Status Evaluation
                  </span>
                  <span className="text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/30 px-3.5 py-1.5 rounded-xl uppercase text-xs tracking-wider">
                    {report.decision}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="bg-slate-950/60 border border-slate-800/60 p-5 rounded-xl">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-emerald-400 mb-3">
                      Observed Candidate Strengths
                    </h4>
                    <ul className="list-disc list-inside space-y-2 text-slate-300 font-medium text-sm">
                      {report.strengths?.map((str: string, idx: number) => (
                        <li key={idx}>{str}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-800/60 p-5 rounded-xl">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-amber-400 mb-3">
                      Development & Strategic Risks
                    </h4>
                    <ul className="list-disc list-inside space-y-2 text-slate-300 font-medium text-sm">
                      {report.risks?.map((risk: string, idx: number) => (
                        <li key={idx}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
