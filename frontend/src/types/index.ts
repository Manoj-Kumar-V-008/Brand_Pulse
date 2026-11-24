export interface MentionItem {
  id: string;
  brand: string;
  source: string;
  author: string;
  title: string;
  text: string;
  clean_text: string;
  url: string;
  published_at: string;
  vader_score: number;
  bert_score: number;
  ensemble_score: number;
  sentiment_label: "Positive" | "Neutral" | "Negative";
  confidence: number;
  aspects: string[];
  keywords: string[];
  reason_snippet: string;
}

export interface CleaningStats {
  raw_count: number;
  duplicates_removed: number;
  short_or_spam_removed: number;
  final_count: number;
  avg_word_count: number;
  sources_breakdown: Record<string, number>;
  emoji_preserved_count: number;
}

export interface RuleTraceItem {
  rule_id: string;
  rule_name: string;
  condition_expression: string;
  matched: boolean;
  derived_fact: string;
  priority: number;
}

export interface DominantAspect {
  aspect: string;
  count: number;
  share_pct: number;
  neg_ratio: number;
  pos_ratio: number;
  avg_score: number;
}

export interface ReasoningOutput {
  overall_verdict: string;
  crisis_level: "NORMAL" | "WATCH" | "ELEVATED" | "CRITICAL_CRISIS";
  confidence: number;
  primary_reason: string;
  supporting_reasons: string[];
  recommended_actions: string[];
  dominant_aspects: DominantAspect[];
  working_memory_facts: Record<string, unknown>;
  fired_rules: RuleTraceItem[];
  all_rules_evaluated: RuleTraceItem[];
}

export interface RootCauseNode {
  node_id: string;
  node_type: "BRAND" | "ASPECT" | "KEYWORD";
  label: string;
  heuristic_score: number;
  mention_count: number;
  avg_sentiment: number;
}

export interface RootCausePath {
  aspect: string;
  trigger_keyword: string;
  path_score: number;
  frequency: number;
  avg_sentiment: number;
  explanation: string;
  nodes: RootCauseNode[];
}

export interface CrisisMetrics {
  z_score: number;
  negative_ratio: number;
  positive_ratio: number;
  neutral_ratio: number;
  net_sentiment_score: number;
  baseline_neg_mean: number;
  baseline_neg_std: number;
  is_crisis: boolean;
  severity_label: string;
  simulated: boolean;
}

export interface TimeSeriesPoint {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  total: number;
  net_sentiment: number;
  z_score: number;
  is_anomaly: boolean;
}

export interface ShareOfVoiceEntry {
  brand: string;
  domain?: string;
  accent_color?: string;
  mentions: number;
  share_pct: number;
  net_sentiment: number;
  positive_pct: number;
  negative_pct: number;
  crisis_level: string;
}

export interface AspectBreakdownRow {
  aspect: string;
  positive: number;
  neutral: number;
  negative: number;
  total: number;
}

export interface AnalyzeResponse {
  brand: string;
  industry?: string;
  brand_domain?: string;
  competitors_used?: string[];
  data_mode: string;
  fetched_at: string;
  nlp_backend: string;
  ensemble_alpha: number;
  cleaning_stats: CleaningStats;
  crisis_metrics: CrisisMetrics;
  reasoning: ReasoningOutput;
  root_cause_paths: RootCausePath[];
  time_series: TimeSeriesPoint[];
  share_of_voice: ShareOfVoiceEntry[];
  aspect_breakdown: AspectBreakdownRow[];
  mentions: MentionItem[];
}

export interface HillClimbStep {
  iteration: number;
  alpha: number;
  threshold: number;
  f1_score: number;
  accuracy: number;
  accepted: boolean;
}

export interface HillClimbResult {
  best_alpha: number;
  best_threshold: number;
  initial_f1: number;
  best_f1: number;
  improvement_pct: number;
  total_iterations: number;
  trajectory: HillClimbStep[];
}

export interface ModelMetricRow {
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  macro_f1: number;
  avg_latency_ms: number;
  confusion_matrix: number[][];
}

export interface EvaluationResponse {
  dataset_size: number;
  class_distribution: Record<string, number>;
  hill_climbing: HillClimbResult;
  model_comparison: ModelMetricRow[];
  labels: string[];
}

export interface BrandSummary {
  brand: string;
  category: string;
  is_default: boolean;
  cached_mentions: number;
  last_updated: string;
}

export interface OntologyFrame {
  aspect: string;
  frame_id: string;
  description: string;
  severity_weight: number;
  sample_triggers: string[];
  causal_impact: string;
}
