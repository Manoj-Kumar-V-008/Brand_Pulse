import React from "react";
import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BookOpenCheck,
  BrainCircuit,
  FlaskConical,
  Orbit,
} from "lucide-react";

export type TabKey = "overview" | "analytics" | "ai-internals" | "algorithms" | "evaluation";

interface NavbarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  simulateCrisis: boolean;
  onToggleCrisis: () => void;
  nlpBackend?: string;
  dataMode?: string;
}

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: "overview", label: "3D Core", icon: <Orbit className="h-4 w-4" /> },
  { key: "analytics", label: "Analytics & SoV", icon: <BarChart3 className="h-4 w-4" /> },
  { key: "ai-internals", label: "AI Search & KRR", icon: <BrainCircuit className="h-4 w-4" /> },
  { key: "algorithms", label: "Algorithms", icon: <BookOpenCheck className="h-4 w-4" /> },
  { key: "evaluation", label: "Testing & F1", icon: <FlaskConical className="h-4 w-4" /> },
];

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onTabChange,
  simulateCrisis,
  onToggleCrisis,
  nlpBackend,
  dataMode,
}) => (
  <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-obsidian-950/85 backdrop-blur-xl">
    <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 via-sky-500 to-indigo-600 shadow-lg shadow-cyan-500/25">
          <Activity className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-display text-lg font-extrabold tracking-tight text-white">
              BrandPulse <span className="text-cyan-400">3D</span>
            </h1>
            <span className="hidden rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider text-cyan-300 sm:inline-block">
              v2.0 • AIML + IDA
            </span>
          </div>
          <p className="text-[11px] text-slate-400">
            {nlpBackend || "VADER + RoBERTa Ensemble • Search & KRR"}
          </p>
        </div>
      </div>

      <nav className="flex flex-wrap items-center gap-1 rounded-xl border border-slate-800 bg-obsidian-900/90 p-1">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => onTabChange(tab.key)}
              className={`relative flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-colors sm:px-3 ${
                isActive ? "text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isActive && (
                <motion.span
                  layoutId="activeNavPill"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-600/85 to-indigo-600/85 shadow-md shadow-cyan-500/20"
                />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                {tab.icon}
                <span className="hidden md:inline">{tab.label}</span>
              </span>
            </button>
          );
        })}
      </nav>

      <div className="flex items-center gap-2">
        {dataMode && (
          <span
            className={`hidden items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] font-semibold xl:inline-flex ${
              dataMode === "SIMULATED_CRISIS"
                ? "border-rose-500/40 bg-rose-500/15 text-rose-300"
                : dataMode === "LIVE_WEB" || dataMode === "HYBRID_CACHE"
                ? "border-emerald-500/35 bg-emerald-500/10 text-emerald-300"
                : "border-amber-500/35 bg-amber-500/10 text-amber-300"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                dataMode === "SIMULATED_CRISIS" ? "animate-ping bg-rose-400" : "bg-emerald-400"
              }`}
            />
            {dataMode.replace("_", " ")}
          </span>
        )}
        <button
          onClick={onToggleCrisis}
          className={`flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all ${
            simulateCrisis
              ? "border-rose-400 bg-rose-600 text-white shadow-lg shadow-rose-600/30"
              : "border-rose-500/35 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20"
          }`}
        >
          <AlertTriangle className="h-3.5 w-3.5" />
          {simulateCrisis ? "Exit Crisis Demo" : "Simulate PR Crisis"}
        </button>
      </div>
    </div>
  </header>
);
