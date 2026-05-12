"use client";

import React, { useState } from "react";

export default function InfraDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  const stats = [
    { label: "Medallion Stage", value: "Hybrid-Medallion", status: "Operational" },
    { label: "Primary Driver", value: "LocalFS + Abstraction", status: "Operational" },
    { label: "Schema Engines", value: "Pydantic V2", status: "Validated" },
    { label: "Canonical IDs", value: "RFC4122 v5 UUID", status: "Ready" },
  ];

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10">
          <div className="flex items-center gap-3 text-blue-500 font-semibold tracking-wider text-xs uppercase mb-2">
            <div className="h-2 w-2 bg-blue-500 rounded-full animate-pulse"></div>
            System Infrastructure Status
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">Datalake Readiness Hub</h1>
          <p className="text-slate-400 mt-2">Monitoring architecture migration state and pipeline connectivity assets.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          {stats.map((s, i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="text-slate-500 text-sm font-medium">{s.label}</div>
              <div className="text-xl font-bold text-white mt-1">{s.value}</div>
              <div className="mt-3 inline-flex items-center text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-md">
                {s.status}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-slate-900/40 border border-slate-800 rounded-3xl overflow-hidden">
          <div className="flex border-b border-slate-800 bg-slate-900/80">
            {["overview", "schemas", "ingestion", "identity"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-8 py-4 font-semibold capitalize transition ${
                  activeTab === tab ? "text-blue-400 border-b-2 border-blue-400 bg-blue-500/5" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
          
          <div className="p-8 min-h-[400px]">
             {activeTab === "overview" && (
               <div className="space-y-6">
                 <h3 className="text-xl font-bold">Infrastructure Matrix</h3>
                 <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 font-mono text-sm text-emerald-400 space-y-2">
                    <div>[OK] app.storage.get_default_provider() initialized</div>
                    <div>[OK] app.schemas.base.CanonicalBaseSchema mapped</div>
                    <div>[OK] app.core.identity.IdentityCore active</div>
                    <div>[WARN] app.storage.S3Storage not configured (Credentials Missing)</div>
                 </div>
               </div>
             )}
             
             {activeTab === "schemas" && (
               <div className="space-y-4">
                 <h3 className="text-xl font-bold">Schema Registry</h3>
                 <div className="grid gap-4">
                    {["PlayerBio", "Club", "Match", "GameEvent", "ProviderMapping"].map((s, i) => (
                      <div key={i} className="p-4 bg-slate-800/40 border border-slate-800 rounded-lg flex justify-between items-center">
                         <span className="font-mono font-bold">{s}</span>
                         <span className="text-xs text-slate-500">Semantic Version 1.0.0</span>
                      </div>
                    ))}
                 </div>
               </div>
             )}

             {activeTab !== "overview" && activeTab !== "schemas" && (
               <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                 <div className="text-lg font-semibold">System Skeleton Live</div>
                 <p className="text-sm">Framework bindings present. Waiting for active production data feed linkage.</p>
               </div>
             )}
          </div>
        </div>
      </div>
    </main>
  );
}
