"""C2-K2 code checks (C2-K's, at the chosen level, plus step-by-step teaching) (questions.md, "Validity"). Writes checks.log.

  python studies/C2K2/checks_c2k2.py   (needs difficulty.json)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import json  # noqa: E402
import c2k2 as c2k  # noqa: E402

LEVEL = json.loads((HERE / 'difficulty.json').read_text())['level']
c2k.set_level(LEVEL)

LINES = []


def say(name, ok, extra=""):
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} {extra}".rstrip())
    print(LINES[-1], flush=True)
    return ok


def main():
    ok = True
    homes = [c2k.Home(s) for s in range(1, 49)]
    ok &= say("each box's 3 lid pairs differ", all(len(set(h.pairs[k])) == c2k.LIDS for h in homes for k in range(6)))
    ok &= say("habits are never the right pair",
              all(h.habits[p][k][j] != h.pairs[k][j] for h in homes for p in (0, 1) for k in range(6) for j in range(c2k.LIDS)))
    exp_r, oth_r, stop_ok = [], [], True
    for h in homes:
        for d in range(1, 31):
            for k, look, who, u, hidden, cy, cr in h.day(d):
                dm = c2k.demonstration(h, k, who, u, hidden)
                rate_list = exp_r if who == c2k.expert_of(k) else oth_r
                for j, pr in enumerate(dm["shown"]):
                    rate_list.append(pr == h.pairs[k][j])
                # stops at the first wrong lid: all but the last shown are right; the last is right only if 3 shown
                right = [pr == h.pairs[k][j] for j, pr in enumerate(dm["shown"])]
                stop_ok &= all(right[:-1]) and dm["opened"] == sum(right)
                stop_ok &= (len(right) == c2k.LIDS) or (not right[-1])
    ok &= say("per-lid rates: expert about 0.85, non-expert about 0.25", abs(np.mean(exp_r) - 0.85) < 0.02 and
              abs(np.mean(oth_r) - 0.25) < 0.03, f"({np.mean(exp_r):.3f}, {np.mean(oth_r):.3f})")
    ok &= say("demonstrations stop at the first wrong lid", stop_ok)
    # spy on copies
    log = []
    orig = c2k.copy_lid

    def spy(child, look, demo, j, w):
        log.append((spy.key, j, w, demo))
        return orig(child, look, demo, j, w)
    c2k.copy_lid = spy
    runs = {}
    try:
        for a in c2k.ARMS:
            for c in c2k.CONDS:
                spy.key = (a, c)
                runs[(a, c)] = c2k.run(a, c, 3)
    finally:
        c2k.copy_lid = orig
    g_ok = True
    for a in ("Cb", "Ctk", "Cyk", "Cok", "Cr"):
        tr = [x for x in runs[(a, "G")]["tries"] if x["d"] <= 30]
        # in G: a try stops at the first wrong lid; reached = opened + 1 unless all 3 opened
        g_ok &= all(x["reached"] == min(c2k.LIDS, x["opened"] + 1) for x in runs[(a, "G")]["tries"])
        n_reach = sum(min(x["reached"], len(x["shown"])) for x in tr if x["w"] > 0)
        n_logged = sum(1 for key, j, w, dm in log if key == (a, "G") and w > 0 and j < len(dm["shown"]))
        g_ok &= n_reach == n_logged
    ok &= say("G: tries stop at the first wrong lid; each lid copied only when reached (step by step)", g_ok)
    u_ok = all(x["reached"] == c2k.LIDS for a in c2k.ARMS for x in runs[(a, "U")]["tries"])
    ok &= say("U: every lid is tried", u_ok)
    ok &= say("no copies in T and I", all(key[0] not in ("T", "I") for key, *_ in log))
    ch = c2k.Child(1)
    hid_ok = True
    for key, j, w, dm in log:
        if not dm["seen"]:
            xv = ch.x(np.zeros(c2k.LOOK), dm, j, None, 0)
            hid_ok &= xv[c2k.LOOK + 2 + 8] == 0.0 and xv[c2k.LOOK + 2 + 9] == 0.0
    ok &= say("hidden results carry no result bits", hid_ok)
    # weights: Ctk from an independent replay; Cyk coin; Cok expert; Cr coin
    h3 = c2k.Home(3)
    t = [[0.5] * 6, [0.5] * 6]
    w_ok, i = True, 0
    for d in range(1, 31):
        for k, look, who, u, hidden, cy, cr in h3.day(d):
            dm = c2k.demonstration(h3, k, who, u, hidden)
            p = dm["who"]
            for c in c2k.CONDS:
                w_ok &= abs(runs[("Ctk", c)]["tries"][i]["w"] - c2k.wnorm(t[0][k], t[1][k], t[p][k])) < 1e-12
                w_ok &= abs(runs[("Cyk", c)]["tries"][i]["w"] - c2k.wnorm(t[0][k], t[1][k], t[cy][k])) < 1e-12
                w_ok &= runs[("Cok", c)]["tries"][i]["w"] == (1.0 if p == c2k.expert_of(k) else 0.0)
                w_ok &= runs[("Cr", c)]["tries"][i]["w"] == float(cr)
                w_ok &= runs[("Cb", c)]["tries"][i]["w"] == 1.0
            if dm["seen"]:
                t[p][k] += 0.3 * (dm["opened"] / c2k.LIDS - t[p][k])
            i += 1
    ok &= say("weights per arm as defined (Ctk replayed independently)", w_ok)
    rng = np.random.default_rng(1)
    ch = c2k.Child(9)
    for k in ch.p:
        ch.p[k] = ch.p[k] * 5
    x = rng.normal(0, 1, c2k.N_IN)
    a, scale = 2, 0.7
    g = ch.grad(x, a, scale)

    def loss():
        _, z = ch.logits(x)
        return -scale * np.log(c2k.softmax(z)[a])
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
    ok &= say("the same seed gives the same result twice", c2k.run("Ctk", "G", 4) == c2k.run("Ctk", "G", 4))
    ok &= say("the level is the frozen rule's choice", LEVEL in c2k.LEVELS, f"({LEVEL})")
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
