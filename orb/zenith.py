"""Daily Zenith: six surreal Do/Don't lines and nothing else.

Each line comes from a hidden category (object, color, action, sensation,
abstract concept, impossible entity). Exactly one line names a real national
brand. Word counts per line follow the spec's ranges.
"""

import random

RANGES = [(2, 6), (3, 8), (4, 10), (2, 6), (3, 8), (4, 10)]
PREFIXES = ["Do", "Do", "Do", "Don’t", "Don’t", "Don’t"]

BRANDS = [
    "Waffle House", "Crayola", "Polaroid", "Tupperware", "Duracell", "Sharpie",
    "Jell-O", "Slinky", "Zippo", "Etch A Sketch", "Kodak", "Pez", "Spam",
    "Hot Wheels", "Converse", "Twinkie", "Velcro", "Scotch Tape", "Lite-Brite",
]

OBJECTS = ["teacup", "staircase", "umbrella", "chandelier", "suitcase", "piano",
           "lighthouse", "doorbell", "rotary phone", "birdcage", "snow globe", "compass"]
COLORS = ["chartreuse", "bruised violet", "cathedral gold", "swimming-pool blue",
          "pomegranate", "static gray", "flamingo", "midnight teal", "rust"]
VERBS = ["fold", "baptize", "unbutton", "translate", "whistle at", "rewind",
         "braid", "interrogate", "polish", "pickle", "serenade", "evict"]
SENSATIONS = ["a cold coin", "static", "warm honey", "a second heartbeat",
              "velvet thunder", "a borrowed shiver", "peppermint dread"]
BODY = ["your left wrist", "your molars", "your shadow's knees", "your eyelids",
        "the back of your neck", "your wisdom teeth"]
ABSTRACTS = ["nostalgia", "Tuesday", "forgiveness", "gravity", "ambition",
             "the concept of noon", "regret", "jealousy", "patience"]
IMPOSSIBLES = ["a moth made of radio", "the eighth weekday", "a staircase of breath",
               "a jealous horizon", "the moon's younger sister", "a choir of keys",
               "an orchard of clocks", "a whale who files taxes"]
PLACES = ["under the bridge", "in the glovebox", "at the bottom of the pool",
          "behind the vending machine", "inside the eclipse", "on the 3:14 train",
          "beneath the floorboards", "in the parking garage"]

CATEGORY_TEMPLATES = {
    "object": ["the {obj} {place}", "a hollow {obj} humming {place}",
               "every {obj} that remembers your name"],
    "color": ["{color} at the edge of {abstract}", "anything {color} after midnight",
              "the exact {color} of {abstract}"],
    "action": ["{verb} the {obj}", "{verb} your reflection {place}",
               "{verb} {abstract} until it purrs"],
    "sensation": ["{sensation} behind {body}", "the taste of {sensation}",
                  "{sensation} rising through {body}"],
    "abstract": ["{abstract} folded into a {obj}", "borrowed {abstract}",
                 "{abstract} wearing someone else's coat"],
    "impossible": ["{impossible}", "{impossible} {place}", "bargains with {impossible}"],
}

BRAND_TEMPLATES = [
    "{brand} {obj} orbiting {abstract}", "a {brand} sunrise {place}",
    "{brand} confessions {place}", "the {brand} gospel of {abstract}",
    "a {brand} relic for {abstract}",
]


def _fill(template, rng, brand=None):
    return template.format(
        obj=rng.choice(OBJECTS), color=rng.choice(COLORS), verb=rng.choice(VERBS),
        sensation=rng.choice(SENSATIONS), body=rng.choice(BODY),
        abstract=rng.choice(ABSTRACTS), impossible=rng.choice(IMPOSSIBLES),
        place=rng.choice(PLACES), brand=brand or "",
    )


def word_count(fragment):
    return len(fragment.split())


def _make_fragment(category, lo, hi, rng, brand=None):
    for _ in range(200):
        if brand:
            frag = _fill(rng.choice(BRAND_TEMPLATES), rng, brand)
        else:
            frag = _fill(rng.choice(CATEGORY_TEMPLATES[category]), rng)
        if lo <= word_count(frag) <= hi:
            return frag[0].upper() + frag[1:]
    return None


def daily_zenith(rng=None):
    rng = rng or random.Random()
    categories = list(CATEGORY_TEMPLATES)
    rng.shuffle(categories)
    brand_slot = rng.randrange(6)
    brand = rng.choice(BRANDS)
    lines = []
    for i, (lo, hi) in enumerate(RANGES):
        frag = None
        while frag is None:
            frag = _make_fragment(categories[i], lo, hi, rng, brand if i == brand_slot else None)
        lines.append(f"{PREFIXES[i]}: {frag}")
    return lines
