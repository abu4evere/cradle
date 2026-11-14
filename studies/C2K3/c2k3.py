"""C2-K3: whom to copy when skills build on each other, with the memory brain (studies/C2K3/questions.md, C2K3-frozen).

C2-K's experts and arms; Mind Lab WS's Bm brain: a learned recurrent state; the showing (each shown act, its lid, who
showed it, the result if seen) is fed as steps just before the try and is not in view during it. Copy step before the
try toward every shown lid at 0.05 x 0.5 x w. G: a wrong lid ends the child's try; U: every lid is tried.

  python studies/C2K3/c2k3.py one ARM COND SEED OUT_DIR      (level from difficulty.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ARMS = ("T", "I", "Cb", "Ctk", "Cyk", "Cok", "Cr")
CONDS = ("G", "U")
KINDS, MAXL, ACTS, LOOK, HID = 6, 3, 4, 16, 32
TRIES, DAYS, DEMO_DAYS = 3, 60, 30
N_IN = LOOK + MAXL + ACTS + 1 + ACTS + 1 + 2 + 1 + 1      # look, lid, own first, step, shown act, flag, who, seen, opened
LR, BASE_RATE, CLIP, COPY_RATE = 0.05, 0.01, 1.0, 0.5
EXPERT_RIGHT, OTHER_RIGHT, HIDDEN = 0.85, 0.25, 0.5
TRUST0, TRUST_RATE, TRUST_FLOOR = 0.5, 0.3, 0.25
ANN, BEN = 0, 1
LEVELS = {"K1": 3, "K2": 2}
LIDS = 3
TEST_DAYS = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60]
SHOW0 = LOOK + MAXL + ACTS + 1                                # first index of the showing fields


def set_level(name):
    global LIDS
    LIDS = LEVELS[name]


def expert_of(k):
    return ANN if k < 3 else BEN


def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()


def oh(i, n):
    v = np.zeros(n)
    if i is not None:
        v[i] = 1.0
    return v


def x_try(look, lid, own_first, step):
    return np.concatenate([look, oh(lid, MAXL), oh(own_first, ACTS), [float(step)], np.zeros(N_IN - SHOW0)])


def show_steps(look, demo):
    """The showing as steps: 2 per shown lid (its acts), tagged with who showed it and the result if seen."""
    out = []
    seen = 1.0 if demo["seen"] else 0.0
    opened = demo["opened"] / LIDS if demo["seen"] else 0.0
    for j, pr in enumerate(demo["shown"]):
        for a in pr:
            out.append(np.concatenate([look, oh(j, MAXL), np.zeros(ACTS), [0.0], oh(a, ACTS), [1.0],
                                       oh(demo["who"], 2), [seen], [opened]]))
    return out


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
    rate = EXPERT_RIGHT if who == expert_of(k) else OTHER_RIGHT
    shown, opened = [], 0
    for j in range(LIDS):
        right = u[j] < rate
        shown.append(home.pairs[k][j] if right else home.habits[who][k][j])
        if not right:
            break
        opened += 1
    return {"who": who, "shown": shown, "opened": opened, "seen": not hidden}


class Net:
    """WS's recurrent network: h_t = tanh(Wx x_t + Wh h_(t-1) + b), act scores M h_t + c."""

    def __init__(self, seed):
        r = np.random.default_rng([seed, 4])
        self.p = {"Wx": r.normal(0, 0.1, (HID, N_IN)), "b": np.zeros(HID), "Wh": r.normal(0, 0.1, (HID, HID)),
                  "M": r.normal(0, 0.1, (ACTS, HID)), "c": np.zeros(ACTS)}
        self.base = 0.0

    def step(self, x, hprev):
        h = np.tanh(self.p["Wx"] @ x + self.p["Wh"] @ hprev + self.p["b"])
        return h, self.p["M"] @ h + self.p["c"]

    def grads(self, xs, hs, targets):
        g = {k: np.zeros_like(v) for k, v in self.p.items()}
        dh_next = np.zeros(HID)
        for t in reversed(range(len(xs))):
            h = hs[t]
            dh = dh_next.copy()
            if t in targets:
                a, scale = targets[t]
                dz = softmax(self.p["M"] @ h + self.p["c"])
                dz[a] -= 1.0
                dz *= scale
                g["M"] += np.outer(dz, h)
                g["c"] += dz
                dh += self.p["M"].T @ dz
            dpre = dh * (1.0 - h ** 2)
            g["Wx"] += np.outer(dpre, xs[t])
            g["b"] += dpre
            hp = hs[t - 1] if t > 0 else np.zeros(HID)
            g["Wh"] += np.outer(dpre, hp)
            dh_next = self.p["Wh"].T @ dpre
        return g

    def apply(self, g, lr):
        n = float(np.sqrt(sum(float((v * v).sum()) for v in g.values())))
        s = min(1.0, CLIP / n) if n > 0 else 1.0
        for k in self.p:
            self.p[k] -= lr * s * g[k]


def run_prefix(net, prefix):
    h = np.zeros(HID)
    xs, hs = [], []
    for x in prefix:
        h, _ = net.step(x, h)
        xs.append(x)
        hs.append(h)
    return xs, hs, h


def try_box(net, look, pairs, prefix, rng, learn, cond):
    xs, hs, h = run_prefix(net, prefix)
    targets, opened, reached = {}, 0, 0
    for j in range(LIDS):
        reached += 1
        x1 = x_try(look, j, None, 0)
        h, z1 = net.step(x1, h)
        xs.append(x1)
        hs.append(h)
        a1 = int(rng.choice(ACTS, p=softmax(z1))) if learn else int(np.argmax(z1))
        t1 = len(xs) - 1
        x2 = x_try(look, j, a1, 1)
        h, z2 = net.step(x2, h)
        xs.append(x2)
        hs.append(h)
        a2 = int(rng.choice(ACTS, p=softmax(z2))) if learn else int(np.argmax(z2))
        t2 = len(xs) - 1
        ok = (a1, a2) == pairs[j]
        r = (1.0 / LIDS) if ok else 0.0
        if learn:
            adv = r - net.base
            net.base += BASE_RATE * (r - net.base)
            targets[t1] = (a1, adv)
            targets[t2] = (a2, adv)
        if ok:
            opened += 1
        elif cond == "G" or not learn:
            break
    if learn and targets:
        net.apply(net.grads(xs, hs, targets), LR)
    return reached, opened


def copy_step(net, look, demo, prefix, w):
    if w <= 0:
        return 0
    xs, hs, h = run_prefix(net, prefix)
    targets = {}
    for j, (a1, a2) in enumerate(demo["shown"]):
        for x, a in ((x_try(look, j, None, 0), a1), (x_try(look, j, a1, 1), a2)):
            h, _ = net.step(x, h)
            xs.append(x)
            hs.append(h)
            targets[len(xs) - 1] = (a, 1.0)
    net.apply(net.grads(xs, hs, targets), LR * COPY_RATE * w)
    return len(demo["shown"])


def test(home, net, seed, d):
    r = np.random.default_rng([seed, 6, d])
    full, part = [], []
    for k in range(KINDS):
        _, op = try_box(net, home.looks[k] + r.normal(0, 0.2, LOOK), home.pairs[k], [], None, False, "G")
        full.append(1.0 if op == LIDS else 0.0)
        part.append(op / LIDS)
    return {"success": float(np.mean(full)), "partial": float(np.mean(part))}


def wnorm(ta, tb, tp):
    return tp / max(ta, tb, TRUST_FLOOR)


def run(arm, cond, seed, out=None):
    home = Home(seed)
    net = Net(seed)
    rng = np.random.default_rng([seed, 3, ARMS.index(arm), CONDS.index(cond)])
    t = [[TRUST0] * KINDS, [TRUST0] * KINDS]
    tries, tests, copies_by_lid, wsum = [], {}, [0] * MAXL, 0.0
    for d in range(1, DAYS + 1):
        for k, look, who, u, hidden, coin_y, coin_r in home.day(d):
            demo, w, prefix = None, 0.0, []
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
                if demo["seen"]:
                    t[p][k] += TRUST_RATE * (demo["opened"] / LIDS - t[p][k])
                prefix = show_steps(look, demo)
                n = copy_step(net, look, demo, prefix, w) if arm != "I" else 0
                for j in range(n):
                    copies_by_lid[j] += 1
                if w > 0 and arm != "I":
                    wsum += w
            reached, opened = try_box(net, look, home.pairs[k], prefix, rng, True, cond)
            tries.append({"d": d, "k": k, "who": None if demo is None else demo["who"],
                          "shown": None if demo is None else demo["shown"], "seen": None if demo is None else demo["seen"],
                          "w": w, "reached": reached, "opened": opened})
        if d in TEST_DAYS:
            tests[d] = test(home, net, seed, d)
    res = {"arm": arm, "cond": cond, "seed": seed, "level_lids": LIDS, "pairs": home.pairs, "habits": home.habits,
           "tests": tests, "tries": tries, "trust": t, "copies_by_lid": copies_by_lid, "copy_weight_sum": wsum}
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
