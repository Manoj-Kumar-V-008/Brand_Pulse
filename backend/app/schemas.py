from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MentionItem(BaseModel):
    id: str
    brand: str
    source: str
    author: str
    title: str
    text: str
    clean_text: str
    url: str
    published_at: str
    vader_score: float
    bert_score: float
    ensemble_score: float
    sentiment_label: str
    confidence: float
    aspects: List[str]
    keywords: List[str]
    reason_snippet: str


class CleaningStats(BaseModel):
    raw_count: int
    duplicates_removed: int
    short_or_spam_removed: int
    final_count: int
    avg_word_count: float
    sources_breakdown: Dict[str, int]
    emoji_preserved_count: int


class RuleTraceItem(BaseModel):
    rule_id: str
    rule_name: str
    condition_expression: str
    matched: bool
    derived_fact: str
    priority: int


class ReasoningOutput(BaseModel):
    overall_verdict: str
    crisis_level: str
    confidence: float
    primary_reason: str
    supporting_reasons: List[str]
    recommended_actions: List[str]
    dominant_aspects: List[Dict[str, Any]]
    working_memory_facts: Dict[str, Any]
    fired_rules: List[RuleTraceItem]
    all_rules_evaluated: List[RuleTraceItem]


class RootCauseNode(BaseModel):
    node_id: str
    node_type: str
    label: str
    heuristic_score: float
    mention_count: int
    avg_sentiment: float


class RootCausePath(BaseModel):
    aspect: str
    trigger_keyword: str
    path_score: float
    frequency: int
    avg_sentiment: float
    explanation: str
    nodes: List[RootCauseNode]


class HillClimbStep(BaseModel):
    iteration: int
    alpha: float
    threshold: float
    f1_score: float
    accuracy: float
    accepted: bool


class HillClimbResult(BaseModel):
    best_alpha: float
    best_threshold: float
    initial_f1: float
    best_f1: float
    improvement_pct: float
    total_iterations: int
    trajectory: List[HillClimbStep]


class CrisisMetrics(BaseModel):
    z_score: float
    negative_ratio: float
    positive_ratio: float
    neutral_ratio: float
    net_sentiment_score: float
    baseline_neg_mean: float
    baseline_neg_std: float
    is_crisis: bool
    severity_label: str
    simulated: bool = False


class TimeSeriesPoint(BaseModel):
    date: str
    positive: int
    neutral: int
    negative: int
    total: int
    net_sentiment: float
    z_score: float
    is_anomaly: bool


class ShareOfVoiceEntry(BaseModel):
    brand: str
    domain: str = ""
    accent_color: str = "#06b6d4"
    mentions: int
    share_pct: float
    net_sentiment: float
    positive_pct: float
    negative_pct: float
    crisis_level: str


class AnalyzeResponse(BaseModel):
    brand: str
    industry: str = "General Market"
    brand_domain: str = ""
    competitors_used: List[str] = Field(default_factory=list)
    data_mode: str
    fetched_at: str
    nlp_backend: str
    ensemble_alpha: float
    cleaning_stats: CleaningStats
    crisis_metrics: CrisisMetrics
    reasoning: ReasoningOutput
    root_cause_paths: List[RootCausePath]
    time_series: List[TimeSeriesPoint]
    share_of_voice: List[ShareOfVoiceEntry]
    aspect_breakdown: List[Dict[str, Any]]
    mentions: List[MentionItem]


class ModelMetricRow(BaseModel):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    macro_f1: float
    avg_latency_ms: float
    confusion_matrix: List[List[int]]


class EvaluationResponse(BaseModel):
    dataset_size: int
    class_distribution: Dict[str, int]
    hill_climbing: HillClimbResult
    model_comparison: List[ModelMetricRow]
    labels: List[str] = Field(default_factory=lambda: ["Negative", "Neutral", "Positive"])


class BrandSummary(BaseModel):
    brand: str
    category: str
    is_default: bool
    cached_mentions: int
    last_updated: str
