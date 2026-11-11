"""C1.5's code checks (questions.md, "Validity"). Run before any study run; writes checks.log.

  python studies/C1_5/checks_c15.py
"""
from __future__ import annotations

import copy
import hashlib
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c15  # noqa: E402

LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def twin_sentences(home, n=40):
    r = np.random.default_rng(7)
    out = []
    for _ in range(n):
        a, b = (int(c) for c in r.choice(c15.NC, 2, replace=False))
        kind = ("order", "neg_first", "neg_last", "after")[int(r.integers(4))]
        part = ("life", "test")[int(r.integers(2))]
        fr = int(r.integers(1 << 30))
        out.append((home.sentence(kind, a, b, fr, part), home.sentence(kind, b, a, fr, part)))
    return out


def check_b_twins(home):
    ch = c15.Child("B", home.vocab, 1)
    ok = all(np.allclose(ch.hear(ch.ids(s1))[0], ch.hear(ch.ids(s2))[0]) for s1, s2 in twin_sentences(home))
    return say("B hears a twin pair the same", ok)


def check_q_minus(home):
    ch = c15.Child("Q-", home.vocab, 1)
    worst = 0.0
    for s1, s2 in twin_sentences(home, 10):
        r1, r2 = np.random.default_rng(1), np.random.default_rng(2)
        m1 = np.mean([ch.hear(ch.ids(s1), shuf=r1)[0] for _ in range(3000)], 0)
        m2 = np.mean([ch.hear(ch.ids(s2), shuf=r2)[0] for _ in range(3000)], 0)
        worst = max(worst, float(np.abs(m1 - m2).max()))
    # each mean is over 3,000 shuffles; the reader's outputs lie in (-1, 1)
    return say("Q- carries no order (twins' mean readings over 3,000 shuffles agree)", worst < 0.01, f"(max gap {worst:.4f})")


def check_held(home, seed):
    used = 0
    for day in range(c15.DAYS):
        for st in home.day([seed, 12, day]):
            if st.get("ask") and st["req"][0] != "plain":
                pair = frozenset((st["cats"][st["req"][1]], st["cats"][st["req"][2]]))
                if pair in home.held_set:
                    used += 1
    return say("held-out pairs never in a life request (720 days)", used == 0, f"(seed {seed}, {len(home.held)} held)")


def probe_fingerprint(home, seed):
    h = hashlib.sha256()
    for (a, b) in home.held:
        for tag in (1, 2, 3):
            cats, looks, fr, _ = c15.probe_scene(home, seed, tag, a, b)
            h.update(np.asarray(cats).tobytes() + looks.tobytes() + str(fr).encode())
    return h.hexdigest()


def check_probes(seed):
    fps = set()
    for arm in c15.ARMS:
        home = c15.Home(seed, c15.load_corpus())       # a fresh home per arm, as each run builds its own
        fps.add(probe_fingerprint(home, seed))
    return say("probes identical across arms", len(fps) == 1)


def loss(child, looks, u_fn, target, act, adv):
    """The scalar whose gradient grads() returns: -log p(target) - adv * log pi(act)."""
    u, _ = u_fn()
    x, h = child.state(u, True, True)
    s = child.scores(looks, h)
    p = c15.softmax(s)
    pi = c15.softmax(np.append(s, child.w0))
    return -np.log(p[target]) - adv * np.log(pi[act])


def check_grads(home):
    ok_all = True
    r = np.random.default_rng(3)
    for arm in c15.ARMS:
        ch = c15.Child(arm, home.vocab, 2)
        for name in ("Wx", "M", "Pos", "A", "U"):    # make the small weights larger, so every path carries signal
            if getattr(ch, name, None) is not None:
                setattr(ch, name, getattr(ch, name) * 5)
        ch.prev = [r.normal(0, 1, c15.LOOK) for _ in range(4)]
        cats = [3, 7, 11, 20]
        looks = np.array([home.look(c, 0, r) for c in cats])
        sent = home.sentence("order", 3, 7, 5, "life")
        ids = ch.ids(sent)
        perm_seed = 11

        def u_fn():
            return ch.hear(ids, shuf=np.random.default_rng(perm_seed))
        target, act, adv = 1, 2, 0.7
        u, cache = u_fn()
        x, h = ch.state(u, True, True)
        g = c15.grads(ch, looks, x, h, cache, target, act, adv)
        eps, worst = 1e-6, 0.0
        params = [("M", None), ("Wx", None), ("b", None), ("Pos", None), ("A", None), ("U", None), ("c", None)]
        params += [("E", i) for i in sorted(set(ids))[:6]]
        for name, row in params:
            P = getattr(ch, name, None) if name != "E" else ch.E[row]
            if P is None:
                continue
            G = g[name] if name != "E" else g["E"].get(row, np.zeros_like(P))
            flat, gflat = P.reshape(-1), np.asarray(G).reshape(-1)
            for k in r.choice(flat.size, min(12, flat.size), replace=False):
                old = flat[k]
                flat[k] = old + eps
                lp = loss(ch, looks, u_fn, target, act, adv)
                flat[k] = old - eps
                lm = loss(ch, looks, u_fn, target, act, adv)
                flat[k] = old
                num = (lp - lm) / (2 * eps)
                worst = max(worst, abs(num - gflat[k]) / max(1e-3, abs(num) + abs(gflat[k])))   # floor: tiny gradients are FD noise
        ok = worst < 1e-4
        ok_all &= ok
        say(f"gradients equal finite differences, arm {arm} (through the hearing part)", ok, f"(worst rel. {worst:.2e})")
    return ok_all


def check_same_twice(seed):
    def short():
        c15.DAYS, c15.TEST_DAYS = 20, [20]
        try:
            return c15.run("Q", seed)
        finally:
            c15.DAYS, c15.TEST_DAYS = 720, [30, 90, 180, 360, 720]
    a, b = short(), short()
    return say("the same seed gives the same result twice (arm Q, 20 days)", a == b)


def main():
    corpus = c15.load_corpus()
    home = c15.Home(1, corpus)
    ok = True
    ok &= check_b_twins(home)
    ok &= check_q_minus(home)
    ok &= check_held(home, 1)
    ok &= check_probes(5)
    ok &= check_grads(home)
    ok &= check_same_twice(4)
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    print(LINES[-1])
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
