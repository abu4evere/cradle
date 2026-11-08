"""The city's language (v0): a small vocabulary of words with fixed meanings. NPCs speak about what is happening around
them: a parent names food at a meal and praises a child; a teacher counts and shows books; a doctor speaks of sickness
and help; neighbours greet each other. The words are shown in English for us to read; to anyone inside the city they
are just sounds tied to things and acts.
"""
from __future__ import annotations

NOUNS = ("food", "water", "home", "school", "clinic", "market", "park", "bed", "ball", "book", "mother", "father",
         "friend", "doctor", "teacher", "work", "money")
VERBS = ("eat", "sleep", "come", "go", "play", "learn", "help", "look", "give", "buy")
OTHER = ("good", "no", "yes", "sick", "happy", "hello", "thanks", "please", "one", "two", "three", "four", "five")
VOCAB = NOUNS + VERBS + OTHER

_SYL = ("ka", "mi", "to", "ra", "su", "ne", "lo", "ba", "di", "ya", "ze", "po")


def name(rng) -> str:
    return "".join(rng.choice(_SYL) for _ in range(rng.randint(2, 3))).capitalize()


def say(rng, p, q, act: str, city) -> list:
    """What p says to q while doing `act`: a few words about the moment, as people talk to each other and to children."""
    young = q.age(city.hour) < 6
    parent = q.id in p.children
    if act == "eat":
        return ["eat", "food"] + (["good"] if young and rng.random() < 0.5 else [])
    if act == "be cared for" or (parent and young):
        return rng.choice([["mother"] if p.sex == "F" else ["father"], ["look", rng.choice(("ball", "food", "water"))],
                           ["good"], ["come"], ["no"], ["happy"]])
    if act == "learn" and p.role == "teacher":
        return rng.choice([["one", "two", "three"], ["look", "book"], ["learn", "good"], ["four", "five"]])
    if act == "learn":
        return rng.choice([["hello", "friend"], ["play", "ball"], ["book"]])
    if act == "see doctor" or (act == "work" and p.role == "doctor"):
        return rng.choice([["sick"], ["help"], ["doctor", "help"], ["good"]])
    if act == "shop":
        return rng.choice([["buy", "food"], ["money"], ["thanks"], ["please"]])
    if act == "work":
        return rng.choice([["work"], ["help"], ["thanks"], ["good"]])
    if act in ("play", "visit friends"):
        return rng.choice([["hello"], ["play"], ["friend"], ["go", "park"], ["happy"]])
    if act == "rest":
        return rng.choice([["home"], ["sleep"], ["hello"]])
    return []
