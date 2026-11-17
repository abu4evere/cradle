"""C2-P checks, before any data (questions.md, Validity). Prints All: PASS or the failures."""
import inspect
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2p  # noqa: E402
from c2p import K  # noqa: E402

fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name, flush=True)
    if not ok:
        fails.append(name)


c2p.setup()
c2p.PAIN["p"] = c2p.PAIN["p"] or 0.5          # the checks run before the pilot too

# 1. G reproduces C2-K3's G exactly (same seed and arm)
ok = True
for arm in ("Cb", "Ctk", "T"):
    a = c2p.run(arm, "G", 3)
    b = K.run(arm, "G", 3)
    ok &= a["tests"] == b["tests"] and a["trust"] == b["trust"] and \
        [(x["reached"], x["opened"]) for x in a["tries"]] == [(x["reached"], x["opened"]) for x in b["tries"]]
check("G reproduces C2-K3's G exactly (Cb, Ctk, T; seed 3)", ok)

# 2. GP: the pain is p on every wrong lid in learning, and nothing else; G and GS have none
gp = c2p.run("Cb", "GP", 4)
wrong = sum(1 for x in gp["tries"] if x["opened"] < x["reached"])
total = sum(x["pain"] for x in gp["tries"])
check(f"GP: pain = p x wrong lids ({wrong} wrong lids, pain {total:.2f}, p {c2p.PAIN['p']})",
      abs(total - c2p.PAIN["p"] * wrong) < 1e-9 and wrong > 0)
g = c2p.run("Cb", "G", 4)
gs = c2p.run("Cb", "GS", 4)
check("G and GS feel no pain", sum(x.get("pain", 0) for x in g["tries"] + gs["tries"]) == 0)

# 3. GS: after a failed try of a kind, that kind's remaining tries that day are lost, and only those
ok = True
by_day = {}
for x in gs["tries"]:
    by_day.setdefault(x["d"], []).append(x)
for d, xs in by_day.items():
    broken = set()
    for x in xs:
        if x["k"] in broken:
            ok &= bool(x.get("lost"))
        else:
            ok &= not x.get("lost")
            if x["opened"] < K.LIDS:
                broken.add(x["k"])
lost = sum(1 for x in gs["tries"] if x.get("lost"))
check(f"GS: exactly a broken kind's later tries that day are lost ({lost} lost)", ok and lost > 0)

# 4. tests: C2-K3's (learning off, G rules), so no pain and no broken boxes
src = inspect.getsource(K.test)
check("tests are C2-K3's: learning off, G rules (no pain, no broken box)",
      'try_box(net' in src and 'None, False, "G")' in src and "PAIN" not in src)

# 5. Ch copies with w = 0.5 while showings last
ch = c2p.run("Ch", "G", 5)
ws = {x["w"] for x in ch["tries"] if x["d"] <= K.DEMO_DAYS}
check(f"Ch: every copy weight is 0.5 during showings ({sorted(ws)})", ws == {0.5})

# 6. the same seed twice
a, b = c2p.run("Ctk", "GP", 6), c2p.run("Ctk", "GP", 6)
check("the same seed twice is the same (Ctk, GP)", json.dumps(a) == json.dumps(b))
print("All: PASS" if not fails else f"FAILED: {fails}")
