from collections import defaultdict
from typing import Dict, List


def run_forward_chaining_inference(
    brand: str,
    enriched_mentions: List[Dict],
    crisis_metrics: Dict,
    root_cause_paths: List[Dict],
) -> Dict:
    total = max(len(enriched_mentions), 1)
    nss = float(crisis_metrics["net_sentiment_score"])
    z_score = float(crisis_metrics["z_score"])
    neg_ratio = float(crisis_metrics["negative_ratio"])
    pos_ratio = float(crisis_metrics["positive_ratio"])

    aspect_counts: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"total": 0, "neg": 0, "pos": 0, "neu": 0, "score_sum": 0.0}
    )
    for m in enriched_mentions:
        lbl = m["sentiment_label"]
        sc = float(m["ensemble_score"])
        for asp in m.get("aspects", ["General Brand Perception"]):
            aspect_counts[asp]["total"] += 1
            aspect_counts[asp]["score_sum"] += sc
            if lbl == "Negative":
                aspect_counts[asp]["neg"] += 1
            elif lbl == "Positive":
                aspect_counts[asp]["pos"] += 1
            else:
                aspect_counts[asp]["neu"] += 1

    dominant_aspects = []
    for asp, st in aspect_counts.items():
        cnt = int(st["total"])
        dominant_aspects.append(
            {
                "aspect": asp,
                "count": cnt,
                "share_pct": round((cnt / total) * 100.0, 1),
                "neg_ratio": round(st["neg"] / max(cnt, 1), 3),
                "pos_ratio": round(st["pos"] / max(cnt, 1), 3),
                "avg_score": round(st["score_sum"] / max(cnt, 1), 3),
            }
        )
    dominant_aspects.sort(key=lambda x: x["count"], reverse=True)

    aspect_lookup = {d["aspect"]: d for d in dominant_aspects}
    top_neg_aspects = [d["aspect"] for d in sorted(dominant_aspects, key=lambda x: (x["neg_ratio"] * x["count"]), reverse=True) if d["neg_ratio"] >= 0.35][:3]
    top_pos_aspects = [d["aspect"] for d in sorted(dominant_aspects, key=lambda x: (x["pos_ratio"] * x["count"]), reverse=True) if d["pos_ratio"] >= 0.45][:3]

    facts = {
        "brand": brand,
        "mention_count": len(enriched_mentions),
        "net_sentiment_score": round(nss, 1),
        "z_score": round(z_score, 2),
        "negative_ratio": round(neg_ratio, 3),
        "positive_ratio": round(pos_ratio, 3),
        "dominant_aspect": dominant_aspects[0]["aspect"] if dominant_aspects else "General Brand Perception",
        "top_negative_aspects": top_neg_aspects,
        "top_positive_aspects": top_pos_aspects,
    }

    prod = aspect_lookup.get("Product Quality", {"count": 0, "neg_ratio": 0.0})
    supp = aspect_lookup.get("Customer Support", {"count": 0, "neg_ratio": 0.0})
    pric = aspect_lookup.get("Pricing & Value", {"count": 0, "neg_ratio": 0.0})
    pr_e = aspect_lookup.get("PR & Ethics", {"count": 0, "neg_ratio": 0.0})
    deliv = aspect_lookup.get("Delivery & Operations", {"count": 0, "neg_ratio": 0.0})
    innov = aspect_lookup.get("Innovation & UX", {"count": 0, "pos_ratio": 0.0})

    rule_specs = [
        ("R1", "Critical PR Crisis Detection", "z_score >= 2.0 AND negative_ratio >= 0.38", (z_score >= 2.0 and neg_ratio >= 0.38), "CRITICAL_CRISIS state triggered due to abnormal negative mention velocity.", 100),
        ("R2", "Product Quality / Defect Escalation", "Product_Quality.count >= 2 AND Product_Quality.neg_ratio >= 0.45", (prod["count"] >= 2 and prod["neg_ratio"] >= 0.45), "Hardware/product reliability defects are actively degrading brand trust.", 90),
        ("R3", "Customer Support Friction Rule", "Customer_Support.count >= 2 AND Customer_Support.neg_ratio >= 0.45", (supp["count"] >= 2 and supp["neg_ratio"] >= 0.45), "Slow warranty/refund resolution or chatbot loops are amplifying anger.", 85),
        ("R4", "Pricing & Hidden Fee Backlash", "Pricing_Value.count >= 2 AND Pricing_Value.neg_ratio >= 0.40", (pric["count"] >= 2 and pric["neg_ratio"] >= 0.40), "Perceived overpricing, surge fees, or repair costs are triggering customer pushback.", 80),
        ("R5", "Regulatory / PR Controversy Signal", "PR_Ethics.count >= 1 AND PR_Ethics.neg_ratio >= 0.50", (pr_e["count"] >= 1 and pr_e["neg_ratio"] >= 0.50), "Regulatory scrutiny, executive controversy, or labor friction is creating media risk.", 88),
        ("R6", "Elevated Reputation Watch", "z_score >= 1.25 OR net_sentiment_score <= -12.0", (z_score >= 1.25 or nss <= -12.0), "Reputation trend has crossed early warning thresholds; proactive monitoring advised.", 75),
        ("R7", "Delivery & Logistics Bottleneck", "Delivery_Ops.count >= 2 AND Delivery_Ops.neg_ratio >= 0.40", (deliv["count"] >= 2 and deliv["neg_ratio"] >= 0.40), "Fulfillment delays or shipping quality issues are hurting post-order satisfaction.", 72),
        ("R8", "Strong Brand Advocacy", "net_sentiment_score >= 20.0 AND positive_ratio >= 0.48 AND z_score < 1.25", (nss >= 20.0 and pos_ratio >= 0.48 and z_score < 1.25), "Healthy positive advocacy dominates public discourse with low crisis volatility.", 70),
        ("R9", "Innovation & Ecosystem Moat", "Innovation_UX.count >= 2 AND Innovation_UX.pos_ratio >= 0.50", (innov["count"] >= 2 and innov["pos_ratio"] >= 0.50), "Product features, AI/UX polish, and ecosystem design act as primary brand strengths.", 65),
        ("R10", "Polarized Brand Perception", "positive_ratio >= 0.30 AND negative_ratio >= 0.30", (pos_ratio >= 0.30 and neg_ratio >= 0.30), "Audience is sharply divided—strong product fans coexist with vocal critics.", 60),
    ]

    all_rules, fired_rules, fired_ids = [], [], set()
    for rid, rname, expr, matched, derived, prio in rule_specs:
        item = {
            "rule_id": rid,
            "rule_name": rname,
            "condition_expression": expr,
            "matched": bool(matched),
            "derived_fact": derived,
            "priority": prio,
        }
        all_rules.append(item)
        if matched:
            fired_rules.append(item)
            fired_ids.add(rid)

    if "R1" in fired_ids:
        crisis_level, overall_verdict = "CRITICAL_CRISIS", f"High-Risk PR Crisis Detected for {brand}"
    elif "R6" in fired_ids and (len(fired_ids & {"R2", "R3", "R4", "R5"}) >= 1):
        crisis_level, overall_verdict = "ELEVATED", f"Negative Sentiment Risk & Elevated Watch for {brand}"
    elif "R6" in fired_ids or (len(fired_ids & {"R2", "R3", "R5"}) >= 2):
        crisis_level, overall_verdict = "WATCH", f"Cautious / Under Watch Sentiment for {brand}"
    elif "R8" in fired_ids:
        crisis_level, overall_verdict = "NORMAL", f"Strong Positive Brand Reputation for {brand}"
    elif "R10" in fired_ids:
        crisis_level = "WATCH" if nss < 0 else "NORMAL"
        overall_verdict = f"Polarized Customer Sentiment for {brand}"
    elif nss >= 5:
        crisis_level, overall_verdict = "NORMAL", f"Moderately Positive Reputation for {brand}"
    elif nss <= -5:
        crisis_level, overall_verdict = "WATCH", f"Mildly Negative Reputation for {brand}"
    else:
        crisis_level, overall_verdict = "NORMAL", f"Balanced / Neutral Brand Standing for {brand}"

    neg_pct, pos_pct = round(neg_ratio * 100, 1), round(pos_ratio * 100, 1)
    top_chain = root_cause_paths[0] if root_cause_paths else None

    if crisis_level in ("CRITICAL_CRISIS", "ELEVATED"):
        chain_clause = (
            f" Best-First root-cause search traced the strongest negative cluster to '{top_chain['aspect']}' "
            f"(trigger: '{top_chain['trigger_keyword']}', avg polarity {top_chain['avg_sentiment']:+.2f})."
            if top_chain else ""
        )
        primary_reason = (
            f"{brand} is showing elevated reputation stress with {neg_pct}% negative mentions "
            f"(Net Sentiment Score {nss:+.1f}) and a statistical Z-score anomaly of {z_score:+.2f}σ.{chain_clause}"
        )
    elif crisis_level == "NORMAL" and nss >= 10:
        chain_clause = (
            f" Key advocacy centers on '{top_chain['aspect']}' via '{top_chain['trigger_keyword']}'."
            if top_chain and top_chain["avg_sentiment"] > 0 else ""
        )
        primary_reason = (
            f"{brand} maintains healthy public sentiment ({pos_pct}% positive vs {neg_pct}% negative, "
            f"NSS {nss:+.1f}) with stable mention velocity (Z = {z_score:+.2f}σ).{chain_clause}"
        )
    else:
        primary_reason = (
            f"{brand} reflects mixed public opinion ({pos_pct}% positive, {neg_pct}% negative; NSS {nss:+.1f}), "
            f"most heavily debated around {facts['dominant_aspect']} across tracked news and social feeds."
        )

    supporting_reasons = [r["derived_fact"] for r in fired_rules[:4]] or [
        f"Analyzed {len(enriched_mentions)} deduplicated mentions across live/cached web sources.",
        f"Dominant discussion pillar is '{facts['dominant_aspect']}'.",
    ]

    actions: List[str] = []
    if "R1" in fired_ids:
        actions.append("Activate PR crisis response room: pause scheduled promo ads and publish a transparent official statement within 4 hours.")
    if "R2" in fired_ids:
        actions.append("Issue an engineering/QA advisory addressing reported defects and announce proactive warranty coverage.")
    if "R3" in fired_ids:
        actions.append("Route high-frustration support mentions directly to human escalation agents and audit automated refund flows.")
    if "R4" in fired_ids:
        actions.append("Improve checkout/repair pricing transparency and communicate value bundles to counter fee backlash.")
    if "R5" in fired_ids:
        actions.append("Coordinate legal/PR leadership alignment to address regulatory or ethical concerns proactively.")
    if "R7" in fired_ids:
        actions.append("Audit logistics/fulfillment SLAs in high-complaint corridors and provide proactive delay notifications.")
    if "R8" in fired_ids or "R9" in fired_ids:
        actions.append("Amplify organic positive testimonials around top-performing features in upcoming brand campaigns.")
    if not actions:
        actions.append("Maintain routine weekly sentiment tracking and benchmark Share of Voice against top two competitors.")

    confidence = round(min(0.96, 0.64 + (min(len(enriched_mentions), 40) / 140.0) + (0.04 * min(len(fired_rules), 3))), 2)

    return {
        "overall_verdict": overall_verdict,
        "crisis_level": crisis_level,
        "confidence": confidence,
        "primary_reason": primary_reason,
        "supporting_reasons": supporting_reasons,
        "recommended_actions": actions[:4],
        "dominant_aspects": dominant_aspects[:6],
        "working_memory_facts": facts,
        "fired_rules": fired_rules,
        "all_rules_evaluated": all_rules,
    }
