"""The ORB's brain. Follows the spec's workflow in order:

1. Check whether this matches an earlier question's intent.
2. Parse the question and the natal chart.
3. Determine the response type (yes/no, open-ended, unhinged horoscope, Daily Zenith).
4. Roll the probability (seeded, so it's fixed per intent).
5. Check for the 5% Cosmic Anomaly override.
6. If it's a horoscope or an anomaly, generate a nickname and a surreal horoscope.
7. Generate the explanation without repeating recent phrasing.

No AI anywhere: every outcome is hash math, every sentence is assembled
from the hand-written phrase banks in text.py, nickname.py and zenith.py.
"""

import random

from . import intents, probability, text
from .models import AskRequest, AskResponse
from .nickname import generate_nickname
from .zenith import daily_zenith


class Orb:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()

    # ------------------------------------------------------------------ main
    def ask(self, req: AskRequest) -> AskResponse:
        question = req.question.strip()
        chart, memory = req.chart, req.memory
        kind = intents.classify(question)

        # Daily Zenith: format-only, no chart, no ORB naming, never stored.
        if kind == "zenith":
            lines = daily_zenith(self.rng)
            return AskResponse(kind="zenith", text="\n".join(lines), lines=lines)

        # Natal intake: the Sun is required before anything else.
        if not chart.sun:
            return AskResponse(kind="intake", text=text.compose_intake(chart))

        if kind == "horoscope":
            return self._horoscope(chart, memory)

        key, tokens, reused = intents.resolve(question, memory)
        known = memory.known.get(key)
        if reused and known:
            kind = known.kind  # a follow-up keeps the original question's type

        if kind == "open":
            return self._open(question, key, reused, known, chart, memory)
        return self._yes_no(question, key, tokens, reused, known, chart, memory)

    # ------------------------------------------------------------- handlers
    def _yes_no(self, question, key, tokens, reused, known, chart, memory):
        outcome = known.outcome if known else probability.roll(key, chart, tokens)
        recent = memory.recent

        if outcome == "Cosmic Anomaly":
            line = text.compose_cosmic(chart, recent, reused, self.rng)
            resp = AskResponse(kind="yes_no", text=line, outcome=outcome,
                               intent_key=key, reused=reused)
            if not reused:  # the anomaly's horoscope only appears the first time
                self._attach_horoscope(resp, chart, memory)
            return resp

        line = text.compose_yes_no(outcome, chart, recent, reused, self.rng)
        return AskResponse(kind="yes_no", text=line, outcome=outcome,
                           intent_key=key, reused=reused)

    def _open(self, question, key, reused, known, chart, memory):
        recent = memory.recent

        if known:
            answer = known.outcome
        elif probability.is_cosmic(key):
            answer = "Cosmic Anomaly"
        else:
            answer = None

        if answer == "Cosmic Anomaly":
            line = text.compose_cosmic(chart, recent, reused, self.rng)
            resp = AskResponse(kind="open", text=line, outcome=answer,
                               intent_key=key, reused=reused)
            if not reused:
                self._attach_horoscope(resp, chart, memory)
            return resp

        if answer is None:
            u = probability.seed_floats(key)[2]
            answer = text.fixed_open_answer(intents.question_word(question), u)
        line = text.compose_open(answer, chart, recent, reused, self.rng)
        return AskResponse(kind="open", text=line, outcome=answer,
                           intent_key=key, reused=reused)

    def _horoscope(self, chart, memory):
        resp = AskResponse(kind="horoscope", text="")
        self._attach_horoscope(resp, chart, memory)
        resp.text = f'The ORB declares: your unhinged horoscope is "{resp.nickname}."'
        return resp

    def _attach_horoscope(self, resp, chart, memory):
        resp.nickname = generate_nickname(memory.nicknames, self.rng)
        resp.horoscope = text.compose_horoscope(chart, self.rng)
