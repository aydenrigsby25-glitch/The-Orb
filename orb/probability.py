"""Seeded probability engine.

Why seeded: the server can't remember anything between requests, but the spec
says an answer must never change once given. So the roll comes from a hash of
the intent key. Same question -> same hash -> same number -> same answer,
for everyone, forever. Across many different questions the hashes are
uniformly spread, so the long-run split still lands on 40/40/20 + 5% anomaly.

Natal weights nudge the thresholds a few points. They're small and roughly
cancel across all signs, so the overall balance holds.
"""

import hashlib
import os

from .signs import ELEMENT, MODALITY

BASE = {"Yes": 0.40, "No": 0.40, "Maybe": 0.20}
COSMIC_RATE = 0.05
SALT = os.environ.get("ORB_SALT", "the-orb-sees-all")

CHANGE_WORDS = {
    "quit", "move", "switch", "change", "leave", "start", "new", "break",
    "transfer", "cut", "dye", "sell", "buy", "drop", "apply", "join", "end",
}


def seed_floats(key):
    """Four independent numbers in [0, 1) derived from the intent key."""
    digest = hashlib.sha256(f"{SALT}|{key}".encode()).digest()
    return [int.from_bytes(digest[i:i + 8], "big") / 2**64 for i in range(0, 32, 8)]


def natal_weights(chart, tokens=()):
    """Spec's Natal Influence Weights, as small shifts on the 40/40/20 base."""
    w = dict(BASE)

    if chart.sun and ELEMENT[chart.sun] == "fire":        # fire increases decisiveness
        w["Maybe"] -= 0.04
        w["Yes"] += 0.02
        w["No"] += 0.02
    if chart.moon and ELEMENT[chart.moon] == "water":     # water moon increases uncertainty
        w["Maybe"] += 0.04
        w["Yes"] -= 0.02
        w["No"] -= 0.02
    if chart.moon and ELEMENT[chart.moon] == "air":       # air moon increases variability
        w["Maybe"] += 0.02
        w["Yes"] -= 0.01
        w["No"] -= 0.01
    if chart.rising and MODALITY[chart.rising] == "fixed" and set(tokens) & CHANGE_WORDS:
        w["Yes"] -= 0.03                                   # fixed rising resists change
        w["No"] += 0.03
    # Earth rising (practicality) shapes the wording, not the odds.
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}


def pick(weights, u):
    cumulative = 0.0
    for outcome in ("Yes", "No", "Maybe"):
        cumulative += weights[outcome]
        if u < cumulative:
            return outcome
    return "Maybe"


def is_cosmic(key):
    return seed_floats(key)[1] < COSMIC_RATE


def roll(key, chart, tokens=()):
    """Yes / No / Maybe / Cosmic Anomaly for this intent key."""
    u_outcome, u_cosmic, _, _ = seed_floats(key)
    if u_cosmic < COSMIC_RATE:
        return "Cosmic Anomaly"
    return pick(natal_weights(chart, tokens), u_outcome)
