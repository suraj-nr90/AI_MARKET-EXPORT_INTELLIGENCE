"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, FileBarChart2, SearchCode, TrendingUp, Sparkles, Activity, ShieldCheck as ShieldIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SavedReport {
  id: string;
  product: string;
  region: string;
  score: number;
}

interface ResearchSession {
  id: string;
  status: string;
  product: string;
  region: string;
}

export default function Home() {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [repRes, sessRes] = await Promise.all([
          fetch("/api/reports/"),
          fetch("/api/research/")
        ]);
        if (repRes.ok) {
          const repData = await repRes.json();
          setReports(repData);
        }
        if (sessRes.ok) {
          const sessData = await sessRes.json();
          setSessions(sessData);
        }
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const totalSessionsCount = sessions.length || 0;
  const totalReportsCount = reports.length || 0;

  // Derive top region and top product dynamically
  const getTopRegion = () => {
    if (reports.length === 0) return "Not Evaluated";
    const counts: Record<string, number> = {};
    reports.forEach((r) => {
      counts[r.region] = (counts[r.region] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
  };

  const getTopProduct = () => {
    if (reports.length === 0) return "Not Evaluated";
    const counts: Record<string, number> = {};
    reports.forEach((r) => {
      const pName = r.product.includes("PCM") ? "PCM Panels" : "Gel Packs";
      counts[pName] = (counts[pName] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent flex items-center gap-2">
            <Sparkles className="h-9 w-9 text-[#2D7DD2]" />
            Dashboard
          </h1>
          <p className="text-slate-400 mt-1">Autonomous thermal packaging market intelligence & client discovery platform.</p>
        </div>
        <Link href="/research">
          <Button
            size="lg"
            className="bg-[#2D7DD2] hover:bg-[#1E6CB5] active:bg-[#155A96] text-white font-bold rounded-xl shadow-lg shadow-blue-500/10 flex items-center gap-2"
          >
            <SearchCode className="h-5 w-5" />
            Run New Research
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Research Sessions */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl space-y-4 hover:border-slate-700/50 transition-all">
          <div className="h-10 w-10 rounded-lg bg-[#2D7DD2]/10 border border-[#2D7DD2]/25 flex items-center justify-center">
            <Activity className="h-5 w-5 text-[#2D7DD2]" />
          </div>
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Research Sessions</p>
            <p className="text-3xl font-black text-white mt-1">
              {loading ? <span className="h-6 w-8 bg-slate-800 rounded animate-pulse inline-block" /> : totalSessionsCount}
            </p>
          </div>
        </div>

        {/* Saved Reports */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl space-y-4 hover:border-slate-700/50 transition-all">
          <div className="h-10 w-10 rounded-lg bg-[#2D7DD2]/10 border border-[#2D7DD2]/25 flex items-center justify-center">
            <FileBarChart2 className="h-5 w-5 text-[#2D7DD2]" />
          </div>
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Saved Reports</p>
            <p className="text-3xl font-black text-white mt-1">
              {loading ? <span className="h-6 w-8 bg-slate-800 rounded animate-pulse inline-block" /> : totalReportsCount}
            </p>
          </div>
        </div>

        {/* Top Target Region */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl space-y-4 hover:border-slate-700/50 transition-all">
          <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center">
            <TrendingUp className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Top Target Region</p>
            <p className="text-lg font-extrabold text-white mt-2 leading-tight">
              {loading ? <span className="h-4 w-28 bg-slate-800 rounded animate-pulse inline-block" /> : getTopRegion()}
            </p>
          </div>
        </div>

        {/* Top Product Category */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl space-y-4 hover:border-slate-700/50 transition-all">
          <div className="h-10 w-10 rounded-lg bg-indigo-500/10 border border-indigo-500/25 flex items-center justify-center">
            <ShieldIcon className="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Top Product Focus</p>
            <p className="text-lg font-extrabold text-white mt-2 leading-tight">
              {loading ? <span className="h-4 w-28 bg-slate-800 rounded animate-pulse inline-block" /> : getTopProduct()}
            </p>
          </div>
        </div>
      </div>

      {/* Main Dashboard Panel */}
      <div className="grid gap-6 md:grid-cols-12">
        {/* Info panel */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl md:col-span-8 space-y-4">
          <h3 className="font-extrabold text-white text-lg">Platform Overview</h3>
          <div className="text-sm text-slate-400 space-y-4 leading-relaxed font-medium">
            <p>
              Welcome to the <strong className="text-white font-bold">Export Market Intelligence & Client Discovery Platform</strong>. This system is designed to bypass manual international market studies by automating critical trade research steps.
            </p>
            <p>
              By combining Google Search (via Serper) and Event Intelligence (via PredictHQ), the platform generates real-time market overviews, identifies top-scoring sectors, finds actual potential clients, and compiles upcoming event spikes for:
            </p>
            <ul className="space-y-3 pl-2 pt-2 text-slate-300">
              <li className="flex items-start gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2D7DD2] shrink-0 mt-2" />
                <span><strong className="text-white font-semibold">Advanced Temperature-Controlled Gel Packs</strong>: Cold chain packaging optimized for single-use fresh food logistics and pharmaceutical transport.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2D7DD2] shrink-0 mt-2" />
                <span><strong className="text-white font-semibold">PCM Thermal Panels</strong>: Premium phase-change materials designed for multi-day, long-haul temperature-sensitive air and sea shipments.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Quick start column */}
        <div className="p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl md:col-span-4 flex flex-col justify-between space-y-6">
          <div>
            <h3 className="font-extrabold text-white text-lg">Quick Start</h3>
            <p className="text-sm text-slate-400 mt-1">Ready to explore new markets? Run a regional analysis in under 2 minutes.</p>
          </div>
          
          <div className="space-y-4 text-xs font-semibold text-slate-300">
            <div className="flex items-center gap-3">
              <span className="h-6 w-6 rounded-full bg-[#2D7DD2]/10 border border-[#2D7DD2]/30 text-[#2D7DD2] flex items-center justify-center font-bold">1</span>
              <span>Go to Market Research tab</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="h-6 w-6 rounded-full bg-[#2D7DD2]/10 border border-[#2D7DD2]/30 text-[#2D7DD2] flex items-center justify-center font-bold">2</span>
              <span>Select Product & Target Region</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="h-6 w-6 rounded-full bg-[#2D7DD2]/10 border border-[#2D7DD2]/30 text-[#2D7DD2] flex items-center justify-center font-bold">3</span>
              <span>Generate report & export to PDF</span>
            </div>
          </div>

          <Link href="/research" className="block">
            <Button className="w-full bg-[#2D7DD2] hover:bg-[#1E6CB5] active:bg-[#155A96] text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/10">
              Launch Research Portal
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
