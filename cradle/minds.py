"""The minds of Cradle's AI people (Generative-Agents style), used for the people near the agent ("level of detail", as
open-world games do it). Far people keep the scripted routines of world.py.

A mind has:
  - a persona: who this person is, in a few sentences, built from their facts (role, age, family) and a temperament;
  - a memory stream: what they did, saw, heard and said, with an importance score; recent and important memories are
    recalled when they speak;
  - speech: when two people meet, the model writes what one says to the other, in short everyday English, from their
    persona, memories and the moment.

The model is pluggable: OllamaModel talks to a local Ollama server (on a cloud machine, never the creator's PC);
MockModel returns fixed lines, for code tests without any model. Every call is counted against a budget per world-day.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass, field

TEMPERAMENTS = ("warm and patient", "cheerful and talkative", "quiet and thoughtful", "practical and busy",
                "anxious but caring", "playful and teasing", "strict but fair", "gentle and shy")


class MockModel:
    """For code tests: no model, fixed short lines."""
    name = "mock"

    def __init__(self):
        self.calls = 0

    def chat(self, system: str, messages: list, max_tokens: int = 60) -> str:
        self.calls += 1
        lines = ("Good morning, how did you sleep?", "Look at her, she is smiling.", "Can you pass me the bread?",
                 "Time for school, come on.", "I am tired today.", "Thank you, that helps a lot.")
        return lines[self.calls % len(lines)]


class OllamaModel:
    def __init__(self, model: str = "qwen2.5:3b", url: str = "http://localhost:11434/api/chat"):
        self.name, self.url = model, url
        self.calls, self.tokens, self.seconds = 0, 0, 0.0

    def chat(self, system: str, messages: list, max_tokens: int = 60) -> str:
        body = {"model": self.name, "stream": False, "options": {"temperature": 0.8, "num_predict": max_tokens},
                "messages": [{"role": "system", "content": system}] + messages}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=600) as r:
            out = json.loads(r.read())
        self.calls += 1
        self.tokens += out.get("eval_count", 0)
        self.seconds += time.time() - t0
        return out["message"]["content"].strip()


@dataclass
class Memory:
    hour: int
    text: str
    importance: float = 0.3


@dataclass
class Mind:
    pid: int
    persona: str
    memories: list = field(default_factory=list)

    def remember(self, hour: int, text: str, importance: float = 0.3) -> None:
        self.memories.append(Memory(hour, text, importance))
        if len(self.memories) > 200:                       # keep the important and the recent
            self.memories.sort(key=lambda m: (m.importance, m.hour))
            self.memories = self.memories[-150:]
            self.memories.sort(key=lambda m: m.hour)

    def recall(self, hour: int, k: int = 5) -> list:
        """The most relevant memories now: recent ones count, important ones count more (a simple Generative-Agents
        score without embeddings)."""
        def score(m):
            recency = 0.995 ** max(0, hour - m.hour)
            return recency + m.importance
        return [m.text for m in sorted(self.memories, key=score, reverse=True)[:k]]

    def to_dict(self) -> dict:
        return {"pid": self.pid, "persona": self.persona, "memories": [[m.hour, m.text, m.importance] for m in self.memories]}

    @classmethod
    def from_dict(cls, d: dict) -> "Mind":
        return cls(d["pid"], d["persona"], [Memory(*m) for m in d["memories"]])


def persona_of(city, p) -> str:
    """Who this person is, from the city's facts about them, with a temperament fixed by a rule on who they are."""
    age = int(p.age(city.hour))
    temper = TEMPERAMENTS[(p.id * 7 + int(p.born)) % len(TEMPERAMENTS)]
    job = {"doctor": "a doctor at the city clinic", "teacher": "a teacher at the city school",
           "shopkeeper": "a shopkeeper at the market", "worker": f"a worker at the {p.work}",
           "retired": "retired", "student": "a school student", "child": "a small child"}.get(p.role, p.role)
    fam = []
    if p.partner and p.partner in city.people:
        fam.append(f"your partner is {city.people[p.partner].name}")
    kids = [city.people[c] for c in p.children if c in city.people and city.people[c].alive]
    if kids:
        fam.append("your children are " + ", ".join(f"{k.name} ({int(k.age(city.hour))})" for k in kids))
    if p.mother and p.mother in city.people:
        fam.append(f"your mother is {city.people[p.mother].name}")
    return (f"You are {p.name}, {age} years old, {job}. You are {temper}. " + ("; ".join(fam) + ". " if fam else "")
            + "You live an ordinary life in a small city.")


SPEAK = ("Say one or two short sentences, in plain everyday English, as people really talk. To a baby or a small child, "
         "speak simply and warmly. Do not describe actions and do not narrate; give only the words said aloud.")


class Minds:
    """All the minds in the city, the model, and the budget of model calls per world-day."""

    def __init__(self, model, calls_per_day: int = 8):
        self.model = model
        self.calls_per_day = calls_per_day
        self.by_pid: dict[int, Mind] = {}
        self.spent_today = 0
        self.day = -1

    def mind(self, city, p) -> Mind:
        if p.id not in self.by_pid:
            self.by_pid[p.id] = Mind(p.id, persona_of(city, p))
        return self.by_pid[p.id]

    def can_speak(self, city) -> bool:
        day = city.hour // 24
        if day != self.day:
            self.day, self.spent_today = day, 0
        return self.spent_today < self.calls_per_day

    def speak(self, city, p, q, act: str) -> str | None:
        """What p says to q now, written by the model from p's persona and memories; both remember it."""
        if not self.can_speak(city):
            return None
        mp = self.mind(city, p)
        h = city.hour % 24
        scene = (f"It is {h}:00. You are {act} at {where(city, p)}. With you is {q.name}, "
                 f"{int(q.age(city.hour))} years old" + (", your child" if q.id in p.children else "")
                 + (", your partner" if q.id == p.partner else "") + ".")
        mem = mp.recall(city.hour)
        system = mp.persona + " " + SPEAK + (" Things on your mind: " + " | ".join(mem) if mem else "")
        text = self.model.chat(system, [{"role": "user", "content": scene}])
        self.spent_today += 1
        if text.startswith(p.name + ":"):
            text = text.split(":", 1)[1].strip()
        mp.remember(city.hour, f"I said to {q.name}: {text}", 0.3)
        if q.id in self.by_pid or q.age(city.hour) >= 3:
            self.mind(city, q).remember(city.hour, f"{p.name} said to me: {text}", 0.3)
        return text

    def to_dict(self) -> dict:
        return {"calls_per_day": self.calls_per_day, "minds": [m.to_dict() for m in self.by_pid.values()]}

    def load(self, d: dict) -> None:
        self.calls_per_day = d["calls_per_day"]
        self.by_pid = {m["pid"]: Mind.from_dict(m) for m in d["minds"]}


def where(city, p) -> str:
    from .world import PLACES
    for name, (x, y, _) in PLACES.items():
        if (x, y) == tuple(p.loc):
            return f"the {name}"
    return "home" if tuple(p.loc) == tuple(p.home) else "the street"
