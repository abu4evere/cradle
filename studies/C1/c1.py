"""C1: routines. Can the child take its turn in a day nobody labels? (studies/C1/questions.md, frozen as C1-frozen)

One home with C0-B's 30 things (level L1 looks) and C0-A's corpus. Each child's home has 6 routines (ordered chains of
3-5 steps over a pool of 12 things, shared across routines). Each day runs 3-5 of them with noise. At every step the
child predicts which thing in view the step will use; on its turns it hands a thing or waits. Arms differ only in
memory: N none, P the previous used thing, W the last 4, R recurrent (backprop through time over 8 steps), S as R with
the steps shuffled within routines each day.

  python studies/C1/c1.py one ARM SEED OUT_DIR
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "C0B"))
import c0b  # noqa: E402  (names, families, corpus loader)

NAMES, FAMILY, NC, LOOK = c0b.NAMES, c0b.FAMILY, c0b.NC, c0b.LOOK
SD_MEMBER = c0b.LEVELS["L1"][1]
POOL, N_ROUT = 12, 6
DAYS = 720
TEST_DAYS = [7, 14, 30, 60, 90, 180, 360, 720]
N_TEST = 30
D_HEAR, H = 16, 32
LR, BASE_RATE = 0.05, 0.01
BPTT = 8
CLIP = 1.0                      # implementation reading (IMPLEMENTATION.md): gradient norm clipped, for every arm alike
ORDER_WORDS = {"then", "next", "after", "before", "first", "last", "routine", "breakfast", "bath", "bedtime",
               "dressing", "waking"}
ARMS = {"N": dict(mem="none"), "P": dict(mem="prev1"), "W": dict(mem="prev4"), "R": dict(mem="rec"),
        "S": dict(mem="rec", shuffle=True)}


def tokens(s):
    return re.findall(r"[a-z']+", s.lower())


def load_corpus():
    c = c0b.load_corpus()
    c["frames"] = {k: {part: [f for f in fr if not set(tokens(f.replace("{X}", " "))) & ORDER_WORDS]
                       for part, fr in parts.items()} for k, parts in c["frames"].items()}
    return c


class Home:
    """Looks, routines and the day streams: fixed by the seed, the same in every arm."""

    def __init__(self, seed, corpus):
        self.seed = seed
        rng = np.random.default_rng([seed, 1])
        fam = rng.normal(0, 1, (NC // 3, LOOK))
        self.centre = fam[FAMILY] + rng.normal(0, SD_MEMBER, (NC, LOOK))
        self.offset = rng.normal(0, 0.5, (NC, 5, LOOK))
        r = np.random.default_rng([seed, 11])
        pool = r.choice(NC, POOL, replace=False)
        self.routines = []
        for _ in range(N_ROUT):
            n = int(r.integers(3, 6))
            items = [int(x) for x in r.choice(pool, n, replace=False)]
            turns = [bool(x) for x in (r.random(n) < 0.5)]          # True = the child's turn
            if not any(turns):
                turns[int(r.integers(n))] = True
            self.routines.append(list(zip(items, turns)))
        self.life = corpus["frames"]
        self.vocab = corpus["vocabulary"]

    def look(self, cat, inst, rng):
        return self.centre[cat] + self.offset[cat, inst] + rng.normal(0, 0.2, LOOK)

    def day(self, key, shuffle_key=None):
        """A day: a list of steps (needed, child_turn, cats_in_view, looks, needed_index, noisy, rng_for_words).
        `key` fixes every draw; `shuffle_key` (arm S) shuffles the order of steps within every routine first."""
        rng = np.random.default_rng(key)
        sh = np.random.default_rng(shuffle_key) if shuffle_key is not None else None
        n = int(rng.integers(3, 6))
        which = rng.choice(N_ROUT, n, replace=False)
        steps = []
        for ri in which:
            seq = list(self.routines[int(ri)])
            if sh is not None:
                sh.shuffle(seq)
            u = rng.random()
            noisy = False
            if u < 0.1 and len(seq) > 1:
                del seq[int(rng.integers(len(seq)))]
                noisy = True
            elif u < 0.2 and len(seq) > 1:
                i = int(rng.integers(len(seq) - 1))
                seq[i], seq[i + 1] = seq[i + 1], seq[i]
                noisy = True
            elif u < 0.3 and len(seq) > 1:
                seq = seq[:int(rng.integers(1, len(seq)))]
                noisy = True
            for need, child in seq:
                k = int(rng.integers(3, 5))
                others = [int(x) for x in rng.choice([c for c in range(NC) if c != need], k - 1, replace=False)]
                cats = others + [need]
                rng.shuffle(cats)
                looks = np.array([self.look(c, int(rng.integers(3)), rng) for c in cats])
                steps.append(dict(need=need, child=child, cats=cats, looks=looks, ni=cats.index(need), noisy=noisy,
                                  fr=int(rng.integers(1 << 30)), say=rng.random()))
        return steps

    def fingerprint(self):
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(self.centre).tobytes())
        h.update(json.dumps(self.routines).encode())
        return h.hexdigest()[:16]


class Child:
    def __init__(self, arm, vocab, seed):
        self.mem = ARMS[arm]["mem"]
        self.vi = {w: i for i, w in enumerate(vocab)}
        rng = np.random.default_rng([seed, 4])
        n_mem = {"none": 0, "prev1": LOOK, "prev4": 4 * LOOK, "rec": LOOK}[self.mem]
        self.I = D_HEAR + 1 + n_mem
        self.E = rng.normal(0, 0.1, (len(vocab), D_HEAR))
        self.Wx = rng.normal(0, 0.1, (H, self.I))
        self.b = np.zeros(H)
        self.Wh = rng.normal(0, 0.1, (H, H)) if self.mem == "rec" else None
        self.M = rng.normal(0, 0.1, (LOOK, H))
        self.w0 = 0.0
        self.base = 0.0
        self.reset()

    def reset(self):
        self.h = np.zeros(H)
        self.prev = [np.zeros(LOOK) for _ in range(4)]
        self.trace = []                                    # (x, ids, h_prev, h) for backprop through time

    def ids(self, sentence):
        return [self.vi[w] for w in tokens(sentence) if w in self.vi]

    def x_of(self, ids, child_turn):
        u = self.E[ids].mean(0) if ids else np.zeros(D_HEAR)
        mem = {"none": [], "prev1": [self.prev[0]], "prev4": self.prev, "rec": [self.prev[0]]}[self.mem]
        return np.concatenate([u, [1.0 if child_turn else 0.0]] + list(mem))

    def step_state(self, ids, child_turn):
        x = self.x_of(ids, child_turn)
        hp = self.h if self.mem == "rec" else np.zeros(H)
        pre = self.Wx @ x + self.b + (self.Wh @ hp if self.Wh is not None else 0.0)
        h = np.tanh(pre)
        return x, hp, h

    def scores(self, looks, h):
        return looks @ (self.M @ h)

    def commit(self, x, ids, hp, h, used_look):
        """After the step: keep the state, the trace (recurrent arms) and the memory of what was used."""
        if self.mem == "rec":
            self.h = h
            self.trace.append((x, ids, hp, h))
            self.trace = self.trace[-(BPTT - 1):]          # with the present step: backprop over 8 steps
        self.prev = [used_look] + self.prev[:3]


def softmax(v):
    e = np.exp(v - v.max())
    return e / e.sum()


def clip(g):
    n = float(np.sqrt(sum(float((a * a).sum()) for a in g.values())))
    if n > CLIP:
        for k in g:
            g[k] = g[k] * (CLIP / n)
    return g


def grads(child, looks, x, ids, hp, h, ni, act=None, adv=0.0):
    """The gradients of: the prediction loss -log p(need) (through time for the recurrent arms), and, if act is given,
    of -adv * log pi(act) for the act (this step only). Returned as descents (to subtract)."""
    s = child.scores(looks, h)
    p = softmax(s)
    ds = p.copy()
    ds[ni] -= 1.0                                         # d(-log p[ni]) / ds
    g = {"M": np.outer(looks.T @ ds, h), "w0": 0.0}
    dh_pred = child.M.T @ (looks.T @ ds)
    if act is not None:
        pi = softmax(np.append(s, child.w0))
        da = pi.copy()
        da[act] -= 1.0
        da *= adv                                         # d(-adv log pi(act)) / dlogits
        g["M"] += np.outer(looks.T @ da[:-1], h)
        g["w0"] = float(da[-1])
        dh_act = child.M.T @ (looks.T @ da[:-1])
    else:
        dh_act = np.zeros(H)
    gWx, gb = np.zeros_like(child.Wx), np.zeros(H)
    gWh = np.zeros_like(child.Wh) if child.Wh is not None else None
    gE = {}

    def back(dh, x_k, ids_k, hp_k, h_k):
        dpre = dh * (1.0 - h_k ** 2)
        nonlocal gWx, gb, gWh
        gWx += np.outer(dpre, x_k)
        gb += dpre
        du = child.Wx[:, :D_HEAR].T @ dpre
        for i in ids_k:
            gE[i] = gE.get(i, 0.0) + du / len(ids_k)
        if gWh is not None:
            gWh += np.outer(dpre, hp_k)
            return child.Wh.T @ dpre
        return None
    # the act: this step only
    back(dh_act, x, ids, hp, h)
    # the prediction: this step, then back through the trace (recurrent arms)
    dh = back(dh_pred, x, ids, hp, h)
    if child.mem == "rec" and dh is not None:
        for (x_k, ids_k, hp_k, h_k) in reversed(child.trace):
            dh = back(dh, x_k, ids_k, hp_k, h_k)
    g["Wx"], g["b"] = gWx, gb
    if gWh is not None:
        g["Wh"] = gWh
    g["E"] = gE
    return g


def apply(child, g):
    flat = {k: v for k, v in g.items() if k not in ("E", "w0")}
    flat["w0"] = np.array([g["w0"]])
    for i, v in g["E"].items():
        flat[f"E{i}"] = v
    flat = clip(flat)
    child.M -= LR * flat["M"]
    child.Wx -= LR * flat["Wx"]
    child.b -= LR * flat["b"]
    if "Wh" in flat:
        child.Wh -= LR * flat["Wh"]
    child.w0 -= LR * float(flat["w0"][0])
    for k, v in flat.items():
        if k.startswith("E"):
            child.E[int(k[1:])] -= LR * v


def heard_after(home, st, right, said_rng_frame):
    """What the parent says after a step (heard at the next step)."""
    X = NAMES[st["need"]]
    fr = home.life
    if st["child"]:
        pool = fr["praise"]["life"] if right else fr["this"]["life"]
        return pool[st["fr"] % len(pool)].replace("{X}", X)
    if st["say"] < 0.5:
        pool = fr["naming"]["life"]
        return pool[st["fr"] % len(pool)].replace("{X}", X)
    return ""


def live_day(home, child, steps, learn, rng=None, record=None):
    child.reset()
    heard = ""
    for st in steps:
        ids = child.ids(heard)
        x, hp, h = child.step_state(ids, st["child"])
        s = child.scores(st["looks"], h)
        pred = int(np.argmax(s))
        act = None
        right = False
        if st["child"]:
            logits = np.append(s, child.w0)
            if learn:
                act = int(rng.choice(len(logits), p=softmax(logits)))
            else:
                act = int(np.argmax(logits))
            right = act == st["ni"]
        if record is not None:
            k = len(st["cats"])
            tag = "noisy" if st["noisy"] else "clean"
            record[f"ant_{tag}"].append(pred == st["ni"])
            record[f"chance_ant_{tag}"].append(1.0 / k)
            if st["child"]:
                record[f"turn_{tag}"].append(right)
                record[f"chance_turn_{tag}"].append(1.0 / (k + 1))
        if learn:
            adv = 0.0
            if act is not None:
                r = 1.0 if right else 0.0
                adv = r - child.base
                child.base += BASE_RATE * (r - child.base)
            g = grads(child, st["looks"], x, ids, hp, h, st["ni"], act if act is not None else None, adv)
            apply(child, g)
        child.commit(x, ids, hp, h, st["looks"][st["ni"]])
        heard = heard_after(home, st, right, None)


def test(home, child, seed, day, shuffle):
    rec = {k: [] for k in ("ant_clean", "ant_noisy", "turn_clean", "turn_noisy", "chance_ant_clean",
                           "chance_ant_noisy", "chance_turn_clean", "chance_turn_noisy")}
    for j in range(N_TEST):
        steps = home.day([seed, 13, day, j])               # test days: the same in every arm, never shuffled
        live_day(home, child, steps, learn=False, record=rec)
    return {k: (float(np.mean(v)) if v else None) for k, v in rec.items()} | {
        f"n_{k}": len(v) for k, v in rec.items() if not k.startswith("chance")}


def run(arm, seed, out=None):
    corpus = load_corpus()
    home = Home(seed, corpus)
    child = Child(arm, home.vocab, seed)
    rng = np.random.default_rng([seed, 3, list(ARMS).index(arm)])
    shuffle = ARMS[arm].get("shuffle", False)
    results = {}
    for day in range(DAYS):
        steps = home.day([seed, 12, day], shuffle_key=[seed, 14, day] if shuffle else None)
        live_day(home, child, steps, learn=True, rng=rng)
        if day + 1 in TEST_DAYS:
            results[day + 1] = test(home, child, seed, day + 1, shuffle)
    res = {"arm": arm, "seed": seed, "home": home.fingerprint(), "routines": home.routines, "results": results}
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]))
        last = r["results"][max(r["results"])]
        print(sys.argv[2], sys.argv[3], {k: round(v, 3) for k, v in last.items() if isinstance(v, float)})
