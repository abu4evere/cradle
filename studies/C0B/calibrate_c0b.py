"""C0-B's difficulty check (questions.md, "The difficulty check", frozen before the study). Arms A, P, E; seeds 101-104
(never used in the study); each level L1-L4 up to day 90 only. The hardest level meeting all three criteria is chosen:
  P's mean request accuracy at day 90 >= 0.60; A's at day 30 within [0.35, 0.90]; E's at day 90 within [0.17, 0.33].
If none meets them, L4. Also the feasibility of the looks: a nearest-centroid classifier (30 classes) given the
daily instances' true labels classifies the kept-back instances.

  python studies/C0B/calibrate_c0b.py           (writes calibration.json and calibration.md)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c0b  # noqa: E402

SEEDS = (101, 102, 103, 104)
ARMS = ("A", "P", "E")
c0b.DAYS = 90                                    # day 90 at most: nothing later is computed
c0b.TEST_DAYS = [d for d in c0b.TEST_DAYS if d <= 90]


def feasibility(level, corpus):
    accs = []
    for seed in SEEDS:
        sc = c0b.Scenes(seed, corpus, 1)
        cent = np.array([(sc.centre[c] + sc.offset[c, :3]).mean(0) for c in range(c0b.NC)])
        rng = np.random.default_rng([seed, 77])
        hit = n = 0
        for c in range(c0b.NC):
            for i in (3, 4):
                for _ in range(10):
                    x = sc.centre[c] + sc.offset[c, i] + rng.normal(0, 0.2, c0b.LOOK)
                    hit += int(np.argmin(((cent - x) ** 2).sum(1)) == c)
                    n += 1
        accs.append(hit / n)
    return float(np.mean(accs))


def main():
    rows, chosen = [], None
    for level in ("L1", "L2", "L3", "L4"):
        c0b.LEVEL = level
        c0b.MOMENTS = c0b.LEVELS[level][0]
        corpus = c0b.load_corpus()
        acc = {a: {} for a in ARMS}
        for a in ARMS:
            for s in SEEDS:
                r = c0b.run(a, s, None)["results"]
                acc[a][s] = {d: r[d]["request"] for d in r}
        p90 = float(np.mean([acc["P"][s][90] for s in SEEDS]))
        a30 = float(np.mean([acc["A"][s][30] for s in SEEDS]))
        e90 = float(np.mean([acc["E"][s][90] for s in SEEDS]))
        ok = p90 >= 0.60 and 0.35 <= a30 <= 0.90 and 0.17 <= e90 <= 0.33
        feas = feasibility(level, corpus)
        rows.append({"level": level, "moments": c0b.LEVELS[level][0], "sd": c0b.LEVELS[level][1], "P_day90": p90,
                     "A_day30": a30, "E_day90": e90, "meets": ok, "nearest_centroid": feas, "per_seed": acc})
        if ok and chosen is None:
            chosen = level
    reason = "the hardest level that meets all three criteria" if chosen else "none meets them: L4, as the plan says"
    chosen = chosen or "L4"
    out = {"chosen": chosen, "reason": reason, "levels": rows}
    (HERE / "calibration.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    L = ["# C0-B difficulty check (seeds 101-104; arms A, P, E; up to day 90)", "",
         "| level | moments a day | member sd | P request, day 90 | A request, day 30 | E request, day 90 | meets | nearest-centroid (looks alone) |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['level']} | {r['moments']} | {r['sd']} | {r['P_day90']:.3f} | {r['A_day30']:.3f} | {r['E_day90']:.3f} | "
                 f"{'yes' if r['meets'] else 'no'} | {r['nearest_centroid']:.3f} |")
    L += ["", f"**Chosen: {chosen}** ({reason}). Criteria (frozen): P at day 90 >= 0.60; A at day 30 within [0.35, 0.90]; "
          "E at day 90 within [0.17, 0.33].", ""]
    (HERE / "calibration.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
