"""C1-B code checks (questions.md, "Validity"). Run before any study run; writes checks.log.

  python studies/C1B/checks_c1b.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c1b  # noqa: E402

c1 = c1b.c1
LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def params(ch):
    return np.concatenate([ch.M.ravel(), ch.Wx.ravel(), ch.b, ch.E.ravel(), [ch.w0, ch.base]])


def main():
    corpus = c1.load_corpus()
    home = c1.Home(3, corpus)
    ok = True
    # 1. arm A's day (no sibling) equals C1's own live_day for the same child, steps and generator
    a = c1.Child("W", home.vocab, 1003)
    b = copy.deepcopy(a)
    ra, rb = np.random.default_rng(7), np.random.default_rng(7)
    for day in range(20):
        steps = home.day([3, 12, day])
        coins = np.random.default_rng([3, 40, day]).random(len(steps))
        c1b.joint_day(home, None, a, steps, None, ra, "A", coins, {"own": 0, "sib": 0, "seen": 0, "imitated": 0})
        c1.live_day(home, b, home.day([3, 12, day]), True, rb)
    ok &= say("arm A's day equals C1's live_day exactly (20 days)", np.array_equal(params(a), params(b)))
    # 2. what the younger receives, by arm
    older = c1.Child("W", home.vocab, 3)
    ro = np.random.default_rng([3, 3, 2])
    for day in range(30):
        c1.live_day(home, older, home.day([3, 12, day]), True, ro)
    res = {}
    for arm in ("Ym", "Yo", "Y", "Yi"):
        o, y = copy.deepcopy(older), c1.Child("W", home.vocab, 1003)
        count = {"own": 0, "sib": 0, "seen": 0, "imitated": 0}
        heard_after_sib = []
        orig = c1b.watch

        def spy(ch, st, heard, _y=y):
            if ch is _y:
                heard_after_sib.append(heard)
            return orig(ch, st, heard)
        c1b.watch = spy
        try:
            for day in range(30, 40):
                steps = home.day([3, 12, day])
                coins = np.random.default_rng([3, 40, day]).random(len(steps))
                c1b.joint_day(home, o, y, steps, np.random.default_rng(1), np.random.default_rng(2), arm, coins, count)
        finally:
            c1b.watch = orig
        res[arm] = count
    ok &= say("Y- never sees a sibling step", res["Ym"]["seen"] == 0 and res["Ym"]["sib"] > 0, str(res["Ym"]))
    ok &= say("Yo, Y, Yi see every sibling step", all(res[a]["seen"] == res[a]["sib"] > 0 for a in ("Yo", "Y", "Yi")))
    ok &= say("only Yi imitates", res["Yi"]["imitated"] > 0 and all(res[a]["imitated"] == 0 for a in ("Ym", "Yo", "Y")))
    # 3. Yo hears nothing after a sibling's turn; Y hears the parent's answer (one hand-built step)
    st = home.day([3, 12, 50])
    turn = next(s for s in st if s["child"])
    for arm, want_empty in (("Yo", True), ("Y", False)):
        o, y = copy.deepcopy(older), c1.Child("W", home.vocab, 1003)
        heard = []
        orig = c1b.watch

        def spy2(ch, s, h, _y=y):
            if ch is _y:
                heard.append(h)
            return orig(ch, s, h)
        c1b.watch = spy2
        try:
            c1b.joint_day(home, o, y, [turn, dict(turn, child=False)], np.random.default_rng(1),
                          np.random.default_rng(2), arm, np.array([0.9, 0.9]), {"own": 0, "sib": 0, "seen": 0,
                                                                                "imitated": 0})
        finally:
            c1b.watch = orig
        # heard[0]: at the sibling's step (what it heard before); heard[1]: at the next step (after the answer)
        got_empty = heard[1] == ""
        ok &= say(f"{arm}: after the sibling's turn the younger hears {'nothing' if want_empty else 'the answer'}",
                  got_empty == want_empty, repr(heard[1])[:60])
    # 4. the imitation step = the act part of C1's gradient, at half the learning rate
    y = c1.Child("W", home.vocab, 1003)
    y.base = 0.3
    before = params(y)
    c1b.imitate(y, turn, "")
    ids = []
    x, hp, h = y.step_state(ids, True)
    z = copy.deepcopy(c1.Child("W", home.vocab, 1003))
    z.base = 0.3
    x, hp, h = z.step_state([], True)
    gb = c1.grads(z, turn["looks"], x, [], hp, h, turn["ni"], turn["ni"], 1.0 - 0.3)
    gp = c1.grads(z, turn["looks"], x, [], hp, h, turn["ni"], None, 0.0)
    g = {"M": gb["M"] - gp["M"], "Wx": gb["Wx"] - gp["Wx"], "b": gb["b"] - gp["b"], "w0": gb["w0"] - gp["w0"], "E": {}}
    keep = c1.LR
    c1.LR = keep * 0.5
    c1.apply(z, g)
    c1.LR = keep
    ok &= say("the imitation step equals the act gradient at half the rate, and leaves the baseline",
              np.allclose(params(y), params(z)) and y.base == 0.3 and not np.array_equal(before, params(y)))
    # 5. the same seed twice
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        c1b_days = c1b.DAYS
        c1b.DAYS, c1b.OLDER_DAYS = 20, 20
        try:
            r1 = c1b.run("Yi", 5)
            r2 = c1b.run("Yi", 5)
        finally:
            c1b.DAYS, c1b.OLDER_DAYS = c1b_days, 360
    ok &= say("the same seed gives the same result twice (Yi, short)", r1 == r2)
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
