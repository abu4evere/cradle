"""C2-E code checks (questions.md, "Validity"). Writes checks.log.

  python studies/C2E/checks_c2e.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2e  # noqa: E402

LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def main():
    ok = True
    homes = [c2e.Home(s) for s in range(1, 49)]
    ok &= say("each seed's 6 pairs differ", all(len(set(h.pairs)) == 6 for h in homes))
    ok &= say("each person's habits differ from the right pairs",
              all(h.habits[p][k] != h.pairs[k] for h in homes for p in (0, 1) for k in range(6)))
    # expertise rates over the draws of 48 seeds, days 1-30
    exp_r, oth_r = [], []
    for h in homes:
        for d in range(1, 31):
            for k, look, who, u, hidden, coin in h.day(d):
                dm = c2e.demonstration(h, k, who, u, hidden)
                (exp_r if who == c2e.expert_of(k) else oth_r).append(dm["opened"])
    ok &= say("expert slots right about 0.85, non-expert about 0.25", abs(np.mean(exp_r) - 0.85) < 0.02 and
              abs(np.mean(oth_r) - 0.25) < 0.02, f"({np.mean(exp_r):.3f}, {np.mean(oth_r):.3f})")
    # spies
    seen, copies = {}, {}
    orig_try, orig_copy = c2e.try_box, c2e.copy_step

    def spy_try(child, look, demo, rng, learn, pair):
        if learn:
            seen.setdefault(spy_try.key, []).append((demo, pair))
        return orig_try(child, look, demo, rng, learn, pair)

    def spy_copy(child, look, demo, w):
        copies.setdefault(spy_try.key, []).append((demo, w))
        return orig_copy(child, look, demo, w)
    c2e.try_box, c2e.copy_step = spy_try, spy_copy
    runs = {}
    try:
        for arm in c2e.ARMS:
            for pr in c2e.PRACTICE:
                spy_try.key = (arm, pr)
                runs[(arm, pr)] = c2e.run(arm, pr, 3)
    finally:
        c2e.try_box, c2e.copy_step = orig_try, orig_copy
    h3 = c2e.Home(3)
    # scarce: own tries only on the cycling kind
    sc_ok = True
    for arm in c2e.ARMS:
        tr = runs[(arm, "S")]["tries"]
        sc_ok &= all(t["k"] == (t["d"] - 1) % 6 for t in tr) and len(tr) == 60
        sc_ok &= len(runs[(arm, "F")]["tries"]) == 360
    ok &= say("scarce practice: one own try a day, on the cycling kind; full: six", sc_ok)
    ok &= say("T never sees a demonstration", all(dm is None for dm, _ in seen[("T", "F")]))
    hid_ok = True
    ch = c2e.Child(1)
    for key, lst in copies.items():
        for dm, w in lst:
            if not dm["seen"]:
                xv = ch.x(np.zeros(c2e.LOOK), dm, None, 0)
                hid_ok &= xv[c2e.LOOK + 2 + 8] == 0.0 and xv[c2e.LOOK + 2 + 9] == 0.0
    ok &= say("hidden demonstrations carry no result bits", hid_ok)
    ok &= say("no copy step in T and I", all(k[0] not in ("T", "I") for k in copies))
    ok &= say("copy steps at all 6 slots on days 1-30 in both practice levels",
              all(len(copies[(a, p)]) == 180 for a in ("Cb", "Ct", "Ctk", "Cyk", "Cok", "Cp", "Cpk") for p in c2e.PRACTICE))
    ok &= say("Cb's weights are 1", all(w == 1.0 for p in c2e.PRACTICE for _, w in copies[("Cb", p)]))
    ok &= say("Cok copies only the expert of the kind",
              all((w == 1.0) == (dm["who"] == c2e.expert_of(kk))
                  for (dm, w), kk in zip(copies[("Cok", "F")], [k for d in range(1, 31) for k, *_ in h3.day(d)])))
    # Ct, Ctk weights from an independent replay; Cyk follows the coin
    tct = [0.5, 0.5]
    tck = [[0.5] * 6, [0.5] * 6]
    i, rep_ok = 0, True
    for d in range(1, 31):
        for k, look, who, u, hidden, coin in h3.day(d):
            dm = c2e.demonstration(h3, k, who, u, hidden)
            p = dm["who"]
            for pr in c2e.PRACTICE:
                rep_ok &= abs(copies[("Ct", pr)][i][1] - c2e.wnorm(tct[0], tct[1], tct[p])) < 1e-12
                rep_ok &= abs(copies[("Ctk", pr)][i][1] - c2e.wnorm(tck[0][k], tck[1][k], tck[p][k])) < 1e-12
                rep_ok &= abs(copies[("Cyk", pr)][i][1] - c2e.wnorm(tck[0][k], tck[1][k], tck[coin][k])) < 1e-12
            if dm["seen"]:
                o = 1.0 if dm["opened"] else 0.0
                tct[p] += 0.3 * (o - tct[p])
                tck[p][k] += 0.3 * (o - tck[p][k])
            i += 1
    ok &= say("Ct and Ctk weights equal an independent replay (child-independent); Cyk follows the coin", rep_ok)
    # Cp / Cpk update only after a try that used the shown pair
    upd_ok = True
    for pr in c2e.PRACTICE:
        for arm in ("Cp", "Cpk"):
            tr = [t for t in runs[(arm, pr)]["tries"] if t["d"] <= 30]
            n_used = sum(1 for t in tr if t["pair"] == t["shown"])
            upd_ok &= runs[(arm, pr)]["trust_updates"] == n_used
    ok &= say("Cp and Cpk update only after a try that used the shown pair", upd_ok)
    # gradient check
    rng = np.random.default_rng(1)
    ch = c2e.Child(9)
    for k in ch.p:
        ch.p[k] = ch.p[k] * 5
    x = rng.normal(0, 1, c2e.N_IN)
    a, scale = 2, 0.7
    g = ch.grad(x, a, scale)

    def loss():
        _, z = ch.logits(x)
        return -scale * np.log(c2e.softmax(z)[a])
    worst = 0.0
    for name, P in ch.p.items():
        f, gf = P.reshape(-1), g[name].reshape(-1)
        for j in rng.choice(f.size, min(20, f.size), replace=False):
            o = f[j]
            f[j] = o + 1e-6
            lp = loss()
            f[j] = o - 1e-6
            lm = loss()
            f[j] = o
            num = (lp - lm) / 2e-6
            worst = max(worst, abs(num - gf[j]) / max(1e-3, abs(num) + abs(gf[j])))
    ok &= say("act-head gradients equal finite differences", worst < 1e-5, f"(worst rel. {worst:.1e})")
    ok &= say("the same seed gives the same result twice", c2e.run("Cpk", "S", 4) == c2e.run("Cpk", "S", 4))
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
