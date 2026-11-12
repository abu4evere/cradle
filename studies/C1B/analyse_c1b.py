"""C1-B analysis (questions.md, C1B-frozen). Written before any data.

  python studies/C1B/analyse_c1b.py OUT_DIR        (writes OUT_DIR/results.md and summary.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["A", "Ym", "Yo", "Y", "Yi"]
NAME = {"Ym": "Y-"}
SEEDS = list(range(1, 25))
EARLY = ["7", "14", "30", "60", "90"]
IDX = np.random.default_rng(20261117).integers(0, len(SEEDS), (10_000, len(SEEDS)))


def ci(x):
    x = np.asarray(x, float)
    b = x[IDX].mean(1)
    return float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def f(c):
    return f"{c[0]:+.4f} [{c[1]:+.4f}, {c[2]:+.4f}]"


def main():
    out = Path(sys.argv[1])
    data, missing = {}, []
    for a in ARMS:
        for s in SEEDS:
            p = out / f"{a}_seed_{s}.json"
            if p.exists():
                data[(a, s)] = json.loads(p.read_text(encoding="utf-8"))
            else:
                missing.append(p.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    homes_ok = all(len({data[(a, s)]["home"] for a in ARMS if (a, s) in data}) == 1 for s in SEEDS)
    valid = checks_ok and not missing and homes_ok
    L = ["# C1-B: a sibling (results)", "", "Frozen as `C1B-frozen`. c1b.py, analyse_c1b.py (written before data).", "",
         "## Validity", "", f"- Code checks (All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(SEEDS)} runs present: **{'yes' if not missing else 'NO'}**",
         f"- The same home per seed in every arm: **{'yes' if homes_ok else 'NO'}**", "",
         f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return

    def y(a, day, m="turn_clean"):
        return np.array([data[(a, s)]["younger"][day][m] for s in SEEDS], float)

    def early(a):
        return np.mean([y(a, d) for d in EARLY], axis=0)
    im, fb = ci(early("Yi") - early("Y")), ci(early("Y") - early("Yo"))
    L += ["## Readings (frozen)", "",
          f"- **Imitation helps** (Yi - Y, early learning = mean clean turn accuracy at days 7-90): {f(im)} -> "
          f"**{'yes' if im[1] > 0 else 'no'}**",
          f"- **Hearing the sibling's feedback helps** (Y - Yo): {f(fb)} -> **{'yes' if fb[1] > 0 else 'no'}**",
          f"- Sequence continuity (Yo - Y-): {f(ci(early('Yo') - early('Ym')))}",
          f"- All of watching (Y - Y-): {f(ci(early('Y') - early('Ym')))}",
          f"- Imitation against no sibling (Yi - A): {f(ci(early('Yi') - early('A')))}", ""]
    summary = {"imitation": im, "feedback": fb}
    L += ["## The younger's clean turn accuracy by day (mean over 24 children)", "",
          "| arm | " + " | ".join(str(d) for d in ["7", "14", "30", "60", "90", "180", "360", "720"]) + " | early mean |",
          "|---|" + "---|" * 9]
    for a in ARMS:
        L.append(f"| {NAME.get(a, a)} | " + " | ".join(f"{y(a, d).mean():.3f}" for d in
                                                     ["7", "14", "30", "60", "90", "180", "360", "720"])
                 + f" | {early(a).mean():.3f} |")
    L += ["", "## Day 720 against A (paired)", ""]
    for a in ARMS[1:]:
        L.append(f"- {NAME.get(a, a)} - A, clean turn: {f(ci(y(a, '720') - y('A', '720')))}; noisy turn: "
                 f"{f(ci(y(a, '720', 'turn_noisy') - y('A', '720', 'turn_noisy')))}; clean anticipation: "
                 f"{f(ci(y(a, '720', 'ant_clean') - y('A', '720', 'ant_clean')))}")
    L += ["", "## Turn-matched (descriptive): the arm at day t against A at day t/2 (about the same own turns)", "",
          "| t | " + " | ".join(NAME.get(a, a) for a in ARMS[1:]) + " | A at t/2 |", "|---|" + "---|" * 5]
    for t, half in (("14", "7"), ("60", "30"), ("180", "90"), ("720", "360")):
        L.append(f"| {t} | " + " | ".join(f"{y(a, t).mean():.3f}" for a in ARMS[1:]) + f" | {y('A', half).mean():.3f} |")
    L += ["", "## The older sibling's clean turn accuracy (at the younger's days; day 0 = just before the birth)", "",
          "| arm | 0 | 7 | 14 | 30 | 90 | 360 | 720 |", "|---|---|---|---|---|---|---|---|"]
    for a in ARMS[1:]:
        L.append(f"| {NAME.get(a, a)} | " + " | ".join(
            f"{np.mean([data[(a, s)]['older'][d]['turn_clean'] for s in SEEDS]):.3f}"
            for d in ["0", "7", "14", "30", "90", "360", "720"]) + " |")
    L += ["", "## Turns per younger child (mean)", "", "| arm | own | sibling's | seen | imitated |",
          "|---|---|---|---|---|"]
    for a in ARMS:
        t = {k: np.mean([data[(a, s)]["turns"][k] for s in SEEDS]) for k in ("own", "sib", "seen", "imitated")}
        L.append(f"| {NAME.get(a, a)} | {t['own']:.0f} | {t['sib']:.0f} | {t['seen']:.0f} | {t['imitated']:.0f} |")
    L += ["", "Rules (frozen): 'imitation helps' if Yi - Y has a lower bound above 0; 'hearing the sibling's feedback "
          "helps' if Y - Yo has a lower bound above 0 (early learning, paired by seed, 10,000 draws, seed 20261117).", ""]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
