"""C2-S code checks (questions.md, "Validity"). Writes checks.log.

  python studies/C2S/checks_c2s.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2s  # noqa: E402

LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def main():
    ok = True
    homes = [c2s.Home(s) for s in range(1, 49)]
    ok &= say("each seed's 6 pairs differ", all(len(set(h.pairs)) == 6 for h in homes))
    ok &= say("Ben's habits differ from the right pairs", all(h.habits[k] != h.pairs[k] for h in homes for k in range(6)))
    # spy on what each arm sees and copies
    seen, copies = {}, {}
    orig_try, orig_copy = c2s.try_box, c2s.copy_step

    def spy_try(child, look, demo, rng, learn, pair):
        if learn:
            seen.setdefault(spy_try.arm, []).append(demo)
        return orig_try(child, look, demo, rng, learn, pair)

    def spy_copy(child, look, demo, w):
        copies.setdefault(spy_try.arm, []).append((demo, w))
        return orig_copy(child, look, demo, w)
    c2s.try_box, c2s.copy_step = spy_try, spy_copy
    runs = {}
    try:
        for arm in c2s.ARMS:
            spy_try.arm = arm
            runs[arm] = c2s.run(arm, 3)
    finally:
        c2s.try_box, c2s.copy_step = orig_try, orig_copy
    ok &= say("T never sees a demonstration", all(d is None for d in seen["T"]))
    ok &= say("Ca sees only Ann", all(d["who"] == c2s.ANN for d in seen["Ca"] if d is not None))
    ok &= say("no demonstrations after day 30", all(all(d is None for d in seen[a][30 * 6:]) for a in c2s.ARMS))
    hid_ok = all(not d["seen"] for a in ("Cb100", "Cp100") for d in seen[a] if d is not None)
    x_ok = True
    ch = c2s.Child(1)
    for a in c2s.ARMS:
        for d in seen[a]:
            if d is not None and not d["seen"]:
                xv = ch.x(np.zeros(c2s.LOOK), d, None, 0)
                x_ok &= xv[c2s.LOOK + 2 + 8] == 0.0 and xv[c2s.LOOK + 2 + 9] == 0.0
    ok &= say("hidden demonstrations carry no result bits; the 100 arms are always hidden", hid_ok and x_ok)
    half = np.mean([not d["seen"] for d in seen["Cb"] if d is not None])
    ok &= say("about half the results hidden in the other arms", 0.4 < half < 0.6, f"({half:.3f})")
    ok &= say("no copy step in T and I", "T" not in copies and "I" not in copies)
    ok &= say("Co copies only seen-open demonstrations",
              all((w > 0) == (d["seen"] and d["opened"]) for d, w in copies["Co"]))
    ok &= say("Cb, Ca, Cb100 copy every demonstration at weight 1",
              all(w == 1.0 for a in ("Cb", "Ca", "Cb100") for _, w in copies[a]))
    # Ct's trust is the same for every child of a seed; Cy's weights equal Ct's for the coin's person
    tr = {a: [t["ct"] for t in runs[a]["trust"]] for a in ("Ct", "Cy", "Cb", "Cp")}
    ok &= say("Ct's trust is independent of the child (same in Ct, Cy, Cb, Cp)", tr["Ct"] == tr["Cy"] == tr["Cb"] == tr["Cp"])
    h3 = c2s.Home(3)
    trust = [c2s.TRUST0, c2s.TRUST0]
    cy_ok, i = True, 0
    for d in range(1, 31):
        for k, look, who, ben_right, hidden, coin_y, coin_px in h3.day(d):
            demo = c2s.demonstration(h3, "Cy", k, who, ben_right, hidden)
            want = c2s.norm(trust, coin_y)
            cy_ok &= abs(copies["Cy"][i][1] - want) < 1e-12
            ct_want = c2s.norm(trust, demo["who"])
            cy_ok &= abs(copies["Ct"][i][1] - ct_want) < 1e-12
            if demo["seen"]:
                trust[demo["who"]] += c2s.TRUST_RATE * ((1.0 if demo["opened"] else 0.0) - trust[demo["who"]])
            i += 1
    ok &= say("Ct's weights follow the demonstrator's trust; Cy's follow the coin's person", cy_ok)
    # Cp updates only when the try used the demonstrated pair; Cpx credits the coin's person
    def replay_p(arm):
        tp = [c2s.TRUST0, c2s.TRUST0]
        good = True
        tries = runs[arm]["tries"]
        j = 0
        for d in range(1, 31):
            for k, look, who, ben_right, hidden, coin_y, coin_px in h3.day(d):
                t = tries[j]
                good &= abs(t["w"] - c2s.norm(tp, t["who"])) < 1e-12
                if t["pair"] == t["shown"]:
                    q = t["who"] if arm != "Cpx" else coin_px
                    tp[q] += c2s.TRUST_RATE * (t["r"] - tp[q])
                j += 1
            good &= runs[arm]["trust"][d - 1]["p"] == tp
        return good
    ok &= say("Cp updates trust only after a try that used the shown pair", replay_p("Cp") and replay_p("Cp100"))
    ok &= say("Cpx credits the coin's person", replay_p("Cpx"))
    # gradient check (C2's)
    rng = np.random.default_rng(1)
    ch = c2s.Child(9)
    for k in ch.p:
        ch.p[k] = ch.p[k] * 5
    x = rng.normal(0, 1, c2s.N_IN)
    a, scale = 2, 0.7
    g = ch.grad(x, a, scale)

    def loss():
        _, z = ch.logits(x)
        return -scale * np.log(c2s.softmax(z)[a])
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
    ok &= say("the same seed gives the same result twice", c2s.run("Cp", 4) == c2s.run("Cp", 4))
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
