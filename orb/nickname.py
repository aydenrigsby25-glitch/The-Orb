"""Unhinged Horoscope nicknames.

Rules from the spec:
- Six patterns, chosen at random.
- A nickname counts as a repeat if it shares two components with any earlier one.
- Make at least three candidates and keep the most unusual one.
"""

import random
import re

ROLES = [
    "Keeper", "Witness", "Collector", "Archivist", "Cartographer", "Herald",
    "Shepherd", "Curator", "Smuggler", "Duchess", "Warden", "Ferryman",
    "Apprentice", "Magistrate", "Choirmaster", "Locksmith", "Translator",
    "Beekeeper", "Lamplighter", "Auctioneer", "Botanist", "Night Clerk",
]
ADJECTIVES = [
    "Electric", "Forgotten", "Laughing", "Shattered", "Velvet", "Feral",
    "Upside-Down", "Humming", "Lukewarm", "Unbothered", "Radioactive",
    "Overdue", "Bioluminescent", "Haunted", "Microwaved", "Sleepwalking",
    "Iridescent", "Unlicensed", "Carbonated", "Moth-Eaten", "Thunderstruck",
    "Gilded", "Borrowed", "Sideways", "Whispering", "Crooked", "Molten",
    "Anxious", "Hollow", "Neon", "Prismatic", "Damp", "Feverish", "Clockwork",
]
PLURAL_NOUNS = [
    "Comets", "Echoes", "Teeth", "Lanterns", "Spoons", "Tides", "Receipts",
    "Mirrors", "Hymns", "Pigeons", "Voicemails", "Keys", "Moths", "Lullabies",
    "Satellites", "Doorknobs", "Shadows", "Rumors", "Antlers", "Raincoats",
    "Thimbles", "Ghosts", "Marbles", "Bells", "Weather Vanes", "Sardines",
]
CREATURES = [
    "Owl", "Axolotl", "Heron", "Jackal", "Octopus", "Moth", "Stag", "Lynx",
    "Eel", "Raven", "Possum", "Salamander", "Narwhal", "Mantis", "Crow",
    "Tortoise", "Hare", "Jellyfish", "Badger", "Peacock", "Coyote", "Cicada",
]
CELESTIAL = [
    "Seventh Moon", "Crooked Comet", "Last Eclipse", "Quiet Nebula",
    "Blue Hour", "Dying Star", "Forgotten Asteroid", "Inner Ring of Saturn",
    "Midnight Sun", "Wandering Planet", "Ninth House", "Waning Crescent",
    "Leaking Galaxy", "Unnamed Constellation", "Morning Star",
]
IMPOSSIBLE = [
    "Square Circle", "Silent Thunder", "Dry Ocean", "Yesterday's Tomorrow",
    "Frozen Flame", "Heavy Feather", "Unopened Door", "Loud Library",
    "Last Prime Number", "Fourth Primary Color", "Unmelting Snowman",
    "Married Bachelor", "Nameless Name", "Wet Desert", "Endless Intermission",
]

PATTERNS = [
    lambda r: f"The {r.choice(ROLES)} of {r.choice(ADJECTIVES)} {r.choice(PLURAL_NOUNS)}",
    lambda r: f"The {r.choice(ADJECTIVES)} {r.choice(CREATURES)}",
    lambda r: f"Child of the {r.choice(CELESTIAL)}",
    lambda r: f"{r.choice(ADJECTIVES)} Oracle",
    lambda r: f"Keeper of the {r.choice(IMPOSSIBLE)}",
    lambda r: f"{r.choice(ADJECTIVES)} {r.choice(PLURAL_NOUNS)}",   # "no title at all"
]

_GLUE = {"the", "of"}


def _components(name):
    words = re.findall(r"[a-z'\-]+", name.lower())
    return {w for w in words if w not in _GLUE}


def is_repeat(candidate, used):
    cand = _components(candidate)
    for old in used:
        old_parts = _components(old)
        if candidate.lower() == old.lower() or len(cand & old_parts) >= 2:
            return True
    return False


def _unusualness(candidate, used):
    """Lower = fresher. Counts how often its words already showed up."""
    seen = {}
    for old in used:
        for w in _components(old):
            seen[w] = seen.get(w, 0) + 1
    return sum(seen.get(w, 0) for w in _components(candidate))


def generate_nickname(used=(), rng=None):
    rng = rng or random.Random()
    used = list(used)
    candidates = []
    for _ in range(300):
        name = rng.choice(PATTERNS)(rng)
        if not is_repeat(name, used) and name not in candidates:
            candidates.append(name)
        if len(candidates) >= 3:
            break
    if not candidates:
        # Banks exhausted after a very long session: add a roman-numeral suffix.
        return f"{rng.choice(PATTERNS)(rng)} the {len(used) + 1}th"
    rng.shuffle(candidates)
    return min(candidates, key=lambda c: _unusualness(c, used))
