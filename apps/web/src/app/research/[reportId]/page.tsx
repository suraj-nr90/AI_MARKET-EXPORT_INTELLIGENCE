"use client";

import { useState, useEffect, Fragment } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  MapPin,
  Calendar,
  Building2,
  Sparkles,
  FileText,
  ChevronDown,
  ChevronUp,
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  Briefcase,
  ChevronLeft,
  Layers
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

interface CompanyDetail {
  company: string;
  rationale: string;
  estimated_need: string;
}

interface SectorDetail {
  rank: number;
  sector_name: string;
  demand_score: number;
  key_drivers: string[];
  top_companies: CompanyDetail[];
  entry_difficulty: string;
}

interface EventDetail {
  event: string;
  date_window: string;
  procurement_start: string;
  sector: string;
  demand_spike_score: number;
  outreach_recommendation: string;
}

interface ClientDetail {
  company_name: string;
  sector: string;
  region_country: string;
  relevance_rationale: string;
  estimated_annual_need: string;
  contact_strategy: string;
}

interface ReportData {
  product: string;
  region: string;
  generated_at: string;
  executive_summary: string;
  product_regional_fit: {
    fit_score: number;
    fit_rationale: string;
  };
  top_sectors: SectorDetail[];
  event_procurement_windows: EventDetail[];
  potential_clients: ClientDetail[];
  competitive_landscape: {
    main_competitors: string[];
    competitive_advantages_to_emphasize: string[];
    market_gaps: string[];
  };
  market_attractiveness_score: number;
  market_attractiveness_breakdown: {
    market_size: number;
    growth_trajectory: number;
    competitive_intensity: number;
    event_driven_demand: number;
  };
  strategic_recommendations: {
    priority: number;
    action: string;
    timeline: string;
    expected_outcome: string;
  }[];
}

interface ReportRecord {
  id: string;
  session_id: string;
  report_json: ReportData;
  created_at: string;
}

export default function ReportDetailPage() {
  const { reportId } = useParams();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<ReportRecord | null>(null);
  const [error, setError] = useState("");
  
  // Interactive UI states
  const [expandedSectors, setExpandedSectors] = useState<Record<number, boolean>>({});
  const [expandedClients, setExpandedClients] = useState<Record<number, boolean>>({});
  const [selectedEvent, setSelectedEvent] = useState<EventDetail | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await fetch(`/api/reports/${reportId}`);
        if (!res.ok) {
          throw new Error(`Report not found (Status: ${res.status})`);
        }
        const data = await res.json();
        setReport(data);
        
        // Auto-select first event for timeline detail preview
        const reportJson = data.report_json as ReportData;
        if (reportJson.event_procurement_windows && reportJson.event_procurement_windows.length > 0) {
          setSelectedEvent(reportJson.event_procurement_windows[0]);
        }
      } catch (err: unknown) {
        console.error("Failed to fetch report:", err);
        const errMsg = err instanceof Error ? err.message : "Could not load report details.";
        setError(errMsg);
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      fetchReport();
    }
  }, [reportId]);

  const toggleSector = (rank: number) => {
    setExpandedSectors((prev) => ({ ...prev, [rank]: !prev[rank] }));
  };

  const toggleClient = (idx: number) => {
    setExpandedClients((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const response = await fetch(`/api/reports/${reportId}/export`, {
        method: "GET"
      });
      if (!response.ok) throw new Error("Failed to export PDF");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Market_Report_${report?.report_json?.region.replace(/\s+/g, "_")}_${report?.report_json?.product.includes("Gel") ? "Gel_Packs" : "PCM_Panels"}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Export failure:", err);
      alert("Failed to download PDF. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="h-10 w-10 border-4 border-[#2D7DD2] border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-semibold animate-pulse">Retrieving market intelligence...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto mt-12 bg-[#111625] border border-red-800/40 rounded-2xl p-6 text-center space-y-4">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Error Loading Report</h2>
        <p className="text-slate-400 text-sm">{error || "The requested report could not be found."}</p>
        <Link href="/reports">
          <Button className="mt-2 bg-slate-800 hover:bg-slate-700 text-white">
            Back to Saved Reports
          </Button>
        </Link>
      </div>
    );
  }

  const data = report.report_json as ReportData;

  // Circular gauge score compiler
  const CircularGauge = ({ value, label }: { value: number; label: string }) => {
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    let strokeColor = "stroke-emerald-500";
    let textColor = "text-emerald-500";
    
    if (value < 40) {
      strokeColor = "stroke-red-500";
      textColor = "text-red-500";
    } else if (value < 70) {
      strokeColor = "stroke-amber-500";
      textColor = "text-amber-500";
    }

    return (
      <div className="flex flex-col items-center justify-center p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl flex-1 min-w-[200px]">
        <div className="relative h-24 w-24 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="48"
              cy="48"
              r={radius}
              className="stroke-slate-800"
              strokeWidth="7"
              fill="transparent"
            />
            <circle
              cx="48"
              cy="48"
              r={radius}
              className={`${strokeColor} transition-all duration-1000 ease-out`}
              strokeWidth="7"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute text-center">
            <span className={`text-2xl font-extrabold tracking-tighter ${textColor}`}>
              {value}
            </span>
            <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Score</span>
          </div>
        </div>
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-4 text-center">
          {label}
        </span>
      </div>
    );
  };

  // Recharts horizontal bar chart data mapper
  const chartData = data.top_sectors.map((s) => ({
    name: s.sector_name.length > 30 ? s.sector_name.substring(0, 28) + "..." : s.sector_name,
    score: s.demand_score,
    fullName: s.sector_name
  }));

  // Timeline Event Window Parser
  // Generates timeline grid columns relative to a 12 month block
  const getTimelineMonths = () => {
    const months = [];
    const date = new Date(report.created_at || new Date());
    for (let i = 0; i < 12; i++) {
      months.push({
        label: date.toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
        monthNum: date.getMonth(),
        year: date.getFullYear()
      });
      date.setMonth(date.getMonth() + 1);
    }
    return months;
  };

  const timelineMonths = getTimelineMonths();

  const getEventPlacementIndex = (procurementStartStr: string) => {
    try {
      const date = new Date(procurementStartStr);
      if (isNaN(date.getTime())) return -1;
      
      for (let i = 0; i < timelineMonths.length; i++) {
        const m = timelineMonths[i];
        if (date.getMonth() === m.monthNum && date.getFullYear() === m.year) {
          return i;
        }
      }
    } catch (e) {
      console.error(e);
    }
    return -1;
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-24 text-white">
      {/* Back button & title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-1">
          <Link href="/reports" className="text-xs font-bold text-slate-400 hover:text-[#2D7DD2] transition-colors flex items-center gap-1 mb-2">
            <ChevronLeft className="h-4 w-4" />
            Back to Saved Reports
          </Link>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-2.5">
            <TrendingUp className="h-8 w-8 text-[#2D7DD2]" />
            Market Intelligence Analysis
          </h1>
          <p className="text-slate-400 text-sm">
            Product: <span className="font-semibold text-white">{data.product}</span> | Region: <span className="font-semibold text-white">{data.region}</span>
          </p>
        </div>
        <div className="text-xs text-slate-500 font-bold bg-[#111625] border border-slate-800 px-3 py-1.5 rounded-lg shrink-0">
          Generated: {new Date(data.generated_at).toLocaleDateString()}
        </div>
      </div>

      {/* Section 1 — Hero Stats Row */}
      <section className="grid gap-6 sm:grid-cols-2 md:grid-cols-3">
        <CircularGauge value={data.market_attractiveness_score} label="Market Attractiveness" />
        <CircularGauge value={data.product_regional_fit.fit_score} label="Product-Region Fit" />
        <div className="flex flex-col items-center justify-center p-6 bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl flex-1 min-w-[200px]">
          <div className="relative h-24 w-24 rounded-full bg-slate-900 border border-slate-800 flex flex-col items-center justify-center shadow-inner">
            <Building2 className="h-8 w-8 text-[#2D7DD2] mb-1 stroke-[1.5]" />
            <span className="text-2xl font-extrabold tracking-tighter text-white">
              {data.potential_clients.length}
            </span>
          </div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-4 text-center">
            Potential Clients Listed
          </span>
        </div>
      </section>

      {/* Section 2 — Executive Summary */}
      <section className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-3">
        <h2 className="text-lg font-bold flex items-center gap-2 text-[#2D7DD2] border-b border-slate-800 pb-2">
          <FileText className="h-5 w-5" />
          Executive Summary
        </h2>
        <p className="text-slate-300 text-md leading-relaxed">
          {data.executive_summary}
        </p>
        <div className="p-4 bg-[#0A0F1E] border border-slate-800/60 rounded-xl mt-4 space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Product Fit Rationale</span>
          <p className="text-sm text-slate-300 leading-relaxed">{data.product_regional_fit.fit_rationale}</p>
        </div>
      </section>

      {/* Section 3 — Top Sectors Analysis */}
      <section className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
        <h2 className="text-lg font-bold flex items-center gap-2 text-[#2D7DD2] border-b border-slate-800 pb-2">
          <Layers className="h-5 w-5" />
          Sector Demand Analysis
        </h2>

        {/* Recharts Bar Chart */}
        <div className="h-64 w-full bg-[#0A0F1E] border border-slate-800/60 rounded-xl p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
              <XAxis type="number" domain={[0, 10]} stroke="#64748B" fontSize={12} tickCount={11} />
              <YAxis dataKey="name" type="category" stroke="#64748B" fontSize={11} width={150} />
              <Tooltip
                contentStyle={{ backgroundColor: "#111625", borderColor: "#334155", color: "#fff" }}
                formatter={(value) => [`Score: ${value}/10`, "Demand Score"]}
              />
              <Bar dataKey="score" fill="#2D7DD2" radius={[0, 4, 4, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 2x2 Sector Cards Grid */}
        <div className="grid gap-6 md:grid-cols-2">
          {data.top_sectors.map((s) => {
            const isExpanded = !!expandedSectors[s.rank];
            
            let diffColor = "bg-emerald-950/30 text-emerald-400 border-emerald-800/50";
            if (s.entry_difficulty.toLowerCase() === "high") {
              diffColor = "bg-red-950/30 text-red-400 border-red-800/50";
            } else if (s.entry_difficulty.toLowerCase() === "medium") {
              diffColor = "bg-amber-950/30 text-amber-400 border-amber-800/50";
            }

            return (
              <div
                key={s.rank}
                className="bg-[#0A0F1E] border border-slate-800/80 rounded-xl p-5 shadow-lg space-y-4 hover:border-slate-700/60 transition-all flex flex-col justify-between"
              >
                <div className="space-y-3">
                  {/* Header info */}
                  <div className="flex justify-between items-start gap-4">
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Rank #{s.rank}</div>
                      <h3 className="font-bold text-white text-md leading-tight">{s.sector_name}</h3>
                    </div>
                    <span className="text-xs font-bold text-white bg-[#2D7DD2]/10 border border-[#2D7DD2]/40 px-2.5 py-0.5 rounded-full shrink-0">
                      Score: {s.demand_score}/10
                    </span>
                  </div>

                  {/* Drivers pills */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {s.key_drivers.map((d, i) => (
                      <span key={i} className="text-[10px] font-semibold bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-md text-slate-400">
                        {d}
                      </span>
                    ))}
                  </div>

                  {/* Difficulty Badge */}
                  <div className="flex items-center gap-1.5 text-xs text-slate-400 pt-1">
                    <span>Entry Difficulty:</span>
                    <span className={`px-2 py-0.5 rounded-md border font-bold text-[10px] uppercase ${diffColor}`}>
                      {s.entry_difficulty}
                    </span>
                  </div>
                </div>

                {/* Companies expansion */}
                <div className="pt-3 border-t border-slate-800/60 mt-4">
                  <button
                    onClick={() => toggleSector(s.rank)}
                    className="w-full flex items-center justify-between text-xs font-bold text-slate-400 hover:text-white transition-colors"
                  >
                    <span>Target Companies & Needs ({s.top_companies.length})</span>
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-3 space-y-3 divide-y divide-slate-900">
                      {s.top_companies.map((c, i) => (
                        <div key={i} className={`pt-2.5 ${i === 0 ? "pt-0" : ""}`}>
                          <div className="flex justify-between items-start gap-2">
                            <span className="text-xs font-bold text-white flex items-center gap-1">
                              <Building2 className="h-3 w-3 text-[#2D7DD2]" />
                              {c.company}
                            </span>
                            <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950/20 border border-emerald-800/40 px-2 rounded-md">
                              Vol: {c.estimated_need}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 leading-snug mt-1.5">
                            {c.rationale}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Section 4 — Event Procurement Windows (Timeline) */}
      <section className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2 text-[#2D7DD2] border-b border-slate-800 pb-2">
            <Calendar className="h-5 w-5" />
            12-Month Procurement Timeline
          </h2>
          <p className="text-slate-400 text-xs mt-1.5">
            Trade events mapped by their projected 90-day lead-time procurement windows. Select a flag to analyze strategic outreach triggers.
          </p>
        </div>

        {/* Timeline Visualization */}
        <div className="overflow-x-auto pb-4">
          <div className="min-w-[768px] relative pt-16 pb-8 px-4">
            {/* Timeline Horizontal Line */}
            <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-slate-800 -translate-y-1/2" />
            
            {/* 12 Month Grid */}
            <div className="grid grid-cols-12 gap-0 relative">
              {timelineMonths.map((m, idx) => {
                // Find events placed in this month
                const eventsInMonth = data.event_procurement_windows.filter(
                  (e) => getEventPlacementIndex(e.procurement_start) === idx
                );

                return (
                  <div key={idx} className="relative flex flex-col items-center select-none">
                    {/* Tick Mark */}
                    <div className="absolute top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-slate-900 border-2 border-slate-700 z-10" />

                    {/* Events list at month */}
                    <div className="absolute bottom-[20px] flex flex-col gap-2.5 items-center">
                      {eventsInMonth.map((e, eIdx) => {
                        const isSelected = selectedEvent?.event === e.event;
                        return (
                          <button
                            key={eIdx}
                            onClick={() => setSelectedEvent(e)}
                            className={`px-2 py-1 rounded-md text-[10px] font-bold border transition-all ${
                              isSelected
                                ? "bg-[#2D7DD2] text-white border-[#2D7DD2] scale-110 shadow-lg shadow-blue-500/20"
                                : "bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-600"
                            }`}
                          >
                            🚩 {e.event.substring(0, 12)}...
                          </button>
                        );
                      })}
                    </div>

                    {/* Month Label */}
                    <div className="absolute top-[20px] text-xs font-bold text-slate-500">
                      {m.label}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Event Details Panel */}
        {selectedEvent ? (
          <div className="p-5 bg-[#0A0F1E] border border-slate-800/80 rounded-xl space-y-4 animate-fadeIn">
            <div className="flex justify-between items-start gap-4 flex-wrap border-b border-slate-800 pb-3">
              <div className="space-y-1">
                <div className="text-[10px] font-bold text-[#2D7DD2] uppercase tracking-widest">Active Procurement Target</div>
                <h4 className="font-extrabold text-white text-md">{selectedEvent.event}</h4>
                <p className="text-xs text-slate-400">Target Sector: <span className="font-medium text-slate-200">{selectedEvent.sector}</span></p>
              </div>
              <div className="flex gap-2">
                <span className="text-xs font-bold text-emerald-400 bg-emerald-950/20 border border-emerald-800/40 px-2.5 py-0.5 rounded-full shrink-0">
                  Spike Index: {selectedEvent.demand_spike_score}/10
                </span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">Key Deadlines</span>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-900 border border-slate-800/60 rounded-lg">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Procurement Window Start</span>
                    <span className="font-bold text-slate-200 text-xs flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5 text-[#2D7DD2]" />
                      {new Date(selectedEvent.procurement_start).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-900 border border-slate-800/60 rounded-lg">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block mb-1">Event Run Date</span>
                    <span className="font-bold text-slate-200 text-xs flex items-center gap-1.5">
                      <Calendar className="h-3.5 w-3.5 text-emerald-400" />
                      {selectedEvent.date_window}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">Outreach Recommendation</span>
                <div className="p-3 bg-[#111625] border border-[#2D7DD2]/30 rounded-lg">
                  <p className="text-xs text-slate-200 leading-relaxed font-medium">
                    {selectedEvent.outreach_recommendation}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs bg-[#0A0F1E] rounded-xl border border-slate-800/40">
            Select an event on the timeline track above to display details.
          </div>
        )}
      </section>

      {/* Section 5 — Top 10 Potential Clients */}
      <section className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-4">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2 text-[#2D7DD2] border-b border-slate-800 pb-2">
            <Building2 className="h-5 w-5" />
            Top Potential Clients
          </h2>
          <p className="text-slate-400 text-xs mt-1.5">
            Identified regional clients with a high likelihood of thermal packaging consumption. Click a row to expand Contact & Relevance Strategy.
          </p>
        </div>

        <div className="bg-[#0A0F1E] border border-slate-800/80 rounded-xl overflow-hidden shadow-inner">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                  <th className="p-3.5 pl-5">Company</th>
                  <th className="p-3.5">Sector</th>
                  <th className="p-3.5">Country</th>
                  <th className="p-3.5">Annual Need</th>
                  <th className="p-3.5 text-right pr-5">Strategy Detail</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900 text-slate-300 font-medium">
                {data.potential_clients.map((c, idx) => {
                  const isExpanded = !!expandedClients[idx];
                  return (
                    <Fragment key={idx}>
                      <tr
                        onClick={() => toggleClient(idx)}
                        className="hover:bg-slate-800/25 transition-colors cursor-pointer"
                      >
                        <td className="p-3.5 pl-5 font-bold text-white flex items-center gap-2">
                          <span className="h-5 w-5 bg-slate-900 border border-slate-800 rounded flex items-center justify-center text-[10px] text-slate-400 font-bold">
                            {idx + 1}
                          </span>
                          {c.company_name}
                        </td>
                        <td className="p-3.5">{c.sector}</td>
                        <td className="p-3.5 flex-row items-center gap-1">
                          <MapPin className="inline h-3 w-3 text-slate-500 mr-1" />
                          {c.region_country}
                        </td>
                        <td className="p-3.5">
                          <span className="text-emerald-400 font-semibold">{c.estimated_annual_need}</span>
                        </td>
                        <td className="p-3.5 text-right pr-5">
                          <button
                            type="button"
                            className="inline-flex items-center gap-1 text-[10px] font-bold text-[#2D7DD2] hover:underline"
                          >
                            {isExpanded ? "Hide" : "Expand"}
                            {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-[#0b101e]/85">
                          <td colSpan={5} className="p-5 pl-5 pr-5 border-t border-slate-900/60">
                            <div className="grid md:grid-cols-2 gap-6 text-[11px] leading-relaxed">
                              <div className="space-y-1.5">
                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Relevance Rationale</span>
                                <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-slate-300 font-medium">
                                  {c.relevance_rationale}
                                </div>
                              </div>
                              <div className="space-y-1.5">
                                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Contact & Sales Strategy</span>
                                <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-slate-300 font-medium">
                                  {c.contact_strategy}
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Section 6 — Competitive Landscape */}
      <section className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
        <h2 className="text-lg font-bold flex items-center gap-2 text-[#2D7DD2] border-b border-slate-800 pb-2">
          <Briefcase className="h-5 w-5" />
          Competitive Landscape
        </h2>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Competitors column */}
          <div className="bg-[#0A0F1E] border border-slate-800/60 rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-900 pb-2">
              Main Regional Competitors
            </h3>
            <ul className="space-y-3">
              {data.competitive_landscape.main_competitors.map((comp, i) => (
                <li key={i} className="text-xs font-bold text-white flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-red-400 shrink-0" />
                  {comp}
                </li>
              ))}
            </ul>
          </div>

          {/* Advantages column */}
          <div className="bg-[#0A0F1E] border border-slate-800/60 rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-900 pb-2">
              Advantages to Emphasize
            </h3>
            <ul className="space-y-3">
              {data.competitive_landscape.competitive_advantages_to_emphasize.map((adv, i) => (
                <li key={i} className="text-xs font-semibold text-slate-200 flex items-start gap-2 leading-relaxed">
                  <CheckCircle className="h-4 w-4 text-[#2D7DD2] shrink-0 mt-0.5" />
                  <span>{adv}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Market Gaps column */}
          <div className="bg-[#0A0F1E] border border-slate-800/60 rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-900 pb-2">
              Market Gaps & Opportunities
            </h3>
            <div className="flex flex-wrap gap-2 pt-1">
              {data.competitive_landscape.market_gaps.map((gap, i) => (
                <span key={i} className="text-[10px] font-bold bg-[#2D7DD2]/10 border border-[#2D7DD2]/30 text-white px-2.5 py-1 rounded-full">
                  🔍 {gap}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Section 7 — Strategic Recommendations */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold flex items-center gap-2 text-white border-b border-slate-800 pb-2">
          <Sparkles className="h-5 w-5 text-[#2D7DD2]" />
          Strategic Recommendations
        </h2>

        <div className="grid gap-6 md:grid-cols-3">
          {data.strategic_recommendations.map((rec) => {
            let priorityLabel = "Priority 1 (Immediate)";
            let badgeStyle = "bg-red-950/30 text-red-400 border-red-800/50";
            if (rec.priority === 2) {
              priorityLabel = "Priority 2 (Mid-term)";
              badgeStyle = "bg-amber-950/30 text-amber-400 border-amber-800/50";
            } else if (rec.priority === 3) {
              priorityLabel = "Priority 3 (Long-term)";
              badgeStyle = "bg-blue-950/30 text-blue-400 border-blue-800/50";
            }

            return (
              <div
                key={rec.priority}
                className="bg-[#111625] border border-slate-800/80 rounded-2xl p-5 flex flex-col justify-between shadow-xl space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className={`px-2 py-0.5 rounded-md border text-[9px] font-bold uppercase ${badgeStyle}`}>
                      {priorityLabel}
                    </span>
                    <span className="text-[10px] font-bold text-slate-500 flex items-center gap-1">
                      <Clock className="h-3 w-3 text-slate-600" />
                      {rec.timeline}
                    </span>
                  </div>
                  <p className="text-xs font-bold text-white leading-relaxed">
                    {rec.action}
                  </p>
                </div>
                
                <div className="p-3 bg-slate-900 border border-slate-800/40 rounded-xl mt-2">
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Expected Outcome</span>
                  <p className="text-xs text-slate-400 leading-snug">{rec.expected_outcome}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* EXPORT BUTTON (sticky bottom bar) */}
      <div className="fixed bottom-0 left-64 right-0 h-16 border-t border-slate-800 bg-[#111625]/85 backdrop-blur-md flex items-center justify-between px-8 z-40 shadow-2xl">
        <div className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
          <CheckCircle className="h-4 w-4 text-emerald-400" />
          <span>Report Generated Successfully</span>
        </div>
        <Button
          onClick={handleExportPDF}
          disabled={exporting}
          className="bg-[#2D7DD2] hover:bg-[#1E6CB5] active:bg-[#155A96] text-white font-bold text-xs px-5 py-2.5 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-all shadow-lg shadow-blue-500/10"
        >
          {exporting ? (
            <>
              <span className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating PDF...
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              Export PDF Report
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
