import React from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowRight, BookOpen, Cpu, GitBranch, Mountain, Scale } from "lucide-react";
import { AnalyzeResponse, EvaluationResponse, OntologyFrame } from "../types";

export const AIInternalsTab: React.FC<{
  data: AnalyzeResponse;
  evaluation: EvaluationResponse | null;
  ontologyFrames: OntologyFrame[];
}> = ({ data, evaluation, ontologyFrames }) => {
  const hc = evaluation?.hill_climbing;

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="glass-panel rounded-2xl p-5 lg:col-span-6">
          <div className="mb-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Mountain className="h-5 w-5 text-cyan-400" />
              <div>
                <h3 className="text-base font-bold text-white">AI Search #1: Steepest-Ascent Hill-Climbing</h3>
                <p className="text-xs text-slate-400">Optimizes ensemble weight α & threshold τ to maximize Macro F1</p>
              </div>
            </div>
            {hc && <span className="rounded-full border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-1 font-mono text-xs font-bold text-emerald-300">+{hc.improvement_pct}% F1</span>}
          </div>

          {hc ? (
            <>
              <div className="mb-3 grid grid-cols-3 gap-2 text-center font-mono text-xs">
                <div className="rounded-xl border border-slate-800 bg-obsidian-950/80 p-2.5">
                  <div className="text-[10px] text-slate-400">Optimal α (BERT wt)</div>
                  <div className="mt-0.5 text-base font-bold text-cyan-300">{hc.best_alpha.toFixed(2)}</div>
                </div>
                <div className="rounded-xl border border-slate-800 bg-obsidian-950/80 p-2.5">
                  <div className="text-[10px] text-slate-400">Optimal τ</div>
                  <div className="mt-0.5 text-base font-bold text-indigo-300">±{hc.best_threshold.toFixed(2)}</div>
                </div>
                <div className="rounded-xl border border-slate-800 bg-obsidian-950/80 p-2.5">
                  <div className="text-[10px] text-slate-400">Peak Macro F1</div>
                  <div className="mt-0.5 text-base font-bold text-emerald-400">{(hc.best_f1 * 100).toFixed(1)}%</div>
                </div>
              </div>

              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={hc.trajectory.map((t) => ({ ...t, f1_pct: Number((t.f1_score * 100).toFixed(1)) }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="iteration" stroke="#94a3b8" fontSize={11} />
                    <YAxis domain={["auto", 100]} stroke="#94a3b8" fontSize={11} unit="%" />
                    <Tooltip contentStyle={{ backgroundColor: "#0b1020", borderColor: "#334155", borderRadius: "10px", fontSize: "12px" }} />
                    <Line type="monotone" dataKey="f1_pct" name="Macro F1 (%)" stroke="#06b6d4" strokeWidth={3} dot={{ r: 4, fill: "#22d3ee" }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <p className="text-xs text-slate-400">Loading Hill-Climbing trajectory...</p>
          )}
        </div>

        <div className="glass-panel rounded-2xl p-5 lg:col-span-6">
          <div className="mb-3 flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-indigo-400" />
            <div>
              <h3 className="text-base font-bold text-white">AI Search #2: Best-First Root-Cause Graph Search</h3>
              <p className="text-xs text-slate-400">Priority-queue heuristic h(n) = (|s| + bias)·log(1+freq)·severity tracing sentiment drivers</p>
            </div>
          </div>

          <div className="space-y-3">
            {data.root_cause_paths.map((path, idx) => {
              const isNeg = path.avg_sentiment < -0.05;
              const isPos = path.avg_sentiment > 0.05;
              return (
                <div key={`${path.aspect}-${path.trigger_keyword}-${idx}`} className="rounded-xl border border-slate-800/90 bg-obsidian-950/75 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-1.5 text-xs font-bold">
                      <span className="rounded-md bg-slate-800 px-2 py-0.5 text-slate-200">{data.brand}</span>
                      <ArrowRight className="h-3.5 w-3.5 text-slate-500" />
                      <span className="rounded-md bg-indigo-500/20 px-2 py-0.5 text-indigo-200">{path.aspect}</span>
                      <ArrowRight className="h-3.5 w-3.5 text-slate-500" />
                      <span className={`rounded-md px-2 py-0.5 ${isNeg ? "bg-rose-500/20 text-rose-300" : isPos ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}>
                        "{path.trigger_keyword}"
                      </span>
                    </div>
                    <span className="font-mono text-[11px] font-semibold text-cyan-300">h = {path.path_score.toFixed(2)}</span>
                  </div>
                  <p className="mt-1.5 text-[11px] text-slate-400">{path.explanation}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Scale className="h-5 w-5 text-amber-400" />
            <div>
              <h3 className="text-base font-bold text-white">Knowledge Representation & Reasoning: Forward-Chaining Rule Engine</h3>
              <p className="text-xs text-slate-400">Live evaluation of all 10 IF–THEN production rules over Working Memory facts</p>
            </div>
          </div>
          <span className="rounded-full border border-cyan-500/35 bg-cyan-500/10 px-3 py-1 font-mono text-xs font-semibold text-cyan-300">
            {data.reasoning.fired_rules.length} / {data.reasoning.all_rules_evaluated.length} Rules Fired
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                <th className="py-2 pr-3">ID</th>
                <th className="px-3 py-2">Rule Name</th>
                <th className="px-3 py-2">IF Condition Expression</th>
                <th className="px-3 py-2">Status</th>
                <th className="py-2 pl-3">THEN Derived Conclusion</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {data.reasoning.all_rules_evaluated.map((rule) => (
                <tr key={rule.rule_id} className={rule.matched ? "bg-emerald-500/5" : "opacity-55"}>
                  <td className="py-2.5 pr-3 font-mono font-bold text-cyan-300">{rule.rule_id}</td>
                  <td className="px-3 py-2.5 font-semibold text-white">{rule.rule_name}</td>
                  <td className="px-3 py-2.5 font-mono text-[11px] text-indigo-200">{rule.condition_expression}</td>
                  <td className="px-3 py-2.5">
                    <span className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-bold ${rule.matched ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-400"}`}>
                      {rule.matched ? "FIRED" : "FALSE"}
                    </span>
                  </td>
                  <td className="py-2.5 pl-3 text-slate-300">{rule.derived_fact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 rounded-xl border border-slate-800 bg-obsidian-950/90 p-3.5">
          <div className="mb-1.5 flex items-center gap-1.5 font-mono text-[11px] font-bold uppercase text-cyan-400">
            <Cpu className="h-3.5 w-3.5" /> Live Working Memory Fact Base
          </div>
          <pre className="overflow-x-auto font-mono text-[11px] text-slate-300">
            {JSON.stringify(data.reasoning.working_memory_facts, null, 2)}
          </pre>
        </div>
      </div>

      {ontologyFrames.length > 0 && (
        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-4 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-emerald-400" />
            <div>
              <h3 className="text-base font-bold text-white">Brand Aspect Ontology (Frame-Based Knowledge Representation)</h3>
              <p className="text-xs text-slate-400">Structured domain frames mapping lexical triggers to business severity & causal impact</p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {ontologyFrames.map((f) => (
              <div key={f.frame_id} className="rounded-xl border border-slate-800 bg-obsidian-950/75 p-3.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-white">{f.aspect}</span>
                  <span className="rounded bg-cyan-500/15 px-2 py-0.5 font-mono text-[10px] font-bold text-cyan-300">w = {f.severity_weight}</span>
                </div>
                <p className="mt-1 text-xs text-slate-400">{f.description}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {f.sample_triggers.slice(0, 6).map((kw) => (
                    <span key={kw} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">{kw}</span>
                  ))}
                </div>
                <p className="mt-2 border-t border-slate-800/80 pt-2 text-[11px] text-indigo-200/90">
                  <strong>Causal Link:</strong> {f.causal_impact}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
