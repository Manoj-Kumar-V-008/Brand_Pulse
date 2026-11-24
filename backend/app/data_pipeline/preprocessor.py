import re
from typing import Dict, List, Tuple

import pandas as pd

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@[A-Za-z0-9_.-]+")
WHITESPACE_RE = re.compile(r"\s+")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]+", flags=re.UNICODE)
SPAM_PATTERNS = re.compile(
    r"(buy followers|crypto giveaway|click my bio|100% free gift card|dm for promo)",
    re.IGNORECASE,
)


def clean_mention_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = URL_RE.sub("", text)
    cleaned = MENTION_RE.sub("", cleaned)
    cleaned = cleaned.replace("&nbsp;", " ").replace("&amp;", "&")
    cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned


def preprocess_mentions(raw_mentions: List[Dict]) -> Tuple[List[Dict], Dict]:
    raw_count = len(raw_mentions)
    if raw_count == 0:
        return [], {
            "raw_count": 0,
            "duplicates_removed": 0,
            "short_or_spam_removed": 0,
            "final_count": 0,
            "avg_word_count": 0.0,
            "sources_breakdown": {},
            "emoji_preserved_count": 0,
        }

    df = pd.DataFrame(raw_mentions)
    for col in ["id", "brand", "source", "author", "title", "text", "url", "published_at"]:
        if col not in df.columns:
            df[col] = ""

    df["combined_raw"] = df.apply(
        lambda r: r["text"] if len(str(r["text"]).strip()) >= len(str(r["title"]).strip()) else f"{r['title']}. {r['text']}",
        axis=1,
    )
    df["clean_text"] = df["combined_raw"].apply(clean_mention_text)
    df["dedup_key"] = (
        df["clean_text"]
        .str.lower()
        .str.replace(r"[^a-z0-9\s]", "", regex=True)
        .str.strip()
        .str.slice(0, 95)
    )

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["dedup_key"], keep="first").copy()
    duplicates_removed = before_dedup - len(df)

    df["word_count"] = df["clean_text"].apply(lambda s: len(s.split()))
    df["is_spam"] = df["clean_text"].apply(lambda s: bool(SPAM_PATTERNS.search(s)))

    before_filter = len(df)
    df = df[(df["word_count"] >= 4) & (~df["is_spam"])].copy()
    short_or_spam_removed = before_filter - len(df)

    df = df.sort_values(by="published_at", ascending=False)

    emoji_preserved_count = int(df["clean_text"].apply(lambda s: bool(EMOJI_RE.search(s))).sum())
    avg_word_count = round(float(df["word_count"].mean()), 1) if len(df) > 0 else 0.0
    sources_breakdown = {str(k): int(v) for k, v in df["source"].value_counts().to_dict().items()}

    records = df[
        ["id", "brand", "source", "author", "title", "text", "clean_text", "url", "published_at"]
    ].to_dict(orient="records")

    stats = {
        "raw_count": int(raw_count),
        "duplicates_removed": int(duplicates_removed),
        "short_or_spam_removed": int(short_or_spam_removed),
        "final_count": int(len(records)),
        "avg_word_count": avg_word_count,
        "sources_breakdown": sources_breakdown,
        "emoji_preserved_count": emoji_preserved_count,
    }
    return records, stats
