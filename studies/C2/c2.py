"""C2: learning how (studies/C2/questions.md, frozen as C2-frozen).

6 kinds of toy box, each opened by its own ordered pair of acts (4 acts, 16 pairs). A day: 6 tries, one per kind.
Before each try in days 1-30 the older sibling demonstrates (arms differ in what the child sees and whether it copies).
  T  no demonstration     E  sees only that the box opened     I  sees the acts and that it opened
  Ic I + a blind copy step (half rate)      Iw  Ic, but a third of demonstrations use a wrong pair (it stays shut)

  python studies/C2/c2.py one ARM SEED OUT_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ARMS = ("T", "E", "I", "Ic", "Iw")
KINDS, ACTS, LOOK, HID = 6, 4, 16, 32
N_IN = LOOK + 4 + 4 + 1 + 4 + 1          # look, demo act 1, demo act 2, demo opened, own first act, step flag
DAYS, DEMO_DAYS = 60, 30
TEST_DAYS = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60]
LR, BASE_RATE, CLIP, COPY_RATE = 0.05, 0.01, 1.0, 0.5
NOVEL = 3


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
        self.seed = seed

    def day(self, d):
        """The day's tries: (kind, look seen, demo-wrong draw, the wrong pair) - the same draws in every arm."""
        r = np.random.default_rng([self.seed, 2, d])
        out = []
        for k in r.permutation(KINDS):
            k = int(k)
            look = self.looks[k] + r.normal(0, 0.2, LOOK)
            wrong = r.random() < 1 / 3
            wp = int(r.integers(ACTS * ACTS - 1))
            right = self.pairs[k][0] * ACTS + self.pairs[k][1]
            wp = wp + (wp >= right)
            out.append((k, look, wrong, (wp // ACTS, wp % ACTS)))
        return out


class Child:
    def __init__(self, seed):
        r = np.random.default_rng([seed, 4])
        self.p = {"W": r.normal(0, 0.1, (HID, N_IN)), "b": np.zeros(HID), "M": r.normal(0, 0.1, (ACTS, HID)),
                  "c": np.zeros(ACTS)}
        self.base = 0.0

    def x(self, look, demo, own_first, step):
        """demo: None (nothing seen), ("result", opened) or ("acts", a1, a2, opened)."""
        d1 = d2 = np.zeros(ACTS)
        opened = 0.0
        if demo is not None:
            opened = 1.0 if demo[-1] else 0.0
            if demo[0] == "acts":
                d1, d2 = one_hot(demo[1]), one_hot(demo[2])
        return np.concatenate([look, d1, d2, [opened], one_hot(own_first), [float(step)]])

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


def copy_step(child, look, demo, a1, a2):
    x1 = child.x(look, demo, None, 0)
    x2 = child.x(look, demo, a1, 1)
    child.apply([child.grad(x1, a1, 1.0), child.grad(x2, a2, 1.0)], LR * COPY_RATE)


def test(home, child, seed, d):
    r = np.random.default_rng([seed, 6, d])
    ok = [try_box(child, home.looks[k] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[k])[1]
          for k in range(KINDS)]
    nov = [try_box(child, home.novel[j] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[j])[1]
           for j in range(NOVEL)]
    return {"success": float(np.mean(ok)), "novel": float(np.mean(nov))}


def run(arm, seed, out=None):
    home = Home(seed)
    child = Child(seed)
    rng = np.random.default_rng([seed, 3, ARMS.index(arm)])
    tries, tests = [], {}
    for d in range(1, DAYS + 1):
        for k, look, wrong_draw, wpair in home.day(d):
            pair = home.pairs[k]
            demo = None
            if d <= DEMO_DAYS and arm != "T":
                shown = wpair if (arm == "Iw" and wrong_draw) else pair
                opened = shown == pair
                demo = ("result", opened) if arm == "E" else ("acts", shown[0], shown[1], opened)
                if arm in ("Ic", "Iw"):
                    copy_step(child, look, demo, shown[0], shown[1])
            got, r = try_box(child, look, demo, rng, True, pair)
            tries.append({"d": d, "k": k, "wrong_demo": bool(d <= DEMO_DAYS and wrong_draw), "wrong_pair": list(wpair),
                          "pair": list(got), "r": r})
        if d in TEST_DAYS:
            tests[d] = test(home, child, seed, d)
    res = {"arm": arm, "seed": seed, "pairs": home.pairs, "tests": tests, "tries": tries}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], int(sys.argv[3]), sys.argv[4])
        print(sys.argv[2], sys.argv[3], {d: round(t["success"], 2) for d, t in r["tests"].items()}, flush=True)
