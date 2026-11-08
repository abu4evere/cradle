"""The Director: the assistant as an unseen ghost who writes Cradle's history as it happens (PLAN.md, "The Director").

The routine hours run by themselves. Once a world month, and at once when something notable happens near the focus (a
birth, a death, an illness), the world reaches a pause point.
  - Live (the ghost in a session): the pause point is written to a file (`pause.json`: who, where, what just happened)
    and the run stops; the ghost reads it, decides, and resumes the run with its decisions (`apply`).
  - Autopilot (between sessions): the director picks from the ghost's own library of situations, by weight and pacing
    (quiet stretches and eventful ones).
Every decision, live or autopilot, goes into the chronicle with who made it, so what the director did and what the
agent did can always be told apart. Situations touch the focus's world naturally; nothing tells anyone a story is
being written (the Neo principle).
"""
from __future__ import annotations

import json
import random

from .world import HOURS_PER_DAY, HOURS_PER_YEAR, PLACES, WORK_SITES

MONTH_DAYS = 30


def _focus_people(city):
    return [city.people[i] for i in sorted(city.focus) if i in city.people and city.people[i].alive]


# --- the ghost's library of situations: (id, size, weight, can(city) -> bool, do(city, rng) -> text) ----------------------
def _sick(city, rng):
    fam = _focus_people(city)
    p = rng.choice(fam)
    p.sick = 0.8
    return f"{p.name} falls ill with a fever."


def _visit(city, rng):
    fam = _focus_people(city)
    home = fam[0].home if fam else None
    others = [q for q in city.living() if q.id not in city.focus and q.age(city.hour) >= 18]
    if not others or home is None:
        return None
    q = rng.choice(others)
    q.loc = home
    for p in fam:
        p.friends[q.id] = p.friends.get(q.id, 0.0) + 0.2
        q.friends[p.id] = q.friends.get(p.id, 0.0) + 0.2
    return f"{q.name}, a neighbour, drops by the house and stays for tea."


def _festival(city, rng):
    x, y, _ = PLACES["park"]
    for p in city.living():
        if rng.random() < 0.7:
            p.loc = (x, y)
            p.doing = "festival"
    return "The city holds its spring festival in the park; almost everyone comes."


def _storm(city, rng):
    for p in city.living():
        p.loc = p.home
        p.doing = "shelter"
    return "A storm hits the city; everyone stays home."


def _job_change(city, rng):
    fam = [p for p in _focus_people(city) if p.role in ("worker", "shopkeeper")]
    if not fam:
        return None
    p = rng.choice(fam)
    p.work = rng.choice([w for w in WORK_SITES if w != p.work])
    return f"{p.name} starts a new job at the {p.work}."


def _friend_moves(city, rng):
    fam = _focus_people(city)
    pairs = [(p, f) for p in fam for f in p.friends if f in city.people and city.people[f].alive and f not in city.focus]
    if not pairs:
        return None
    p, fid = rng.choice(pairs)
    f = city.people[fid]
    f.alive, f.died = False, city.hour          # leaves the city: gone from this world, as a death is
    f.doing = "moved away"
    return f"{f.name}, a friend of {p.name}, moves away to another city."


def _lost_thing(city, rng):
    fam = [p for p in _focus_people(city) if p.age(city.hour) < 12]
    if not fam:
        return None
    p = rng.choice(fam)
    return f"{p.name} loses a favourite toy in the park; the family looks for it all evening."


LIBRARY = [
    ("sick", "big", 1.0, lambda c: bool(_focus_people(c)), _sick),
    ("visit", "small", 3.0, lambda c: bool(_focus_people(c)), _visit),
    ("festival", "big", 0.6, lambda c: True, _festival),
    ("storm", "small", 1.0, lambda c: True, _storm),
    ("job_change", "big", 0.4, lambda c: bool(_focus_people(c)), _job_change),
    ("friend_moves", "big", 0.4, lambda c: bool(_focus_people(c)), _friend_moves),
    ("lost_thing", "small", 1.5, lambda c: bool(_focus_people(c)), _lost_thing),
]
BY_ID = {e[0]: e for e in LIBRARY}


class Director:
    def __init__(self, seed: int = 1, live: bool = False, pause_file: str = "pause.json"):
        self.rng = random.Random(seed * 7919 + 17)
        self.live = live
        self.pause_file = pause_file
        self.chronicle: list = []          # {hour, by, event, text}
        self.paused = False
        self.quiet = 0                     # months since the last big event (pacing)
        self.seen_focus_births: set = set()
        self.ill: set = set()               # who is already known to be sick (noticed once, until they recover)

    # called once a day by the city
    def day(self, city) -> None:
        notable = self._notable(city)
        month = (city.hour // HOURS_PER_DAY) % MONTH_DAYS == 0
        if not (month or notable):
            return
        if self.live:
            self._pause(city, notable)
        else:
            self._autopilot(city, notable)

    def _notable(self, city) -> list:
        out = []
        for p in _focus_people(city):
            for c in p.children:
                if c not in self.seen_focus_births and c in city.people and city.people[c].born >= city.hour - HOURS_PER_DAY:
                    self.seen_focus_births.add(c)
                    out.append(f"{city.people[c].name} is born to {p.name}.")
            if p.sick > 0.5 and p.id not in self.ill:
                self.ill.add(p.id)
                out.append(f"{p.name} is sick.")
            elif p.sick <= 0.5:
                self.ill.discard(p.id)
        return out

    def _autopilot(self, city, notable) -> None:
        for n in notable:
            self.chronicle.append({"hour": city.hour, "by": "world", "event": "notable", "text": n})
        if (city.hour // HOURS_PER_DAY) % MONTH_DAYS != 0:
            return                                                     # the ghost's autopilot acts monthly
        self.quiet += 1
        big_due = self.quiet >= 6 and self.rng.random() < 0.5          # quiet stretches, then something big
        pool = [e for e in LIBRARY if e[3](city) and ((e[1] == "big") == big_due or e[1] == "small")]
        if not pool or self.rng.random() < 0.3:
            return                                                     # some months nothing happens
        tot = sum(e[2] for e in pool)
        r, pick = self.rng.random() * tot, pool[-1]
        for e in pool:
            r -= e[2]
            if r <= 0:
                pick = e
                break
        self.apply(city, pick[0], by="autopilot")

    def apply(self, city, event_id: str, by: str = "ghost", note: str = "") -> str | None:
        e = BY_ID[event_id]
        text = e[4](city, self.rng)
        if text:
            if e[1] == "big":
                self.quiet = 0
            self.chronicle.append({"hour": city.hour, "by": by, "event": event_id, "text": text + (f" ({note})" if note else "")})
        return text

    def _pause(self, city, notable) -> None:
        """Live: write what the ghost needs to decide, and ask the run to stop here."""
        fam = [{"id": p.id, "name": p.name, "age": round(p.age(city.hour), 1), "role": p.role, "doing": p.doing,
                "sick": p.sick > 0.5} for p in _focus_people(city)]
        state = {"year": round(city.hour / HOURS_PER_YEAR, 2), "focus": fam, "notable": notable,
                 "recent_speech": [list(x) for x in city.log[-20:]], "library": [e[0] for e in LIBRARY]}
        with open(self.pause_file, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=1)
        self.paused = True

    def to_dict(self) -> dict:
        return {"rng": repr(self.rng.getstate()), "live": self.live, "pause_file": self.pause_file,
                "chronicle": self.chronicle, "quiet": self.quiet, "seen": sorted(self.seen_focus_births),
                "ill": sorted(self.ill)}

    @classmethod
    def from_dict(cls, d: dict) -> "Director":
        import ast
        x = cls(live=d["live"], pause_file=d["pause_file"])
        x.rng.setstate(ast.literal_eval(d["rng"]))
        x.chronicle, x.quiet, x.seen_focus_births = d["chronicle"], d["quiet"], set(d["seen"])
        x.ill = set(d.get("ill", []))
        return x
