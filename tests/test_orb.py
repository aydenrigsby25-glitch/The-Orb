"""Checks the spec's hard rules.   Run:  python -m pytest -q"""

import random
import re
from collections import Counter

from orb import AskRequest, Memory, NatalChart, Orb
from orb import probability
from orb.intents import resolve
from orb.models import KnownIntent
from orb.nickname import generate_nickname, is_repeat
from orb.zenith import RANGES, daily_zenith

CHART = NatalChart(sun="Leo", moon="Pisces", rising="Aquarius")
NEUTRAL = NatalChart(sun="Virgo")  # earth sun, no moon/rising: no weight shifts


def _ask(orb, memory, q, chart=CHART):
    r = orb.ask(AskRequest(question=q, chart=chart, memory=memory))
    if r.intent_key:
        memory.known[r.intent_key] = KnownIntent(kind=r.kind, outcome=r.outcome)
        memory.last_key = r.intent_key
    if r.nickname:
        memory.nicknames.append(r.nickname)
    memory.recent.append(r.text)
    return r


def test_long_run_balance():
    counts = Counter(probability.roll(f"question {i}", NEUTRAL) for i in range(40_000))
    n = sum(counts.values())
    assert abs(counts["Cosmic Anomaly"] / n - 0.05) < 0.006
    # remaining 95% splits 40/40/20
    rest = n - counts["Cosmic Anomaly"]
    assert abs(counts["Yes"] / rest - 0.40) < 0.01
    assert abs(counts["No"] / rest - 0.40) < 0.01
    assert abs(counts["Maybe"] / rest - 0.20) < 0.01


def test_same_question_same_answer_forever():
    assert len({probability.roll("go gym today", CHART) for _ in range(50)}) == 1


def test_follow_ups_and_rephrasings_keep_the_answer():
    orb, mem = Orb(), Memory()
    first = _ask(orb, mem, "Should I go to the gym today?")
    for q in ["What if I REALLY want to?", "but i feel like it", "Should I still do it?",
              "Is it a good idea instead?", "Is going to the gym today a good idea?",
              "are you sure?"]:
        r = _ask(orb, mem, q)
        assert r.outcome == first.outcome, q
        assert r.intent_key == first.intent_key, q
        assert r.reused, q


def test_meaningful_change_rolls_fresh():
    mem = Memory(known={"go gym today": KnownIntent(kind="yes_no", outcome="Yes")},
                 last_key="go gym today")
    for q in ["Should I go to the gym tomorrow?", "Should I quit my job?"]:
        key, _, reused = resolve(q, mem)
        assert not reused and key != "go gym today", q


def test_responses_start_with_the_orb_and_stay_short():
    orb, mem = Orb(), Memory()
    for i in range(60):
        r = _ask(orb, mem, f"Should I adopt cat number {i}?")
        assert r.text.startswith("The ORB")
        assert r.outcome in r.text
        assert len(re.findall(r"[.!?](\s|$)", r.text)) <= 4


def test_no_exact_repeats_in_explanations():
    orb, mem = Orb(), Memory()
    texts = [_ask(orb, mem, f"Will thing {i} happen?").text for i in range(40)]
    assert len(set(texts)) == len(texts)


def test_open_ended_answer_is_fixed():
    orb = Orb()
    a = _ask(orb, Memory(), "What should I eat tonight?").outcome
    b = _ask(orb, Memory(), "what should i eat tonight").outcome
    assert a == b


def test_nicknames_never_repeat():
    rng, used = random.Random(1), []
    for _ in range(60):
        name = generate_nickname(used, rng)
        assert not is_repeat(name, used)
        used.append(name)


def test_daily_zenith_format():
    for seed in range(200):
        lines = daily_zenith(random.Random(seed))
        assert len(lines) == 6
        for i, line in enumerate(lines):
            prefix, frag = line.split(": ", 1)
            assert prefix == ("Do" if i < 3 else "Don’t")
            lo, hi = RANGES[i]
            assert lo <= len(frag.split()) <= hi
        assert not any("ORB" in ln for ln in lines)


def test_zenith_does_not_need_chart_or_touch_memory():
    r = Orb().ask(AskRequest(question="give me my DAILY ZENITH"))
    assert r.kind == "zenith" and r.intent_key is None and len(r.lines) == 6


def test_missing_sun_asks_for_chart():
    r = Orb().ask(AskRequest(question="Should I text him?"))
    assert r.kind == "intake" and r.text.startswith("The ORB")



def test_no_ai_anywhere():
    """The site's code and dependencies contain no AI services."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    files = [p for p in root.rglob("*.py") if ".venv" not in p.parts and "tests" not in p.parts]
    code = " ".join(p.read_text() for p in files).lower()
    reqs = (root / "requirements.txt").read_text().lower()
    for banned in ("openai", "anthropic", "api_key", "llm"):  # not "gemini": it is a zodiac sign
        assert banned not in code, banned
        assert banned not in reqs, banned
