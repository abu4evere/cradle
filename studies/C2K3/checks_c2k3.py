"""C2-K3 code checks (C2-K's adapted to the memory brain, plus WS's) (questions.md, "Validity"). Writes checks.log.

  python studies/C2K3/checks_c2k3.py   (needs difficulty.json)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import json  # noqa: E402
import c2k3 as c2k  # noqa: E402

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
    ok &= say("each box's lid pairs differ", all(len(set(h.pairs[k])) == c2k.LIDS for h in homes for k in range(6)))
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
    # spy on what the network sees, and on copies
    seen_x, copy_log = {}, []
    orig_step, orig_copy = c2k.Net.step, c2k.copy_step

    def spy_step(self, x, hprev):
        seen_x.setdefault(spy_step.key, []).append(x.copy())
        return orig_step(self, x, hprev)

    def spy_copy(net, look, demo, prefix, w):
        copy_log.append((spy_step.key, w, demo))
        return orig_copy(net, look, demo, prefix, w)
    c2k.Net.step, c2k.copy_step = spy_step, spy_copy
    runs = {}
    try:
        for a in c2k.ARMS:
            for c in c2k.CONDS:
                spy_step.key = (a, c)
                runs[(a, c)] = c2k.run(a, c, 3)
    finally:
        c2k.Net.step, c2k.copy_step = orig_step, orig_copy
    g_ok = all(x["reached"] == min(c2k.LIDS, x["opened"] + 1) for a in c2k.ARMS for x in runs[(a, "G")]["tries"])
    ok &= say("G: a try stops at the first wrong lid", g_ok)
    u_ok = all(x["reached"] == c2k.LIDS for a in c2k.ARMS for x in runs[(a, "U")]["tries"])
    ok &= say("U: every lid is tried", u_ok)
    ok &= say("no copies in T and I", all(key[0] not in ("T", "I") or w <= 0 for key, w, dm in copy_log)
              and all(key[0] != "I" for key, w, dm in copy_log))
    # the showing reaches the network only as flagged showing steps carrying who; never inside a try step
    S0 = c2k.SHOW0
    tag_ok, try_ok, n_show = True, True, 0
    for key, xs in seen_x.items():
        for x in xs:
            if x[S0 + c2k.ACTS] == 1.0:
                n_show += 1
                tag_ok &= x[S0 + c2k.ACTS + 1: S0 + c2k.ACTS + 3].sum() == 1.0
            else:
                try_ok &= not np.any(x[S0:])
    ok &= say("showing steps carry who showed it; try steps carry no showing", tag_ok and try_ok and n_show > 0)
    hid_ok = True
    for key, xs in seen_x.items():
        for x in xs:
            if x[S0 + c2k.ACTS] == 1.0 and x[S0 + c2k.ACTS + 3] == 0.0:
                hid_ok &= x[S0 + c2k.ACTS + 4] == 0.0
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
    net = c2k.Net(9)
    for k in net.p:
        net.p[k] = net.p[k] * 4
    xs = [rng.normal(0, 1, c2k.N_IN) for _ in range(7)]
    targets = {2: (1, 0.7), 4: (3, -0.4), 6: (0, 1.0)}

    def loss():
        h, total = np.zeros(c2k.HID), 0.0
        for tt, x in enumerate(xs):
            h, z = net.step(x, h)
            if tt in targets:
                a, sc = targets[tt]
                total += -sc * np.log(c2k.softmax(z)[a])
        return total
    hs, h = [], np.zeros(c2k.HID)
    for x in xs:
        h, _ = net.step(x, h)
        hs.append(h)
    g = net.grads(xs, hs, targets)
    worst = 0.0
    for name, P in net.p.items():
        f, gf = P.reshape(-1), g[name].reshape(-1)
        for j in rng.choice(f.size, min(25, f.size), replace=False):
            o = f[j]
            f[j] = o + 1e-6
            lp = loss()
            f[j] = o - 1e-6
            lm = loss()
            f[j] = o
            num = (lp - lm) / 2e-6
            worst = max(worst, abs(num - gf[j]) / max(1e-3, abs(num) + abs(gf[j])))
    ok &= say("gradients through time equal finite differences", worst < 1e-5, f"(worst rel. {worst:.1e})")
    ok &= say("the same seed gives the same result twice", c2k.run("Ctk", "G", 4) == c2k.run("Ctk", "G", 4))
    ok &= say("the level is the frozen rule's choice", LEVEL in c2k.LEVELS, f"({LEVEL})")
    LINES.append(f"All: {'PASS' if ok else 'FAIL'}")
    (HERE / "checks.log").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    print(LINES[-1])


if __name__ == "__main__":
    main()
