"""C2-P: whom to copy when mistakes hurt (questions.md, C2P-frozen). C2-K3's code (imported, unchanged) with three
conditions in learning: G (C2-K3's), GP (a wrong lid's reward is -p), GS (a wrong lid breaks the box: that kind's
remaining tries that day are lost); and the arm Ch (copy everyone at w = 0.5). Tests are C2-K3's (no pain, no broken
boxes).

  python studies/C2P/c2p.py one ARM COND SEED OUTDIR
  python studies/C2P/c2p.py pilot OUTDIR        (the pain level: Cb, seeds 1001-1024, G and GP at p = 1.0, 0.5, 0.25)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "C2K3"))
import c2k3 as K  # noqa: E402

ARMS = ("T", "I", "Cb", "Ch", "Ctk", "Cyk", "Cok")
CONDS = ("G", "GP", "GS")
# random-stream indices: C2-K3's for its arms and for G, so that G reproduces C2-K3's G exactly
ARM_INDEX = {"T": 0, "I": 1, "Cb": 2, "Ctk": 3, "Cyk": 4, "Cok": 5, "Ch": 7}
COND_INDEX = {"G": 0, "GP": 2, "GS": 3}
PAIN = {"p": None}
PAIN_LIST = (1.0, 0.5, 0.25)
PILOT_SEEDS = range(1001, 1025)


def try_box(net, look, pairs, prefix, rng, cond):
    """C2-K3's learning try (G rules), with -p as the reward of a wrong lid in GP. Returns (reached, opened, pain)."""
    xs, hs, h = K.run_prefix(net, prefix)
    targets, opened, reached, pain = {}, 0, 0, 0.0
    for j in range(K.LIDS):
        reached += 1
        x1 = K.x_try(look, j, None, 0)
        h, z1 = net.step(x1, h)
        xs.append(x1)
        hs.append(h)
        a1 = int(rng.choice(K.ACTS, p=K.softmax(z1)))
        t1 = len(xs) - 1
        x2 = K.x_try(look, j, a1, 1)
        h, z2 = net.step(x2, h)
        xs.append(x2)
        hs.append(h)
        a2 = int(rng.choice(K.ACTS, p=K.softmax(z2)))
        t2 = len(xs) - 1
        ok = (a1, a2) == pairs[j]
        r = (1.0 / K.LIDS) if ok else (-PAIN["p"] if cond == "GP" else 0.0)
        if not ok and cond == "GP":
            pain += PAIN["p"]
        adv = r - net.base
        net.base += K.BASE_RATE * (r - net.base)          # the running baseline tracks the reward, pain included
        targets[t1] = (a1, adv)
        targets[t2] = (a2, adv)
        if ok:
            opened += 1
        else:
            break                                          # G, GP and GS all end the try at a wrong lid
    if targets:
        net.apply(net.grads(xs, hs, targets), K.LR)
    return reached, opened, pain


def run(arm, cond, seed, out=None):
    home = K.Home(seed)
    net = K.Net(seed)
    rng = np.random.default_rng([seed, 3, ARM_INDEX[arm], COND_INDEX[cond]])
    t = [[K.TRUST0] * K.KINDS, [K.TRUST0] * K.KINDS]
    tries, tests, wsum = [], {}, 0.0
    w_expert, w_other = [], []
    for d in range(1, K.DAYS + 1):
        broken = set()
        for k, look, who, u, hidden, coin_y, coin_r in home.day(d):
            if cond == "GS" and k in broken:
                tries.append({"d": d, "k": k, "lost": True})
                continue
            demo, w, prefix = None, 0.0, []
            if d <= K.DEMO_DAYS and arm != "T":
                demo = K.demonstration(home, k, who, u, hidden)
                p = demo["who"]
                if arm == "Cb":
                    w = 1.0
                elif arm == "Ch":
                    w = 0.5
                elif arm == "Ctk":
                    w = K.wnorm(t[K.ANN][k], t[K.BEN][k], t[p][k])
                elif arm == "Cyk":
                    w = K.wnorm(t[K.ANN][k], t[K.BEN][k], t[coin_y][k])
                elif arm == "Cok":
                    w = 1.0 if p == K.expert_of(k) else 0.0
                if demo["seen"]:
                    t[p][k] += K.TRUST_RATE * (demo["opened"] / K.LIDS - t[p][k])
                prefix = K.show_steps(look, demo)
                if arm != "I":
                    K.copy_step(net, look, demo, prefix, w)
                    if w > 0:
                        wsum += w
                    (w_expert if p == K.expert_of(k) else w_other).append(w)
            reached, opened, pain = try_box(net, look, home.pairs[k], prefix, rng, cond)
            if cond == "GS" and opened < K.LIDS:
                broken.add(k)
            tries.append({"d": d, "k": k, "who": None if demo is None else demo["who"], "w": w, "reached": reached,
                          "opened": opened, "pain": pain})
        if d in K.TEST_DAYS:
            tests[d] = K.test(home, net, seed, d)
    res = {"arm": arm, "cond": cond, "seed": seed, "p": PAIN["p"], "level_lids": K.LIDS, "tests": tests,
           "tries": tries, "trust": t, "copy_weight_sum": wsum,
           "w_expert_mean": float(np.mean(w_expert)) if w_expert else None,
           "w_other_mean": float(np.mean(w_other)) if w_other else None}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_{cond}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


def setup():
    K.set_level(json.loads((HERE.parent / "C2K3" / "difficulty.json").read_text())["level"])
    pj = HERE / "pain.json"
    if pj.exists():
        PAIN["p"] = json.loads(pj.read_text())["p"]


def pilot(outdir):
    """The pain level (questions.md): the first p, strongest first, with Cb's GP day-30 success >= half its G success."""
    setup()
    g = [run("Cb", "G", s)["tests"][30]["success"] for s in PILOT_SEEDS]
    rows, chosen = [], None
    for p in PAIN_LIST:
        PAIN["p"] = p
        gp = [run("Cb", "GP", s)["tests"][30]["success"] for s in PILOT_SEEDS]
        rows.append({"p": p, "Cb_G": float(np.mean(g)), "Cb_GP": float(np.mean(gp)),
                     "qualifies": float(np.mean(gp)) >= 0.5 * float(np.mean(g))})
        print(rows[-1], flush=True)
        if rows[-1]["qualifies"]:
            chosen = p
            break
    (HERE / "pain.json").write_text(json.dumps({"p": chosen, "rows": rows, "seeds": list(PILOT_SEEDS)}, indent=1))
    print("chosen", chosen)


if __name__ == "__main__":
    if sys.argv[1] == "one":
        setup()
        r = run(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
        print(sys.argv[2], sys.argv[3], sys.argv[4], {d: round(v["success"], 2) for d, v in r["tests"].items()}, flush=True)
    elif sys.argv[1] == "pilot":
        pilot(sys.argv[2] if len(sys.argv) > 2 else None)
