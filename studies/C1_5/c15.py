"""C1.5: word order (studies/C1_5/questions.md, frozen as C1_5-frozen).

C1's home (30 things, 6 routines, noise, 720 days) with C1's window memory W in every arm. At a child's turn, with chance
1/2, the parent makes a request instead: order ("the X, then the Y": hand X, then Y), negation first ("not the X, the
Y": hand Y), negation last ("the Y, not the X": hand Y) or plain ("the X"). X is the step's needed thing; Y another thing
in view, never one of the child's held-out pairs with X. Arms differ only in how a sentence is heard:
  B  mean of word embeddings        P  mean of (word + position embeddings)    K  first 8 words in fixed slots
  Q  an Elman reader over the words (16 units, last state)                    Q- Q with the words shuffled first
Tests (days 30, 90, 180, 360, 720; learning off): matched probes from an empty memory, the same 4 things in view and
the same frame for both twins.

  python studies/C1_5/c15.py one ARM SEED OUT_DIR
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "C1"))
import c1  # noqa: E402  (the home, the routines, C1's corpus filter)

NAMES, NC, LOOK = c1.NAMES, c1.NC, c1.LOOK
tokens, softmax = c1.tokens, c1.softmax
DAYS = 720
TEST_DAYS = [30, 90, 180, 360, 720]
D_WORD, H, D_READ, N_POS, N_SLOT = 16, 32, 16, 12, 8
LR, BASE_RATE, CLIP = c1.LR, c1.BASE_RATE, c1.CLIP
HELD_SHARE = 0.2
N_ASK = 24                      # correction 1: asking moments a day (memory empty at each)
REQ_KINDS = ("order", "neg_first", "neg_last", "plain")
ARMS = {"B": "mean", "P": "pos", "K": "slots", "Q": "read", "Q-": "read_shuffled"}


def load_corpus():
    c = c1.load_corpus()                                   # C0-A's frames, C0-B's names, C1's order-word filter
    path = Path(os.environ.get("C15_CORPUS", HERE / "corpus_c15.json"))
    c15 = json.loads(path.read_text(encoding="utf-8"))
    c["requests"] = c15["frames"]
    c["vocabulary"] = sorted(set(c["vocabulary"]) | set(c15["vocabulary"]))
    return c


def held_pairs(seed):
    pairs = list(itertools.combinations(range(NC), 2))
    r = np.random.default_rng([seed, 15])
    pick = r.choice(len(pairs), round(HELD_SHARE * len(pairs)), replace=False)
    return sorted(pairs[int(i)] for i in pick)


class Home(c1.Home):
    def __init__(self, seed, corpus):
        super().__init__(seed, corpus)
        self.req = corpus["requests"]
        self.held = held_pairs(seed)
        self.held_set = {frozenset(p) for p in self.held}

    def day(self, key, shuffle_key=None):
        """C1's routine steps (no requests), then the day's asking moments (correction 1)."""
        steps = super().day(key)
        for st in steps:
            st["req"] = None
        rng = np.random.default_rng([*key, 99])            # the asking moments: their own stream, the same in every arm
        for _ in range(N_ASK):
            kind = REQ_KINDS[int(rng.integers(4))]
            while True:
                cats = [int(c) for c in rng.choice(NC, 4, replace=False)]
                if kind == "plain" or frozenset(cats[:2]) not in self.held_set:
                    break
            looks = np.array([self.look(c, int(rng.integers(3)), rng) for c in cats])
            perm = [int(i) for i in rng.permutation(4)]
            looks, cats = looks[perm], [cats[i] for i in perm]
            xi, yi = perm.index(0), perm.index(1)            # X and Y: the first two drawn, then shuffled in view
            steps.append(dict(ask=True, cats=cats, looks=looks, req=(kind, xi, None if kind == "plain" else yi,
                                                                       int(rng.integers(1 << 30))),
                              fr=int(rng.integers(1 << 30))))
        return steps

    def sentence(self, kind, x, y, fr, part="life"):
        if kind == "plain":
            pool = self.life["asking"][part]
            return pool[fr % len(pool)].replace("{X}", NAMES[x])
        pool = self.req[kind][part]
        return pool[fr % len(pool)].replace("{X}", NAMES[x]).replace("{Y}", NAMES[y])

    def fingerprint(self):
        h = hashlib.sha256(super().fingerprint().encode())
        h.update(json.dumps(self.held).encode())
        return h.hexdigest()[:16]


class Child:
    def __init__(self, arm, vocab, seed):
        self.arm, self.hear_kind = arm, ARMS[arm]
        self.vi = {w: i for i, w in enumerate(vocab)}
        rng = np.random.default_rng([seed, 4])
        self.E = rng.normal(0, 0.1, (len(vocab), D_WORD))
        self.DU = {"mean": D_WORD, "pos": D_WORD, "slots": N_SLOT * D_WORD, "read": D_READ,
                   "read_shuffled": D_READ}[self.hear_kind]
        self.I = self.DU + 2 + 4 * LOOK                    # sentence, child's turn, second act, the window of 4 looks
        r2 = np.random.default_rng([seed, 5])              # the hearing parts' own draws (B draws nothing from it)
        self.Pos = r2.normal(0, 0.1, (N_POS, D_WORD)) if self.hear_kind == "pos" else None
        if self.hear_kind.startswith("read"):
            self.A = r2.normal(0, 0.1, (D_READ, D_WORD))
            self.U = r2.normal(0, 0.1, (D_READ, D_READ))
            self.c = np.zeros(D_READ)
        else:
            self.A = self.U = self.c = None
        self.Wx = rng.normal(0, 0.1, (H, self.I))
        self.b = np.zeros(H)
        self.M = rng.normal(0, 0.1, (LOOK, H))
        self.w0 = 0.0
        self.base = 0.0
        self.shuf = np.random.default_rng([seed, 30])      # Q-'s shuffles in life
        self.reset()

    def reset(self):
        self.prev = [np.zeros(LOOK) for _ in range(4)]

    def ids(self, sentence):
        return [self.vi[w] for w in tokens(sentence) if w in self.vi]

    # --- hearing: u and a cache for the backward pass ---------------------------------------------------------------
    def hear(self, ids, shuf=None):
        k = self.hear_kind
        if k == "read_shuffled" and ids:
            ids = [ids[int(i)] for i in (shuf or self.shuf).permutation(len(ids))]
        if not ids:
            return np.zeros(self.DU), (k, [], None)
        if k == "mean":
            return self.E[ids].mean(0), (k, ids, None)
        if k == "pos":
            pos = [min(t, N_POS - 1) for t in range(len(ids))]
            return (self.E[ids] + self.Pos[pos]).mean(0), (k, ids, pos)
        if k == "slots":
            u = np.zeros(self.DU)
            for t, i in enumerate(ids[:N_SLOT]):
                u[t * D_WORD:(t + 1) * D_WORD] = self.E[i]
            return u, (k, ids, None)
        r, rs = np.zeros(D_READ), []
        for i in ids:
            rp = r
            r = np.tanh(self.A @ self.E[i] + self.U @ rp + self.c)
            rs.append((i, rp, r))
        return r, (k, ids, rs)

    def hear_back(self, du, cache, g):
        k, ids, extra = cache
        if not ids:
            return
        gE = g["E"]
        if k in ("mean", "pos"):
            n = len(ids)
            for i in ids:
                gE[i] = gE.get(i, 0.0) + du / n
            if k == "pos":
                for t in extra:
                    g["Pos"][t] += du / n
        elif k == "slots":
            for t, i in enumerate(ids[:N_SLOT]):
                gE[i] = gE.get(i, 0.0) + du[t * D_WORD:(t + 1) * D_WORD]
        else:
            dr = du
            for i, rp, r in reversed(extra):
                dpre = dr * (1.0 - r ** 2)
                g["A"] += np.outer(dpre, self.E[i])
                g["U"] += np.outer(dpre, rp)
                g["c"] += dpre
                gE[i] = gE.get(i, 0.0) + self.A.T @ dpre
                dr = self.U.T @ dpre

    def state(self, u, child_turn, second):
        x = np.concatenate([u, [1.0 if child_turn else 0.0, 1.0 if second else 0.0]] + self.prev)
        return x, np.tanh(self.Wx @ x + self.b)

    def scores(self, looks, h):
        return looks @ (self.M @ h)

    def commit(self, used_look):
        self.prev = [used_look] + self.prev[:3]


def grads(child, looks, x, h, cache, ni, act=None, adv=0.0):
    """Descents for -log p(used thing) and, if act is given, -adv log pi(act); through the hearing parts."""
    s = child.scores(looks, h)
    p = softmax(s)
    ds = p.copy()
    ds[ni] -= 1.0
    g = {"M": np.outer(looks.T @ ds, h), "w0": 0.0, "E": {}}
    dh = child.M.T @ (looks.T @ ds)
    if act is not None:
        pi = softmax(np.append(s, child.w0))
        da = pi.copy()
        da[act] -= 1.0
        da *= adv
        g["M"] += np.outer(looks.T @ da[:-1], h)
        g["w0"] = float(da[-1])
        dh = dh + child.M.T @ (looks.T @ da[:-1])
    dpre = dh * (1.0 - h ** 2)
    g["Wx"], g["b"] = np.outer(dpre, x), dpre
    if child.Pos is not None:
        g["Pos"] = np.zeros_like(child.Pos)
    if child.A is not None:
        g["A"], g["U"], g["c"] = np.zeros_like(child.A), np.zeros_like(child.U), np.zeros_like(child.c)
    child.hear_back(child.Wx[:, :child.DU].T @ dpre, cache, g)
    return g


def apply(child, g):
    flat = {k: v for k, v in g.items() if k not in ("E", "w0")}
    flat["w0"] = np.array([g["w0"]])
    for i, v in g["E"].items():
        flat[f"E{i}"] = v
    flat = c1.clip(flat)
    for name in ("M", "Wx", "b", "Pos", "A", "U", "c"):
        if name in flat:
            setattr(child, name, getattr(child, name) - LR * flat[name])
    child.w0 -= LR * float(flat["w0"][0])
    for k, v in flat.items():
        if k.startswith("E"):
            child.E[int(k[1:])] -= LR * v


def act_once(child, looks, u, cache, target, second, learn, rng):
    """One act on the child's turn. Returns (act, right) and learns if asked."""
    x, h = child.state(u, True, second)
    logits = np.append(child.scores(looks, h), child.w0)
    act = int(rng.choice(len(logits), p=softmax(logits))) if learn else int(np.argmax(logits))
    right = act == target
    if learn:
        r = 1.0 if right else 0.0
        adv = r - child.base
        child.base += BASE_RATE * (r - child.base)
        apply(child, grads(child, looks, x, h, cache, target, act, adv))
    child.commit(looks[target])
    return act, right


def live_day(home, child, steps, rng):
    child.reset()
    heard = ""
    for st in steps:
        looks = st["looks"]
        if st["req"] is not None:
            kind, xi, yi, fr2 = st["req"]
            child.reset()                              # an asking moment starts from an empty memory
            y = st["cats"][yi] if yi is not None else None
            u, cache = child.hear(child.ids(home.sentence(kind, st["cats"][xi], y, fr2)))
            if kind == "order":
                acts = [(xi, False), (yi, True)]
            elif kind in ("neg_first", "neg_last"):
                acts = [(yi, False)]
            else:
                acts = [(xi, False)]
            for target, second in acts:                # the request is held in mind for both acts
                _, right = act_once(child, looks, u, cache, target, second, True, rng)
            heard = ""                                 # the moment ends; the answer is not carried on
            continue
        u, cache = child.hear(child.ids(heard))
        x, h = child.state(u, st["child"], False)
        s = child.scores(looks, h)
        act, right = None, False
        if st["child"]:
            act = int(rng.choice(len(s) + 1, p=softmax(np.append(s, child.w0))))
            right = act == st["ni"]
        adv = 0.0
        if act is not None:
            r = 1.0 if right else 0.0
            adv = r - child.base
            child.base += BASE_RATE * (r - child.base)
        apply(child, grads(child, looks, x, h, cache, st["ni"], act, adv))
        child.commit(looks[st["ni"]])
        heard = c1.heard_after(home, st, right, None)


# --- the probes ---------------------------------------------------------------------------------------------------------
def probe_scene(home, seed, tag, a, b):
    """The same 4 things in view (a, b and two others, in a fixed order) and the same frame index for both twins."""
    r = np.random.default_rng([seed, 20, tag, min(a, b), max(a, b)])
    others = [int(c) for c in r.choice([c for c in range(NC) if c not in (a, b)], 2, replace=False)]
    cats = [min(a, b), max(a, b)] + others
    r.shuffle(cats)
    looks = np.array([home.look(c, int(r.integers(3)), r) for c in cats])
    return cats, looks, int(r.integers(1 << 30)), r


def probes(home, child, seed, day):
    out = {}
    rng0 = np.random.default_rng(0)                        # unused for greedy acts; act_once needs an rng argument
    inlife = [p for p in itertools.combinations(range(NC), 2) if frozenset(p) not in home.held_set]
    pick = np.random.default_rng([seed, 21]).choice(len(inlife), len(home.held), replace=False)
    sets = {"held": home.held, "life": [inlife[int(i)] for i in sorted(pick)]}
    for setname, pairs in sets.items():
        for part in ("test", "life"):
            if setname == "life" and part == "life":
                continue
            rec = {"first": [], "second": [], "both": [], "neg": [], "neg_x": [], "after_first": []}
            for (a, b) in pairs:
                for tag, kinds in ((1, ("order",)), (2, ("neg_first", "neg_last")), (3, ("after",))):
                    cats, looks, fr, r = probe_scene(home, seed, tag, a, b)
                    for kind in kinds:
                        for x, y in ((a, b), (b, a)):
                            child.reset()
                            sh = np.random.default_rng([seed, 31, day, tag, a, b, x, REQ_KINDS.index(kind)
                                                        if kind in REQ_KINDS else 9])
                            u, cache = child.hear(child.ids(home.sentence(kind, x, y, fr, part)), shuf=sh)
                            xi, yi = cats.index(x), cats.index(y)
                            if kind == "order":
                                a1, r1 = act_once(child, looks, u, cache, xi, False, False, rng0)
                                a2, r2 = act_once(child, looks, u, cache, yi, True, False, rng0)
                                rec["first"].append(r1)
                                rec["second"].append(r2)
                                rec["both"].append(r1 and r2)
                            elif kind == "after":               # act order X then Y; words name Y first
                                a1, r1 = act_once(child, looks, u, cache, xi, False, False, rng0)
                                rec["after_first"].append(r1)
                            else:
                                a1, r1 = act_once(child, looks, u, cache, yi, False, False, rng0)
                                rec["neg"].append(r1)
                                rec["neg_x"].append(a1 == xi)
            for k, v in rec.items():
                out[f"{setname}_{part}_{k}"] = float(np.mean(v)) if v else None
            out[f"{setname}_{part}_n_order"] = len(rec["first"])
    plain = []
    for c in range(NC):
        cats, looks, fr, r = probe_scene(home, seed, 4, c, (c + 1) % NC)
        child.reset()
        u, cache = child.hear(child.ids(home.sentence("plain", c, None, fr, "test")))
        _, r1 = act_once(child, looks, u, cache, cats.index(c), False, False, rng0)
        plain.append(r1)
    out["plain"] = float(np.mean(plain))
    out["chance_first"], out["chance_named"] = 1 / 5, 1 / 2
    return out


def run(arm, seed, out=None):
    corpus = load_corpus()
    home = Home(seed, corpus)
    child = Child(arm, home.vocab, seed)
    rng = np.random.default_rng([seed, 3, list(ARMS).index(arm)])
    results = {}
    for day in range(DAYS):
        live_day(home, child, home.day([seed, 12, day]), rng)
        if day + 1 in TEST_DAYS:
            results[day + 1] = probes(home, child, seed, day + 1)
    res = {"arm": arm, "seed": seed, "home": home.fingerprint(), "held": home.held, "results": results}
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm.replace('-', 'm')}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], int(sys.argv[3]), Path(sys.argv[4]))
        last = r["results"][max(r["results"])]
        print(sys.argv[2], sys.argv[3], {k: round(v, 3) for k, v in last.items() if isinstance(v, float)})
