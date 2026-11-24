import React, { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CheckSquare, Database, FlaskConical, Grid } from "lucide-react";
import { AnalyzeResponse, EvaluationResponse } from "../types";

export const EvaluationTab: React.FC<{ data: AnalyzeResponse; evaluation: EvaluationResponse | null }> = ({ data, evaluation }) => {
  const [selectedModelIdx, setSelectedModelIdx] = useState(2);

  if (!evaluation) {
    return <div className="glass-panel rounded-2xl p-8 text-center text-sm text-slate-400">Loading preliminary benchmark evaluation metrics...</div>;
  }

  const chartData = evaluation.model_comparison.map((m) => ({
    name: m.model_name.replace(" (Lexicon Rules)", "").replace("Hill-Climbed ", ""),
    Accuracy: m.accuracy,
    Precision: m.precision,
    Recall: m.recall,
    "Macro F1": m.macro_f1,
  }));
  const activeModel = evaluation.model_comparison[selectedModelIdx] || evaluation.model_comparison[0];

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="glass-panel rounded-2xl p-5 lg:col-span-7">
          <div className="mb-4 flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-bold text-white">Preliminary Testing: VADER vs BERT/ML vs Hill-Climbed Ensemble</h3>
              <p className="text-xs text-slate-400">Evaluated on {evaluation.dataset_size} balanced labeled brand mentions (Neg/Neu/Pos)</p>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#cbd5e1" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: "#0b1020", borderColor: "#334155", borderRadius: "10px", fontSize: "12px" }} />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="Accuracy" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Precision" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Recall" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Macro F1" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-5 lg:col-span-5">
          <div className="mb-3 flex items-center gap-2">
            <Grid className="h-5 w-5 text-emerald-400" />
            <div>
              <h3 className="text-base font-bold text-white">3×3 Confusion Matrix</h3>
              <p className="text-xs text-slate-400">Inspect classification errors across Negative / Neutral / Positive</p>
            </div>
          </div>
          <div className="mb-4 flex flex-wrap gap-1.5">
            {evaluation.model_comparison.map((m, i) => (
              <button key={m.model_name} onClick={() => setSelectedModelIdx(i)} className={`rounded-lg border px-2.5 py-1 text-[11px] font-semibold transition ${selectedModelIdx === i ? "border-cyan-400 bg-cyan-500/20 text-cyan-200" : "border-slate-700 bg-obsidian-950/70 text-slate-400 hover:text-white"}`}>
                {i === 0 ? "VADER" : i === 1 ? "BERT / ML" : "Ensemble"}
              </button>
            ))}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-separate border-spacing-1.5 text-center font-mono text-xs">
              <thead>
                <tr className="text-[10px] uppercase text-slate-400">
                  <th className="p-1 text-left">Actual \ Pred</th>
                  {evaluation.labels.map((lbl) => <th key={lbl} className="p-1">{lbl}</th>)}
                </tr>
              </thead>
              <tbody>
                {activeModel.confusion_matrix.map((row, rIdx) => (
                  <tr key={evaluation.labels[rIdx]}>
                    <td className="p-1.5 text-left font-sans text-xs font-semibold text-slate-300">{evaluation.labels[rIdx]}</td>
                    {row.map((val, cIdx) => {
                      const isDiag = rIdx === cIdx;
                      return (
                        <td key={cIdx} className={`rounded-lg p-3 text-base font-extrabold ${isDiag ? "border border-emerald-500/40 bg-emerald-500/20 text-emerald-200" : val > 0 ? "border border-rose-500/30 bg-rose-500/15 text-rose-300" : "border border-slate-800 bg-obsidian-950/70 text-slate-500"}`}>
                          {val}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-3 flex items-center gap-2">
          <CheckSquare className="h-5 w-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">Quantitative Benchmark Summary</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                <th className="py-2.5 pr-3">Model / Pipeline</th>
                <th className="px-3 py-2.5">Accuracy</th>
                <th className="px-3 py-2.5">Precision</th>
                <th className="px-3 py-2.5">Recall</th>
                <th className="px-3 py-2.5">Macro F1</th>
                <th className="py-2.5 pl-3">Avg Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70 font-mono">
              {evaluation.model_comparison.map((row, idx) => (
                <tr key={row.model_name} className={idx === 2 ? "bg-emerald-500/10" : ""}>
                  <td className="py-3 pr-3 font-sans font-bold text-white">{row.model_name}</td>
                  <td className="px-3 py-3 text-cyan-300">{row.accuracy}%</td>
                  <td className="px-3 py-3 text-indigo-300">{row.precision}%</td>
                  <td className="px-3 py-3 text-amber-300">{row.recall}%</td>
                  <td className="px-3 py-3 font-bold text-emerald-400">{row.macro_f1}%</td>
                  <td className="py-3 pl-3 text-slate-400">{row.avg_latency_ms} ms/post</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-cyan-400" />
          <div>
            <h3 className="text-base font-bold text-white">Data Science Pipeline Audit (Pandas Cleaning Stats for {data.brand})</h3>
            <p className="text-xs text-slate-400">End-to-end preprocessing metrics: URL/HTML removal, deduplication, spam filtering & emoji retention</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {[
            { label: "Raw Fetched", val: data.cleaning_stats.raw_count, color: "text-white" },
            { label: "Duplicates Removed", val: data.cleaning_stats.duplicates_removed, color: "text-amber-300" },
            { label: "Spam/Short Filtered", val: data.cleaning_stats.short_or_spam_removed, color: "text-rose-300" },
            { label: "Clean Mentions", val: data.cleaning_stats.final_count, color: "text-emerald-400" },
            { label: "Avg Word Count", val: data.cleaning_stats.avg_word_count, color: "text-cyan-300" },
            { label: "Emojis Preserved", val: data.cleaning_stats.emoji_preserved_count, color: "text-indigo-300" },
          ].map((stat) => (
            <div key={stat.label} className="rounded-xl border border-slate-800 bg-obsidian-950/80 p-3.5 text-center">
              <div className="text-[11px] text-slate-400">{stat.label}</div>
              <div className={`mt-1 font-mono text-xl font-extrabold ${stat.color}`}>{stat.val}</div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-300">
          <span className="font-semibold text-slate-400">Sources Breakdown:</span>
          {Object.entries(data.cleaning_stats.sources_breakdown).map(([src, cnt]) => (
            <span key={src} className="rounded-full border border-slate-700 bg-obsidian-900 px-3 py-1 font-mono text-[11px]">
              {src}: <strong className="text-cyan-300">{cnt}</strong>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
