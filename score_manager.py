import os
import json
from typing import Dict

SCORES_DIR = os.path.join(os.path.dirname(__file__), "data")
SCORES_PATH = os.path.join(SCORES_DIR, "scores.json")


def _ensure_dir():
    os.makedirs(SCORES_DIR, exist_ok=True)


def load_scores() -> Dict[str, int]:
    _ensure_dir()
    if not os.path.exists(SCORES_PATH):
        return {}
    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_scores(scores: Dict[str, int]):
    _ensure_dir()
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def update_best(difficulty: str, score: int) -> int:
    """Update best score for difficulty. Return previous best."""
    scores = load_scores()
    prev = int(scores.get(difficulty, 0))
    if score > prev:
        scores[difficulty] = int(score)
        save_scores(scores)
    return prev
