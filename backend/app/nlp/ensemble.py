from typing import Dict, List

from app.ai_core.ontology import build_mention_reason_snippet, extract_aspects_and_keywords
from app.nlp.bert_engine import ContextualBertEngine
from app.nlp.vader_engine import VaderSentimentEngine


class SentimentEnsemble:
    def __init__(self, alpha: float = 0.70, threshold: float = 0.18) -> None:
        self.vader = VaderSentimentEngine()
        self.bert = ContextualBertEngine()
        self.alpha = alpha
        self.threshold = threshold

    def update_params(self, alpha: float, threshold: float) -> None:
        self.alpha = float(alpha)
        self.threshold = float(threshold)

    @property
    def backend_description(self) -> str:
        return f"{self.bert.backend_label} + {self.vader.engine_name}"

    def classify_score(self, score: float, threshold: float | None = None) -> str:
        tau = self.threshold if threshold is None else threshold
        if score >= tau:
            return "Positive"
        if score <= -tau:
            return "Negative"
        return "Neutral"

    def analyze_mentions(self, cleaned_mentions: List[Dict], allow_transformer: bool = True) -> List[Dict]:
        if not cleaned_mentions:
            return []

        texts = [m["clean_text"] for m in cleaned_mentions]
        vader_scores = self.vader.score_batch(texts)
        bert_scores = self.bert.score_batch(texts, allow_transformer=allow_transformer)

        enriched: List[Dict] = []
        for mention, v_score, b_score in zip(cleaned_mentions, vader_scores, bert_scores):
            ens = round(self.alpha * b_score + (1.0 - self.alpha) * v_score, 4)
            label = self.classify_score(ens)
            agreement_bonus = 0.15 if (v_score * b_score > 0) else 0.0
            confidence = round(min(0.98, max(0.52, 0.55 + abs(ens) * 0.38 + agreement_bonus)), 3)

            aspects, keywords = extract_aspects_and_keywords(mention["clean_text"])
            reason_snippet = build_mention_reason_snippet(
                label, ens, v_score, b_score, aspects, keywords
            )

            enriched.append(
                {
                    **mention,
                    "vader_score": round(v_score, 4),
                    "bert_score": round(b_score, 4),
                    "ensemble_score": ens,
                    "sentiment_label": label,
                    "confidence": confidence,
                    "aspects": aspects,
                    "keywords": keywords,
                    "reason_snippet": reason_snippet,
                }
            )
        return enriched
