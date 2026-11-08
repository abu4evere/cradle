"""Cradle v0: a small developed city whose people (NPCs) live ordinary lives, written by the assistant as a program.

Time moves in hours. Each NPC has a home, a family, a role (doctor, teacher, shopkeeper, worker, student, child,
retired) and a daily rhythm. Children are born, raised, schooled and grow up into jobs; people age and die. Everyone
speaks a small language of words (see `words.py`) about what is happening around them.

There is no agent in v0 (milestone 1: the city lives on its own). The design rule for later (the Neo principle): a
child of ours will be raised exactly as NPC children are; nothing in the city is made only for it.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from . import words

HOURS_PER_DAY, DAYS_PER_YEAR = 24, 360
HOURS_PER_YEAR = HOURS_PER_DAY * DAYS_PER_YEAR
W, H = 40, 30

PLACES = {                                  # name -> (x, y, kind)
    "school": (20, 10, "school"), "clinic": (28, 12, "clinic"), "market": (14, 15, "market"),
    "workshop": (32, 20, "work"), "farm": (6, 24, "work"), "office": (24, 22, "work"), "park": (18, 4, "park"),
}
ROLE_WORK = {"doctor": "clinic", "teacher": "school", "shopkeeper": "market", "worker": None}
WORK_SITES = ("workshop", "farm", "office")


@dataclass
class NPC:
    id: int
    name: str
    sex: str
    born: int                      # hour of birth
    home: tuple
    role: str = "child"
    work: str | None = None
    mother: int | None = None
    father: int | None = None
    partner: int | None = None
    children: list = field(default_factory=list)
    alive: bool = True
    died: int | None = None
    loc: tuple = (0, 0)
    hunger: float = 0.2
    tired: float = 0.2
    sick: float = 0.0
    doing: str = "sleep"
    known: dict = field(default_factory=dict)       # word -> how well known (children learn by hearing)
    friends: dict = field(default_factory=dict)     # id -> closeness

    def age(self, hour: int) -> float:
        return (hour - self.born) / HOURS_PER_YEAR


class City:
    def __init__(self, seed: int = 1, families: int = 12):
        self.rng = random.Random(seed)
        self.hour = 0
        self.people: dict[int, NPC] = {}
        self.next_id = 1
        self.log: list = []                 # (hour, speaker id, listener id, words) - what was said, for watching
        self.homes = [(4 + (k % 6) * 6, 2 + (k // 6) * 8) for k in range(families + 8)]
        self.minds = None                   # minds.Minds: model-driven speech for the people near the focus
        self.focus: set = set()             # the people whose lives get full minds (the agent's family, later)
        self.director = None                # director.Director: the ghost (or its autopilot)
        self._found(families)

    # --- people ---------------------------------------------------------------------------------------------------
    def _new(self, sex, born, home, **kw) -> NPC:
        p = NPC(self.next_id, words.name(self.rng), sex, born, home, loc=home, **kw)
        self.people[p.id] = p
        self.next_id += 1
        return p

    def _found(self, families: int) -> None:
        roles = ["doctor", "teacher", "teacher", "shopkeeper", "shopkeeper"] + ["worker"] * (2 * families)
        k = 0
        for f in range(families):
            home = self.homes[f]
            a = self._new("F", -self.rng.randint(25, 45) * HOURS_PER_YEAR, home)
            b = self._new("M", a.born - self.rng.randint(-3, 5) * HOURS_PER_YEAR, home)
            for adult in (a, b):
                adult.role = roles[k] if k < len(roles) else "worker"
                adult.work = ROLE_WORK.get(adult.role) or self.rng.choice(WORK_SITES)
                k += 1
            a.partner, b.partner = b.id, a.id
            for _ in range(self.rng.randint(0, 3)):
                c = self._new(self.rng.choice("FM"), -self.rng.randint(0, 15) * HOURS_PER_YEAR, home,
                              mother=a.id, father=b.id)
                c.role = "student" if c.age(0) >= 6 else "child"
                for w_ in list(words.VOCAB)[: int(min(c.age(0), 12) * 12)]:
                    c.known[w_] = 1.0           # older founding children already speak
                a.children.append(c.id)
                b.children.append(c.id)
            for adult in (a, b):
                for w_ in words.VOCAB:
                    adult.known[w_] = 1.0

    def living(self) -> list[NPC]:
        return [p for p in self.people.values() if p.alive]

    # --- one hour ---------------------------------------------------------------------------------------------------
    def step(self) -> None:
        h = self.hour % HOURS_PER_DAY
        day = (self.hour // HOURS_PER_DAY) % 7
        for p in sorted(self.living(), key=lambda q: q.id):
            self._live(p, h, day)
        if h == 0:
            self._daily()
            if self.director is not None:
                self.director.day(self)
        self.hour += 1

    def _live(self, p: NPC, h: int, day: int) -> None:
        age = p.age(self.hour)
        p.hunger = min(1.0, p.hunger + 0.04)
        p.tired = min(1.0, p.tired + 0.03)
        weekend = day >= 5
        if h < 6 or h >= 22:
            act, place = "sleep", p.home
        elif h in (7, 12, 19):
            act, place = "eat", p.home if h != 12 or age < 6 else (p.loc)
        elif p.sick > 0.5:
            act, place = "see doctor", PLACES["clinic"][:2]
        elif age < 3:
            act, place = "be cared for", self._carer_loc(p)
        elif age < 6:
            act, place = "play", p.home if h < 15 else PLACES["park"][:2]
        elif age < 18 and not weekend and 8 <= h < 15:
            act, place = "learn", PLACES["school"][:2]
        elif p.role in ROLE_WORK and p.role != "worker" and not weekend and 8 <= h < 17:
            act, place = "work", PLACES[p.work][:2]
        elif p.role == "worker" and not weekend and 8 <= h < 17:
            act, place = "work", PLACES[p.work][:2]
        elif 17 <= h < 19 and not weekend:
            act, place = "shop", PLACES["market"][:2]
        else:
            act, place = ("visit friends", PLACES["park"][:2]) if self.rng.random() < 0.3 else ("rest", p.home)
        p.doing, p.loc = act, place
        if act == "eat":
            p.hunger = 0.0
        if act == "sleep":
            p.tired = max(0.0, p.tired - 0.15)
        self._talk(p, act)

    def _carer_loc(self, p: NPC):
        mum = self.people.get(p.mother) if p.mother else None
        return mum.loc if mum is not None and mum.alive else p.home

    def _talk(self, p: NPC, act: str) -> None:
        """Speak a little about what is happening, to someone nearby: a parent to a child, a teacher to a class."""
        if act == "sleep" or self.rng.random() > 0.25:
            return
        near = [q for q in self.living() if q.id != p.id and q.loc == p.loc]
        if not near:
            return
        q = self.rng.choice(near)
        if self.minds is not None and (p.id in self.focus or q.id in self.focus):
            text = self.minds.speak(self, p, q, act)       # a full mind: English written by the model
            if text:
                self.log.append((self.hour, p.id, q.id, text))
                return
        said = words.say(self.rng, p, q, act, self)
        if said:
            self.log.append((self.hour, p.id, q.id, said))
            for w_ in said:                    # children pick up the words they hear
                if q.age(self.hour) < 18:
                    q.known[w_] = min(1.0, q.known.get(w_, 0.0) + 0.02)
            q.friends[p.id] = q.friends.get(p.id, 0.0) + 0.01
            p.friends[q.id] = p.friends.get(q.id, 0.0) + 0.01

    # --- once a day: illness, ageing, births, deaths, growing up -------------------------------------------------------
    def _daily(self) -> None:
        rng = self.rng
        for p in self.living():
            age = p.age(self.hour)
            if p.sick > 0:
                p.sick = max(0.0, p.sick - (0.2 if p.doing == "see doctor" else 0.05))
            elif rng.random() < 0.002:
                p.sick = 0.8
            if rng.random() < self._death_risk(age):
                p.alive, p.died = False, self.hour
            if 6 <= age < 18 and p.role == "child":
                p.role = "student"
            if age >= 18 and p.role == "student":
                p.role = rng.choice(["worker", "worker", "worker", "shopkeeper", "teacher", "doctor"])
                p.work = ROLE_WORK.get(p.role) or rng.choice(WORK_SITES)
            if age >= 65 and p.role not in ("retired", "child", "student"):
                p.role, p.work = "retired", None
        self._pair()
        self._births()
        if self.focus:                      # a focus family's newborns join the focus
            for i in list(self.focus):
                q = self.people.get(i)
                if q is not None:
                    self.focus.update(c for c in q.children if c in self.people and self.people[c].alive)

    def pick_focus(self) -> None:
        """For milestone 1's tests: the youngest founding couple and their children get full minds."""
        mums = sorted((p for p in self.living() if p.sex == "F" and p.partner and p.age(self.hour) < 36),
                      key=lambda p: (-p.born, p.id))
        if mums:
            m = mums[0]
            self.focus = {m.id, m.partner} | {c for c in m.children if self.people[c].alive}

    def _death_risk(self, age: float) -> float:
        if age < 1:
            return 0.00005
        if age < 60:
            return 0.00001
        return 0.00001 * 1.1 ** (age - 60) * 30

    def _pair(self) -> None:
        single = [p for p in self.living() if p.partner is None and 20 <= p.age(self.hour) < 40]
        f = [p for p in single if p.sex == "F"]
        m = [p for p in single if p.sex == "M"]
        if f and m and self.rng.random() < 0.02:
            a, b = self.rng.choice(f), self.rng.choice(m)
            if a.mother != b.mother:
                a.partner, b.partner = b.id, a.id
                free = [hm for hm in self.homes if not any(q.home == hm for q in self.living())]
                home = free[0] if free else a.home
                a.home = b.home = home

    def _births(self) -> None:
        for a in self.living():
            if a.sex != "F" or a.partner is None or not (20 <= a.age(self.hour) < 42):
                continue
            b = self.people.get(a.partner)
            if b is None or not b.alive or len(a.children) >= 3:
                continue
            last = max((self.people[c].born for c in a.children), default=-10 ** 9)
            if self.hour - last < 2 * HOURS_PER_YEAR or self.rng.random() > 0.0015:
                continue
            c = self._new(self.rng.choice("FM"), self.hour, a.home, mother=a.id, father=b.id)
            a.children.append(c.id)
            b.children.append(c.id)

    # --- reports ---------------------------------------------------------------------------------------------------
    def census(self) -> dict:
        liv = self.living()
        roles: dict = {}
        for p in liv:
            roles[p.role] = roles.get(p.role, 0) + 1
        kids = [p for p in liv if p.age(self.hour) < 18]
        vocab = sum(sum(1 for v in p.known.values() if v >= 0.5) for p in kids) / max(1, len(kids))
        return {"year": round(self.hour / HOURS_PER_YEAR, 2), "people": len(liv), "roles": roles,
                "children_words_known_mean": round(vocab, 1)}


def run(years: int = 30, seed: int = 1) -> None:
    c = City(seed)
    for y in range(years):
        for _ in range(HOURS_PER_YEAR):
            c.step()
        if (y + 1) % 5 == 0:
            print(json.dumps(c.census()), flush=True)


# --- save and resume (a long life spans many cloud jobs) ---------------------------------------------------------------
def save(city: City, path) -> None:
    from dataclasses import asdict
    d = {"hour": city.hour, "next_id": city.next_id, "homes": city.homes, "rng": repr(city.rng.getstate()),
         "people": [asdict(p) for p in city.people.values()], "focus": sorted(city.focus),
         "log_tail": city.log[-2000:],
         "minds": city.minds.to_dict() if city.minds is not None else None,
         "director": city.director.to_dict() if city.director is not None else None}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh)


def load(path, model=None) -> City:
    import ast
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    c = City.__new__(City)
    c.rng = random.Random()
    c.rng.setstate(ast.literal_eval(d["rng"]))
    c.hour, c.next_id = d["hour"], d["next_id"]
    c.homes = [tuple(h) for h in d["homes"]]
    c.people = {}
    for pd in d["people"]:
        pd["home"], pd["loc"] = tuple(pd["home"]), tuple(pd["loc"])
        pd["friends"] = {int(k): v for k, v in pd["friends"].items()}     # JSON keys come back as text
        c.people[pd["id"]] = NPC(**pd)
    c.focus = set(d["focus"])
    c.log = [tuple(x) for x in d["log_tail"]]
    c.minds = None
    if d["minds"] is not None:
        from .minds import Minds
        c.minds = Minds(model, d["minds"]["calls_per_day"])
        c.minds.load(d["minds"])
    c.director = None
    if d["director"] is not None:
        from .director import Director
        c.director = Director.from_dict(d["director"])
    return c
