import re
from typing import List

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
    _VADER_AVAILABLE = True
except ImportError:
    SentimentIntensityAnalyzer = None
    _VADER_AVAILABLE = False

_POS_WORDS = {
    "awesome", "great", "amazing", "excellent", "love", "loved", "best", "smooth",
    "fast", "reliable", "impressive", "praise", "praised", "crisp", "unmatched",
    "top", "win", "rave", "seamless", "helpful", "clean", "premium", "affordable",
    "happy", "glad", "saved", "solid", "strong", "growth", "rally", "comfort",
    "unbelievable", "joy", "accurate", "timeless", "polite", "hot", "piping", "🔥", "👏", "🚀"
}
_NEG_WORDS = {
    "terrible", "horrible", "worst", "hate", "hated", "bad", "poor", "slow", "late",
    "broken", "glitch", "crash", "crashed", "froze", "recall", "recalls", "overpriced",
    "ridiculous", "unacceptable", "frustrating", "painful", "delayed", "delay", "delays",
    "refused", "deceptive", "spilled", "cold", "stale", "bloatware", "cluttered",
    "controversial", "controversy", "protest", "scrutiny", "peeling", "defective",
    "annoyed", "annoys", "shrink", "shrinking", "losses", "lag", "lags", "slipped",
    "absurd", "scam", "fraud", "unsafe", "outage", "angry", "disappointed", "fail", "failed"
}
_NEGATIONS = {"not", "no", "never", "neither", "nobody", "nothing", "hardly", "barely", "cant", "cannot", "dont", "didnt", "wasnt", "isnt"}


class VaderSentimentEngine:
    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer() if _VADER_AVAILABLE else None
        self.engine_name = "VADER-Official" if _VADER_AVAILABLE else "VADER-LexiconFallback"

    def score_text(self, text: str) -> float:
        if not text:
            return 0.0
        if self.analyzer is not None:
            return float(self.analyzer.polarity_scores(text)["compound"])

        tokens = re.findall(r"[a-zA-Z']+|[🔥👏🚀😡💔]", text.lower())
        score = 0.0
        for idx, tok in enumerate(tokens):
            window = set(tokens[max(0, idx - 2):idx])
            negated = bool(window & _NEGATIONS)
            if tok in _POS_WORDS:
                score += -0.65 if negated else 0.75
            elif tok in _NEG_WORDS:
                score += 0.55 if negated else -0.80
        if "!" in text:
            score *= 1.12
        norm = score / ((score * score + 4.0) ** 0.5)
        return round(float(max(-1.0, min(1.0, norm))), 4)

    def score_batch(self, texts: List[str]) -> List[float]:
        return [self.score_text(t) for t in texts]
