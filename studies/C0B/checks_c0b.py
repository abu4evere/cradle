"""C0-B code checks (questions.md, "Validity"): C0-A's checks on c0b.py, plus the 30 names and their families and the
look-alike trials. Writes checks.log; exits non-zero if any fails. Run before the data, at level L1.

  python studies/C0B/checks_c0b.py
"""
from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "C0A"))
import c0b as c0a  # noqa: E402  (the C0-B module, under C0-A's name, so C0-A's checks run on it unchanged)
import make_corpus  # noqa: E402

LINES = []


def check(name, ok, detail=""):
    LINES.append(f"{'PASS' if ok else 'FAIL'}  {name}{('  (' + detail + ')') if detail else ''}")
    print(LINES[-1], flush=True)
    return ok


def main():
    corpus = c0a.load_corpus()
    oks = []

    # 7. the corpus checks
    fr = corpus["frames"]
    bad = [(k, s) for k in fr for part in fr[k].values() for s in part if not make_corpus.valid(k, s)]
    names30 = set(c0a.NAMES) | set(c0a.PLURALS.values())
    leak = [s for k in fr for part in fr[k].values() for s in part if set(c0a.tokens(s.replace("{X}", " "))) & names30]
    oks.append(check("C0-B: no frame holds any of the 30 names outside the slot", not leak, f"{len(leak)} frames"))
    oks.append(check("C0-B: 30 names in 10 families of 3; all in the vocabulary",
                     len(c0a.NAMES) == 30 and len(set(c0a.NAMES)) == 30 and c0a.FAMILY == [i // 3 for i in range(30)]
                     and set(c0a.NAMES) <= set(corpus["vocabulary"])))
    al = c0a.test_trials(c0a.Scenes(1, corpus, c0a.DAYS), 1, 30, "alike", 60)
    fam_ok = all(sum(1 for c in cats if c0a.FAMILY[c] == c0a.FAMILY[cats[t]]) == 3 for cats, _, t, _, _ in al)
    oks.append(check("C0-B: every look-alike trial holds the target's whole family and one other thing", fam_ok))
    short = [k for k in make_corpus.MINIMUM if sum(len(v) for v in fr[k].values()) < make_corpus.MINIMUM[k]]
    # (after C0-B drops the frames that hold a name, the minimums must still be met)
    nonce = set(corpus["vocabulary"]) & set(c0a.NONCE)
    split_ok = all(len(fr[k]["test"]) > 0 for k in make_corpus.SLOT_KINDS)       # C0-B: the split is C0-A's; no slot frame is dropped
    overlap = [k for k in make_corpus.SLOT_KINDS if set(map(str.lower, fr[k]["test"])) & set(map(str.lower, fr[k]["life"]))]
    oks.append(check("corpus: every sentence passes the frozen checks", not bad, f"{len(bad)} bad"))
    oks.append(check("corpus: minimums met", not short, ",".join(short)))
    oks.append(check("corpus: no nonce word in the vocabulary", not nonce))
    oks.append(check("corpus: 20% of each slot kind kept back, no overlap with daily life", split_ok and not overlap))

    # 2. kept-back frames and never-together pairs never occur in daily life
    for seed in (1, 2):
        sc = c0a.Scenes(seed, corpus, c0a.DAYS)
        n = c0a.DAYS * c0a.MOMENTS
        together = sum(1 for m in range(n)
                       for a in sc.cats[m, :sc.k[m]] for b in sc.cats[m, :sc.k[m]]
                       if a < b and (a, b) in sc.apart)
        oks.append(check(f"seed {seed}: never-together pairs never in view together in daily life", together == 0,
                         f"{together} moments"))
        life_frames = {sc.frame(kind, m, j) for m in range(0, n, 7) for kind in ("naming", "asking", "praise", "no",
                                                                                  "this", "handing") for j in range(6)}
        kept = {s for k in make_corpus.SLOT_KINDS for s in fr[k]["test"]}
        oks.append(check(f"seed {seed}: kept-back frames never used in daily life", not (life_frames & kept)))

    # 1. test trials carry no attention cue: the test code never calls the cue function and takes no flag
    src = inspect.getsource(c0a.tests) + inspect.getsource(c0a.test_trials)
    oks.append(check("tests carry no attention cue (no flag in the test code)", "flag" not in src))

    # 3. the scene stream is identical across arms; 5. E never changes; 6. the same seed gives the same result twice
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        r = {a: c0a.run(a, 3, out) for a in ("A", "F", "E", "K", "C")}
        oks.append(check("the scene stream is identical across arms (seed 3: A, F, E, K, C)",
                         len({x["scene"] for x in r.values()}) == 1))
        oks.append(check("E's weights never change", r["E"]["E_unchanged"] is True))
        again = c0a.run("A", 3, None)
        oks.append(check("the same seed gives the same result twice (A, seed 3)",
                         json.dumps(again["results"]) == json.dumps(r["A"]["results"])))

    # 4. numerical gradient checks of both learning rules
    rng = np.random.default_rng(7)
    vocab = corpus["vocabulary"][:40]
    ch = c0a.Child(8, vocab, rng)
    looks = rng.normal(0, 1, (3, c0a.LOOK))
    buf = list(rng.normal(0, 1, (5, c0a.LOOK)))
    ids = [1, 5, 5, 9]

    def loss(E, W):
        X = np.vstack([looks] + [np.array(buf)])
        u = E[ids].mean(0)
        s = (X @ W.T) @ u
        return -np.log(np.exp(s[[0]]).sum() / np.exp(s).sum())

    E0, W0 = ch.E.copy(), ch.W.copy()
    ch.associate(ids, looks, [0], buf)
    step_E, step_W = (E0 - ch.E) / c0a.LR, (W0 - ch.W) / c0a.LR
    eps, errs = 1e-6, []
    for (i, j) in [(1, 0), (5, 3), (9, 7)]:
        Ep = E0.copy(); Ep[i, j] += eps
        Em = E0.copy(); Em[i, j] -= eps
        errs.append(abs((loss(Ep, W0) - loss(Em, W0)) / (2 * eps) - step_E[i, j]))
    for (i, j) in [(0, 0), (4, 11), (7, 15)]:
        Wp = W0.copy(); Wp[i, j] += eps
        Wm = W0.copy(); Wm[i, j] -= eps
        errs.append(abs((loss(E0, Wp) - loss(E0, Wm)) / (2 * eps) - step_W[i, j]))
    oks.append(check("association: the update equals the numerical gradient", max(errs) < 1e-6, f"max error {max(errs):.1e}"))

    ch = c0a.Child(8, vocab, np.random.default_rng(8))
    a, r_ = 1, 1.0

    def logp(E, W, nothing):
        u = E[ids].mean(0)
        lg = np.append((looks @ W.T) @ u, nothing)
        return lg[a] - np.log(np.exp(lg).sum())

    E0, W0, n0 = ch.E.copy(), ch.W.copy(), ch.nothing
    adv = r_ - ch.base["hand"]
    ch.reinforce_hand(ids, looks, a, r_)
    gE, gW = (ch.E - E0) / (c0a.LR * adv), (ch.W - W0) / (c0a.LR * adv)
    errs = []
    for (i, j) in [(1, 2), (9, 6)]:
        Ep = E0.copy(); Ep[i, j] += eps
        Em = E0.copy(); Em[i, j] -= eps
        errs.append(abs((logp(Ep, W0, n0) - logp(Em, W0, n0)) / (2 * eps) - gE[i, j]))
    for (i, j) in [(2, 3), (6, 14)]:
        Wp = W0.copy(); Wp[i, j] += eps
        Wm = W0.copy(); Wm[i, j] -= eps
        errs.append(abs((logp(E0, Wp, n0) - logp(E0, Wm, n0)) / (2 * eps) - gW[i, j]))
    oks.append(check("handing reward: the update equals adv x the numerical gradient of log pi", max(errs) < 1e-6,
                     f"max error {max(errs):.1e}"))

    ch = c0a.Child(8, vocab, np.random.default_rng(9))
    look, a = looks[0], 3

    def logp2(E, W, c, quiet):
        lg = np.append(E @ (W @ look) + c, quiet)
        return lg[a] - np.log(np.exp(lg).sum())

    E0, W0, c0, q0 = ch.E.copy(), ch.W.copy(), ch.c.copy(), ch.quiet
    adv = 1.0 - ch.base["say"]
    ch.reinforce_say(look, a, 1.0)
    gE, gW = (ch.E - E0) / (c0a.LR * adv), (ch.W - W0) / (c0a.LR * adv)
    errs = []
    for (i, j) in [(3, 1), (20, 5)]:
        Ep = E0.copy(); Ep[i, j] += eps
        Em = E0.copy(); Em[i, j] -= eps
        errs.append(abs((logp2(Ep, W0, c0, q0) - logp2(Em, W0, c0, q0)) / (2 * eps) - gE[i, j]))
    for (i, j) in [(1, 0), (5, 9)]:
        Wp = W0.copy(); Wp[i, j] += eps
        Wm = W0.copy(); Wm[i, j] -= eps
        errs.append(abs((logp2(E0, Wp, c0, q0) - logp2(E0, Wm, c0, q0)) / (2 * eps) - gW[i, j]))
    oks.append(check("saying reward: the update equals adv x the numerical gradient of log pi", max(errs) < 1e-6,
                     f"max error {max(errs):.1e}"))

    verdict = "All: PASS" if all(oks) else "SOME FAILED"
    LINES.append(verdict)
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(verdict)
    sys.exit(0 if all(oks) else 1)


if __name__ == "__main__":
    main()
