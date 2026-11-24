import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.ai_core.evaluation import run_benchmark_and_optimize
from app.ai_core.ontology import get_ontology_summary
from app.ai_core.reasoning_engine import run_forward_chaining_inference
from app.ai_core.search_algorithms import run_best_first_root_cause_search
from app.analytics.competitors import get_brand_meta, resolve_brand_competitors
from app.analytics.metrics import (
    compute_crisis_and_timeseries,
    compute_share_of_voice,
    inject_simulated_crisis_mentions,
)
from app.data_pipeline.fetcher import fetch_brand_mentions_hybrid
from app.data_pipeline.preprocessor import preprocess_mentions
from app.database import get_cached_mentions, init_db, list_known_brands
from app.nlp.ensemble import SentimentEnsemble
from app.schemas import AnalyzeResponse, BrandSummary, EvaluationResponse

app = FastAPI(
    title="BrandPulse 3D — Brand Sentiment & Reputation Monitor API",
    description="Hybrid Data Science (Pandas + VADER + RoBERTa), Data Analytics (Domain-Aware SoV + Z-score PR Crisis), and AI (Hill-Climbing + Best-First Search + Forward-Chaining KRR).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensemble_engine = SentimentEnsemble()


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    run_benchmark_and_optimize(ensemble_engine)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "nlp_backend": ensemble_engine.backend_description,
        "ensemble_alpha": ensemble_engine.alpha,
        "decision_threshold": ensemble_engine.threshold,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/brands", response_model=List[BrandSummary])
def get_brands():
    init_db()
    return list_known_brands()


@app.get("/api/competitors")
def get_suggested_competitors(brand: str = Query(..., min_length=1, max_length=60)):
    industry, comps = resolve_brand_competitors(brand)
    meta = get_brand_meta(brand)
    return {
        "brand": brand.strip(),
        "industry": industry,
        "domain": meta["domain"],
        "competitors": comps,
    }


@app.get("/api/ontology")
def get_ontology():
    return {"frames": get_ontology_summary()}


@app.get("/api/evaluation", response_model=EvaluationResponse)
def get_evaluation(refresh: bool = Query(default=False)):
    return run_benchmark_and_optimize(ensemble_engine, force_refresh=refresh)


async def _analyze_single_competitor(comp: str, live: bool) -> Dict:
    # Use cached data if already populated (>= 6 mentions) for speed; otherwise fetch live!
    cached = get_cached_mentions(comp, limit=35)
    should_fetch_live = live and len(cached) < 6
    comp_raw, _ = await fetch_brand_mentions_hybrid(
        comp, force_live=should_fetch_live, max_total=35
    )
    comp_clean, _ = preprocess_mentions(comp_raw)
    comp_enriched = ensemble_engine.analyze_mentions(comp_clean, allow_transformer=False)
    comp_metrics, _, _ = compute_crisis_and_timeseries(comp_enriched, simulated=False)
    return {
        "brand": comp,
        "mentions_count": len(comp_enriched),
        "net_sentiment": comp_metrics["net_sentiment_score"],
        "positive_ratio": comp_metrics["positive_ratio"],
        "negative_ratio": comp_metrics["negative_ratio"],
        "crisis_level": comp_metrics["severity_label"],
    }


@app.get("/api/analyze", response_model=AnalyzeResponse)
async def analyze_brand(
    brand: str = Query(..., min_length=1, max_length=60),
    competitors: Optional[str] = Query(default=None),
    live: bool = Query(default=True),
    simulate_crisis: bool = Query(default=False),
    use_transformer: bool = Query(default=True),
):
    init_db()
    clean_brand = brand.strip()
    brand_meta = get_brand_meta(clean_brand)

    # 1. Hybrid Data Collection
    raw_mentions, data_mode = await fetch_brand_mentions_hybrid(clean_brand, force_live=live)
    if simulate_crisis:
        raw_mentions = inject_simulated_crisis_mentions(clean_brand, raw_mentions)
        data_mode = "SIMULATED_CRISIS"

    # 2. Data Science Preprocessing (Pandas)
    cleaned_mentions, cleaning_stats = preprocess_mentions(raw_mentions)

    # 3. NLP Ensemble (VADER + RoBERTa/Contextual ML)
    enriched_mentions = ensemble_engine.analyze_mentions(
        cleaned_mentions, allow_transformer=use_transformer
    )

    # 4. Data Analytics (Net Sentiment + Z-Score PR Crisis + Time-Series)
    crisis_metrics, time_series, aspect_breakdown = compute_crisis_and_timeseries(
        enriched_mentions, simulated=simulate_crisis
    )

    # 5. AI Search (Best-First Root-Cause Graph Search)
    root_cause_paths = run_best_first_root_cause_search(clean_brand, enriched_mentions, max_paths=5)

    # 6. KRR (Forward-Chaining Production Rule Engine)
    reasoning = run_forward_chaining_inference(
        clean_brand, enriched_mentions, crisis_metrics, root_cause_paths
    )

    # 7. Domain-Aware Share of Voice (SoV) — Only True Industry Competitors!
    industry, default_comps = resolve_brand_competitors(clean_brand, cleaned_mentions)
    if competitors:
        comp_list = [
            c.strip()
            for c in competitors.split(",")
            if c.strip() and c.strip().lower() != clean_brand.lower()
        ][:4]
    else:
        comp_list = default_comps[:3]

    sov_inputs = [
        {
            "brand": clean_brand,
            "mentions_count": len(enriched_mentions),
            "net_sentiment": crisis_metrics["net_sentiment_score"],
            "positive_ratio": crisis_metrics["positive_ratio"],
            "negative_ratio": crisis_metrics["negative_ratio"],
            "crisis_level": reasoning["crisis_level"],
        }
    ]

    if comp_list:
        comp_results = await asyncio.gather(
            *[_analyze_single_competitor(comp, live=live) for comp in comp_list],
            return_exceptions=True,
        )
        for res in comp_results:
            if isinstance(res, dict):
                sov_inputs.append(res)

    return {
        "brand": clean_brand,
        "industry": industry,
        "brand_domain": brand_meta["domain"],
        "competitors_used": comp_list,
        "data_mode": data_mode,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "nlp_backend": ensemble_engine.backend_description,
        "ensemble_alpha": ensemble_engine.alpha,
        "cleaning_stats": cleaning_stats,
        "crisis_metrics": crisis_metrics,
        "reasoning": reasoning,
        "root_cause_paths": root_cause_paths,
        "time_series": time_series,
        "share_of_voice": compute_share_of_voice(sov_inputs),
        "aspect_breakdown": aspect_breakdown,
        "mentions": enriched_mentions,
    }
