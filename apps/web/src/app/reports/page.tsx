"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Eye, Download, Trash2, Calendar, FileText, Globe2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SavedReport {
  id: string;
  created_at: string;
  product: string;
  region: string;
  score: number;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchReports = async () => {
    try {
      const res = await fetch("/api/reports/");
      if (!res.ok) {
        throw new Error(`Server returned status: ${res.status}`);
      }
      const data = await res.json();
      setReports(data);
    } catch (err: unknown) {
      console.error("Failed to fetch saved reports:", err);
      setError("Could not load saved reports. Ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (id: string) => {
    if (!window.confirm("Are you sure you want to permanently delete this intelligence report?")) {
      return;
    }
    
    setDeletingId(id);
    try {
      const res = await fetch(`/api/reports/${id}`, {
        method: "DELETE"
      });
      
      if (!res.ok) {
        throw new Error("Failed to delete report from database");
      }
      
      // Filter out deleted report from view
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch (err: unknown) {
      console.error(err);
      const errMsg = err instanceof Error ? err.message : "An error occurred while deleting the report.";
      alert(errMsg);
    } finally {
      setDeletingId(null);
    }
  };

  const handleExportPDF = async (id: string, product: string, region: string) => {
    try {
      const response = await fetch(`/api/reports/${id}/export`, {
        method: "GET"
      });
      if (!response.ok) throw new Error("Failed to export PDF");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Market_Report_${region.replace(/\s+/g, "_")}_${product.includes("Gel") ? "Gel_Packs" : "PCM_Panels"}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Export failure:", err);
      alert("Failed to download PDF. Please try again.");
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto text-white">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-2.5">
          <FileText className="h-8 w-8 text-[#2D7DD2]" />
          <span>Saved Reports</span>
        </h1>
        <p className="text-slate-400 mt-1">Access, review, and export previously generated autonomous market intelligence records.</p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <div className="h-8 w-8 border-4 border-[#2D7DD2] border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 text-sm animate-pulse">Loading saved intelligence records...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-red-950/20 border border-red-900/40 rounded-2xl text-center space-y-3">
          <AlertTriangle className="h-10 w-10 text-red-500 mx-auto" />
          <h3 className="font-bold text-white">Service Unreachable</h3>
          <p className="text-slate-400 text-xs max-w-md mx-auto">{error}</p>
          <Button onClick={() => { setLoading(true); fetchReports(); }} className="bg-slate-800 hover:bg-slate-700 text-xs px-4 py-2 text-white">
            Retry Connection
          </Button>
        </div>
      ) : reports.length === 0 ? (
        <div className="bg-[#111625] border border-slate-800/80 rounded-2xl p-12 text-center space-y-4">
          <FileText className="h-12 w-12 text-slate-700 mx-auto stroke-[1.5]" />
          <h3 className="text-lg font-bold text-white">No Reports Saved Yet</h3>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            You have not run any market intelligence reports. Navigate to the Market Research module to begin.
          </p>
          <Link href="/research">
            <Button className="bg-[#2D7DD2] hover:bg-[#1E6CB5] text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-lg">
              Start Market Research
            </Button>
          </Link>
        </div>
      ) : (
        <div className="bg-[#111625] border border-slate-800/80 rounded-2xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                  <th className="p-4 pl-6">Report Date</th>
                  <th className="p-4">Product Line</th>
                  <th className="p-4">Export Region</th>
                  <th className="p-4 text-center">Attractiveness</th>
                  <th className="p-4 text-right pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-300 font-medium">
                {reports.map((r) => {
                  const isDeleting = deletingId === r.id;
                  
                  let scoreBadge = "bg-emerald-950/30 text-emerald-400 border-emerald-800/50";
                  if (r.score < 40) {
                    scoreBadge = "bg-red-950/30 text-red-400 border-red-800/50";
                  } else if (r.score < 70) {
                    scoreBadge = "bg-amber-950/30 text-amber-400 border-amber-800/50";
                  }

                  return (
                    <tr key={r.id} className="hover:bg-slate-800/20 transition-colors">
                      <td className="p-4 pl-6 text-slate-400 font-semibold flex items-center gap-2">
                        <Calendar className="h-3.5 w-3.5 text-slate-500" />
                        {new Date(r.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-4 font-bold text-white">{r.product}</td>
                      <td className="p-4">
                        <span className="flex items-center gap-1.5">
                          <Globe2 className="h-3.5 w-3.5 text-slate-500" />
                          {r.region}
                        </span>
                      </td>
                      <td className="p-4 text-center">
                        <span className={`px-2 py-0.5 rounded-md border font-bold text-[10px] uppercase ${scoreBadge}`}>
                          {r.score}/100
                        </span>
                      </td>
                      <td className="p-4 text-right pr-6 space-x-2">
                        <Link href={`/research/${r.id}`}>
                          <button
                            type="button"
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold text-slate-300 bg-slate-800 border border-slate-700/60 hover:bg-slate-700 hover:text-white transition-all shadow-sm"
                          >
                            <Eye className="h-3 w-3" />
                            Open
                          </button>
                        </Link>
                        
                        <button
                          type="button"
                          onClick={() => handleExportPDF(r.id, r.product, r.region)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold text-white bg-[#2D7DD2] hover:bg-[#1E6CB5] transition-all shadow-sm shadow-blue-500/10"
                        >
                          <Download className="h-3 w-3" />
                          PDF
                        </button>

                        <button
                          type="button"
                          disabled={isDeleting}
                          onClick={() => handleDelete(r.id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold text-red-400 bg-red-950/20 border border-red-800/40 hover:bg-red-950/40 hover:text-red-300 transition-all disabled:opacity-40"
                        >
                          <Trash2 className="h-3 w-3" />
                          {isDeleting ? "..." : "Delete"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
