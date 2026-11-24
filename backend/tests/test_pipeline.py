import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ai_core.evaluation import run_benchmark_and_optimize
from app.ai_core.reasoning_engine import run_forward_chaining_inference
from app.ai_core.search_algorithms import run_best_first_root_cause_search
from app.analytics.metrics import compute_crisis_and_timeseries, inject_simulated_crisis_mentions
from app.data_pipeline.preprocessor import preprocess_mentions
from app.database import get_cached_mentions, init_db
from app.nlp.ensemble import SentimentEnsemble


def test_full_ai_and_data_science_pipeline():
    init_db()
    ens = SentimentEnsemble()
    eval_res = run_benchmark_and_optimize(ens, force_refresh=True)

    hc = eval_res["hill_climbing"]
    assert 0.05 <= hc["best_alpha"] <= 0.95
    assert hc["best_f1"] >= hc["initial_f1"]
    assert len(eval_res["model_comparison"]) == 3

    raw = get_cached_mentions("Zomato")
    assert len(raw) >= 10
    cleaned, stats = preprocess_mentions(raw)
    assert stats["final_count"] == len(cleaned)
    assert stats["final_count"] >= 10

    enriched = ens.analyze_mentions(cleaned, allow_transformer=False)
    crisis, ts, asp = compute_crisis_and_timeseries(enriched, simulated=False)
    paths = run_best_first_root_cause_search("Zomato", enriched)
    reasoning = run_forward_chaining_inference("Zomato", enriched, crisis, paths)

    assert len(paths) >= 1
    assert reasoning["overall_verdict"]
    assert reasoning["primary_reason"]
    assert len(reasoning["all_rules_evaluated"]) == 10

    crisis_raw = inject_simulated_crisis_mentions("Zomato", raw)
    crisis_clean, _ = preprocess_mentions(crisis_raw)
    crisis_enriched = ens.analyze_mentions(crisis_clean, allow_transformer=False)
    crisis_m, _, _ = compute_crisis_and_timeseries(crisis_enriched, simulated=True)
    crisis_paths = run_best_first_root_cause_search("Zomato", crisis_enriched)
    crisis_reasoning = run_forward_chaining_inference("Zomato", crisis_enriched, crisis_m, crisis_paths)

    assert crisis_m["is_crisis"] is True
    assert crisis_reasoning["crisis_level"] == "CRITICAL_CRISIS"
    assert any(r["rule_id"] == "R1" for r in crisis_reasoning["fired_rules"])
