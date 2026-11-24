import re
from typing import Dict, List, Tuple

BRAND_ASPECT_ONTOLOGY: Dict[str, Dict] = {
    "Product Quality": {
        "frame_id": "FRAME_PROD_QUAL",
        "description": "Hardware reliability, durability, defects, recalls, display, battery, or physical quality.",
        "severity_weight": 1.35,
        "keywords": [
            "battery", "camera", "display", "screen", "green line", "defect", "recall",
            "overheating", "peeling", "glue", "broken", "glitch", "bug", "crash", "froze",
            "panel", "build quality", "durable", "cushioning", "smooth", "reliable", "stale",
            "spilled", "cold", "hardware", "quality", "sensor", "wiper", "braking", "sound",
            "zoom", "audio", "ssd", "chip", "foam", "fit", "thermal"
        ],
        "causal_impact": "Direct impact on customer churn, warranty costs, and viral negative reviews.",
    },
    "Customer Support": {
        "frame_id": "FRAME_CUST_SUPP",
        "description": "Refunds, warranty replacements, service centers, chatbots, and human agent resolution.",
        "severity_weight": 1.25,
        "keywords": [
            "support", "refund", "warranty", "service center", "chatbot", "agent", "bot",
            "replacement", "technician", "claim", "customer service", "appointment",
            "wait time", "resolved", "after-sales", "helpline", "return", "credited", "coupon"
        ],
        "causal_impact": "Amplifies minor product issues into public social media escalations.",
    },
    "Pricing & Value": {
        "frame_id": "FRAME_PRICING",
        "description": "Product pricing, hidden checkout fees, surge charges, repair bills, and membership value.",
        "severity_weight": 1.15,
        "keywords": [
            "price", "pricing", "fee", "fees", "overpriced", "expensive", "surge",
            "platform fee", "cost", "bill", "discount", "affordable", "margin", "commission",
            "surcharge", "membership", "worth", "value", "rupee", "₹", "$", "steep", "hidden"
        ],
        "causal_impact": "Drives price-elasticity switching toward competing brands.",
    },
    "Delivery & Operations": {
        "frame_id": "FRAME_DELIVERY",
        "description": "Shipping times, quick-commerce speed, logistics routing, rider experience, and delays.",
        "severity_weight": 1.10,
        "keywords": [
            "delivery", "delivered", "shipping", "late", "delay", "delays", "delayed",
            "rider", "tracking", "customs", "10-minute", "15-minute", "11 minutes",
            "9 minutes", "minutes", "logistics", "routing", "dark store", "stockout", "eta",
            "bolt", "instamart", "blinkit", "supercharger"
        ],
        "causal_impact": "Directly shapes repeat purchase frequency in logistics-heavy brands.",
    },
    "Privacy & Security": {
        "frame_id": "FRAME_PRIVACY",
        "description": "Data protection, security updates, bot protection, account safety, and compliance.",
        "severity_weight": 1.40,
        "keywords": [
            "privacy", "security", "breach", "leak", "hack", "bots", "bot", "scam",
            "fraud", "data", "tracking", "encryption", "safety", "unsafe", "vulnerable"
        ],
        "causal_impact": "Triggers severe institutional trust erosion and regulatory penalties.",
    },
    "PR & Ethics": {
        "frame_id": "FRAME_PR_ETHICS",
        "description": "Antitrust scrutiny, executive controversy, labor protests, sustainability, and brand image.",
        "severity_weight": 1.45,
        "keywords": [
            "antitrust", "regulators", "regulatory", "controversy", "controversial",
            "protest", "union", "lawsuit", "boycott", "scandal", "sustainability",
            "carbon", "ethics", "leadership", "executive", "pr", "scrutiny", "fine", "ban"
        ],
        "causal_impact": "Causes high-velocity media amplification and rapid PR crisis spikes.",
    },
    "Innovation & UX": {
        "frame_id": "FRAME_INNOV_UX",
        "description": "AI features, software ecosystem, design polish, app usability, and developer experience.",
        "severity_weight": 1.05,
        "keywords": [
            "ai", "intelligence", "ux", "ui", "ecosystem", "update", "feature", "features",
            "customization", "bloatware", "cluttered", "popups", "design", "app", "software",
            "webgl", "3d", "translate", "silicon", "llm", "fsd", "autopilot", "robotaxi", "dex"
        ],
        "causal_impact": "Differentiates long-term brand loyalty and organic word-of-mouth advocacy.",
    },
}


def extract_aspects_and_keywords(text: str) -> Tuple[List[str], List[str]]:
    lowered = text.lower()
    matched_aspects: List[str] = []
    matched_keywords: List[str] = []

    for aspect_name, frame in BRAND_ASPECT_ONTOLOGY.items():
        aspect_hits: List[str] = []
        for kw in frame["keywords"]:
            if len(kw) <= 2:
                if kw in ("₹", "$"):
                    if kw in lowered:
                        aspect_hits.append(kw)
                elif re.search(rf"\b{re.escape(kw)}\b", lowered):
                    aspect_hits.append(kw)
            else:
                if re.search(rf"\b{re.escape(kw)}", lowered):
                    aspect_hits.append(kw)
        if aspect_hits:
            matched_aspects.append(aspect_name)
            for h in aspect_hits[:3]:
                if h not in matched_keywords:
                    matched_keywords.append(h)

    if not matched_aspects:
        matched_aspects.append("General Brand Perception")

    return matched_aspects[:3], matched_keywords[:6]


def build_mention_reason_snippet(
    sentiment_label: str,
    ensemble_score: float,
    vader_score: float,
    bert_score: float,
    aspects: List[str],
    keywords: List[str],
) -> str:
    primary_aspect = aspects[0] if aspects else "General Brand Perception"
    kw_part = f" (cues: {', '.join(keywords[:3])})" if keywords else ""

    agreement = "Both VADER and contextual model agree"
    if (vader_score >= 0.05 and bert_score <= -0.05) or (vader_score <= -0.05 and bert_score >= 0.05):
        agreement = "Contextual model overrode surface lexicon tone"

    if sentiment_label == "Negative":
        return f"Negative signal on {primary_aspect}{kw_part}. {agreement} (score {ensemble_score:+.2f})."
    if sentiment_label == "Positive":
        return f"Positive advocacy around {primary_aspect}{kw_part}. {agreement} (score {ensemble_score:+.2f})."
    return f"Balanced or informational mention on {primary_aspect}{kw_part} (score {ensemble_score:+.2f})."


def get_ontology_summary() -> List[Dict]:
    return [
        {
            "aspect": name,
            "frame_id": frame["frame_id"],
            "description": frame["description"],
            "severity_weight": frame["severity_weight"],
            "sample_triggers": frame["keywords"][:8],
            "causal_impact": frame["causal_impact"],
        }
        for name, frame in BRAND_ASPECT_ONTOLOGY.items()
    ]
