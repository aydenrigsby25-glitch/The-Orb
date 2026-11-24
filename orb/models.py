"""Request/response shapes for the API.

The server is stateless (serverless functions forget everything between
requests), so the visitor's browser keeps the ORB's memory and sends it back
with each question. The server trusts it only for continuity, never for rolls.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .signs import clean_sign

MAX_KNOWN = 200
MAX_NICKNAMES = 80
MAX_RECENT = 15


class NatalChart(BaseModel):
    sun: Optional[str] = None
    moon: Optional[str] = None
    rising: Optional[str] = None

    @field_validator("sun", "moon", "rising", mode="before")
    @classmethod
    def _clean(cls, v):
        return clean_sign(v)


class KnownIntent(BaseModel):
    kind: str            # "yes_no" or "open"
    outcome: str         # Yes / No / Maybe / Cosmic Anomaly, or the fixed open-ended answer


class Memory(BaseModel):
    known: Dict[str, KnownIntent] = Field(default_factory=dict)
    last_key: Optional[str] = None
    nicknames: List[str] = Field(default_factory=list)
    recent: List[str] = Field(default_factory=list)

    @field_validator("known")
    @classmethod
    def _cap_known(cls, v):
        if len(v) > MAX_KNOWN:
            v = dict(list(v.items())[-MAX_KNOWN:])
        return v

    @field_validator("nicknames")
    @classmethod
    def _cap_nicknames(cls, v):
        return [str(n)[:80] for n in v[-MAX_NICKNAMES:]]

    @field_validator("recent")
    @classmethod
    def _cap_recent(cls, v):
        return [str(t)[:600] for t in v[-MAX_RECENT:]]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    chart: NatalChart = Field(default_factory=NatalChart)
    memory: Memory = Field(default_factory=Memory)


class AskResponse(BaseModel):
    kind: str                         # yes_no | open | horoscope | zenith | intake
    text: str                         # the main line, always starts "The ORB" (except Daily Zenith)
    outcome: Optional[str] = None     # Yes / No / Maybe / Cosmic Anomaly / fixed open answer
    intent_key: Optional[str] = None  # what the browser stores so follow-ups match
    reused: bool = False              # True when this was a rephrase/follow-up of an earlier question
    nickname: Optional[str] = None
    horoscope: Optional[str] = None
    lines: Optional[List[str]] = None  # Daily Zenith lines
