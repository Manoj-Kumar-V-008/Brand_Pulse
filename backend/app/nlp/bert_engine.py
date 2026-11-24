import os
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

_CONTEXTUAL_SEED_DATA: List[Tuple[str, int]] = [
    ("cracked back glass and absurd repair price without warranty", 0),
    ("order arrived 50 minutes late cold and spilled everywhere", 0),
    ("ai chatbot refused a proper refund and gave a tiny coupon", 0),
    ("green vertical line appeared on screen after software update", 0),
    ("service center asked for a huge replacement fee unacceptable", 0),
    ("company recalls over 200000 vehicles for camera safety glitch", 0),
    ("app crashed during limited drop and bots took everything", 0),
    ("sole started peeling after three months quality control slipped", 0),
    ("platform fee keeps creeping up pricing feels deceptive now", 0),
    ("wrong item delivered and impossible to reach a human agent", 0),
    ("too much preinstalled bloatware and sponsored apps", 0),
    ("waiting five weeks for replacement bumper painful experience", 0),
    ("regulators warn brand over antitrust fee restrictions", 0),
    ("controversial executive tweets hurting brand perception", 0),
    ("delivery delays and uneven trim gaps spark customer complaints", 0),
    ("phantom braking in heavy rain remains a safety concern", 0),
    ("stale veggies delivered and refund took three chats", 0),
    ("gig worker unions protest payout structure during monsoon", 0),
    ("membership hiked fees while shrinking free delivery radius", 0),
    ("shipping stuck in customs for ten days with vague tracking", 0),
    ("not good at all completely disappointed with customer support", 0),
    ("overheating issue ruined the flagship phone experience", 0),
    ("app feels cluttered with annoying promo popups", 0),
    ("service appointment wait times are getting frustrating", 0),
    ("privacy data leak raises serious security concerns", 0),
    ("terrible outage left users locked out of accounts for hours", 0),
    ("charging extra for basic storage tiers feels overpriced", 0),
    ("phantom wiper activation still annoys me fix sensor bugs", 0),
    ("intensifying price war and shrinking profit margins", 0),
    ("restaurant partners raise concerns over rising commissions", 0),
    ("solid incremental update nothing revolutionary just reliable", 1),
    ("one year ownership low cost decent software average interior", 1),
    ("analysts debate robotaxi timeline amid regulatory reviews", 1),
    ("launches new mid range smartphone lineup across india", 1),
    ("audio quality is crisp though design feels derivative", 1),
    ("food arrived on time tasted fine menu prices slightly higher", 1),
    ("expands quick food service to four hundred towns", 1),
    ("standard late night snack order packaging intact nothing unusual", 1),
    ("fabric is soft fits true to size standard athletic wear", 1),
    ("overhauls wholesale retail partnerships to win shelf space", 1),
    ("invests in athlete storytelling campaigns ahead of season", 1),
    ("partners with regional chains for combo meal options", 1),
    ("company announced quarterly earnings scheduled for next week", 1),
    ("neutral take on the latest tablet hardware refresh", 1),
    ("mixed reactions from early adopters praising privacy but noting gaps", 1),
    ("hardware is decent though browser api compatibility lags slightly", 1),
    ("released routine maintenance patch version two point four", 1),
    ("industry observers monitor unit economics of rapid delivery", 1),
    ("store opened a new branch in bengaluru tech park today", 1),
    ("comparing specifications between flagship models this quarter", 1),
    ("battery life tops benchmarks with zero thermal throttling impressing creators", 2),
    ("blown away by camera stabilization and crisp video quality seamless ecosystem", 2),
    ("unified memory remains unmatched massive win for ai developers", 2),
    ("software update fixed battery drain phone stays cool and super smooth", 2),
    ("hearing health feature is genuinely awesome crystal clear sound", 2),
    ("expands india manufacturing footprint with record exports", 2),
    ("customer support resolved warranty replacement in thirty minutes top service", 2),
    ("quarterly revenue beat analyst expectations driven by strong services growth", 2),
    ("supercharger network is unbeatable worked seamlessly zero range anxiety", 2),
    ("cabin quietness acoustic glass and responsive ui feel genuinely premium", 2),
    ("energy storage division hits record deployment with strong reliability", 2),
    ("anti reflective display praised in lab tests industry leading", 2),
    ("live translate saved me on business trip super useful and accurate", 2),
    ("customization modules make phone feel like workstation love flexibility", 2),
    ("oled tv wins top ratings for gaming latency and vibrant brightness", 2),
    ("zoom camera is unreal at concerts crisp photos worth every rupee", 2),
    ("delivered hot dosas in eleven minutes insanely smooth experience", 2),
    ("free delivery membership saved me a lot reliable live map tracking", 2),
    ("delivery partner was polite arrived ahead of time in heavy rain", 2),
    ("support agent refunded missing item within two minutes pleasantly surprised", 2),
    ("dineout offers made team outing super affordable clean ui", 2),
    ("running shoes receive rave reviews for responsive cushioning and grip", 2),
    ("clocked a new personal best unbelievable energy return featherlight fit", 2),
    ("sustainability collection cuts carbon footprint with breathable comfort", 2),
    ("warranty return honored smoothly received full credit within four days", 2),
    ("classic design never misses clean comfortable pairs with every outfit", 2),
    ("impressive backend logistics scalability handling peak traffic smoothly", 2),
    ("memory chip profits rebound on surging ai server demand", 2),
    ("healthier meal filters and transparent nutrition labels welcomed by users", 2),
    ("instamart delivered essentials in nine minutes most used app", 2),
]


class ContextualBertEngine:
    MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def __init__(self) -> None:
        self._hf_pipeline = None
        self._hf_attempted = False
        self.backend_label = "Contextual-ML (Bigram LR)"

        texts = [t for t, _ in _CONTEXTUAL_SEED_DATA]
        labels = [y for _, y in _CONTEXTUAL_SEED_DATA]
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=3500)
        X = self._vectorizer.fit_transform(texts)
        self._clf = LogisticRegression(C=2.5, max_iter=500, random_state=42)
        self._clf.fit(X, labels)

    def _try_load_roberta(self) -> None:
        if self._hf_attempted:
            return
        self._hf_attempted = True
        mode = os.getenv("ENABLE_BERT", "auto").strip().lower()
        if mode in ("0", "false", "no", "off"):
            return
        try:
            import torch  # type: ignore
            from transformers import pipeline  # type: ignore

            device = 0 if torch.cuda.is_available() else -1
            self._hf_pipeline = pipeline(
                "sentiment-analysis",
                model=self.MODEL_ID,
                tokenizer=self.MODEL_ID,
                top_k=None,
                truncation=True,
                max_length=256,
                device=device,
            )
            hw = "CUDA-GPU" if device == 0 else "CPU"
            self.backend_label = f"RoBERTa-Transformer ({hw})"
        except Exception:
            self._hf_pipeline = None
            self.backend_label = "Contextual-ML (Bigram LR)"

    def score_batch(self, texts: List[str], allow_transformer: bool = True) -> List[float]:
        if not texts:
            return []
        if allow_transformer:
            self._try_load_roberta()

        if self._hf_pipeline is not None:
            try:
                outputs = self._hf_pipeline(texts, batch_size=16)
                scores: List[float] = []
                for item in outputs:
                    label_map = {entry["label"].lower(): float(entry["score"]) for entry in item}
                    p_pos = label_map.get("positive", label_map.get("label_2", 0.0))
                    p_neg = label_map.get("negative", label_map.get("label_0", 0.0))
                    scores.append(round(p_pos - p_neg, 4))
                return scores
            except Exception:
                pass

        X = self._vectorizer.transform(texts)
        probs = self._clf.predict_proba(X)
        return [round(float(np.tanh(float(row[2] - row[0]) * 1.45)), 4) for row in probs]
