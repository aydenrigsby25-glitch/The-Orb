"""The ORB's voice: hand-written phrase banks, no AI.

Every reply is assembled from interchangeable parts (opener, natal clause,
celestial flourish), which gives thousands of combinations. compose() also
checks the visitor's recent replies and re-draws if an opener or full line
would repeat.
"""

import random

from .signs import ELEMENT, MODALITY

# ------------------------------------------------------------------ openers
OPENERS = {
    "Yes": [
        "The ORB brightens to a clean white flame: Yes.",
        "The ORB hums in a major key: Yes.",
        "The ORB tilts toward you and whispers, Yes.",
        "The ORB has decided, and it is Yes.",
        "The ORB's mist parts cleanly around a single word: Yes.",
        "The ORB glows warm as a porch light: Yes.",
        "The ORB stops swirling. Yes.",
        "The ORB answers before the echo fades: Yes.",
    ],
    "No": [
        "The ORB dims to a bruise-blue hush: No.",
        "The ORB turns its face to the wall: No.",
        "The ORB clouds over like a fogged window: No.",
        "The ORB speaks low and certain: No.",
        "The ORB lets the question sink and does not float it back: No.",
        "The ORB's light flickers once, then holds at No.",
        "The ORB shakes its many heads: No.",
        "The ORB has already closed this door: No.",
    ],
    "Maybe": [
        "The ORB swirls in two directions at once: Maybe.",
        "The ORB shrugs its silver shoulders: Maybe.",
        "The ORB is still listening to the tide: Maybe.",
        "The ORB flickers between colors and settles on none: Maybe.",
        "The ORB keeps one eye closed: Maybe.",
        "The ORB's answer arrives wearing a veil: Maybe.",
        "The ORB says the ink is still wet: Maybe.",
    ],
}

# ------------------------------------------------------------ natal clauses
SUN = {
    "fire": ["your {sign} Sun is already halfway out the door",
             "your {sign} Sun crackles toward a decision",
             "your {sign} Sun has never once waited for permission",
             "your {sign} Sun hates a lukewarm ending"],
    "earth": ["your {sign} Sun wants receipts before it moves",
              "your {sign} Sun weighs this like a harvest",
              "your {sign} Sun trusts only what it can hold",
              "your {sign} Sun is counting the cost in quiet coins"],
    "air": ["your {sign} Sun has argued both sides twice already",
            "your {sign} Sun circles the idea like a kite",
            "your {sign} Sun wants the conversation more than the verdict",
            "your {sign} Sun is drafting three versions of this in its head"],
    "water": ["your {sign} Sun felt the answer before you finished asking",
              "your {sign} Sun is reading the undercurrent",
              "your {sign} Sun remembers how this went last time",
              "your {sign} Sun is listening for what you didn't say"],
}
MOON = {
    "fire": ["your {sign} Moon wants the thrill more than the outcome",
             "your {sign} Moon burns hot and forgets fast"],
    "earth": ["your {sign} Moon craves something steady underfoot",
              "your {sign} Moon is soothed by a plan"],
    "air": ["your {sign} Moon keeps changing the wallpaper on this feeling",
            "your {sign} Moon flits between moods like a moth between lamps"],
    "water": ["your {sign} Moon is fogging the glass",
              "your {sign} Moon is pulling the tide both ways",
              "your {sign} Moon keeps the answer half underwater"],
}
RISING = {
    "fixed": ["your {sign} Rising plants its feet",
              "your {sign} Rising does not love a sudden turn"],
    "earth": ["your {sign} Rising wants the practical road",
              "your {sign} Rising checks the weather before it leaves"],
    "cardinal": ["your {sign} Rising wants to be first through the door",
                 "your {sign} Rising points the compass"],
    "mutable": ["your {sign} Rising can bend whichever way this goes",
                "your {sign} Rising is already improvising"],
}

FLOURISHES = [
    "while Mercury mutters from the shadow of its retrograde",
    "as the waning Moon trims what you no longer need",
    "with Venus lingering in the doorway",
    "under a Saturn transit that is checking your math",
    "while Jupiter leans an elbow on the scale",
    "as Mars paces the hallway of your eighth house",
    "with the North Node tugging at your sleeve",
    "beneath a gibbous Moon that keeps its own counsel",
    "while Neptune smears the edges of the map",
    "as Uranus rattles the window latch",
    "with Pluto quietly rearranging the basement",
    "under a sky that has seen this question before",
    "while the Moon slips void of course",
    "as a crescent Moon sharpens its edge",
]

TAILS = {
    "Yes": ["Go.", "Step through.", "The door is open.", "Let it begin.",
            "Move while the light holds.", "Take the first step tonight."],
    "No": ["Let it pass.", "Hold still.", "Not this orbit.", "Leave it on the shelf.",
           "Keep your coat on.", "Wait for a kinder sky."],
    "Maybe": ["Ask the morning.", "Watch for a sign with feathers.",
              "The tide hasn't turned yet.", "Some doors open from the other side.",
              "Neither the stars nor I will rush you.", "Let it ripen."],
}

# -------------------------------------------------------- open-ended answers
OPEN_ANSWERS = {
    "when": ["After the next new Moon", "Thursday, after dark", "Sooner than you planned",
             "When the third reminder arrives", "Before the season turns",
             "The moment you stop checking", "At the next full Moon",
             "In nine days, give or take a tide"],
    "where": ["Somewhere with running water nearby", "The place you almost didn't go",
              "Facing east", "Close to home, but not inside it",
              "Wherever the music is too loud", "Up a flight of stairs",
              "The second place you thought of", "Under an open sky"],
    "who": ["The one who texts first", "Someone wearing green",
            "The friend you underestimate", "You, eventually",
            "The person who asks you a question back", "An old acquaintance with new news",
            "Whoever laughs at the wrong moment", "The quiet one in the room"],
    "why": ["Because you outgrew the old shape", "Because the timing finally fits",
            "Because something unfinished is asking to end",
            "Because you already know, and want a witness",
            "Because the pattern is ready to break"],
    "how": ["Slowly, then all at once", "With a list and a deadline",
            "By asking for help out loud", "One honest conversation at a time",
            "Sideways, never head-on", "The simplest way you've been avoiding"],
    "what": ["The option you dismissed first", "Something blue",
             "The harder one", "The one that scares you a little",
             "Whatever lets you sleep tonight", "The smallest version of it",
             "The thing you'd do if no one was watching", "Something with a deadline",
             "The second choice", "The one that feels like summer"],
}
OPEN_OPENERS = [
    "The ORB answers once, and only once: {answer}.",
    "The ORB has etched it in starlight: {answer}.",
    "The ORB speaks, and the answer will not change: {answer}.",
    "The ORB's mist forms a single shape: {answer}.",
    "The ORB draws one card from the dark: {answer}.",
]
OPEN_REPEAT_OPENERS = [
    "The ORB does not rewrite the sky: {answer}.",
    "The ORB has answered this already, and it stands: {answer}.",
    "The ORB repeats itself only once: {answer}.",
    "The ORB's answer has not moved an inch: {answer}.",
]
REPEAT_OPENERS = {
    "Yes": ["The ORB has spoken, and pleading won't move it: still Yes.",
            "The ORB's answer has not cooled: Yes.",
            "The ORB hears you, and it is still Yes."],
    "No": ["The ORB has spoken, and wanting it harder won't move it: still No.",
           "The ORB hears your longing, and it is still No.",
           "The ORB does not re-roll the heavens: No."],
    "Maybe": ["The ORB will not be hurried: still Maybe.",
              "The ORB's fog has not lifted: Maybe.",
              "The ORB answers the same way twice: Maybe."],
    "Cosmic Anomaly": ["The ORB is still glitching: Cosmic Anomaly.",
                       "The ORB's static has not cleared: Cosmic Anomaly."],
}

COSMIC_OPENERS = [
    "The ORB cracks down the middle and a different sky leaks through: Cosmic Anomaly.",
    "The ORB flickers violently, then speaks in a voice that isn't its own: Cosmic Anomaly.",
    "The ORB rolls off its stand and returns from somewhere else: Cosmic Anomaly.",
    "The ORB's light runs backwards for a full second: Cosmic Anomaly.",
]

# ------------------------------------------------------ unhinged horoscopes
HORO_OPENERS = [
    "This week a {thing} will {verb} your {noun}, and you will let it.",
    "Expect a {thing} to {verb} your {noun} before Friday.",
    "Somewhere a {thing} is rehearsing how to {verb} your {noun}.",
    "The stars have hired a {thing} to {verb} your {noun}.",
]
HORO_THINGS = ["damp pigeon", "retired lighthouse", "stranger in a bucket hat",
               "possessed vending machine", "very confident moth", "lukewarm soup",
               "rogue shopping cart", "choir of crows", "sentient parking meter"]
HORO_VERBS = ["rename", "audit", "serenade", "misplace", "knight", "laminate", "haunt", "renovate"]
HORO_NOUNS = ["ambitions", "Tuesday", "left shoe", "group chat", "entire vibe",
              "Wi-Fi password", "self-esteem", "sock drawer", "inner child"]
HORO_MIDDLES = {
    "fire": "Your {sign} fire will want to fight it; instead, buy it a coffee.",
    "earth": "Your {sign} steadiness will be tested by something shaped like a spoon.",
    "air": "Your {sign} mind will narrate all of this in a fake accent, and it will help.",
    "water": "Your {sign} heart will cry at a commercial and be right to.",
}
HORO_CLOSERS = [
    "Lucky number: the one on the receipt you threw away.",
    "Avoid ladders, ex-situationships, and anything labeled 'mystery flavor'.",
    "Wear something with pockets. You'll need them.",
    "The Moon says hi. Don't say it back.",
    "Lucky color: whatever your microwave glows.",
    "Drink water. The cosmos is watching your hydration.",
]


# ------------------------------------------------------------------ helpers
def _natal_clauses(chart, rng):
    clauses = []
    if chart.sun:
        clauses.append(rng.choice(SUN[ELEMENT[chart.sun]]).format(sign=chart.sun))
    if chart.moon:
        clauses.append(rng.choice(MOON[ELEMENT[chart.moon]]).format(sign=chart.moon))
    if chart.rising:
        if MODALITY[chart.rising] == "fixed":
            bucket = "fixed"
        elif ELEMENT[chart.rising] == "earth":
            bucket = "earth"
        else:
            bucket = MODALITY[chart.rising]
        clauses.append(rng.choice(RISING[bucket]).format(sign=chart.rising))
    rng.shuffle(clauses)
    return clauses


def _reason(chart, rng, recent=()):
    clauses = _natal_clauses(chart, rng)
    picked = clauses[: rng.choice([1, 2]) if len(clauses) > 1 else 1]
    if len(picked) == 2:
        body = f"{picked[0]}, and {picked[1]}"
    else:
        body = picked[0] if picked else "the sky itself"
    body = body[0].upper() + body[1:]
    fresh = [f for f in FLOURISHES if not any(f in r for r in recent)] or FLOURISHES
    return f"{body} {rng.choice(fresh)}."


def _not_recent(build, recent, rng, tries=12):
    """Re-draw until neither the opener nor the whole line was used recently."""
    recent_openers = {r.split(":")[0] for r in recent}
    text = build()
    for _ in range(tries):
        if text not in recent and text.split(":")[0] not in recent_openers:
            break
        text = build()
    return text


# ------------------------------------------------------------- composers
def compose_yes_no(outcome, chart, recent=(), reused=False, rng=None):
    rng = rng or random.Random()

    def build():
        opener = rng.choice(REPEAT_OPENERS[outcome] if reused else OPENERS[outcome])
        return f"{opener} {_reason(chart, rng, recent)} {rng.choice(TAILS[outcome])}"

    return _not_recent(build, recent, rng)


def compose_cosmic(chart, recent=(), reused=False, rng=None):
    rng = rng or random.Random()

    def build():
        opener = rng.choice(REPEAT_OPENERS["Cosmic Anomaly"] if reused else COSMIC_OPENERS)
        return f"{opener} {_reason(chart, rng, recent)}"

    return _not_recent(build, recent, rng)


def fixed_open_answer(qword, u):
    """Deterministic: the same intent always gets the same answer."""
    bank = OPEN_ANSWERS.get(qword, OPEN_ANSWERS["what"])
    return bank[int(u * len(bank)) % len(bank)]


def compose_open(answer, chart, recent=(), reused=False, rng=None):
    rng = rng or random.Random()

    def build():
        opener = rng.choice(OPEN_REPEAT_OPENERS if reused else OPEN_OPENERS)
        return f"{opener.format(answer=answer)} {_reason(chart, rng, recent)}"

    return _not_recent(build, recent, rng)


def compose_horoscope(chart, rng=None):
    rng = rng or random.Random()
    first = rng.choice(HORO_OPENERS).format(
        thing=rng.choice(HORO_THINGS), verb=rng.choice(HORO_VERBS), noun=rng.choice(HORO_NOUNS))
    middle = ""
    if chart.sun:
        middle = HORO_MIDDLES[ELEMENT[chart.sun]].format(sign=chart.sun) + " "
    return f"{first} {middle}{rng.choice(HORO_CLOSERS)}"


def compose_intake(chart):
    if not chart.sun:
        return ("The ORB cannot see you yet. Tell it your Sun sign (and your Moon and Rising, "
                "if the stars gave them to you) and it will open its eye.")
    missing = [p for p in ("moon", "rising") if not getattr(chart, p)]
    return (f"The ORB sees your {chart.sun} Sun, but your "
            f"{' and '.join(m.title() for m in missing)} {'are' if len(missing) > 1 else 'is'} still in shadow.")
