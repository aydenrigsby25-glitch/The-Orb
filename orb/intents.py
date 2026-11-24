"""Intent matching: decides whether a question is new or a re-ask of an old one.

How it works, step by step:
1. Strip filler ("should i", "do you think", "is it a good idea") and punctuation.
2. Drop stopwords and vague words ("it", "still", "really", "want", "feel").
3. Lightly stem what's left ("going" -> "go") and sort it. That sorted list is
   the intent key, e.g. "should I go to the gym?" and
   "is going to the gym a good idea" both become "go gym".
4. If nothing meaningful is left ("what if I really want to?", "but I feel like
   it", "should I still do it?"), it's a follow-up to the LAST question.
5. Otherwise compare against earlier keys. Close matches (Jaccard >= 0.75) count
   as the same question, unless the time changed (today vs tomorrow), which
   the spec says is a meaningful change.
"""

import re

FILLER_PHRASES = [
    "hey orb", "dear orb", "oh orb", "the orb", "orb",
    "do you think", "what do you think", "is it a good idea to", "is it a good idea",
    "would it be a good idea to", "would it be wise to", "is it wise to",
    "should i still", "should i", "or not", "tell me", "can you tell me",
    "i want to know", "i wonder", "please", "be honest",
]

STOPWORDS = {
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "with", "and", "or",
    "but", "if", "is", "are", "am", "be", "been", "being", "was", "were", "will",
    "would", "should", "could", "can", "shall", "may", "might", "must", "do",
    "does", "did", "have", "has", "had", "i", "me", "my", "mine", "myself", "we",
    "us", "our", "you", "your", "it", "its", "this", "that", "these", "those",
    "what", "which", "who", "whom", "where", "when", "why", "how", "about",
    "from", "by", "as", "into", "than", "then", "so", "too", "very", "just",
    "not", "no", "yes", "any", "some", "there", "here", "up", "out", "im",
    "ill", "ive", "id", "dont", "isnt", "arent", "wont", "cant", "shouldnt",
}

# Words that carry emotion or emphasis but not a new scenario.
VAGUE = {
    "still", "really", "anyway", "instead", "again", "though", "even", "actually",
    "want", "wanna", "feel", "felt", "like", "think", "good", "bad", "idea",
    "sure", "ok", "okay", "right", "honestly", "seriously", "pretty", "maybe",
    "what", "if", "but", "thing", "something", "stuff", "orb", "wise", "fine",
    "need", "badly", "much", "lot", "more", "kinda", "sort", "kind", "absolutely",
}

TIME_WORDS = {
    "today", "tonight", "tomorrow", "yesterday", "now", "later", "soon",
    "week", "weekend", "month", "year", "morning", "afternoon", "evening",
    "night", "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "next", "summer", "winter", "spring", "fall",
}

# Opening phrases that signal a re-ask or a push. Lower-cased, no punctuation.
FOLLOW_UP_STARTS = (
    "what if i", "but i", "but what", "but should", "should i still",
    "is it a good idea instead", "is it still", "are you sure", "really",
    "seriously", "please", "come on", "ask again", "try again", "roll again",
    "reroll", "re roll", "what about now", "ok but", "okay but", "and if",
    "even if", "how about if", "you sure", "why not", "why",
)

SIMILARITY_THRESHOLD = 0.75


def _normalize(text):
    text = text.lower().replace("’", "'").replace("'", "")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


IRREGULAR = {
    "going": "go", "goes": "go", "went": "go", "gone": "go", "doing": "do",
    "ate": "eat", "eaten": "eat", "bought": "buy", "took": "take", "taken": "take",
    "saw": "see", "seen": "see", "seeing": "see", "made": "make", "having": "have",
    "left": "leave", "got": "get", "gotten": "get", "getting": "get", "texting": "text",
    "lying": "lie", "dying": "dye", "dyed": "dye", "told": "tell", "sold": "sell",
}


def _stem(word):
    word = IRREGULAR.get(word, word)
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    # "runn" -> "run", "stopp" -> "stop" after stripping -ing/-ed
    if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "aeiouls":
        word = word[:-1]
    # "move"/"moving"/"moved" all end up as "mov"
    if len(word) > 3 and word.endswith("e"):
        word = word[:-1]
    return word


def content_tokens(question):
    """The words that actually define the scenario, stemmed and de-duplicated."""
    text = " " + _normalize(question) + " "
    for phrase in FILLER_PHRASES:
        text = text.replace(" " + phrase + " ", " ")
    words = [w for w in text.split() if w not in STOPWORDS and w not in VAGUE]
    return sorted({_stem(w) for w in words if len(w) > 1 or w.isdigit()})


def _time_tokens(tokens):
    return {t for t in tokens if t in TIME_WORDS}


def similarity(a, b):
    a, b = set(a), set(b)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def make_key(tokens, question):
    if tokens:
        return " ".join(tokens)
    # Nothing meaningful at all and no earlier question to attach to.
    return "~" + _normalize(question)


def is_follow_up(question, tokens, last_key):
    if not last_key:
        return False
    last_tokens = set(last_key.split()) if not last_key.startswith("~") else set()
    if not tokens:
        return True  # "should I still do it?", "but I feel like it"
    starts_like_follow_up = _normalize(question).startswith(FOLLOW_UP_STARTS)
    new_words = set(tokens) - last_tokens
    # A push that adds no new scenario words is still the same question.
    return starts_like_follow_up and not new_words


def resolve(question, memory):
    """Return (intent_key, tokens, reused)."""
    tokens = content_tokens(question)

    if is_follow_up(question, tokens, memory.last_key):
        return memory.last_key, tokens, True

    key = make_key(tokens, question)
    if key in memory.known:
        return key, tokens, True

    best_key, best_score = None, 0.0
    for old_key in memory.known:
        if old_key.startswith("~"):
            continue
        old_tokens = old_key.split()
        if _time_tokens(old_tokens) != _time_tokens(tokens):
            continue  # different time = different scenario
        score = similarity(tokens, old_tokens)
        if score > best_score:
            best_key, best_score = old_key, score
    if best_key and best_score >= SIMILARITY_THRESHOLD:
        return best_key, tokens, True

    return key, tokens, False


# ---------------------------------------------------------------- classify

YES_NO_STARTERS = {
    "should", "will", "would", "could", "can", "is", "are", "am", "do", "does",
    "did", "was", "were", "has", "have", "had", "shall", "may", "might", "must",
    "isnt", "arent", "wont", "wouldnt", "shouldnt", "cant", "dont", "doesnt",
    "didnt", "hasnt", "havent",
}
LEAD_INS = {"so", "but", "and", "ok", "okay", "well", "hmm", "um", "hey", "orb", "oh", "dear", "the", "also", "now"}


def classify(question):
    """zenith | horoscope | yes_no | open"""
    text = _normalize(question)
    if "daily zenith" in text:
        return "zenith"
    if "unhinged" in text:
        return "horoscope"
    words = [w for w in text.split()]
    while words and words[0] in LEAD_INS:
        words.pop(0)
    first = words[0] if words else ""
    if first in YES_NO_STARTERS or " or not" in f" {text} " or text.startswith("what if"):
        return "yes_no"
    if "horoscope" in text or "reading" in text.split():
        return "horoscope"
    return "open"


def question_word(question):
    """Which open-ended flavour this is, for picking a fitting fixed answer."""
    text = _normalize(question)
    for w in text.split():
        if w in ("who", "where", "when", "why", "how", "what", "which"):
            return w
    return "what"
