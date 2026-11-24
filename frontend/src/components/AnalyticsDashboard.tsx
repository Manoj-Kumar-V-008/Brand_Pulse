import React, { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AlertTriangle, Layers, PieChart as PieIcon, RefreshCw, SlidersHorizontal, TrendingUp } from "lucide-react";
import { AnalyzeResponse } from "../types";
import { BrandLogo } from "./BrandLogo";

interface AnalyticsDashboardProps {
  data: AnalyzeResponse;
  loading?: boolean;
  onCompareCompetitors?: (competitors: string[]) => void;
}

const SOV_COLORS = ["#06b6d4", "#6366f1", "#10b981", "#f59e0b", "#ec4899"];

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  data,
  loading = false,
  onCompareCompetitors,
}) => {
  const [customCompsInput, setCustomCompsInput] = useState(
    (data.competitors_used || []).join(", ")
  );

  useEffect(() => {
    setCustomCompsInput((data.competitors_used || []).join(", "));
  }, [data.brand, data.competitors_used]);

  const handleApplyCompetitors = (e: React.FormEvent) => {
    e.preventDefault();
    if (!onCompareCompetitors) return;
    const list = customCompsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    onCompareCompetitors(list);
  };

  return (
    <div className="space-y-6">
      {/* Industry & Custom Competitor Selector Banner */}
      <div className="glass-panel holo-border flex flex-col justify-between gap-4 rounded-2xl p-4 sm:p-5 lg:flex-row lg:items-center">
        <div className="flex items-center gap-3">
          <BrandLogo brand={data.brand} domain={data.brand_domain} size="md" glow />
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-cyan-400">
                Domain-Aware Share of Voice
              </span>
              <span className="rounded-full border border-emerald-500/40 bg-emerald-500/15 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300">
                Sector: {data.industry || "Matched Industry"}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-300">
              Comparing <strong>{data.brand}</strong> strictly against same-industry peers (
              {(data.competitors_used || []).join(", ") || "Auto-detected"}).
            </p>
          </div>
        </div>

        {onCompareCompetitors && (
          <form onSubmit={handleApplyCompetitors} className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <SlidersHorizontal className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={customCompsInput}
                onChange={(e) => setCustomCompsInput(e.target.value)}
                placeholder="Custom rivals (comma separated)"
                className="w-64 rounded-xl border border-slate-700 bg-obsidian-950/90 py-2 pl-8 pr-3 text-xs text-white placeholder-slate-500 outline-none focus:border-cyan-400"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 px-3.5 py-2 text-xs font-bold text-white transition hover:brightness-110 disabled:opacity-60"
            >
              {loading && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
              Update Rivals
            </button>
          </form>
        )}
      </div>

      {/* Row 1: Share of Voice Donut + Competitor Leaderboard with Real Logos */}
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="glass-panel rounded-2xl p-5 lg:col-span-5">
          <div className="mb-4 flex items-center gap-2">
            <PieIcon className="h-5 w-5 text-cyan-400" />
            <div>
              <h3 className="font-display text-base font-bold text-white">Share of Voice (SoV) Distribution</h3>
              <p className="text-xs text-slate-400">Relative mention volume share across true industry rivals</p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.share_of_voice}
                  dataKey="share_pct"
                  nameKey="brand"
                  cx="50%"
                  cy="50%"
                  innerRadius={58}
                  outerRadius={92}
                  paddingAngle={4}
                  label={({ brand, share_pct }) => `${brand} ${share_pct}%`}
                >
                  {data.share_of_voice.map((entry, index) => (
                    <Cell key={entry.brand} fill={SOV_COLORS[index % SOV_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0a1020",
                    borderColor: "#334155",
                    borderRadius: "10px",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-5 lg:col-span-7">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-400" />
            <div>
              <h3 className="font-display text-base font-bold text-white">
                Competitor Reputation & Net Sentiment Benchmark
              </h3>
              <p className="text-xs text-slate-400">
                Side-by-side Net Sentiment Score (-100 to +100) & Share of Voice
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] uppercase tracking-wider text-slate-400">
                  <th className="py-2.5 pr-3">Brand</th>
                  <th className="px-3 py-2.5">Mentions</th>
                  <th className="px-3 py-2.5">SoV Share</th>
                  <th className="px-3 py-2.5">Net Sentiment</th>
                  <th className="px-3 py-2.5">Pos / Neg</th>
                  <th className="py-2.5 pl-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70">
                {data.share_of_voice.map((row, idx) => {
                  const isTarget = row.brand.toLowerCase() === data.brand.toLowerCase();
                  return (
                    <tr
                      key={row.brand}
                      className={isTarget ? "bg-cyan-500/10" : "hover:bg-slate-800/35"}
                    >
                      <td className="py-3 pr-3 font-bold text-white">
                        <div className="flex items-center gap-2.5">
                          <BrandLogo brand={row.brand} domain={row.domain} size="sm" glow={isTarget} />
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span>{row.brand}</span>
                              {isTarget && (
                                <span className="rounded bg-cyan-500/20 px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase text-cyan-300">
                                  Target
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3 font-mono text-slate-300">{row.mentions}</td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-16 overflow-hidden rounded-full bg-slate-800">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${Math.min(100, row.share_pct)}%`,
                                backgroundColor: SOV_COLORS[idx % SOV_COLORS.length],
                              }}
                            />
                          </div>
                          <span className="font-mono font-semibold text-cyan-300">
                            {row.share_pct}%
                          </span>
                        </div>
                      </td>
                      <td
                        className={`px-3 py-3 font-mono font-bold ${
                          row.net_sentiment >= 10
                            ? "text-emerald-400"
                            : row.net_sentiment <= -10
                            ? "text-rose-400"
                            : "text-amber-300"
                        }`}
                      >
                        {row.net_sentiment >= 0 ? "+" : ""}
                        {row.net_sentiment.toFixed(1)}
                      </td>
                      <td className="px-3 py-3 font-mono text-slate-300">
                        <span className="text-emerald-400">{row.positive_pct}%</span> /{" "}
                        <span className="text-rose-400">{row.negative_pct}%</span>
                      </td>
                      <td className="py-3 pl-3">
                        <span
                          className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-bold ${
                            row.crisis_level === "CRITICAL_CRISIS"
                              ? "bg-rose-500/20 text-rose-300"
                              : row.crisis_level === "ELEVATED"
                              ? "bg-orange-500/20 text-orange-300"
                              : row.crisis_level === "WATCH"
                              ? "bg-amber-500/20 text-amber-300"
                              : "bg-emerald-500/20 text-emerald-300"
                          }`}
                        >
                          {row.crisis_level}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 2: Live PR Crisis Velocity & Z-Score Monitor */}
      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-rose-400" />
            <div>
              <h3 className="font-display text-base font-bold text-white">
                PR Crisis Velocity & Statistical Z-Score Monitor
              </h3>
              <p className="text-xs text-slate-400">
                Daily polarity volume overlaid with Z-score anomaly index (PR Crisis triggers at Z ≥ 2.0σ)
              </p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-800 bg-obsidian-950/80 px-3 py-1.5 font-mono text-xs text-slate-300">
            Baseline μ = {data.crisis_metrics.baseline_neg_mean} | σ ={" "}
            {data.crisis_metrics.baseline_neg_std} | Current Z ={" "}
            <strong className={data.crisis_metrics.z_score >= 2.0 ? "text-rose-400" : "text-cyan-300"}>
              {data.crisis_metrics.z_score >= 0 ? "+" : ""}
              {data.crisis_metrics.z_score}σ
            </strong>
          </div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data.time_series}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
              <YAxis yAxisId="left" stroke="#94a3b8" fontSize={11} />
              <YAxis yAxisId="right" orientation="right" stroke="#f43f5e" fontSize={11} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0a1020",
                  borderColor: "#334155",
                  borderRadius: "10px",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Bar yAxisId="left" dataKey="positive" name="Positive" stackId="a" fill="#10b981" />
              <Bar yAxisId="left" dataKey="neutral" name="Neutral" stackId="a" fill="#f59e0b" />
              <Bar yAxisId="left" dataKey="negative" name="Negative" stackId="a" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="z_score"
                name="Anomaly Z-Score (σ)"
                stroke="#38bdf8"
                strokeWidth={2.5}
                dot={{ r: 4, fill: "#38bdf8" }}
              />
              <ReferenceLine
                yAxisId="right"
                y={2.0}
                stroke="#ef4444"
                strokeDasharray="5 5"
                label={{ value: "PR Crisis Threshold (2.0σ)", fill: "#fca5a5", fontSize: 11, position: "insideTopRight" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3: Aspect Breakdown */}
      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-emerald-400" />
          <div>
            <h3 className="font-display text-base font-bold text-white">
              Aspect-Based Sentiment Breakdown (Ontology Frames)
            </h3>
            <p className="text-xs text-slate-400">Which brand pillars drive customer delight versus complaints</p>
          </div>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.aspect_breakdown} layout="vertical" margin={{ left: 25, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#94a3b8" fontSize={11} />
              <YAxis type="category" dataKey="aspect" stroke="#e2e8f0" fontSize={11} width={145} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0a1020",
                  borderColor: "#334155",
                  borderRadius: "10px",
                  fontSize: "12px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Bar dataKey="positive" name="Positive" stackId="a" fill="#10b981" />
              <Bar dataKey="neutral" name="Neutral" stackId="a" fill="#f59e0b" />
              <Bar dataKey="negative" name="Negative" stackId="a" fill="#f43f5e" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
