"""C2 code checks (questions.md, "Validity"). Writes checks.log.

  python studies/C2/checks_c2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2  # noqa: E402

LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def main():
    ok = True
    homes = [c2.Home(s) for s in range(1, 25)]
    ok &= say("each seed's 6 pairs differ", all(len(set(h.pairs)) == 6 for h in homes))
    # what each arm sees, read from a spy on try_box
    seen = {}
    orig = c2.try_box

    def spy(child, look, demo, rng, learn, pair, _arm=[None]):
        if learn:
            seen.setdefault(spy.arm, []).append(demo)
        return orig(child, look, demo, rng, learn, pair)
    c2.try_box = spy
    copies = {}
    orig_copy = c2.copy_step

    def spy_copy(child, look, demo, a1, a2):
        copies[spy.arm] = copies.get(spy.arm, 0) + 1
        return orig_copy(child, look, demo, a1, a2)
    c2.copy_step = spy_copy
    try:
        for arm in c2.ARMS:
            spy.arm = arm
            c2.run(arm, 3)
    finally:
        c2.try_box, c2.copy_step = orig, orig_copy
    ok &= say("T never sees a demonstration", all(d is None for d in seen["T"]))
    ok &= say("E sees only the result (no acts)", all(d is None or d[0] == "result" for d in seen["E"]) and
              any(d is not None for d in seen["E"]))
    ok &= say("I, Ic, Iw see the acts on days 1-30 and nothing after",
              all(any(d is not None and d[0] == "acts" for d in seen[a]) and all(d is None for d in seen[a][30 * 6:])
                  for a in ("I", "Ic", "Iw")))
    ok &= say("the copy step only in Ic and Iw", set(copies) == {"Ic", "Iw"} and copies["Ic"] == 30 * 6, str(copies))
    iw = [d for d in seen["Iw"] if d is not None]
    h = c2.Home(3)
    # every wrong demonstration (shown pair differs from the right one) is shown as not opened
    days = [t for d in range(1, 31) for t in h.day(d)]
    wrong_ok = all((d[3] is False) == (tuple(d[1:3]) != h.pairs[k]) for d, (k, _, _, _) in zip(iw, days))
    ok &= say("Iw: a demonstration opens the box exactly when its pair is right", wrong_ok and any(not d[3] for d in iw))
    # gradient check of the act head
    rng = np.random.default_rng(1)
    ch = c2.Child(9)
    for k in ch.p:
        ch.p[k] = ch.p[k] * 5
    x = rng.normal(0, 1, c2.N_IN)
    a, scale = 2, 0.7
    g = ch.grad(x, a, scale)

    def loss():
        _, z = ch.logits(x)
        return -scale * np.log(c2.softmax(z)[a])
    worst = 0.0
    for name, P in ch.p.items():
        f, gf = P.reshape(-1), g[name].reshape(-1)
        for i in rng.choice(f.size, min(20, f.size), replace=False):
            o = f[i]
            f[i] = o + 1e-6
            lp = loss()
            f[i] = o - 1e-6
            lm = loss()
            f[i] = o
            num = (lp - lm) / 2e-6
            worst = max(worst, abs(num - gf[i]) / max(1e-3, abs(num) + abs(gf[i])))
    ok &= say("act-head gradients equal finite differences", worst < 1e-5, f"(worst rel. {worst:.1e})")
    ok &= say("the same seed gives the same result twice", c2.run("Iw", 4) == c2.run("Iw", 4))
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
