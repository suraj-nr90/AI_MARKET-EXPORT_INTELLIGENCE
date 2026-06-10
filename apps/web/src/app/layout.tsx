import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import Providers from "@/components/providers";
import Link from "next/link";
import { LayoutDashboard, SearchCode, FileBarChart2, ShieldAlert } from "lucide-react";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "ExportIntel - Thermal Packaging Market Intelligence",
  description: "Market Intelligence & Client Discovery Platform for Thermal Packaging",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans h-full", inter.variable)}>
      <body className="h-full bg-background text-foreground antialiased">
        <Providers>
          <div className="flex h-full overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 bg-[#080C16] text-slate-200 flex flex-col border-r border-slate-800/80 shrink-0">
              {/* Logo / Brand */}
              <div className="h-16 flex items-center px-6 border-b border-slate-800/80">
                <Link href="/" className="flex items-center gap-2 font-bold text-lg text-white">
                  <ShieldAlert className="h-6 w-6 text-[#2D7DD2]" />
                  <span className="tracking-tight font-extrabold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">ExportIntel</span>
                </Link>
              </div>

              {/* Navigation Links */}
              <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
                <Link
                  href="/"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all hover:bg-slate-800/50 hover:text-white text-slate-400"
                >
                  <LayoutDashboard className="h-5 w-5 text-slate-400" />
                  Dashboard
                </Link>
                <Link
                  href="/research"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all hover:bg-slate-800/50 hover:text-white text-slate-400"
                >
                  <SearchCode className="h-5 w-5 text-slate-400" />
                  Market Research
                </Link>
                <Link
                  href="/reports"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all hover:bg-slate-800/50 hover:text-white text-slate-400"
                >
                  <FileBarChart2 className="h-5 w-5 text-slate-400" />
                  Saved Reports
                </Link>
              </nav>

              {/* Sidebar Footer */}
              <div className="p-4 border-t border-slate-800/80 bg-[#060A12]">
                <div className="flex items-center gap-3 px-2">
                  <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-sm text-white shadow-inner">
                    EM
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">Export Manager</div>
                    <div className="text-[10px] text-slate-400 font-medium">Thermal Packaging Corp</div>
                  </div>
                </div>
              </div>
            </aside>

            {/* Main Content Wrapper */}
            <div className="flex flex-col flex-1 h-full overflow-hidden bg-background">
              {/* Main Content Area */}
              <main className="flex-1 overflow-y-auto p-8">
                {children}
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}

