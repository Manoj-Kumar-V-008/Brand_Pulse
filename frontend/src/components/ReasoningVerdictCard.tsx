import React from "react";
import { AlertOctagon, CheckCircle2, ShieldAlert, Sparkles, Target, Zap } from "lucide-react";
import { CrisisMetrics, ReasoningOutput } from "../types";

interface ReasoningVerdictCardProps {
  reasoning: ReasoningOutput;
  crisisMetrics: CrisisMetrics;
  ensembleAlpha: number;
}

export const ReasoningVerdictCard: React.FC<ReasoningVerdictCardProps> = ({
  reasoning,
  ensembleAlpha,
}) => {
  const badgeStyles: Record<string, { bg: string; icon: React.ReactNode; label: string }> = {
    CRITICAL_CRISIS: { bg: "border-rose-500/50 bg-rose-500/15 text-rose-300", icon: <AlertOctagon className="h-4 w-4 text-rose-400" />, label: "CRITICAL PR CRISIS" },
    ELEVATED: { bg: "border-orange-500/50 bg-orange-500/15 text-orange-300", icon: <ShieldAlert className="h-4 w-4 text-orange-400" />, label: "ELEVATED RISK" },
    WATCH: { bg: "border-amber-500/50 bg-amber-500/15 text-amber-300", icon: <Zap className="h-4 w-4 text-amber-400" />, label: "REPUTATION WATCH" },
    NORMAL: { bg: "border-emerald-500/50 bg-emerald-500/15 text-emerald-300", icon: <CheckCircle2 className="h-4 w-4 text-emerald-400" />, label: "HEALTHY / NORMAL" },
  };
  const badge = badgeStyles[reasoning.crisis_level] || badgeStyles.NORMAL;

  return (
    <div className="glass-panel flex h-full flex-col justify-between rounded-2xl p-5">
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-xs font-bold ${badge.bg}`}>
            {badge.icon}
            {badge.label}
          </span>
          <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
            <span>Confidence:</span>
            <span className="font-bold text-cyan-300">{Math.round(reasoning.confidence * 100)}%</span>
            <span className="text-slate-600">|</span>
            <span>α = {ensembleAlpha.toFixed(2)}</span>
          </div>
        </div>

        <h2 className="mt-3 text-xl font-extrabold leading-snug text-white">{reasoning.overall_verdict}</h2>

        <div className="mt-3 rounded-xl border border-cyan-500/25 bg-cyan-500/5 p-3.5">
          <div className="mb-1 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-cyan-300">
            <Sparkles className="h-3.5 w-3.5" /> AI Justification & Root Reason
          </div>
          <p className="text-sm leading-relaxed text-slate-200">{reasoning.primary_reason}</p>
        </div>

        <div className="mt-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Forward-Chaining Inferred Signals ({reasoning.fired_rules.length} Rules Fired)
          </h3>
          <ul className="mt-2 space-y-1.5">
            {reasoning.supporting_reasons.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-4 border-t border-slate-800/80 pt-3.5">
        <div className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-indigo-300">
          <Target className="h-3.5 w-3.5" /> Recommended Strategic PR Actions
        </div>
        <div className="space-y-1.5">
          {reasoning.recommended_actions.slice(0, 3).map((act, idx) => (
            <div key={idx} className="rounded-lg border border-indigo-500/20 bg-indigo-500/10 px-3 py-2 text-xs text-indigo-100">
              {act}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
