"""C1.5 analysis (questions.md, C1_5-frozen, with correction 1). Written before any data.

  python studies/C1_5/analyse_c15.py OUT_DIR        (writes OUT_DIR/summary.json and OUT_DIR/results.md)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["B", "P", "K", "Q", "Q-"]
FILE = {a: a.replace("-", "m") for a in ARMS}
SEEDS = list(range(1, 25))
DAYS = ["30", "90", "180", "360", "720"]
DAY = "720"
MARGIN = 0.05
CHANCE_FIRST = 1 / 5
IDX = np.random.default_rng(20261111).integers(0, len(SEEDS), (10_000, len(SEEDS)))
MEASURES = ["held_test_first", "held_test_second", "held_test_both", "held_test_neg", "held_test_neg_x", "plain",
            "held_test_after_first", "held_life_first", "held_life_neg", "life_test_first", "life_test_neg"]


def ci(x):
    x = np.asarray(x, dtype=float)
    b = x[IDX].mean(1)
    return {"mean": round(float(x.mean()), 4), "lo": round(float(np.percentile(b, 2.5)), 4),
            "hi": round(float(np.percentile(b, 97.5)), 4), "n": len(x)}


def main():
    out = Path(sys.argv[1])
    data, missing = {}, []
    for a in ARMS:
        for s in SEEDS:
            f = out / f"{FILE[a]}_seed_{s}.json"
            if f.exists():
                data[(a, s)] = json.loads(f.read_text(encoding="utf-8"))
            else:
                missing.append(f.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    homes_ok = all(len({data[(a, s)]["home"] for a in ARMS if (a, s) in data}) == 1 for s in SEEDS)
    valid = checks_ok and not missing and homes_ok
    L = ["# C1.5: word order (results)", "",
         "Frozen as `C1_5-frozen` (with correction 1, before data). c15.py, analyse_c15.py (written before data).", "",
         "## Validity", "",
         f"- Code checks (checks.log, All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(SEEDS)} children present: **{'yes' if not missing else 'NO, missing ' + str(len(missing))}**",
         f"- The same home per seed in every arm: **{'yes' if homes_ok else 'NO'}**", "",
         f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    summary = {"valid": valid, "missing": missing}
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
        print("\n".join(L))
        return

    def v(a, m, day=DAY):
        return np.array([data[(a, s)]["results"][day][m] for s in SEEDS], dtype=float)

    def d(a, b, m):
        return ci(v(a, m) - v(b, m))

    def f(c):
        return f"{c['mean']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}]"

    plain_b = ci(v("B", "plain"))
    informative = plain_b["lo"] > CHANCE_FIRST
    qb, qq = d("Q", "B", "held_test_first"), d("Q", "Q-", "held_test_first")
    hears = qb["lo"] > 0 and qq["lo"] > 0
    pos = {}
    for a in ("P", "K"):
        ab, aq = d(a, "B", "held_test_first"), d(a, "Q", "held_test_first")
        pos[a] = {"vs_B": ab, "vs_Q": aq, "enough": ab["lo"] > 0 and aq["lo"] >= -MARGIN and aq["hi"] <= MARGIN}
    position_enough = any(p["enough"] for p in pos.values())
    nb, nq = d("Q", "B", "held_test_neg"), d("Q", "Q-", "held_test_neg")
    neg_learned = nb["lo"] > 0 and nq["lo"] > 0
    if not informative:
        reading = "not informative (B did not learn the names)"
    elif hears and position_enough:
        reading = "it hears order; position is enough"
    elif hears:
        reading = "it hears order"
    elif position_enough:
        reading = "position is enough"
    else:
        reading = "not learned"
    L += ["## Reading (frozen)", "", f"- **{reading}.**",
          f"- Guard: B's plain accuracy at day 720 {plain_b['mean']:.4f} [{plain_b['lo']:.4f}, {plain_b['hi']:.4f}] "
          f"against chance {CHANCE_FIRST:.2f}: informative **{'yes' if informative else 'no'}**.",
          f"- **Primary**, first-act order accuracy on held-out pairs (test frames): Q - B {f(qb)}; Q - Q- {f(qq)}; "
          f"hears order **{'yes' if hears else 'no'}**.",
          "- Position: " + "; ".join(f"{a} - B {f(p['vs_B'])}, {a} - Q {f(p['vs_Q'])} (within +-{MARGIN}: "
                                     f"{'yes' if p['enough'] else 'no'})" for a, p in pos.items()) + ".",
          f"- Negation (secondary): Q - B {f(nb)}; Q - Q- {f(nq)}; learned **{'yes' if neg_learned else 'no'}**.", "",
          "Rules (frozen): 'it hears order' if the lower bounds of Q - B and Q - Q- (first act, held-out pairs) are "
          "above 0; 'position is enough' if P or K beats B (lower bound above 0) and its difference from Q lies within "
          "+-0.05; 'not learned' otherwise; no reading if B's plain accuracy is not above chance. Chance: first act 1/5; "
          "among the two named things 1/2.", "",
          "Caution (GPT, council 5): passing shows order-sensitive behaviour, not compositional understanding.", ""]
    summary.update({"reading": reading, "informative": informative, "plain_B": plain_b, "Q_B": qb, "Q_Qm": qq,
                    "position": pos, "neg_Q_B": nb, "neg_Q_Qm": nq})
    L += ["## Day 720, every arm (mean [95%], 24 children)", "",
          "| measure | " + " | ".join(ARMS) + " |", "|---|" + "---|" * len(ARMS)]
    table = {}
    for m in MEASURES:
        row = []
        for a in ARMS:
            c = ci(v(a, m))
            table[(a, m)] = c
            row.append(f"{c['mean']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}]")
        L.append(f"| {m} | " + " | ".join(row) + " |")
    L += ["", "## First-act order accuracy over life (held-out pairs, test frames; mean over children)", "",
          "| arm | " + " | ".join(DAYS) + " |", "|---|" + "---|" * len(DAYS)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{v(a, 'held_test_first', dd).mean():.3f}" for dd in DAYS) + " |")
    L += ["", "## Plain accuracy over life (mean over children)", "",
          "| arm | " + " | ".join(DAYS) + " |", "|---|" + "---|" * len(DAYS)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{v(a, 'plain', dd).mean():.3f}" for dd in DAYS) + " |")
    summary["table"] = {f"{a}|{m}": c for (a, m), c in table.items()}
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
