"""C1 code checks (questions.md, "Validity"; run before the data). Writes checks.log; exits non-zero if any fails.

  python studies/C1/checks_c1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c1  # noqa: E402

LINES = []


def check(name, ok, detail=""):
    LINES.append(f"{'PASS' if ok else 'FAIL'}  {name}{('  (' + detail + ')') if detail else ''}")
    print(LINES[-1], flush=True)
    return ok


def loss_window(child, xs_fixed, ids_list, turns, h0, looks, ni):
    """The prediction loss at the last step, recomputed from h0 over the window with the child's present numbers."""
    h = h0
    for (xf, ids, turn) in zip(xs_fixed, ids_list, turns):
        u = child.E[ids].mean(0) if ids else np.zeros(c1.D_HEAR)
        x = np.concatenate([u, xf[c1.D_HEAR:]])
        h = np.tanh(child.Wx @ x + child.b + (child.Wh @ h if child.Wh is not None else 0.0))
    s = c1.softmax(looks @ (child.M @ h))
    return -np.log(s[ni]), h


def main():
    corpus = c1.load_corpus()
    oks = []
    # the corpus: no order words, no routine names
    leak = [f for parts in corpus["frames"].values() for fr in parts.values() for f in fr
            if set(c1.tokens(f.replace("{X}", " "))) & c1.ORDER_WORDS]
    oks.append(check("no frame names a routine or uses an order word", not leak, f"{len(leak)}"))
    mins = {k: sum(len(v) for v in corpus["frames"][k].values()) for k in ("naming", "praise", "this")}
    oks.append(check("the frames C1 uses remain (naming, praise, this)", all(v >= 20 for v in mins.values()), str(mins)))
    # routines share things across routines
    shared = []
    for seed in range(1, 17):
        home = c1.Home(seed, corpus)
        from collections import Counter
        cnt = Counter(it for r in home.routines for it, _ in r)
        shared.append(sum(1 for v in cnt.values() if v >= 2))
    oks.append(check("every child's routines share things (seeds 1-16)", min(shared) >= 1, f"shared things: {shared}"))
    # no memory leak in N: the state ignores everything before the present step
    home = c1.Home(1, corpus)
    ch = c1.Child("N", home.vocab, 1)
    st = home.day([1, 13, 7, 0])[0]
    ids = ch.ids("Look, a cup!")
    _, _, h1 = ch.step_state(ids, st["child"])
    ch.prev = [np.ones(c1.LOOK) * 3 for _ in range(4)]
    ch.h = np.ones(c1.H)
    _, _, h2 = ch.step_state(ids, st["child"])
    oks.append(check("N's state depends on nothing before the present step", np.array_equal(h1, h2)))
    # test days identical across arms; S's life days differ from R's only by the order within routines
    a = c1.Home(2, corpus).day([2, 13, 30, 5])
    b = c1.Home(2, corpus).day([2, 13, 30, 5])
    oks.append(check("test days are identical whatever the arm",
                     [s["need"] for s in a] == [s["need"] for s in b] and all(np.array_equal(x["looks"], y["looks"]) for x, y in zip(a, b))))
    # gradients: prediction through time (R), and the act (this step), against finite differences
    home = c1.Home(5, corpus)
    ch = c1.Child("R", home.vocab, 5)
    steps = home.day([5, 12, 40])
    ch.reset()
    heard = ""
    xs, idss, turns = [], [], []
    for st in steps[:10]:
        ids = ch.ids(heard)
        x, hp, h = ch.step_state(ids, st["child"])
        ch.commit(x, ids, hp, h, st["looks"][st["ni"]])
        heard = c1.heard_after(home, st, True, None)
    st = steps[10] if len(steps) > 10 else steps[-1]
    ids = ch.ids(heard)
    x, hp, h = ch.step_state(ids, st["child"])
    g = c1.grads(ch, st["looks"], x, ids, hp, h, st["ni"])
    window = ch.trace + [(x, ids, hp, h)]
    h0 = window[0][2]
    xs_fixed = [w[0] for w in window]
    ids_list = [w[1] for w in window]
    errs = []
    eps = 1e-6
    for name, idx in (("Wx", (3, 2)), ("Wx", (10, 17)), ("Wh", (4, 9)), ("Wh", (20, 1)), ("M", (2, 5)), ("b", (7,))):
        P = getattr(ch, name)
        old = P[idx]
        P[idx] = old + eps
        lp, _ = loss_window(ch, xs_fixed, ids_list, None or [0] * len(window), h0, st["looks"], st["ni"])
        P[idx] = old - eps
        lm, _ = loss_window(ch, xs_fixed, ids_list, [0] * len(window), h0, st["looks"], st["ni"])
        P[idx] = old
        errs.append(abs((lp - lm) / (2 * eps) - g[name][idx]))
    wid = [i for i in set(i for w in ids_list for i in w)][:2]
    for i in wid:
        for j in (0, 5):
            old = ch.E[i, j]
            ch.E[i, j] = old + eps
            lp, _ = loss_window(ch, xs_fixed, ids_list, [0] * len(window), h0, st["looks"], st["ni"])
            ch.E[i, j] = old - eps
            lm, _ = loss_window(ch, xs_fixed, ids_list, [0] * len(window), h0, st["looks"], st["ni"])
            ch.E[i, j] = old
            errs.append(abs((lp - lm) / (2 * eps) - g["E"].get(i, np.zeros(c1.D_HEAR))[j]))
    oks.append(check("prediction gradient through time (R, 8 steps) = finite differences", max(errs) < 1e-6,
                     f"max error {max(errs):.1e}; window {len(window)} steps"))
    # the act gradient (this step only): -adv log pi(act)
    act, adv = 1, 0.7
    g0 = c1.grads(ch, st["looks"], x, ids, hp, h, st["ni"])
    g1 = c1.grads(ch, st["looks"], x, ids, hp, h, st["ni"], act=act, adv=adv)

    def nlogpi():
        u = ch.E[ids].mean(0) if ids else np.zeros(c1.D_HEAR)
        xx = np.concatenate([u, x[c1.D_HEAR:]])
        hh = np.tanh(ch.Wx @ xx + ch.b + ch.Wh @ hp)
        lg = np.append(st["looks"] @ (ch.M @ hh), ch.w0)
        return -adv * (lg[act] - lg.max() - np.log(np.exp(lg - lg.max()).sum()))
    errs = []
    for name, idx in (("Wx", (1, 1)), ("Wx", (12, 20)), ("M", (3, 3)), ("b", (2,))):
        P = getattr(ch, name)
        old = P[idx]
        P[idx] = old + eps
        lp = nlogpi()
        P[idx] = old - eps
        lm = nlogpi()
        P[idx] = old
        errs.append(abs((lp - lm) / (2 * eps) - (g1[name][idx] - g0[name][idx])))
    old = ch.w0
    ch.w0 = old + eps
    lp = nlogpi()
    ch.w0 = old - eps
    lm = nlogpi()
    ch.w0 = old
    errs.append(abs((lp - lm) / (2 * eps) - g1["w0"]))
    oks.append(check("act gradient (this step) = finite differences", max(errs) < 1e-6, f"max error {max(errs):.1e}"))
    # the same seed gives the same result twice
    r1 = c1.run("P", 3, None)
    r2 = c1.run("P", 3, None)
    oks.append(check("the same seed gives the same result twice (P, seed 3)",
                     json.dumps(r1["results"]) == json.dumps(r2["results"])))
    verdict = "All: PASS" if all(oks) else "SOME FAILED"
    LINES.append(verdict)
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(verdict)
    sys.exit(0 if all(oks) else 1)


if __name__ == "__main__":
    main()
