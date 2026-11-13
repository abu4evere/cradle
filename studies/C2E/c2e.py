"""C2-E: experts and costly practice (studies/C2E/questions.md, frozen as C2E-frozen). Built on C2-S's code.

C2-S's 6 toy boxes. Days 1-30: before each of 6 daily slots (one per kind) Ann or Ben demonstrates. Ann is the expert
for kinds 0-2, Ben for 3-5 (right pair 0.85 on their own kinds, 0.25 on the others; otherwise their own wrong habit).
Practice F: an own try in every slot; S: an own try only in the slot of kind (d-1) mod 6. Arms differ in the copy
weight w.

  python studies/C2E/c2e.py one ARM PRACTICE SEED OUT_DIR       (PRACTICE: F or S)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ARMS = ("T", "I", "Cb", "Ct", "Ctk", "Cyk", "Cok", "Cp", "Cpk")
PRACTICE = ("F", "S")
KINDS, ACTS, LOOK, HID = 6, 4, 16, 32
N_IN = LOOK + 2 + 4 + 4 + 1 + 1 + 4 + 1
DAYS, DEMO_DAYS = 60, 30
TEST_DAYS = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60]
LR, BASE_RATE, CLIP, COPY_RATE = 0.05, 0.01, 1.0, 0.5
NOVEL = 3
EXPERT_RIGHT, OTHER_RIGHT, HIDDEN = 0.85, 0.25, 0.5
TRUST0, TRUST_RATE, TRUST_FLOOR = 0.5, 0.3, 0.25
ANN, BEN = 0, 1


def expert_of(k):
    return ANN if k < 3 else BEN


def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()


def one_hot(i, n=ACTS):
    v = np.zeros(n)
    if i is not None:
        v[i] = 1.0
    return v


class Home:
    def __init__(self, seed):
        r = np.random.default_rng([seed, 1])
        self.looks = r.normal(0, 1, (KINDS, LOOK))
        pairs = r.permutation(ACTS * ACTS)[:KINDS]
        self.pairs = [(int(p) // ACTS, int(p) % ACTS) for p in pairs]
        self.novel = np.random.default_rng([seed, 5]).normal(0, 1, (NOVEL, LOOK))
        h = np.random.default_rng([seed, 7])
        self.habits = [[], []]                            # each person's fixed wrong pair per kind
        for p in (ANN, BEN):
            for k in range(KINDS):
                right = self.pairs[k][0] * ACTS + self.pairs[k][1]
                w = int(h.integers(ACTS * ACTS - 1))
                w = w + (w >= right)
                self.habits[p].append((w // ACTS, w % ACTS))
        self.seed = seed

    def day(self, d):
        """The day's 6 slots, the same draws in every arm and practice level:
        (kind, look, who, right_draw, hidden, coin)."""
        r = np.random.default_rng([self.seed, 2, d])
        out = []
        for k in r.permutation(KINDS):
            k = int(k)
            look = self.looks[k] + r.normal(0, 0.2, LOOK)
            who = int(r.integers(2))
            u = float(r.random())
            hidden = bool(r.random() < HIDDEN)
            coin = int(r.integers(2))
            out.append((k, look, who, u, hidden, coin))
        return out


class Child:
    def __init__(self, seed):
        r = np.random.default_rng([seed, 4])
        self.p = {"W": r.normal(0, 0.1, (HID, N_IN)), "b": np.zeros(HID), "M": r.normal(0, 0.1, (ACTS, HID)),
                  "c": np.zeros(ACTS)}
        self.base = 0.0

    def x(self, look, demo, own_first, step):
        who = np.zeros(2)
        d1 = d2 = np.zeros(ACTS)
        seen = opened = 0.0
        if demo is not None:
            who[demo["who"]] = 1.0
            d1, d2 = one_hot(demo["a1"]), one_hot(demo["a2"])
            seen = 1.0 if demo["seen"] else 0.0
            opened = 1.0 if (demo["seen"] and demo["opened"]) else 0.0
        return np.concatenate([look, who, d1, d2, [seen], [opened], one_hot(own_first), [float(step)]])

    def logits(self, x):
        h = np.tanh(self.p["W"] @ x + self.p["b"])
        return h, self.p["M"] @ h + self.p["c"]

    def grad(self, x, a, scale):
        h, z = self.logits(x)
        dz = softmax(z)
        dz[a] -= 1.0
        dz *= scale
        dh = self.p["M"].T @ dz * (1.0 - h ** 2)
        return {"W": np.outer(dh, x), "b": dh, "M": np.outer(dz, h), "c": dz}

    def apply(self, gs, lr):
        g = {k: sum(gg[k] for gg in gs) for k in self.p}
        n = float(np.sqrt(sum(float((v * v).sum()) for v in g.values())))
        s = min(1.0, CLIP / n) if n > 0 else 1.0
        for k in self.p:
            self.p[k] -= lr * s * g[k]


def try_box(child, look, demo, rng, learn, pair):
    x1 = child.x(look, demo, None, 0)
    _, z1 = child.logits(x1)
    a1 = int(rng.choice(ACTS, p=softmax(z1))) if learn else int(np.argmax(z1))
    x2 = child.x(look, demo, a1, 1)
    _, z2 = child.logits(x2)
    a2 = int(rng.choice(ACTS, p=softmax(z2))) if learn else int(np.argmax(z2))
    r = 1.0 if (a1, a2) == pair else 0.0
    if learn:
        adv = r - child.base
        child.base += BASE_RATE * (r - child.base)
        child.apply([child.grad(x1, a1, adv), child.grad(x2, a2, adv)], LR)
    return (a1, a2), r


def copy_step(child, look, demo, w):
    if w <= 0:
        return
    x1 = child.x(look, demo, None, 0)
    x2 = child.x(look, demo, demo["a1"], 1)
    child.apply([child.grad(x1, demo["a1"], 1.0), child.grad(x2, demo["a2"], 1.0)], LR * COPY_RATE * w)


def test(home, child, seed, d):
    r = np.random.default_rng([seed, 6, d])
    ok = [try_box(child, home.looks[k] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[k])[1]
          for k in range(KINDS)]
    nov = [try_box(child, home.novel[j] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[j])[1]
           for j in range(NOVEL)]
    return {"success": float(np.mean(ok)), "novel": float(np.mean(nov))}


def demonstration(home, k, who, u, hidden):
    pair = home.pairs[k]
    right_p = EXPERT_RIGHT if who == expert_of(k) else OTHER_RIGHT
    shown = pair if u < right_p else home.habits[who][k]
    return {"who": who, "a1": shown[0], "a2": shown[1], "seen": not hidden, "opened": shown == pair}


def wnorm(t_a, t_b, t_p):
    return t_p / max(t_a, t_b, TRUST_FLOOR)


def run(arm, practice, seed, out=None):
    home = Home(seed)
    child = Child(seed)
    rng = np.random.default_rng([seed, 3, ARMS.index(arm), PRACTICE.index(practice)])
    t_ct = [TRUST0, TRUST0]                            # per person, from seen results (independent of the child)
    t_ctk = [[TRUST0] * KINDS, [TRUST0] * KINDS]       # per person and kind, from seen results
    t_p = [TRUST0, TRUST0]                             # per person, own experience
    t_pk = [[TRUST0] * KINDS, [TRUST0] * KINDS]        # per person and kind, own experience
    tries, tests, trust_log, wsum, ncopy, nown, nupd = [], {}, [], 0.0, 0, 0, 0
    for d in range(1, DAYS + 1):
        own_kind = (d - 1) % KINDS
        for k, look, who, u, hidden, coin in home.day(d):
            pair = home.pairs[k]
            demo, w = None, 0.0
            if d <= DEMO_DAYS and arm != "T":
                demo = demonstration(home, k, who, u, hidden)
                p = demo["who"]
                if arm == "Cb":
                    w = 1.0
                elif arm == "Ct":
                    w = wnorm(t_ct[ANN], t_ct[BEN], t_ct[p])
                elif arm == "Ctk":
                    w = wnorm(t_ctk[ANN][k], t_ctk[BEN][k], t_ctk[p][k])
                elif arm == "Cyk":
                    w = wnorm(t_ctk[ANN][k], t_ctk[BEN][k], t_ctk[coin][k])
                elif arm == "Cok":
                    w = 1.0 if p == expert_of(k) else 0.0
                elif arm == "Cp":
                    w = wnorm(t_p[ANN], t_p[BEN], t_p[p])
                elif arm == "Cpk":
                    w = wnorm(t_pk[ANN][k], t_pk[BEN][k], t_pk[p][k])
                if demo["seen"]:                         # seen-result trust (Ct, Ctk; also drives Cyk)
                    o = 1.0 if demo["opened"] else 0.0
                    t_ct[p] += TRUST_RATE * (o - t_ct[p])
                    t_ctk[p][k] += TRUST_RATE * (o - t_ctk[p][k])
                if arm != "I":
                    copy_step(child, look, demo, w)
                    if w > 0:
                        wsum += w
                        ncopy += 1
            if practice == "F" or k == own_kind:
                got, r = try_box(child, look, demo, rng, True, pair)
                nown += 1
                if demo is not None and arm in ("Cp", "Cpk") and got == (demo["a1"], demo["a2"]):
                    q = demo["who"]
                    t_p[q] += TRUST_RATE * (r - t_p[q])
                    t_pk[q][k] += TRUST_RATE * (r - t_pk[q][k])
                    nupd += 1
                tries.append({"d": d, "k": k, "who": None if demo is None else demo["who"],
                              "shown": None if demo is None else [demo["a1"], demo["a2"]],
                              "seen": None if demo is None else demo["seen"], "w": w, "pair": list(got), "r": r})
        if d <= DEMO_DAYS:
            trust_log.append({"d": d, "ct": list(t_ct), "ctk": [list(t_ctk[0]), list(t_ctk[1])],
                              "p": list(t_p), "pk": [list(t_pk[0]), list(t_pk[1])]})
        if d in TEST_DAYS:
            tests[d] = test(home, child, seed, d)
    res = {"arm": arm, "practice": practice, "seed": seed, "pairs": home.pairs, "habits": home.habits, "tests": tests,
           "tries": tries, "trust": trust_log, "copy_weight_sum": wsum, "copies": ncopy, "own_tries": nown,
           "trust_updates": nupd}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_{practice}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
        print(sys.argv[2], sys.argv[3], sys.argv[4], {d: round(t["success"], 2) for d, t in r["tests"].items()}, flush=True)
