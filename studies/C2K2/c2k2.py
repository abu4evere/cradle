"""C2-K2: skills that build on each other, difficulty check first (studies/C2K2/questions.md, C2K2-frozen). Built on C2-K.

Changes from C2-K: step-by-step teaching (lid j copied just before its attempt, only when reached) and a difficulty
level (LIDS, TRIES per kind per day) set by set_level() from difficulty.json or the pilot.

6 kinds of box, each with 3 lids; each lid opens by its own ordered pair of acts. Condition G (cumulative): a wrong lid
ends the try, and lids 2-3 are copied only when the child reached them. Condition U (flat): every lid is tried and every
shown lid copied. Days 1-30: Ann (expert for kinds 0-2) or Ben (3-5) demonstrates; a demonstration stops at the
demonstrator's first wrong lid.

  python studies/C2K2/c2k2.py one ARM COND SEED OUT_DIR   (level from difficulty.json)        (COND: G or U)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ARMS = ("T", "I", "Cb", "Ctk", "Cyk", "Cok", "Cr")
CONDS = ("G", "U")
KINDS, ACTS, LOOK, HID = 6, 4, 16, 32
MAXL = 3                                                  # the lid one-hot is always 3 wide
N_IN = LOOK + 2 + 4 + 4 + 1 + 1 + MAXL + 4 + 1          # 36
LEVELS = {"L1": (3, 1), "L2": (2, 1), "L3": (2, 3)}     # (lids, tries per kind per day)
LIDS, TRIES = 3, 1


def set_level(name):
    global LIDS, TRIES
    LIDS, TRIES = LEVELS[name]
DAYS, DEMO_DAYS = 60, 30
TEST_DAYS = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60]
LR, BASE_RATE, CLIP, COPY_RATE = 0.05, 0.01, 1.0, 0.5
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
        self.pairs = []
        for k in range(KINDS):
            ps = r.permutation(ACTS * ACTS)[:LIDS]
            self.pairs.append([(int(p) // ACTS, int(p) % ACTS) for p in ps])
        h = np.random.default_rng([seed, 7])
        self.habits = [[[None] * LIDS for _ in range(KINDS)] for _ in (ANN, BEN)]
        for p in (ANN, BEN):
            for k in range(KINDS):
                for j in range(LIDS):
                    right = self.pairs[k][j][0] * ACTS + self.pairs[k][j][1]
                    w = int(h.integers(ACTS * ACTS - 1))
                    w = w + (w >= right)
                    self.habits[p][k][j] = (w // ACTS, w % ACTS)
        self.seed = seed

    def day(self, d):
        """The day's tries, the same draws everywhere: (kind, look, who, u per lid, hidden, coin_y, coin_r)."""
        r = np.random.default_rng([self.seed, 2, d])
        out = []
        for k in np.tile(r.permutation(KINDS), TRIES):
            k = int(k)
            look = self.looks[k] + r.normal(0, 0.2, LOOK)
            who = int(r.integers(2))
            u = [float(x) for x in r.random(LIDS)]
            hidden = bool(r.random() < HIDDEN)
            coin_y = int(r.integers(2))
            coin_r = int(r.integers(2))
            out.append((k, look, who, u, hidden, coin_y, coin_r))
        return out


def demonstration(home, k, who, u, hidden):
    """Shown pairs lid by lid, stopping at the demonstrator's first wrong lid (that wrong attempt is shown)."""
    rate = EXPERT_RIGHT if who == expert_of(k) else OTHER_RIGHT
    shown, opened = [], 0
    for j in range(LIDS):
        right = u[j] < rate
        shown.append(home.pairs[k][j] if right else home.habits[who][k][j])
        if not right:
            break
        opened += 1
    return {"who": who, "shown": shown, "opened": opened, "seen": not hidden}


class Child:
    def __init__(self, seed):
        r = np.random.default_rng([seed, 4])
        self.p = {"W": r.normal(0, 0.1, (HID, N_IN)), "b": np.zeros(HID), "M": r.normal(0, 0.1, (ACTS, HID)),
                  "c": np.zeros(ACTS)}
        self.base = 0.0

    def x(self, look, demo, lid, own_first, step):
        who = np.zeros(2)
        d1 = d2 = np.zeros(ACTS)
        seen = opened = 0.0
        if demo is not None:
            who[demo["who"]] = 1.0
            if lid < len(demo["shown"]):
                d1, d2 = one_hot(demo["shown"][lid][0]), one_hot(demo["shown"][lid][1])
            seen = 1.0 if demo["seen"] else 0.0
            opened = demo["opened"] / LIDS if demo["seen"] else 0.0
        return np.concatenate([look, who, d1, d2, [seen], [opened], one_hot(lid, MAXL), one_hot(own_first),
                               [float(step)]])

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


def try_box(child, look, demo, rng, learn, pairs, cond, copy=None):
    """Works the lids in order. Returns (lids reached, lids opened, reward, the pairs chosen)."""
    reached, opened, total, chosen = 0, 0, 0.0, []
    for j in range(LIDS):
        reached += 1
        if copy is not None:
            copy(j)                                       # step by step: lid j copied just before its attempt
        x1 = child.x(look, demo, j, None, 0)
        _, z1 = child.logits(x1)
        a1 = int(rng.choice(ACTS, p=softmax(z1))) if learn else int(np.argmax(z1))
        x2 = child.x(look, demo, j, a1, 1)
        _, z2 = child.logits(x2)
        a2 = int(rng.choice(ACTS, p=softmax(z2))) if learn else int(np.argmax(z2))
        ok = (a1, a2) == pairs[j]
        r = (1.0 / LIDS) if ok else 0.0
        chosen.append([a1, a2])
        if learn:
            adv = r - child.base
            child.base += BASE_RATE * (r - child.base)
            child.apply([child.grad(x1, a1, adv), child.grad(x2, a2, adv)], LR)
        if ok:
            opened += 1
            total += r
        elif cond == "G" or not learn:
            break
    return reached, opened, total, chosen


def copy_lid(child, look, demo, j, w):
    if w <= 0 or j >= len(demo["shown"]):
        return 0
    a1, a2 = demo["shown"][j]
    x1 = child.x(look, demo, j, None, 0)
    x2 = child.x(look, demo, j, a1, 1)
    child.apply([child.grad(x1, a1, 1.0), child.grad(x2, a2, 1.0)], LR * COPY_RATE * w)
    return 1


def test(home, child, seed, d):
    r = np.random.default_rng([seed, 6, d])
    full, part = [], []
    for k in range(KINDS):
        _, op, _, _ = try_box(child, home.looks[k] + r.normal(0, 0.2, LOOK), None, None, False, home.pairs[k], "G")
        full.append(1.0 if op == LIDS else 0.0)
        part.append(op / LIDS)
    return {"success": float(np.mean(full)), "partial": float(np.mean(part))}


def wnorm(ta, tb, tp):
    return tp / max(ta, tb, TRUST_FLOOR)


def run(arm, cond, seed, out=None):
    home = Home(seed)
    child = Child(seed)
    rng = np.random.default_rng([seed, 3, ARMS.index(arm), CONDS.index(cond)])
    t = [[TRUST0] * KINDS, [TRUST0] * KINDS]
    tries, tests, copies_by_lid, wsum = [], {}, [0] * MAXL, 0.0
    for d in range(1, DAYS + 1):
        for k, look, who, u, hidden, coin_y, coin_r in home.day(d):
            demo, w = None, 0.0
            if d <= DEMO_DAYS and arm != "T":
                demo = demonstration(home, k, who, u, hidden)
                p = demo["who"]
                if arm == "Cb":
                    w = 1.0
                elif arm == "Ctk":
                    w = wnorm(t[ANN][k], t[BEN][k], t[p][k])
                elif arm == "Cyk":
                    w = wnorm(t[ANN][k], t[BEN][k], t[coin_y][k])
                elif arm == "Cok":
                    w = 1.0 if p == expert_of(k) else 0.0
                elif arm == "Cr":
                    w = float(coin_r)
                if demo["seen"]:                         # Ctk's trust (also drives Cyk), independent of the child
                    t[p][k] += TRUST_RATE * (demo["opened"] / LIDS - t[p][k])
            cp = None
            if demo is not None and arm != "I":
                def cp(j, _demo=demo, _look=look, _w=w):
                    copies_by_lid[j] += copy_lid(child, _look, _demo, j, _w)
            reached, opened, rew, chosen = try_box(child, look, demo, rng, True, home.pairs[k], cond, cp)
            if demo is not None and arm != "I" and w > 0:
                wsum += w
            tries.append({"d": d, "k": k, "who": None if demo is None else demo["who"],
                          "shown": None if demo is None else demo["shown"], "seen": None if demo is None else demo["seen"],
                          "demo_opened": None if demo is None else demo["opened"], "w": w, "reached": reached,
                          "opened": opened, "r": rew, "chosen": chosen})
        if d in TEST_DAYS:
            tests[d] = test(home, child, seed, d)
    res = {"arm": arm, "cond": cond, "seed": seed, "pairs": home.pairs, "habits": home.habits, "tests": tests,
           "tries": tries, "trust": t, "copies_by_lid": copies_by_lid, "copy_weight_sum": wsum}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_{cond}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        set_level(json.loads((Path(__file__).parent / "difficulty.json").read_text())["level"])
        r = run(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
        print(sys.argv[2], sys.argv[3], sys.argv[4], {d: round(v["success"], 2) for d, v in r["tests"].items()}, flush=True)
