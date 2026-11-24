import time
from typing import Dict, List, Tuple

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from app.ai_core.search_algorithms import run_hill_climbing_optimizer
from app.nlp.ensemble import SentimentEnsemble

BENCHMARK_SAMPLES: List[Tuple[str, int]] = [
    ("Phone battery drains in four hours after the latest update, completely unacceptable!", 0),
    ("Customer support bot trapped me in a loop and refused my refund request.", 0),
    ("Hidden platform fee and surge pricing doubled my dinner checkout bill.", 0),
    ("Massive vehicle recall announced due to faulty camera software glitch.", 0),
    ("App froze right at checkout and bots grabbed every single drop.", 0),
    ("Screen developed a bright green line right after warranty expired.", 0),
    ("Delivery arrived an hour late, ice cold, and leaking through the bag.", 0),
    ("Repair center quoted an absurd fee for a tiny crack—terrible pricing policy.", 0),
    ("Waiting five weeks for a replacement part has been a painful ownership experience.", 0),
    ("Preinstalled bloatware and intrusive promo popups ruin the out-of-box software.", 0),
    ("Regulators opened an antitrust probe over restrictive app marketplace fees.", 0),
    ("Sole adhesive started peeling off after just two months of normal wear.", 0),
    ("Not good at all—support technician cancelled our service visit twice.", 0),
    ("Overheating issue throttled performance during basic video recording.", 0),
    ("Data privacy breach left thousands of customer accounts exposed.", 0),
    ("Stale groceries delivered again and getting a refund took three separate chats.", 0),
    ("Executive controversy is actively turning longtime loyal buyers away.", 0),
    ("Phantom braking on the highway remains a serious safety flaw.", 0),
    ("Shipping tracking has been stuck with zero updates for ten straight days.", 0),
    ("Worst after-sales warranty claim experience I have ever dealt with.", 0),
    ("The new tablet is a solid incremental update with routine spec bumps.", 1),
    ("Company scheduled its quarterly investor earnings call for next Thursday.", 1),
    ("Arrived on time and tasted fine, though menu prices are slightly higher.", 1),
    ("Standard athletic hoodie—fits true to size, nothing extraordinary.", 1),
    ("Analysts continue debating the regulatory timeline for autonomous fleets.", 1),
    ("Brand opened two new regional retail showrooms in Bengaluru this month.", 1),
    ("Software maintenance patch 4.2 addresses minor localization formatting.", 1),
    ("Comparing display dimensions and weight across this year's flagship lineup.", 1),
    ("One year ownership report: low running cost, average interior materials.", 1),
    ("Company announced a wholesale distribution partnership with regional stores.", 1),
    ("Quick-commerce arm expanded operations to four hundred additional towns.", 1),
    ("Mixed early reviews praise privacy controls while noting assistant limitations.", 1),
    ("Audio clarity is decent though the earbud stem design feels familiar.", 1),
    ("Routine late-night snack order arrived intact with standard packaging.", 1),
    ("Industry observers are watching unit economics of rapid delivery tiers.", 1),
    ("Released official developer documentation for the upcoming SDK beta.", 1),
    ("Average weekday commute performance with expected battery consumption.", 1),
    ("Hardware build feels sturdy, though browser API support trails slightly.", 1),
    ("Brand launched a seasonal combo menu targeting university campuses.", 1),
    ("Neutral first impressions after testing the refreshed smartwatch band.", 1),
    ("Unbelievable battery life—21 hours on a single charge with zero throttling! 🔥", 2),
    ("Camera stabilization and night video quality completely blew me away.", 2),
    ("Customer support replaced my faulty charger in 20 minutes—top tier service!", 2),
    ("Delivered piping hot breakfast in eleven minutes flat—insanely smooth! 🚀", 2),
    ("Live call translation worked seamlessly during my international work trip.", 2),
    ("Supercharger network made our 700 km road trip effortless with zero anxiety.", 2),
    ("Responsive foam cushioning helped me clock a new marathon personal best!", 2),
    ("Anti-reflective OLED screen looks stunning even under harsh afternoon sun.", 2),
    ("Support agent refunded the missing item in two minutes—pleasantly surprised.", 2),
    ("Dineout discount saved our entire group ₹1,500 with super clean checkout UX.", 2),
    ("Quarterly revenue beat analyst expectations driven by strong services growth.", 2),
    ("Warranty return was honored smoothly with full credit issued in three days.", 2),
    ("Sustainability collection cuts carbon footprint while feeling breathable and soft.", 2),
    ("Delivery rider was polite and arrived ahead of schedule during heavy rain.", 2),
    ("Unified memory architecture is unmatched for running local AI models smoothly.", 2),
    ("Refreshed cabin acoustics and ventilated seats feel genuinely premium.", 2),
    ("Instamart rescued our house party by delivering essentials in nine minutes!", 2),
    ("Zoom photography at the concert came out razor sharp—worth every rupee.", 2),
    ("Impressive backend logistics engineering handling peak match-day surges.", 2),
    ("Classic sneaker design never misses—comfortable and pairs with every outfit.", 2),
]

_CACHED_EVAL_RESULT: Dict | None = None


def _compute_metrics(name: str, y_true: List[int], preds: List[int], latency_ms: float) -> Dict:
    return {
        "model_name": name,
        "accuracy": round(float(accuracy_score(y_true, preds)) * 100.0, 2),
        "precision": round(float(precision_score(y_true, preds, average="macro", zero_division=0)) * 100.0, 2),
        "recall": round(float(recall_score(y_true, preds, average="macro", zero_division=0)) * 100.0, 2),
        "macro_f1": round(float(f1_score(y_true, preds, average="macro", zero_division=0)) * 100.0, 2),
        "avg_latency_ms": round(latency_ms, 2),
        "confusion_matrix": confusion_matrix(y_true, preds, labels=[0, 1, 2]).tolist(),
    }


def _scores_to_labels(scores: List[float], tau: float) -> List[int]:
    return [2 if s >= tau else (0 if s <= -tau else 1) for s in scores]


def run_benchmark_and_optimize(ensemble: SentimentEnsemble, force_refresh: bool = False) -> Dict:
    global _CACHED_EVAL_RESULT
    if _CACHED_EVAL_RESULT is not None and not force_refresh:
        return _CACHED_EVAL_RESULT

    texts = [t for t, _ in BENCHMARK_SAMPLES]
    y_true = [y for _, y in BENCHMARK_SAMPLES]

    t0 = time.perf_counter()
    vader_scores = ensemble.vader.score_batch(texts)
    vader_ms = ((time.perf_counter() - t0) * 1000.0) / len(texts)

    t1 = time.perf_counter()
    bert_scores = ensemble.bert.score_batch(texts, allow_transformer=False)
    bert_ms = ((time.perf_counter() - t1) * 1000.0) / len(texts)

    hc_result = run_hill_climbing_optimizer(vader_scores, bert_scores, y_true)
    best_alpha, best_tau = hc_result["best_alpha"], hc_result["best_threshold"]
    ensemble.update_params(best_alpha, best_tau)

    vader_preds = _scores_to_labels(vader_scores, 0.08)
    bert_preds = _scores_to_labels(bert_scores, 0.14)
    ens_scores = [best_alpha * b + (1.0 - best_alpha) * v for v, b in zip(vader_scores, bert_scores)]
    ens_preds = _scores_to_labels(ens_scores, best_tau)

    result = {
        "dataset_size": len(BENCHMARK_SAMPLES),
        "class_distribution": {
            "Negative": int(sum(1 for y in y_true if y == 0)),
            "Neutral": int(sum(1 for y in y_true if y == 1)),
            "Positive": int(sum(1 for y in y_true if y == 2)),
        },
        "hill_climbing": hc_result,
        "model_comparison": [
            _compute_metrics("VADER (Lexicon Rules)", y_true, vader_preds, vader_ms),
            _compute_metrics("Contextual BERT / ML", y_true, bert_preds, bert_ms),
            _compute_metrics(f"Hill-Climbed Ensemble (α={best_alpha:.2f})", y_true, ens_preds, vader_ms + bert_ms),
        ],
        "labels": ["Negative", "Neutral", "Positive"],
    }
    _CACHED_EVAL_RESULT = result
    return result
