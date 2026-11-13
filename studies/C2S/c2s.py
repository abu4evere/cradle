"""C2-S: copy who succeeds (studies/C2S/questions.md, frozen as C2S-frozen). Built on C2's code (studies/C2/c2.py).

C2's 6 toy boxes, each opened by its own ordered pair of acts. On days 1-30, before each try, Ann (always right) or Ben
(a consistently wrong model: his own wrong pair per kind 80% of the time, the right pair 20%) demonstrates; half the
results are hidden (all in the "100" arms). Arms differ in how much the child copies each demonstration (the weight w).

  python studies/C2S/c2s.py one ARM SEED OUT_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ARMS = ("T", "I", "Cb", "Co", "Ct", "Cy", "Cp", "Cpx", "Ca", "Cb100", "Cp100")
KINDS, ACTS, LOOK, HID = 6, 4, 16, 32
N_IN = LOOK + 2 + 4 + 4 + 1 + 1 + 4 + 1   # look, who, demo act 1, demo act 2, result seen, opened, own first act, step
DAYS, DEMO_DAYS = 60, 30
TEST_DAYS = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60]
LR, BASE_RATE, CLIP, COPY_RATE = 0.05, 0.01, 1.0, 0.5
NOVEL = 3
BEN_RIGHT, HIDDEN = 0.2, 0.5
TRUST0, TRUST_RATE, TRUST_FLOOR = 0.5, 0.3, 0.25
ANN, BEN = 0, 1


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
        self.habits = []                                   # Ben's fixed wrong pair per kind
        for k in range(KINDS):
            right = self.pairs[k][0] * ACTS + self.pairs[k][1]
            w = int(h.integers(ACTS * ACTS - 1))
            w = w + (w >= right)
            self.habits.append((w // ACTS, w % ACTS))
        self.seed = seed

    def day(self, d):
        """The day's tries, the same draws in every arm: (kind, look, who, ben_right, hidden, coin_y, coin_px)."""
        r = np.random.default_rng([self.seed, 2, d])
        out = []
        for k in r.permutation(KINDS):
            k = int(k)
            look = self.looks[k] + r.normal(0, 0.2, LOOK)
            who = int(r.integers(2))
            ben_right = bool(r.random() < BEN_RIGHT)
            hidden = bool(r.random() < HIDDEN)
            coin_y = int(r.integers(2))
            coin_px = int(r.integers(2))
            out.append((k, look, who, ben_right, hidden, coin_y, coin_px))
        return out


class Child:
    def __init__(self, seed):
        r = np.random.default_rng([seed, 4])
        self.p = {"W": r.normal(0, 0.1, (HID, N_IN)), "b": np.zeros(HID), "M": r.normal(0, 0.1, (ACTS, HID)),
                  "c": np.zeros(ACTS)}
        self.base = 0.0

    def x(self, look, demo, own_first, step):
        """demo: None, or dict(who, a1, a2, seen, opened)."""
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
        """Gradient (to subtract) of -scale * log pi(a | x)."""
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


def norm(trust, p):
    return trust[p] / max(trust[ANN], trust[BEN], TRUST_FLOOR)


def test(home, child, seed, d):
    r = np.random.default_rng([seed, 6, d])
    ok = [try_box(child, home.looks[k] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[k])[1]
          for k in range(KINDS)]
    nov = [try_box(child, home.novel[j] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[j])[1]
           for j in range(NOVEL)]
    return {"success": float(np.mean(ok)), "novel": float(np.mean(nov))}


def demonstration(home, arm, k, who, ben_right, hidden):
    pair = home.pairs[k]
    if arm == "Ca":
        who = ANN
    shown = pair if (who == ANN or ben_right) else home.habits[k]
    seen = not (hidden or arm in ("Cb100", "Cp100"))
    return {"who": who, "a1": shown[0], "a2": shown[1], "seen": seen, "opened": shown == pair}


def run(arm, seed, out=None):
    home = Home(seed)
    child = Child(seed)
    rng = np.random.default_rng([seed, 3, ARMS.index(arm)])
    trust_ct = [TRUST0, TRUST0]         # Ct's trust: from the demonstration stream only (also drives Cy)
    trust_p = [TRUST0, TRUST0]          # Cp / Cpx / Cp100's trust: from the child's own tries
    tries, tests, trust_log = [], {}, []
    for d in range(1, DAYS + 1):
        for k, look, who, ben_right, hidden, coin_y, coin_px in home.day(d):
            pair = home.pairs[k]
            demo, w = None, 0.0
            if d <= DEMO_DAYS and arm != "T":
                demo = demonstration(home, arm, k, who, ben_right, hidden)
                p = demo["who"]
                ct_w = {q: norm(trust_ct, q) for q in (ANN, BEN)}          # before this demonstration's result
                if arm in ("Cb", "Ca", "Cb100"):
                    w = 1.0
                elif arm == "Co":
                    w = 1.0 if (demo["seen"] and demo["opened"]) else 0.0
                elif arm == "Ct":
                    w = ct_w[p]
                elif arm == "Cy":
                    w = ct_w[coin_y]
                elif arm in ("Cp", "Cpx", "Cp100"):
                    w = norm(trust_p, p)
                if demo["seen"]:                                           # Ct's trust: seen results only
                    trust_ct[p] += TRUST_RATE * ((1.0 if demo["opened"] else 0.0) - trust_ct[p])
                if arm != "I":
                    copy_step(child, look, demo, w)
            got, r = try_box(child, look, demo, rng, True, pair)
            if demo is not None and arm in ("Cp", "Cpx", "Cp100") and got == (demo["a1"], demo["a2"]):
                q = demo["who"] if arm != "Cpx" else coin_px
                trust_p[q] += TRUST_RATE * (r - trust_p[q])
            tries.append({"d": d, "k": k, "who": None if demo is None else demo["who"],
                          "shown": None if demo is None else [demo["a1"], demo["a2"]],
                          "seen": None if demo is None else demo["seen"], "w": w, "habit": list(home.habits[k]),
                          "pair": list(got), "r": r})
        if d <= DEMO_DAYS:
            trust_log.append({"d": d, "ct": list(trust_ct), "p": list(trust_p)})
        if d in TEST_DAYS:
            tests[d] = test(home, child, seed, d)
    res = {"arm": arm, "seed": seed, "pairs": home.pairs, "habits": home.habits, "tests": tests, "tries": tries,
           "trust": trust_log}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], int(sys.argv[3]), sys.argv[4])
        print(sys.argv[2], sys.argv[3], {d: round(t["success"], 2) for d, t in r["tests"].items()}, flush=True)
