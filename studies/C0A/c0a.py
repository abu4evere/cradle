"""C0-A: can a newborn neural child learn ten words by living with two AI parents? (questions.md, frozen as C0A-frozen)

The parents' sentences come from corpus.json (generated once by qwen2.5:7b). The engine decides what the parents do; the
model only worded the sentences. The child is a small network (never a language model) that starts knowing no words.

  python studies/C0A/c0a.py one ARM SEED OUT_DIR
  python studies/C0A/c0a.py scenehash SEED          (the scene stream's fingerprint; must not depend on the arm)

Implementation readings of points the plan leaves open are listed in IMPLEMENTATION.md beside this file.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
NAMES = ["ball", "cup", "spoon", "bread", "apple", "banana", "shoe", "hat", "book", "duck"]
NONCE = ["dax", "wug", "blicket", "toma", "fep", "zib", "kiv", "modi", "pilk", "gazzer"]
NC, LOOK = 10, 16
MOMENTS, DAYS, DAYS_GL = 20, 1080, 4320
TEST_DAYS = [90, 180, 270, 360, 540, 720, 1080]
TEST_DAYS_GL = TEST_DAYS + [1440, 2160, 2880, 3600, 4320]
ACTS = ["naming", "asking", "want", "background"]
ACT_P = [0.35, 0.25, 0.15, 0.25]
LR, BASE_RATE = 0.05, 0.01
BUFFER = 20
ARMS = {
    #       d          cues        association  reward  names
    "A": dict(d=64, cues="ambig", assoc=True, reward=True, shuffle=False),
    "B": dict(d=8, cues="ambig", assoc=True, reward=True, shuffle=False),
    "C": dict(d=8, cues="ambig", assoc=True, reward=True, shuffle=False, grow=True),
    "H": dict(d=32, cues="ambig", assoc=True, reward=True, shuffle=False),
    "D": dict(d=64, cues="none", assoc=True, reward=True, shuffle=False),
    "P": dict(d=64, cues="perfect", assoc=True, reward=True, shuffle=False),
    "G": dict(d=64, cues="ambig", assoc=False, reward=True, shuffle=False),
    "E": dict(d=64, cues="ambig", assoc=False, reward=False, shuffle=False),
    "F": dict(d=64, cues="ambig", assoc=True, reward=True, shuffle=True),
    "K": dict(d=None, cues="ambig", assoc=False, reward=False, shuffle=False, counting=True),
    "GL": dict(d=64, cues="ambig", assoc=False, reward=True, shuffle=False, long=True),
}
GROW = {375: 16, 735: 32}
SEEDS = range(1, 17)


def tokens(s: str) -> list:
    return re.findall(r"[a-z']+", s.lower())


def load_corpus():
    import os
    path = Path(os.environ.get("C0A_CORPUS", HERE / "corpus.json"))     # a stand-in corpus only for code tests
    return json.loads(path.read_text(encoding="utf-8"))


# --- the scene stream: fixed in advance per seed, the same in every arm ------------------------------------------------
class Scenes:
    def __init__(self, seed: int, corpus: dict, days: int):
        rng = np.random.default_rng([seed, 1])
        self.centre = rng.normal(0, 1, (NC, LOOK))
        self.offset = rng.normal(0, 0.5, (NC, 5, LOOK))        # instances 0-2 daily, 3-4 kept for the new-instance test
        pairs = [(a, b) for a in range(NC) for b in range(a + 1, NC)]
        idx = rng.choice(len(pairs), 9, replace=False)
        self.apart = {pairs[i] for i in idx}
        fr = corpus["frames"]
        self.life = {k: fr[k]["life"] for k in fr}
        self.test = {k: fr[k].get("test", []) for k in fr}
        self.days = days
        n = days * MOMENTS
        self.k = rng.integers(2, 4, n)
        self.act = rng.choice(4, n, p=ACT_P)
        self.cats = np.zeros((n, 3), dtype=int)
        self.inst = rng.integers(0, 3, (n, 3))
        for m in range(n):
            while True:
                c = rng.choice(NC, self.k[m], replace=False)
                if not any((min(a, b), max(a, b)) in self.apart for a in c for b in c if a != b):
                    break
            self.cats[m, :self.k[m]] = c
        self.noise = rng.normal(0, 0.2, (n, 3, LOOK))
        self.target = (rng.random(n) * self.k).astype(int)      # index into the things in view, even over them
        self.u = rng.random((n, 6))                              # attention draws for up to six heard frames
        self.other = rng.integers(0, 3, (n, 6))
        self.fidx = rng.integers(0, 1 << 30, (n, 6))             # frame choices for every possible response
        prng = np.random.default_rng([seed, 2])
        self.perm = np.array([prng.permutation(NC) for _ in range(days)])   # arm F: a fresh shuffle of names each day

    def looks(self, m):
        k = self.k[m]
        cats = self.cats[m, :k]
        return cats, self.centre[cats] + self.offset[cats, self.inst[m, :k]] + self.noise[m, :k]

    def frame(self, kind, m, j, test=False):
        pool = self.test[kind] if test else self.life[kind]
        return pool[self.fidx[m, j] % len(pool)]

    def fingerprint(self):
        h = hashlib.sha256()
        for a in (self.centre, self.offset, self.k, self.act, self.cats, self.inst, self.noise, self.target, self.u,
                  self.other, self.fidx, self.perm):
            h.update(np.ascontiguousarray(a).tobytes())
        return h.hexdigest()[:16]


# --- the neural child ---------------------------------------------------------------------------------------------------
class Child:
    def __init__(self, d, vocab, rng):
        self.vocab = vocab
        self.vi = {w: i for i, w in enumerate(vocab)}
        self.E = rng.normal(0, 0.1, (len(vocab), d))
        self.W = rng.normal(0, 0.1, (d, LOOK))
        self.c = np.zeros(len(vocab))
        self.nothing = 0.0
        self.quiet = 0.0
        self.base = {"hand": 0.0, "say": 0.0}

    def grow(self, d, rng):
        old = self.E.shape[1]
        self.E = np.hstack([self.E, rng.normal(0, 0.01, (self.E.shape[0], d - old))])
        self.W = np.vstack([self.W, rng.normal(0, 0.01, (d - old, LOOK))])

    def ids(self, sentence):
        return [self.vi[w] for w in tokens(sentence) if w in self.vi]

    def hear(self, ids):
        return self.E[ids].mean(0) if ids else np.zeros(self.E.shape[1])

    def associate(self, ids, looks, pos, buffer):
        """loss = -log(sum_pos e^s / sum_all e^s); SGD on the heard words' rows of E and on W."""
        if not ids:
            return
        X = np.vstack([looks] + ([np.array(buffer)] if buffer else []))
        u = self.hear(ids)
        Z = X @ self.W.T
        s = Z @ u
        p = np.exp(s - s.max())
        p /= p.sum()
        q = np.zeros(len(s))
        q[pos] = p[pos] / p[pos].sum()
        g = p - q                                                  # dL/ds
        gu = g @ Z
        gW = np.outer(u, g @ X)
        for i in ids:                                              # u is the mean, so each occurrence gets 1/n
            self.E[i] -= LR * gu / len(ids)
        self.W -= LR * gW

    def hand_logits(self, u, looks):
        return np.append((looks @ self.W.T) @ u, self.nothing)

    def say_logits(self, look):
        return np.append(self.E @ (self.W @ look) + self.c, self.quiet)

    def reinforce_hand(self, ids, looks, a, r):
        u = self.hear(ids)
        z = looks @ self.W.T
        lg = np.append(z @ u, self.nothing)
        pi = np.exp(lg - lg.max())
        pi /= pi.sum()
        adv = r - self.base["hand"]
        self.base["hand"] += BASE_RATE * (r - self.base["hand"])
        coef = -pi
        coef[a] += 1.0
        coef *= adv                                               # gradient ascent on adv * log pi(a)
        n = len(looks)
        gu = coef[:n] @ z
        gW = np.outer(u, coef[:n] @ looks)
        if ids:
            for i in ids:
                self.E[i] += LR * gu / len(ids)
        self.W += LR * gW
        self.nothing += LR * coef[n]

    def reinforce_say(self, look, a, r):
        z = self.W @ look
        lg = np.append(self.E @ z + self.c, self.quiet)
        pi = np.exp(lg - lg.max())
        pi /= pi.sum()
        adv = r - self.base["say"]
        self.base["say"] += BASE_RATE * (r - self.base["say"])
        coef = -pi
        coef[a] += 1.0
        coef *= adv
        V = len(self.vocab)
        gz = coef[:V] @ self.E
        self.E += LR * np.outer(coef[:V], z)
        self.c += LR * coef[:V]
        self.quiet += LR * coef[V]
        self.W += LR * np.outer(gz, look)


# --- the counting baseline (arm K, non-neural) ----------------------------------------------------------------------------
class Counter_:
    def __init__(self, vocab):
        self.vocab = vocab
        self.vi = {w: i for i, w in enumerate(vocab)}
        self.centres, self.sizes = [], []
        self.wc = {}                                               # (word, cluster) -> count
        self.w = np.zeros(len(vocab))

    def cluster(self, look, learn=True):
        if self.centres:
            d = np.linalg.norm(np.array(self.centres) - look, axis=1)
            j = int(d.argmin())
            if d[j] < 2.0:
                if learn:
                    self.sizes[j] += 1
                    self.centres[j] += (look - self.centres[j]) / self.sizes[j]
                return j
        if not learn:
            return None
        self.centres.append(look.copy())
        self.sizes.append(1)
        return len(self.centres) - 1

    def ids(self, sentence):
        return [self.vi[w] for w in tokens(sentence) if w in self.vi]

    def hear(self, ids, looks, flag):
        cl = [self.cluster(x) for x in looks]
        targets = [(cl[flag], 1.0)] if flag is not None else [(c, 1.0 / len(cl)) for c in cl]
        for i in ids:
            self.w[i] += 1
            for c, wt in targets:
                self.wc[(i, c)] = self.wc.get((i, c), 0.0) + wt

    def scores(self, ids, looks):
        out = []
        for x in looks:
            c = self.cluster(x, learn=False)
            out.append(0.0 if c is None else sum(self.wc.get((i, c), 0.0) / self.w[i] for i in ids if self.w[i] > 0))
        return np.array(out)

    def say(self, look):
        c = self.cluster(look, learn=False)
        if c is None:
            return None
        best, bi = 0.0, None
        for i in range(len(self.vocab)):
            v = self.wc.get((i, c), 0.0)
            if v > best:
                best, bi = v, i
        return bi


# --- life and tests -----------------------------------------------------------------------------------------------------
def flag_for(cues, kind, named, k, u, other):
    """Which thing in view the inborn 'where is the parent looking' flag falls on (None = no flag)."""
    if cues == "none":
        return None
    if cues == "perfect":
        return named if kind not in ("background", "asking") and named is not None else None
    if kind == "asking":
        return None
    if kind == "background":
        return int(other % k) if u < 0.5 else None
    if u < 0.75:
        return named
    if u < 0.85:
        others = [i for i in range(k) if i != named]
        return others[other % len(others)]
    return None


def run(arm: str, seed: int, out: Path | None = None) -> dict:
    cfg = ARMS[arm]
    corpus = load_corpus()
    vocab = corpus["vocabulary"]
    days = DAYS_GL if cfg.get("long") else DAYS
    tests_at = TEST_DAYS_GL if cfg.get("long") else TEST_DAYS
    sc = Scenes(seed, corpus, days)
    crng = np.random.default_rng([seed, 3, list(ARMS).index(arm)])
    counting = cfg.get("counting", False)
    child = Counter_(vocab) if counting else Child(cfg["d"], vocab, np.random.default_rng([seed, 4]))
    E0 = None if counting else child.E.copy()
    buffer = []
    exposure = np.zeros(NC, dtype=int)
    results = {}

    def name_of(cat, day):
        if cfg["shuffle"]:
            return NAMES[sc.perm[day][cat]]
        return NAMES[cat]

    def word_to_cat(word, day):
        for c in range(NC):
            if name_of(c, day) == word:
                return c
        return None

    def heard(sentence, looks, flag):
        ids = child.ids(sentence)
        for w in tokens(sentence):
            if w in NAMES:
                exposure[NAMES.index(w)] += 1
        if counting:
            child.hear(ids, looks, flag)
        elif cfg["assoc"]:
            pos = [flag] if flag is not None else list(range(len(looks)))
            child.associate(ids, looks, pos, buffer)

    for day in range(days):
        if cfg.get("grow") and day in GROW:
            child.grow(GROW[day], np.random.default_rng([seed, 5, day]))
        for mm in range(MOMENTS):
            m = day * MOMENTS + mm
            cats, looks = sc.looks(m)
            k = len(cats)
            t = int(sc.target[m])
            act = ACTS[sc.act[m]]
            if act == "naming":
                s = sc.frame("naming", m, 0).replace("{X}", name_of(cats[t], day))
                heard(s, looks, flag_for(cfg["cues"], "naming", t, k, sc.u[m, 0], sc.other[m, 0]))
            elif act == "background":
                s = sc.frame("background", m, 0)
                heard(s, looks, flag_for(cfg["cues"], "background", None, k, sc.u[m, 0], sc.other[m, 0]))
            elif act == "asking":
                s = sc.frame("asking", m, 0).replace("{X}", name_of(cats[t], day))
                heard(s, looks, None)
                if counting:
                    sc_ = child.scores(child.ids(s), looks)
                    a = int(crng.choice(np.flatnonzero(sc_ == sc_.max())))
                else:
                    lg = child.hand_logits(child.hear(child.ids(s)), looks)
                    pi = np.exp(lg - lg.max())
                    pi /= pi.sum()
                    a = int(crng.choice(k + 1, p=pi))
                r = 1.0 if a == t else 0.0
                if cfg["reward"] and not counting:
                    child.reinforce_hand(child.ids(s), looks, a, r)
                if a == t:
                    s2 = sc.frame("praise", m, 1).replace("{X}", name_of(cats[t], day))
                    heard(s2, looks, flag_for(cfg["cues"], "praise", t, k, sc.u[m, 1], sc.other[m, 1]))
                else:
                    if a < k:
                        s2 = sc.frame("no", m, 2).replace("{X}", name_of(cats[a], day))
                        heard(s2, looks, flag_for(cfg["cues"], "no", a, k, sc.u[m, 2], sc.other[m, 2]))
                    s3 = sc.frame("this", m, 3).replace("{X}", name_of(cats[t], day))
                    heard(s3, looks, flag_for(cfg["cues"], "this", t, k, sc.u[m, 3], sc.other[m, 3]))
            else:                                                       # want: the child wants the target thing
                if counting:
                    a = child.say(looks[t])
                    a = len(vocab) if a is None else a
                else:
                    lg = child.say_logits(looks[t])
                    pi = np.exp(lg - lg.max())
                    pi /= pi.sum()
                    a = int(crng.choice(len(vocab) + 1, p=pi))
                word = vocab[a] if a < len(vocab) else None
                got = word_to_cat(word, day) if word else None
                in_view = [i for i in range(k) if cats[i] == got] if got is not None else []
                r = 1.0 if in_view and in_view[0] == t else 0.0
                if cfg["reward"] and not counting:
                    child.reinforce_say(looks[t], a, r)
                if word is None:
                    heard(sc.frame("whatwant", m, 4), looks, None)
                elif in_view:
                    j = in_view[0]
                    s2 = sc.frame("handing", m, 4).replace("{X}", name_of(cats[j], day))
                    heard(s2, looks, flag_for(cfg["cues"], "handing", j, k, sc.u[m, 4], sc.other[m, 4]))
                else:
                    heard(sc.frame("confusion", m, 4), looks, None)
            buffer.extend(list(looks))
            buffer = buffer[-BUFFER:]
        if day + 1 in tests_at:
            results[day + 1] = tests(child, sc, seed, day + 1, counting, vocab)
    out_d = {"arm": arm, "seed": seed, "scene": sc.fingerprint(), "results": results,
             "E_unchanged": (None if counting else bool(np.array_equal(E0, child.E)))}
    out_d["exposure"] = exposure.tolist()
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_seed_{seed}.json").write_text(json.dumps(out_d), encoding="utf-8")
    return out_d


def test_trials(sc, seed, day, kind, n):
    """Test trials: 4 things with at least one never-together pair; drawn from their own stream, the same in every arm."""
    rng = np.random.default_rng([seed, 9, day, ["request", "new", "novel", "saying", "repair"].index(kind)])
    trials = []
    apart = sorted(sc.apart)
    for _ in range(n):
        a, b = apart[rng.integers(len(apart))]
        rest = [c for c in range(NC) if c not in (a, b)]
        cats = [a, b] + list(rng.choice(rest, 2, replace=False))
        rng.shuffle(cats)
        inst = rng.integers(3, 5, 4) if kind == "new" else rng.integers(0, 3, 4)
        looks = sc.centre[cats] + sc.offset[cats, inst] + rng.normal(0, 0.2, (4, LOOK))
        trials.append((np.array(cats), looks, int(rng.integers(4)), int(rng.integers(1 << 30)), int(rng.integers(1 << 30))))
    return trials


def tests(child, sc, seed, day, counting, vocab):
    tf = sc.test

    def choose(ids, looks, tie):
        if counting:                                          # greedy; ties broken at random, as in daily life
            s = child.scores(ids, looks)
            best = np.flatnonzero(s == s.max())
            return int(best[tie % len(best)])
        return int(child.hand_logits(child.hear(ids), looks).argmax())

    res = {}
    for kind, n in (("request", 60), ("new", 60)):
        ok = []
        for cats, looks, t, f1, _ in test_trials(sc, seed, day, kind, n):
            s = tf["asking"][f1 % len(tf["asking"])].replace("{X}", NAMES[cats[t]])
            ok.append(choose(child.ids(s), looks, f1) == t)
        res[kind] = float(np.mean(ok))
        if kind == "request":
            res["request_by_word"] = {}
            for c in range(NC):
                hits = [o for o, (cats, _, t, _, _) in zip(ok, test_trials(sc, seed, day, kind, n)) if cats[t] == c]
                res["request_by_word"][NAMES[c]] = float(np.mean(hits)) if hits else None
    ok = []
    for cats, looks, t, f1, f2 in test_trials(sc, seed, day, "novel", 30):
        s = tf["asking"][f1 % len(tf["asking"])].replace("{X}", NONCE[f2 % len(NONCE)])
        ok.append(choose(child.ids(s), looks, f2) == t)        # scored against a random one of the four
    res["novel"] = float(np.mean(ok))
    ok = []
    for cats, looks, t, _, _ in test_trials(sc, seed, day, "saying", 30):
        if counting:
            a = child.say(looks[t])
            word = vocab[a] if a is not None else None
        else:
            a = int(child.say_logits(looks[t]).argmax())
            word = vocab[a] if a < len(vocab) else None
        ok.append(word == NAMES[cats[t]])
    res["saying"] = float(np.mean(ok))
    with_c, without = [], []
    for cats, looks, t, f1, f2 in test_trials(sc, seed, day, "repair", 30):
        y = (t + 1 + f2 % 3) % 4                                # the wrong thing handed (by construction)
        keep = [i for i in range(4) if i != y]
        lk = looks[keep]
        tt = keep.index(t)
        ask = tf["asking"][f1 % len(tf["asking"])].replace("{X}", NAMES[cats[t]])
        no = tf["no"][f2 % len(tf["no"])].replace("{X}", NAMES[cats[y]])
        with_c.append(choose(child.ids(no + " " + ask), lk, f1) == tt)
        without.append(choose(child.ids(ask), lk, f1) == tt)
    res["repair_with"] = float(np.mean(with_c))
    res["repair_without"] = float(np.mean(without))
    return res


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "one":
        r = run(sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]))
        last = max(r["results"])
        print(sys.argv[2], sys.argv[3], "day", last, {k: v for k, v in r["results"][last].items() if k != "request_by_word"})
    elif cmd == "scenehash":
        print(Scenes(int(sys.argv[2]), load_corpus(), DAYS).fingerprint())
