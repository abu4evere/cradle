"""C1 analysis (questions.md, C1-frozen). Written before any data.

  python studies/C1/analyse_c1.py OUT_DIR        (writes OUT_DIR/summary.json and OUT_DIR/results.md)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["N", "P", "W", "R", "S"]
MEM = ["P", "W", "R"]
SEEDS = list(range(1, 17))
DAY = "720"
IDX = np.random.default_rng(20261112).integers(0, len(SEEDS), (10_000, len(SEEDS)))


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
            f = out / f"{a}_seed_{s}.json"
            if f.exists():
                data[(a, s)] = json.loads(f.read_text(encoding="utf-8"))
            else:
                missing.append(f.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    homes_ok = all(len({data[(a, s)]["home"] for a in ARMS if (a, s) in data}) == 1 for s in SEEDS)
    if missing:
        print("missing:", missing)
        sys.exit(1)

    def col(a, k, day=DAY):
        return np.array([data[(a, s)]["results"][day][k] for s in SEEDS], dtype=float)

    S = {"validity": {"all_files": True, "checks_pass": checks_ok, "one_home_per_seed": homes_ok}, "arms": {}, "diff": {}}
    for a in ARMS:
        S["arms"][a] = {k: ci(col(a, k)) for k in ("ant_clean", "ant_noisy", "turn_clean", "turn_noisy")}
        S["arms"][a]["curve_ant_clean"] = {d: round(float(col(a, "ant_clean", d).mean()), 4)
                                           for d in data[(a, 1)]["results"]}
    chance_ant = float(np.mean([data[("N", s)]["results"][DAY]["chance_ant_clean"] for s in SEEDS]))
    chance_turn = float(np.mean([data[("N", s)]["results"][DAY]["chance_turn_clean"] for s in SEEDS]))
    S["chance"] = {"ant": round(chance_ant, 4), "turn": round(chance_turn, 4)}

    def d(a, b, k):
        return ci(col(a, k) - col(b, k))
    keeps = {}
    for m in MEM:
        above = (S["arms"][m]["ant_clean"]["lo"] > chance_ant and S["arms"][m]["turn_clean"]["lo"] > chance_turn)
        vsN = d(m, "N", "ant_clean")
        S["diff"][f"{m}-N ant_clean"] = vsN
        S["diff"][f"{m}-N turn_clean"] = d(m, "N", "turn_clean")
        keeps[m] = above and vsN["lo"] > 0
    rs = d("R", "S", "ant_clean")
    S["diff"]["R-S ant_clean"] = rs
    for a, b in (("R", "P"), ("W", "P"), ("R", "W")):
        S["diff"][f"{a}-{b} ant_clean"] = d(a, b, "ant_clean")
    keeps_up = any(keeps.values()) and rs["lo"] > 0
    not_enough = any(S["diff"][f"{m}-N ant_clean"]["lo"] > 0 and S["diff"][f"{m}-N turn_clean"]["lo"] <= 0 for m in MEM)
    reading = ("it keeps up" if keeps_up else "memory is not enough" if not_enough else "no improvement shown")
    n_ceiling = S["arms"]["N"]["ant_clean"]["mean"] >= 0.90
    S["reading"] = reading
    S["keeps_by_arm"] = keeps
    S["uninformative_ceiling"] = n_ceiling
    S["valid"] = checks_ok and homes_ok
    (out / "summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
    fmt = lambda c: f"{c['mean']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}] (n={c['n']})"
    L = ["# C1 results (day 720; 95% bootstrap intervals over 16 children)", "",
         f"**Valid:** {S['valid']} (all files; code checks {checks_ok}; one home per seed {homes_ok})", "",
         f"**Reading:** {reading}  (memory arms keeping up: {keeps}; R - S on anticipation {fmt(rs)})", "",
         f"**Ceiling rule:** N's clean anticipation {S['arms']['N']['ant_clean']['mean']:.3f}; uninformative (>= 0.90): {n_ceiling}", "",
         f"**Chance (clean steps):** anticipation {chance_ant:.3f}; taking its turn {chance_turn:.3f}", "",
         "| arm | anticipation, clean | anticipation, noisy | turn, clean | turn, noisy |", "|---|---|---|---|---|"]
    for a in ARMS:
        r = S["arms"][a]
        L.append(f"| {a} | {fmt(r['ant_clean'])} | {fmt(r['ant_noisy'])} | {fmt(r['turn_clean'])} | {fmt(r['turn_noisy'])} |")
    L += ["", "**Paired differences:**", ""] + [f"- {k}: {fmt(v)}" for k, v in S["diff"].items()]
    L += ["", "**Clean anticipation by test day (mean of 16):**", ""]
    for a in ARMS:
        L.append(f"- {a}: " + ", ".join(f"day {dd}: {v:.3f}" for dd, v in S["arms"][a]["curve_ant_clean"].items()))
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
