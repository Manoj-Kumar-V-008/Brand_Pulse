import heapq
import math
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from app.ai_core.ontology import BRAND_ASPECT_ONTOLOGY


def _score_to_class(scores: np.ndarray, threshold: float) -> np.ndarray:
    preds = np.ones(len(scores), dtype=int)
    preds[scores >= threshold] = 2
    preds[scores <= -threshold] = 0
    return preds


def run_hill_climbing_optimizer(
    vader_scores: List[float],
    bert_scores: List[float],
    true_labels: List[int],
    initial_alpha: float = 0.15,
    initial_threshold: float = 0.24,
    max_iterations: int = 30,
) -> Dict:
    v_arr = np.asarray(vader_scores, dtype=float)
    b_arr = np.asarray(bert_scores, dtype=float)
    y_true = np.asarray(true_labels, dtype=int)
    y_continuous = y_true.astype(float) - 1.0

    def evaluate(a: float, t: float) -> Tuple[float, float, float]:
        ens = a * b_arr + (1.0 - a) * v_arr
        preds = _score_to_class(ens, t)
        f1 = float(f1_score(y_true, preds, average="macro", zero_division=0))
        acc = float(accuracy_score(y_true, preds))
        mse = float(np.mean((ens - y_continuous) ** 2))
        alignment = 1.0 / (1.0 + mse)
        return round(f1, 4), round(acc, 4), alignment

    cur_alpha = round(initial_alpha, 3)
    cur_thresh = round(initial_threshold, 3)
    cur_f1, cur_acc, cur_align = evaluate(cur_alpha, cur_thresh)
    initial_f1 = cur_f1

    trajectory = [
        {
            "iteration": 0,
            "alpha": cur_alpha,
            "threshold": cur_thresh,
            "f1_score": cur_f1,
            "accuracy": cur_acc,
            "accepted": True,
        }
    ]
    visited = {(cur_alpha, cur_thresh)}

    for step in range(1, max_iterations + 1):
        deltas = [
            (0.05, 0.0), (-0.05, 0.0), (0.10, 0.0), (-0.10, 0.0),
            (0.0, 0.02), (0.0, -0.02), (0.0, -0.04), (0.0, 0.04),
            (0.05, -0.02), (0.05, 0.02), (-0.05, -0.02), (-0.05, 0.02),
            (0.10, -0.02), (0.10, -0.04),
        ]
        valid_neighbors = []
        for da, dt in deltas:
            na = round(cur_alpha + da, 3)
            nt = round(cur_thresh + dt, 3)
            if 0.05 <= na <= 0.95 and 0.04 <= nt <= 0.28 and (na, nt) not in visited:
                valid_neighbors.append((na, nt))

        best_neighbor = None
        best_n_f1, best_n_acc, best_n_align = cur_f1, cur_acc, cur_align

        for na, nt in valid_neighbors:
            nf1, nacc, nalign = evaluate(na, nt)
            better_f1 = nf1 > best_n_f1 + 1e-5
            same_f1_better_tie = abs(nf1 - best_n_f1) <= 1e-5 and (
                nacc > best_n_acc + 1e-5 or (abs(nacc - best_n_acc) <= 1e-5 and nalign > best_n_align + 1e-4)
            )
            if better_f1 or same_f1_better_tie:
                best_n_f1, best_n_acc, best_n_align = nf1, nacc, nalign
                best_neighbor = (na, nt)

        if best_neighbor is None:
            trajectory.append(
                {
                    "iteration": step,
                    "alpha": cur_alpha,
                    "threshold": cur_thresh,
                    "f1_score": cur_f1,
                    "accuracy": cur_acc,
                    "accepted": False,
                }
            )
            break

        cur_alpha, cur_thresh = best_neighbor
        cur_f1, cur_acc, cur_align = best_n_f1, best_n_acc, best_n_align
        visited.add(best_neighbor)
        trajectory.append(
            {
                "iteration": step,
                "alpha": cur_alpha,
                "threshold": cur_thresh,
                "f1_score": cur_f1,
                "accuracy": cur_acc,
                "accepted": True,
            }
        )

    improvement_pct = round(((cur_f1 - initial_f1) / max(initial_f1, 1e-5)) * 100.0, 2)
    return {
        "best_alpha": cur_alpha,
        "best_threshold": cur_thresh,
        "initial_f1": initial_f1,
        "best_f1": cur_f1,
        "improvement_pct": improvement_pct,
        "total_iterations": len(trajectory) - 1,
        "trajectory": trajectory,
    }


def run_best_first_root_cause_search(
    brand: str,
    enriched_mentions: List[Dict],
    max_paths: int = 5,
) -> List[Dict]:
    if not enriched_mentions:
        return []

    aspect_stats: Dict[str, List[float]] = defaultdict(list)
    aspect_keyword_stats: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    for m in enriched_mentions:
        score = float(m.get("ensemble_score", 0.0))
        aspects = m.get("aspects", ["General Brand Perception"])
        keywords = m.get("keywords", [])
        for asp in aspects:
            aspect_stats[asp].append(score)
            frame_kws = set(BRAND_ASPECT_ONTOLOGY.get(asp, {}).get("keywords", []))
            scoped_kws = [kw for kw in keywords if kw in frame_kws]
            if scoped_kws:
                for kw in scoped_kws:
                    aspect_keyword_stats[(asp, kw)].append(score)
            else:
                aspect_keyword_stats[(asp, "overall perception")].append(score)

    brand_avg = float(np.mean([float(m.get("ensemble_score", 0.0)) for m in enriched_mentions]))
    root_node = {
        "node_id": f"BRAND::{brand}",
        "node_type": "BRAND",
        "label": brand,
        "heuristic_score": 1.0,
        "mention_count": len(enriched_mentions),
        "avg_sentiment": round(brand_avg, 3),
    }

    frontier: List[Tuple[float, int, int, Dict]] = []
    counter = 0

    for asp, scores in aspect_stats.items():
        freq = len(scores)
        avg_s = float(np.mean(scores))
        sev = BRAND_ASPECT_ONTOLOGY.get(asp, {}).get("severity_weight", 1.0)
        neg_bias = 0.35 if avg_s < 0 else 0.15
        h_val = round((abs(avg_s) + neg_bias) * math.log1p(freq) * sev, 4)
        asp_node = {
            "node_id": f"ASPECT::{asp}",
            "node_type": "ASPECT",
            "label": asp,
            "heuristic_score": h_val,
            "mention_count": freq,
            "avg_sentiment": round(avg_s, 3),
        }
        counter += 1
        heapq.heappush(frontier, (-h_val, counter, 1, {"aspect": asp, "aspect_node": asp_node}))

    discovered_paths: List[Dict] = []
    seen_pairs = set()

    while frontier and len(discovered_paths) < max_paths:
        _, _, depth, payload = heapq.heappop(frontier)

        if depth == 1:
            asp = payload["aspect"]
            asp_node = payload["aspect_node"]
            sev = BRAND_ASPECT_ONTOLOGY.get(asp, {}).get("severity_weight", 1.0)

            for (k_asp, kw), k_scores in aspect_keyword_stats.items():
                if k_asp != asp:
                    continue
                k_freq = len(k_scores)
                k_avg = float(np.mean(k_scores))
                neg_bias = 0.40 if k_avg < 0 else 0.12
                k_h = round((abs(k_avg) + neg_bias) * math.log1p(k_freq) * sev, 4)
                kw_node = {
                    "node_id": f"KW::{asp}::{kw}",
                    "node_type": "KEYWORD",
                    "label": kw,
                    "heuristic_score": k_h,
                    "mention_count": k_freq,
                    "avg_sentiment": round(k_avg, 3),
                }
                path_score = round((asp_node["heuristic_score"] + k_h) / 2.0, 4)
                counter += 1
                heapq.heappush(
                    frontier,
                    (
                        -path_score,
                        counter,
                        2,
                        {
                            "aspect": asp,
                            "keyword": kw,
                            "path_score": path_score,
                            "frequency": k_freq,
                            "avg_sentiment": round(k_avg, 3),
                            "nodes": [root_node, asp_node, kw_node],
                        },
                    ),
                )
        elif depth == 2:
            pair = (payload["aspect"], payload["keyword"])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            tone = "negative risk driver" if payload["avg_sentiment"] < -0.05 else (
                "positive brand strength" if payload["avg_sentiment"] > 0.05 else "neutral discussion driver"
            )
            explanation = (
                f"Best-First Search prioritized '{payload['aspect']}' → '{payload['keyword']}' "
                f"as a {tone} ({payload['frequency']} mentions, avg polarity {payload['avg_sentiment']:+.2f})."
            )
            discovered_paths.append(
                {
                    "aspect": payload["aspect"],
                    "trigger_keyword": payload["keyword"],
                    "path_score": payload["path_score"],
                    "frequency": payload["frequency"],
                    "avg_sentiment": payload["avg_sentiment"],
                    "explanation": explanation,
                    "nodes": payload["nodes"],
                }
            )

    return discovered_paths
