"""C1-B: a sibling (studies/C1B/questions.md, frozen as C1B-frozen).

C1's home and C1's W child (window of the last 4 things used). The older lives 360 days alone (exactly C1's W child),
then the younger is born and both live 720 more days. Each child's turn goes to one child by a fair coin
([seed, 40, day]). Arms differ only in what the younger receives from the sibling's turns:
  A   no sibling        Y-  nothing (out of sight)       Yo  sees the thing used, hears nothing
  Y   sees it and hears the parent's answer              Yi  Y + imitation of praised acts at half the learning rate

  python studies/C1B/c1b.py one ARM SEED OUT_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "C1"))
import c1  # noqa: E402

ARMS = ("A", "Ym", "Yo", "Y", "Yi")              # Ym is Y- (file-safe)
OLDER_DAYS = 360
DAYS = 720
TEST_DAYS = [7, 14, 30, 60, 90, 180, 360, 720]
IMIT_RATE = 0.5                                  # imitation at half the learning rate


def softmax(v):
    return c1.softmax(v)


def own_turn(home, child, st, heard, rng):
    """A step that is this child's turn: exactly C1's live_day body for a child turn. Returns (heard_next, right)."""
    ids = child.ids(heard)
    x, hp, h = child.step_state(ids, True)
    s = child.scores(st["looks"], h)
    logits = np.append(s, child.w0)
    act = int(rng.choice(len(logits), p=softmax(logits)))
    right = act == st["ni"]
    r = 1.0 if right else 0.0
    adv = r - child.base
    child.base += c1.BASE_RATE * (r - child.base)
    c1.apply(child, c1.grads(child, st["looks"], x, ids, hp, h, st["ni"], act, adv))
    child.commit(x, ids, hp, h, st["looks"][st["ni"]])
    return c1.heard_after(home, st, right, None), right


def watch(child, st, heard):
    """A step that is not this child's turn (the parent's, or the sibling's when seen): C1's body for a non-turn step."""
    ids = child.ids(heard)
    x, hp, h = child.step_state(ids, False)
    c1.apply(child, c1.grads(child, st["looks"], x, ids, hp, h, st["ni"], None, 0.0))
    child.commit(x, ids, hp, h, st["looks"][st["ni"]])


def imitate(child, st, heard):
    """Yi: one act-learning step toward the thing the praised sibling handed, as if it had handed it with reward 1 (C1's
    REINFORCE, the same baseline, not updated), at half the learning rate. Only the act part of the gradient."""
    ids = child.ids(heard)
    x, hp, h = child.step_state(ids, True)
    adv = 1.0 - child.base
    g_both = c1.grads(child, st["looks"], x, ids, hp, h, st["ni"], st["ni"], adv)
    g_pred = c1.grads(child, st["looks"], x, ids, hp, h, st["ni"], None, 0.0)
    g = {"M": g_both["M"] - g_pred["M"], "Wx": g_both["Wx"] - g_pred["Wx"], "b": g_both["b"] - g_pred["b"],
         "w0": g_both["w0"] - g_pred["w0"],
         "E": {i: g_both["E"].get(i, 0.0) - g_pred["E"].get(i, 0.0) for i in set(g_both["E"]) | set(g_pred["E"])}}
    keep = c1.LR
    c1.LR = keep * IMIT_RATE
    try:
        c1.apply(child, g)
    finally:
        c1.LR = keep


def joint_day(home, older, younger, steps, rng_o, rng_y, arm, coins, count):
    """One day with both children (older may be None: arm A). Parent turns: both watch (C1). A child's turn: the coin
    picks the actor; the other child receives what the arm allows (the older always sees and hears, as in Y)."""
    for ch in (older, younger):
        if ch is not None:
            ch.reset()
    hy, ho = "", ""
    for k, st in enumerate(steps):
        if not st["child"]:
            for ch, which in ((older, "o"), (younger, "y")):
                if ch is None:
                    continue
                watch(ch, st, ho if which == "o" else hy)
            said = c1.heard_after(home, st, False, None)
            ho, hy = said, said
            continue
        younger_acts = older is None or coins[k] < 0.5
        if younger_acts:
            hy_next, right = own_turn(home, younger, st, hy, rng_y)
            count["own"] += 1
            if older is not None:
                watch(older, st, ho)
                ho = hy_next
            hy = hy_next
            continue
        ho_next, right = own_turn(home, older, st, ho, rng_o)
        ho = ho_next
        count["sib"] += 1
        if arm == "Ym":
            continue                                   # out of sight: the younger's step and hearing are untouched
        watch(younger, st, hy)
        count["seen"] += 1
        if arm in ("Y", "Yi"):
            if arm == "Yi" and right:
                imitate(younger, st, hy)
                count["imitated"] += 1
            hy = ho_next                                # hears the parent's answer to the sibling
        else:
            hy = ""                                     # Yo: hears nothing about it


def run(arm, seed, out=None):
    corpus = c1.load_corpus()
    home = c1.Home(seed, corpus)
    older = None
    rng_o = np.random.default_rng([seed, 3, 2])        # C1's W arm stream
    if arm != "A":
        older = c1.Child("W", home.vocab, seed)
        for day in range(OLDER_DAYS):                  # the older's first 360 days: C1's W child exactly
            c1.live_day(home, older, home.day([seed, 12, day]), True, rng_o)
    younger = c1.Child("W", home.vocab, 1000 + seed)
    rng_y = np.random.default_rng([1000 + seed, 3, 2])
    count = {"own": 0, "sib": 0, "seen": 0, "imitated": 0}
    young, old = {}, {}
    if older is not None:
        old[0] = c1.test(home, older, seed, OLDER_DAYS, False)
    for d in range(DAYS):
        day = OLDER_DAYS + d                           # the home's day (the older's age in days)
        steps = home.day([seed, 12, day])
        coins = np.random.default_rng([seed, 40, day]).random(len(steps))
        joint_day(home, older, younger, steps, rng_o, rng_y, arm, coins, count)
        if d + 1 in TEST_DAYS:
            young[d + 1] = c1.test(home, younger, 1000 + seed, d + 1, False)
            if older is not None:
                old[d + 1] = c1.test(home, older, seed, OLDER_DAYS + d + 1, False)
    res = {"arm": arm, "seed": seed, "home": home.fingerprint(), "younger": young, "older": old, "turns": count}
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{arm}_seed_{seed}.json").write_text(json.dumps(res), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "one":
        r = run(sys.argv[2], int(sys.argv[3]), sys.argv[4])
        last = r["younger"][max(r["younger"])]
        print(sys.argv[2], sys.argv[3], round(last["turn_clean"], 3), r["turns"], flush=True)
