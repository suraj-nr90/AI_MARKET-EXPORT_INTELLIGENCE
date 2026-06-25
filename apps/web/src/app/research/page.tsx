"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Globe2, Package2, Sparkles, Calendar, Layers, ShieldCheck, CheckCircle2 } from "lucide-react";

const PRODUCTS = [
  {
    id: "gel_packs",
    name: "Advanced Temperature-Controlled Gel Packs",
    code: "gel_packs",
    sectors: [
      "Pharmaceutical and Life Sciences (Cold Chain)",
      "Food Logistics and E-Commerce",
      "Medical and Therapeutic Custom Applications",
      "Electronics, Art, and Chemical Transport"
    ]
  },
  {
    id: "pcm_panels",
    name: "Phase Change Material (PCM) Thermal Panels",
    code: "pcm_panels",
    sectors: [
      "Passive and Green Building Construction",
      "Cold Chain Logistics and Passive Refrigeration",
      "Telecommunications and Electronics Enclosures",
      "Renewable Energy Storage"
    ]
  }
];

const REGIONS = [
  { id: "us", name: "United States", events: ["RE+ Expo (Solar & Energy Storage)", "LogiPharma US", "Global Cold Chain Expo"] },
  { id: "in", name: "India", events: ["CPHI India", "India Cold Chain Show", "RE+ India (Renewable Energy India)"] },
  { id: "eu", name: "Europe", events: ["CPHI Worldwide", "LogiPharma Europe", "MWC Barcelona (Mobile World Congress)"] },
  { id: "me", name: "Middle East", events: ["Arab Health Exhibition & Congress", "Expo 2030 Riyadh", "Saudi Green Building Forum"] },
  { id: "sea", name: "Southeast Asia", events: ["Cold Chain Asia", "MWC Shanghai", "Singapore International Energy Week (SIEW)"] }
];

const STEPPER_ITEMS = [
  { label: "Searching market databases", key: "market" },
  { label: "Scanning event calendars", key: "events" },
  { label: "Discovering client companies", key: "companies" },
  { label: "AI synthesis & scoring", key: "synthesis" }
];

export default function ResearchPage() {
  const router = useRouter();
  const [product, setProduct] = useState("");
  const [region, setRegion] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 0 to 4
  const [errorMsg, setErrorMsg] = useState("");

  const selectedProduct = PRODUCTS.find((p) => p.code === product);
  const selectedRegion = REGIONS.find((r) => r.name === region);

  const handleRunResearch = async () => {
    if (!product || !region) return;
    setLoading(true);
    setCurrentStep(0);
    setErrorMsg("");

    try {
      const apiHost = process.env.NEXT_PUBLIC_BACKEND_API_URL;
      const url = apiHost ? `${apiHost}/research/generate` : "/api/research/generate";
      
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ product, region })
      });

      if (!response.ok) {
        throw new Error(`Server returned status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to initialize stream reader");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let gotReport = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          if (!gotReport && currentStep === 4) {
            // Fallback: if the stream ended on complete status but we never got the report details
            router.push("/reports");
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.substring(6).trim();
            if (!dataStr) continue;

            try {
              const payload = JSON.parse(dataStr);
              if (payload.status === "Searching market data...") {
                setCurrentStep(0);
              } else if (payload.status === "Scanning event calendars...") {
                setCurrentStep(1);
              } else if (payload.status === "Discovering client companies...") {
                setCurrentStep(2);
              } else if (payload.status === "Running AI synthesis...") {
                setCurrentStep(3);
              } else if (payload.status === "Complete") {
                setCurrentStep(4);
                if (payload.report) {
                  gotReport = true;
                  // Redirect after a brief success delay to show the "Report Saved Successfully!" banner
                  setTimeout(() => {
                    if (payload.report.id) {
                      router.push(`/research/${payload.report.id}`);
                    } else {
                      router.push("/reports");
                    }
                  }, 2000);
                }
              } else if (payload.status === "Error") {
                setErrorMsg(payload.message || "An error occurred during report generation.");
                setLoading(false);
              }
            } catch (err) {
              console.error("JSON parsing error inside stream:", err, dataStr);
            }
          }
        }
      }
    } catch (err: unknown) {
      console.error("Pipeline run failure:", err);
      const errMsg = err instanceof Error ? err.message : "Failed to contact research server. Please check that backend is running.";
      setErrorMsg(errMsg);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-[#2D7DD2]" />
          <span>Export Market Intelligence</span>
        </h1>
        <p className="text-slate-400 mt-1">AI-powered client discovery and regional demand forecasting for thermal packaging products</p>
      </div>

      <div className="grid md:grid-cols-12 gap-8 items-start">
        {/* Left column: Input parameters selection */}
        <div className="md:col-span-7 space-y-6">
          <div className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldCheck className="h-5 w-5 text-[#2D7DD2]" />
              Configuration Parameters
            </h2>

            {/* Select Product Dropdown */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Select Thermal Packaging Product
              </label>
              <div className="relative">
                <Package2 className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-500" />
                <select
                  value={product}
                  onChange={(e) => setProduct(e.target.value)}
                  disabled={loading}
                  className="w-full pl-11 pr-4 py-3 bg-[#0A0F1E] border border-slate-800 rounded-xl text-white font-medium focus:outline-none focus:border-[#2D7DD2] focus:ring-1 focus:ring-[#2D7DD2] transition-colors disabled:opacity-55 cursor-pointer appearance-none"
                >
                  <option value="" disabled className="text-slate-500">
                    -- Choose Product Line --
                  </option>
                  {PRODUCTS.map((p) => (
                    <option key={p.code} value={p.code} className="text-white">
                      {p.name}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Select Target Region Dropdown */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Select Target Export Region
              </label>
              <div className="relative">
                <Globe2 className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-500" />
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  disabled={loading}
                  className="w-full pl-11 pr-4 py-3 bg-[#0A0F1E] border border-slate-800 rounded-xl text-white font-medium focus:outline-none focus:border-[#2D7DD2] focus:ring-1 focus:ring-[#2D7DD2] transition-colors disabled:opacity-55 cursor-pointer appearance-none"
                >
                  <option value="" disabled className="text-slate-500">
                    -- Choose Target Region --
                  </option>
                  {REGIONS.map((r) => (
                    <option key={r.id} value={r.name} className="text-white">
                      {r.name}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl text-red-300 text-sm font-medium">
                {errorMsg}
              </div>
            )}

            {/* Trigger Button */}
            {!loading && (
              <Button
                onClick={handleRunResearch}
                disabled={!product || !region}
                className="w-full py-6 rounded-xl text-sm font-bold bg-[#2D7DD2] hover:bg-[#1E6CB5] active:bg-[#155A96] disabled:bg-slate-800/50 disabled:text-slate-500 shadow-lg text-white transition-all flex items-center justify-center gap-2 mt-4"
              >
                <Sparkles className="h-5 w-5" />
                Generate Intelligence Report
              </Button>
            )}
          </div>
        </div>

        {/* Right column: Dynamic Preview or Loading Progress Stepper */}
        <div className="md:col-span-5">
          {!loading ? (
            <div className="bg-[#111625] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-6 min-h-[340px] flex flex-col justify-between">
              <div>
                <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4">
                  What this report will cover
                </h3>

                {product || region ? (
                  <div className="space-y-6">
                    {/* Sectors coverage */}
                    {selectedProduct && (
                      <div className="space-y-2.5">
                        <div className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                          <Layers className="h-4 w-4 text-[#2D7DD2]" />
                          Industry Sectors (4)
                        </div>
                        <ul className="space-y-2 pl-6 list-disc text-sm text-slate-200">
                          {selectedProduct.sectors.map((s, idx) => (
                            <li key={idx} className="leading-snug">{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Regional Events coverage */}
                    {selectedRegion && (
                      <div className="space-y-2.5 pt-2 border-t border-slate-800/60">
                        <div className="text-xs font-bold text-slate-400 flex items-center gap-1.5">
                          <Calendar className="h-4 w-4 text-emerald-400" />
                          Dominant Trade Events (3)
                        </div>
                        <ul className="space-y-2 pl-6 list-disc text-sm text-slate-200">
                          {selectedRegion.events.map((e, idx) => (
                            <li key={idx} className="leading-snug">{e}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-slate-500 text-sm py-12 text-center flex flex-col items-center justify-center gap-3">
                    <Package2 className="h-12 w-12 text-slate-700 stroke-[1.5]" />
                    <p className="max-w-[240px]">Select a product line and export region on the left to load a report context preview.</p>
                  </div>
                )}
              </div>

              {(product || region) && (
                <div className="text-xs text-slate-500 border-t border-slate-800/40 pt-4 flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-[#2D7DD2]/60" />
                  Instant preview matches target database criteria.
                </div>
              )}
            </div>
          ) : (
            /* Loading Stepper state */
            <div className="bg-[#111625] border border-[#2D7DD2]/30 rounded-2xl p-6 shadow-xl shadow-blue-950/20 space-y-6">
              <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-[#2D7DD2]"></span>
                  </span>
                  Research In Progress...
                </h3>
                <span className="text-xs font-bold text-[#2D7DD2] bg-[#2D7DD2]/10 px-2 py-0.5 rounded-full">
                  Step {Math.min(currentStep + 1, 4)} of 4
                </span>
              </div>

              <div className="space-y-6">
                {STEPPER_ITEMS.map((item, idx) => {
                  const isActive = idx === currentStep;
                  const isCompleted = idx < currentStep;
                  const isPending = idx > currentStep;

                  return (
                    <div key={item.key} className="flex gap-4 items-start relative">
                      {/* Left Connector line */}
                      {idx < STEPPER_ITEMS.length - 1 && (
                        <div
                          className={`absolute left-[13px] top-[28px] w-[2px] h-[calc(100%+8px)] ${
                            isCompleted ? "bg-[#2D7DD2]" : "bg-slate-800"
                          }`}
                        />
                      )}

                      {/* Step Indicator Dot */}
                      <div className="relative shrink-0 z-10">
                        {isCompleted ? (
                          <div className="h-7 w-7 rounded-full bg-[#2D7DD2]/25 border-2 border-[#2D7DD2] flex items-center justify-center text-white">
                            <CheckCircle2 className="h-4 w-4 text-white" />
                          </div>
                        ) : isActive ? (
                          <div className="h-7 w-7 rounded-full bg-[#0A0F1E] border-2 border-[#2D7DD2] flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <div className="h-2 w-2 rounded-full bg-[#2D7DD2] animate-ping" />
                          </div>
                        ) : (
                          <div className="h-7 w-7 rounded-full bg-[#0A0F1E] border-2 border-slate-800 flex items-center justify-center text-xs font-bold text-slate-500">
                            {idx + 1}
                          </div>
                        )}
                      </div>

                      {/* Step Details */}
                      <div className="space-y-1 py-0.5 flex-1">
                        <div
                          className={`text-sm font-bold ${
                            isActive ? "text-white" : isCompleted ? "text-slate-300" : "text-slate-500"
                          }`}
                        >
                          {item.label}
                        </div>
                        {isActive && (
                          <div className="flex gap-1.5 items-center h-4 pt-1">
                            <div className="w-1.5 h-3 bg-[#2D7DD2] rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                            <div className="w-1.5 h-4.5 bg-[#2D7DD2] rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                            <div className="w-1.5 h-2 bg-[#2D7DD2] rounded-full animate-bounce" style={{ animationDelay: "0.3s" }} />
                            <span className="text-[11px] text-slate-400 font-medium ml-1.5 animate-pulse">Running analysis...</span>
                          </div>
                        )}
                        {isCompleted && (
                          <span className="text-[10px] text-emerald-500 font-semibold flex items-center gap-1">
                            Task finished
                          </span>
                        )}
                        {isPending && (
                          <span className="text-[10px] text-slate-600 font-medium">Pending...</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {currentStep === 4 && (
                <div className="p-4 bg-emerald-950/40 border border-emerald-500/50 rounded-xl text-emerald-400 text-sm font-bold text-center flex flex-col items-center justify-center gap-2 animate-bounce">
                  <CheckCircle2 className="h-6 w-6 text-emerald-400 animate-pulse" />
                  <span>Report Saved Successfully!</span>
                  <span className="text-xs text-slate-400 font-medium">Opening report details...</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
