import React, { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Activity, AlertCircle, Flame, ShieldCheck, ThumbsDown, ThumbsUp } from "lucide-react";
import { analyzeBrandApi, fetchEvaluationApi, fetchKnownBrands, fetchOntologyApi } from "./api/client";
import { AIInternalsTab } from "./components/AIInternalsTab";
import { AlgorithmsExplainedTab } from "./components/AlgorithmsExplainedTab";
import { AnalyticsDashboard } from "./components/AnalyticsDashboard";
import { BrandSearchBar } from "./components/BrandSearchBar";
import { EvaluationTab } from "./components/EvaluationTab";
import { MentionsFeed } from "./components/MentionsFeed";
import { Navbar, TabKey } from "./components/Navbar";
import { ReasoningVerdictCard } from "./components/ReasoningVerdictCard";
import { SentimentOrb3D } from "./components/SentimentOrb3D";
import { AnalyzeResponse, BrandSummary, EvaluationResponse, MentionItem, OntologyFrame } from "./types";

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [currentBrand, setCurrentBrand] = useState<string>("Apple");
  const [customCompetitors, setCustomCompetitors] = useState<string[] | undefined>(undefined);
  const [liveMode, setLiveMode] = useState<boolean>(true);
  const [simulateCrisis, setSimulateCrisis] = useState<boolean>(false);

  const [knownBrands, setKnownBrands] = useState<BrandSummary[]>([]);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null);
  const [ontologyFrames, setOntologyFrames] = useState<OntologyFrame[]>([]);

  const [selectedMentionId, setSelectedMentionId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadBrand = useCallback(
    async (brand: string, live: boolean, crisis: boolean, competitors?: string[]) => {
      setLoading(true);
      setError(null);
      setSelectedMentionId(null);
      try {
        const res = await analyzeBrandApi({
          brand,
          competitors,
          live,
          simulateCrisis: crisis,
        });
        setAnalysis(res);
        setCurrentBrand(res.brand);
        fetchKnownBrands().then(setKnownBrands).catch(() => {});
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Could not connect to FastAPI backend on port 8000."
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    loadBrand("Apple", true, false);
    fetchEvaluationApi().then(setEvaluation).catch(() => {});
    fetchOntologyApi().then((res) => setOntologyFrames(res.frames)).catch(() => {});
  }, [loadBrand]);

  const handleSearchBrand = (brand: string) => {
    setSimulateCrisis(false);
    setCustomCompetitors(undefined);
    loadBrand(brand, liveMode, false, undefined);
  };

  const handleToggleLive = () => {
    const nextLive = !liveMode;
    setLiveMode(nextLive);
    loadBrand(currentBrand, nextLive, simulateCrisis, customCompetitors);
  };

  const handleToggleCrisis = () => {
    const nextCrisis = !simulateCrisis;
    setSimulateCrisis(nextCrisis);
    loadBrand(currentBrand, liveMode, nextCrisis, customCompetitors);
  };

  const handleCompareCompetitors = (competitors: string[]) => {
    const cleaned = competitors.length > 0 ? competitors : undefined;
    setCustomCompetitors(cleaned);
    loadBrand(currentBrand, liveMode, simulateCrisis, cleaned);
  };

  const handleSelectMention = (m: MentionItem) => {
    setSelectedMentionId((prev) => (prev === m.id ? null : m.id));
  };

  return (
    <div className="min-h-screen pb-16 text-slate-100">
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        simulateCrisis={simulateCrisis}
        onToggleCrisis={handleToggleCrisis}
        nlpBackend={analysis?.nlp_backend}
        dataMode={analysis?.data_mode}
      />

      <main className="mx-auto max-w-7xl space-y-6 px-4 pt-6 sm:px-6">
        <BrandSearchBar
          currentBrand={currentBrand}
          knownBrands={knownBrands}
          liveMode={liveMode}
          loading={loading}
          onToggleLive={handleToggleLive}
          onSearchBrand={handleSearchBrand}
        />

        {analysis && analysis.reasoning.crisis_level === "CRITICAL_CRISIS" && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-rose-500/60 bg-rose-950/55 px-5 py-3.5 shadow-lg shadow-rose-900/30"
          >
            <div className="flex items-center gap-3">
              <Flame className="h-6 w-6 animate-pulse text-rose-400" />
              <div>
                <div className="font-display text-sm font-extrabold uppercase tracking-wide text-rose-200">
                  Live PR Crisis Warning — Rule R1 Fired (Z = {analysis.crisis_metrics.z_score}σ)
                </div>
                <p className="text-xs text-rose-200/85">{analysis.reasoning.primary_reason}</p>
              </div>
            </div>
          </motion.div>
        )}

        {error && (
          <div className="rounded-2xl border border-rose-500/40 bg-rose-950/30 p-5 text-sm text-rose-200">
            <div className="flex items-center gap-2 font-bold text-rose-300">
              <AlertCircle className="h-5 w-5" /> Backend Connection Error
            </div>
            <p className="mt-1 text-xs text-rose-200/80">{error}</p>
            <p className="mt-2 font-mono text-xs text-slate-300">
              Make sure FastAPI is running: <code>cd backend && uvicorn app.main:app --reload</code>
            </p>
          </div>
        )}

        {loading && !analysis && (
          <div className="grid gap-6 lg:grid-cols-12">
            <div className="glass-panel h-[475px] animate-pulse rounded-2xl lg:col-span-7" />
            <div className="glass-panel h-[475px] animate-pulse rounded-2xl lg:col-span-5" />
          </div>
        )}

        {analysis && (
          <>
            {/* Staggered KPI Cards */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 }} className="glass-panel glass-panel-hover rounded-2xl p-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Net Sentiment Score</span>
                  <Activity className="h-4 w-4 text-cyan-400" />
                </div>
                <div className={`mt-1.5 font-mono text-2xl font-extrabold ${analysis.crisis_metrics.net_sentiment_score >= 10 ? "text-emerald-400" : analysis.crisis_metrics.net_sentiment_score <= -10 ? "text-rose-400" : "text-amber-300"}`}>
                  {analysis.crisis_metrics.net_sentiment_score >= 0 ? "+" : ""}
                  {analysis.crisis_metrics.net_sentiment_score.toFixed(1)}
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500">Sector: {analysis.industry || "Market"}</div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.07 }} className="glass-panel glass-panel-hover rounded-2xl p-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Positive Mentions</span>
                  <ThumbsUp className="h-4 w-4 text-emerald-400" />
                </div>
                <div className="mt-1.5 font-mono text-2xl font-extrabold text-emerald-400">
                  {(analysis.crisis_metrics.positive_ratio * 100).toFixed(1)}%
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500">{analysis.cleaning_stats.final_count} clean posts analyzed</div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.11 }} className="glass-panel glass-panel-hover rounded-2xl p-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Negative Pressure</span>
                  <ThumbsDown className="h-4 w-4 text-rose-400" />
                </div>
                <div className="mt-1.5 font-mono text-2xl font-extrabold text-rose-400">
                  {(analysis.crisis_metrics.negative_ratio * 100).toFixed(1)}%
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500">
                  Z-Score: {analysis.crisis_metrics.z_score >= 0 ? "+" : ""}
                  {analysis.crisis_metrics.z_score}σ
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-panel glass-panel-hover rounded-2xl p-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>AI Rules Fired</span>
                  <ShieldCheck className="h-4 w-4 text-indigo-400" />
                </div>
                <div className="mt-1.5 font-mono text-2xl font-extrabold text-indigo-300">
                  {analysis.reasoning.fired_rules.length} / {analysis.reasoning.all_rules_evaluated.length}
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500">Forward-Chaining Engine</div>
              </motion.div>
            </div>

            {/* Animated Tab Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.24 }}
              >
                {activeTab === "overview" && (
                  <div className="space-y-6">
                    <div className="grid gap-6 lg:grid-cols-12">
                      <div className="lg:col-span-7">
                        <SentimentOrb3D
                          brand={analysis.brand}
                          brandDomain={analysis.brand_domain}
                          industry={analysis.industry}
                          netSentimentScore={analysis.crisis_metrics.net_sentiment_score}
                          crisisLevel={analysis.reasoning.crisis_level}
                          mentions={analysis.mentions}
                          aspectBreakdown={analysis.aspect_breakdown}
                          selectedMentionId={selectedMentionId}
                          onSelectMention={handleSelectMention}
                        />
                      </div>
                      <div className="lg:col-span-5">
                        <ReasoningVerdictCard
                          reasoning={analysis.reasoning}
                          crisisMetrics={analysis.crisis_metrics}
                          ensembleAlpha={analysis.ensemble_alpha}
                        />
                      </div>
                    </div>

                    <MentionsFeed
                      mentions={analysis.mentions}
                      selectedMentionId={selectedMentionId}
                      onSelectMention={handleSelectMention}
                    />
                  </div>
                )}

                {activeTab === "analytics" && (
                  <AnalyticsDashboard
                    data={analysis}
                    loading={loading}
                    onCompareCompetitors={handleCompareCompetitors}
                  />
                )}

                {activeTab === "ai-internals" && (
                  <AIInternalsTab
                    data={analysis}
                    evaluation={evaluation}
                    ontologyFrames={ontologyFrames}
                  />
                )}

                {activeTab === "algorithms" && (
                  <AlgorithmsExplainedTab data={analysis} evaluation={evaluation} />
                )}

                {activeTab === "evaluation" && (
                  <EvaluationTab data={analysis} evaluation={evaluation} />
                )}
              </motion.div>
            </AnimatePresence>
          </>
        )}
      </main>
    </div>
  );
}
