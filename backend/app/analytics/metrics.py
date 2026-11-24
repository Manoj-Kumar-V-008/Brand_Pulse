from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np

from app.analytics.competitors import get_brand_meta


def inject_simulated_crisis_mentions(brand: str, raw_mentions: List[Dict]) -> List[Dict]:
    now_iso = datetime.now(timezone.utc).isoformat()
    synthetic_spike = [
        {"id": f"sim_crisis_1_{brand.lower()}", "brand": brand, "source": "Bluesky", "author": "@viral_alert.bsky.social", "title": f"BREAKING: Widespread {brand} service outage & defective update trending", "text": f"Thousands of {brand} customers reporting sudden crashes, overheating, and broken checkout after today's rollout. Customer support completely unreachable! 😡", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_2_{brand.lower()}", "brand": brand, "source": "Google News", "author": "TechWire India", "title": f"Consumer watchdog questions {brand} over mounting refund delays and fee backlash", "text": f"Regulators issued a formal notice to {brand} following a surge of viral complaints citing refused refunds, hidden pricing surcharges, and unresponsive chatbot loops.", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_3_{brand.lower()}", "brand": brand, "source": "Bluesky", "author": "@angry_buyer.bsky.social", "title": f"Cancelling my {brand} subscription immediately", "text": f"Worst experience ever with {brand}. Defective product, absurd repair bill, and zero warranty support. Switching to a competitor today!", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_4_{brand.lower()}", "brand": brand, "source": "Hacker News", "author": "sec_researcher", "title": f"Security & privacy concerns flagged in latest {brand} release", "text": f"Independent researchers uncovered a concerning data leak vulnerability and unpatched crash bug in {brand}'s consumer platform.", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_5_{brand.lower()}", "brand": brand, "source": "Bluesky", "author": "@metro_consumer.bsky.social", "title": f"{brand} delivery delays & quality drop sparking boycott hashtag", "text": f"Multiple delayed orders, damaged packaging, and deceptive fees—#Boycott{brand.replace(' ', '')} is now trending across social feeds.", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_6_{brand.lower()}", "brand": brand, "source": "Google News", "author": "MarketWatch", "title": f"{brand} faces PR controversy as social sentiment plunges", "text": f"Brand reputation metrics dropped sharply overnight amid mounting complaints over product defects and regulatory scrutiny.", "url": "", "published_at": now_iso},
        {"id": f"sim_crisis_7_{brand.lower()}", "brand": brand, "source": "Bluesky", "author": "@tech_critic.bsky.social", "title": f"Unacceptable quality control failure at {brand}", "text": f"My replacement unit also arrived defective and customer service refused escalation to a human agent. Completely unacceptable!", "url": "", "published_at": now_iso},
    ]
    return synthetic_spike + list(raw_mentions)


def compute_crisis_and_timeseries(
    enriched_mentions: List[Dict],
    simulated: bool = False,
) -> Tuple[Dict, List[Dict], List[Dict]]:
    total = len(enriched_mentions)
    if total == 0:
        return {
            "z_score": 0.0, "negative_ratio": 0.0, "positive_ratio": 0.0, "neutral_ratio": 0.0,
            "net_sentiment_score": 0.0, "baseline_neg_mean": 0.0, "baseline_neg_std": 1.0,
            "is_crisis": False, "severity_label": "NORMAL", "simulated": simulated,
        }, [], []

    pos_cnt = sum(1 for m in enriched_mentions if m["sentiment_label"] == "Positive")
    neg_cnt = sum(1 for m in enriched_mentions if m["sentiment_label"] == "Negative")
    neu_cnt = total - pos_cnt - neg_cnt

    pos_ratio, neg_ratio, neu_ratio = pos_cnt / total, neg_cnt / total, neu_cnt / total
    nss = round((pos_ratio - neg_ratio) * 100.0, 2)

    buckets: Dict[str, Dict[str, int]] = defaultdict(lambda: {"pos": 0, "neu": 0, "neg": 0, "total": 0})
    for m in enriched_mentions:
        date_str = str(m.get("published_at", ""))[:10]
        if len(date_str) != 10:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        buckets[date_str]["total"] += 1
        lbl = m["sentiment_label"]
        if lbl == "Positive":
            buckets[date_str]["pos"] += 1
        elif lbl == "Negative":
            buckets[date_str]["neg"] += 1
        else:
            buckets[date_str]["neu"] += 1

    sorted_dates = sorted(buckets.keys())
    neg_series = [float(buckets[d]["neg"]) for d in sorted_dates]

    if len(neg_series) >= 3:
        baseline_arr = np.asarray(neg_series[:-1], dtype=float)
        mu, sigma = float(np.mean(baseline_arr)), float(np.std(baseline_arr))
    else:
        mu, sigma = max(1.0, total * 0.22), max(1.0, total * 0.12)

    sigma_safe = max(sigma, 0.75)

    time_series, latest_z = [], 0.0
    for d in sorted_dates:
        b = buckets[d]
        day_nss = round(((b["pos"] - b["neg"]) / max(b["total"], 1)) * 100.0, 1)
        day_z = round((float(b["neg"]) - mu) / sigma_safe, 2)
        latest_z = day_z
        time_series.append({
            "date": d, "positive": b["pos"], "neutral": b["neu"], "negative": b["neg"],
            "total": b["total"], "net_sentiment": day_nss, "z_score": day_z, "is_anomaly": bool(day_z >= 2.0),
        })

    if len(sorted_dates) <= 2:
        ratio_z = round((neg_ratio - 0.25) / 0.12, 2)
        overall_z = max(latest_z, ratio_z) if neg_ratio > 0.30 else min(latest_z, ratio_z)
    else:
        overall_z = latest_z

    if simulated and overall_z < 2.3:
        overall_z = 2.65

    is_crisis = bool(overall_z >= 2.0 and neg_ratio >= 0.35)
    severity = "CRITICAL_CRISIS" if is_crisis else ("ELEVATED" if (overall_z >= 1.5 or nss <= -15) else ("WATCH" if (overall_z >= 1.1 or nss < 0) else "NORMAL"))

    crisis_metrics = {
        "z_score": round(float(overall_z), 2),
        "negative_ratio": round(neg_ratio, 3),
        "positive_ratio": round(pos_ratio, 3),
        "neutral_ratio": round(neu_ratio, 3),
        "net_sentiment_score": nss,
        "baseline_neg_mean": round(mu, 2),
        "baseline_neg_std": round(sigma_safe, 2),
        "is_crisis": is_crisis,
        "severity_label": severity,
        "simulated": simulated,
    }

    asp_map: Dict[str, Dict[str, int]] = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0, "total": 0})
    for m in enriched_mentions:
        lbl = m["sentiment_label"].lower()
        for asp in m.get("aspects", ["General Brand Perception"]):
            asp_map[asp][lbl] += 1
            asp_map[asp]["total"] += 1

    aspect_breakdown = [
        {"aspect": asp, **vals}
        for asp, vals in sorted(asp_map.items(), key=lambda kv: kv[1]["total"], reverse=True)
    ][:7]

    return crisis_metrics, time_series, aspect_breakdown


def compute_share_of_voice(brand_analyses: List[Dict]) -> List[Dict]:
    denom = max(sum(max(item["mentions_count"], 0) for item in brand_analyses), 1)
    results = []
    for item in brand_analyses:
        meta = get_brand_meta(item["brand"])
        results.append(
            {
                "brand": item["brand"],
                "domain": meta["domain"],
                "accent_color": meta["accent"],
                "mentions": item["mentions_count"],
                "share_pct": round((item["mentions_count"] / denom) * 100.0, 1),
                "net_sentiment": item["net_sentiment"],
                "positive_pct": round(item["positive_ratio"] * 100.0, 1),
                "negative_pct": round(item["negative_ratio"] * 100.0, 1),
                "crisis_level": item["crisis_level"],
            }
        )
    return results
