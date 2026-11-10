"""Builds c0b.py from C0-A's c0a.py (questions.md, C0B-frozen): C0-A's child and rules unchanged; the home changes.
Every replacement must match exactly once, so a change in c0a.py cannot slip through.

  python studies/C0B/make_c0b.py
"""
from pathlib import Path

HERE = Path(__file__).parent
s = (HERE.parent / "C0A" / "c0a.py").read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


rep('"""C0-A: can a newborn neural child learn ten words by living with two AI parents? (questions.md, frozen as C0A-frozen)',
    '"""C0-B: a harder home (studies/C0B/questions.md, frozen as C0B-frozen). Built from c0a.py by make_c0b.py; every\n'
    'difference is marked "C0-B". C0-A\'s child and rules are unchanged; the home changes: 30 things in 10 look-alike\n'
    'families, fewer moments a day (by level), 3-4 things in view, tests from day 3, a look-alike test.\n\n'
    'C0-A\'s docstring: can a newborn neural child learn ten words by living with two AI parents?')
rep('''  python studies/C0A/c0a.py one ARM SEED OUT_DIR
  python studies/C0A/c0a.py scenehash SEED          (the scene stream's fingerprint; must not depend on the arm)''',
    '''  python studies/C0B/c0b.py one ARM SEED OUT_DIR [LEVEL]     (LEVEL L1-L4; default C0B_LEVEL, else L1)
  python studies/C0B/c0b.py scenehash SEED [LEVEL]''')
rep('''HERE = Path(__file__).parent
NAMES = ["ball", "cup", "spoon", "bread", "apple", "banana", "shoe", "hat", "book", "duck"]''',
    '''HERE = Path(__file__).parent
FAMILIES = [["cup", "mug", "glass"], ["spoon", "fork", "ladle"], ["apple", "orange", "peach"],     # C0-B: fixed in the plan
            ["banana", "carrot", "corn"], ["bread", "cookie", "cracker"], ["shoe", "boot", "sock"],
            ["hat", "cap", "helmet"], ["book", "card", "letter"], ["duck", "chicken", "goose"],
            ["ball", "balloon", "bubble"]]
NAMES = [n for f in FAMILIES for n in f]
FAMILY = [i // 3 for i in range(len(NAMES))]
PLURALS = {n: ("geese" if n == "goose" else n + "es" if n.endswith(("s", "x", "ch", "sh")) else n + "s") for n in NAMES}
LEVELS = {"L1": (6, 0.35), "L2": (10, 0.50), "L3": (14, 0.65), "L4": (20, 0.65)}   # C0-B: (moments a day, member sd)
LEVEL = "L1"''')
rep('''NC, LOOK = 10, 16
MOMENTS, DAYS, DAYS_GL = 20, 1080, 4320
TEST_DAYS = [90, 180, 270, 360, 540, 720, 1080]
TEST_DAYS_GL = TEST_DAYS + [1440, 2160, 2880, 3600, 4320]''',
    '''NC, LOOK = 30, 16
MOMENTS, DAYS, DAYS_GL = 6, 1080, 1080
TEST_DAYS = [3, 7, 14, 30, 60, 90, 180, 360, 720, 1080]                 # C0-B
TEST_DAYS_GL = TEST_DAYS
N_APART = 30                                                              # C0-B: 30 of the 435 pairs''')
rep('''    "K": dict(d=None, cues="ambig", assoc=False, reward=False, shuffle=False, counting=True),
    "GL": dict(d=64, cues="ambig", assoc=False, reward=True, shuffle=False, long=True),
}
GROW = {375: 16, 735: 32}''',
    '''    "K": dict(d=None, cues="ambig", assoc=False, reward=False, shuffle=False, counting=True),
}
GROW = {360: 16, 720: 32}     # C0-B: at the start of day index 360 and 720, just after the tests of days 360 and 720''')
rep('''def load_corpus():
    import os
    path = Path(os.environ.get("C0A_CORPUS", HERE / "corpus.json"))     # a stand-in corpus only for code tests
    return json.loads(path.read_text(encoding="utf-8"))''',
    '''def load_corpus():
    """C0-A's committed corpus. C0-B drops every frame that holds one of the 30 names (or a plural) outside the slot,
    and adds the new names to the vocabulary."""
    import os
    path = Path(os.environ.get("C0A_CORPUS", HERE.parent / "C0A" / "corpus.json"))
    c = json.loads(path.read_text(encoding="utf-8"))
    bad = set(NAMES) | set(PLURALS.values())
    c["frames"] = {k: {part: [f for f in fr if not set(tokens(f.replace("{X}", " "))) & bad] for part, fr in parts.items()}
                   for k, parts in c["frames"].items()}
    c["vocabulary"] = sorted(set(c["vocabulary"]) | set(NAMES))
    c["names"] = NAMES
    return c''')
rep('''        rng = np.random.default_rng([seed, 1])
        self.centre = rng.normal(0, 1, (NC, LOOK))''',
    '''        rng = np.random.default_rng([seed, 1])
        fam = rng.normal(0, 1, (NC // 3, LOOK))                 # C0-B: family centres; members close around them
        self.centre = fam[FAMILY] + rng.normal(0, LEVELS[LEVEL][1], (NC, LOOK))''')
rep('''        idx = rng.choice(len(pairs), 9, replace=False)''', '''        idx = rng.choice(len(pairs), N_APART, replace=False)''')
rep('''        self.k = rng.integers(2, 4, n)
        self.act = rng.choice(4, n, p=ACT_P)
        self.cats = np.zeros((n, 3), dtype=int)
        self.inst = rng.integers(0, 3, (n, 3))''',
    '''        self.k = rng.integers(3, 5, n)                          # C0-B: 3 or 4 things in view
        self.act = rng.choice(4, n, p=ACT_P)
        self.cats = np.zeros((n, 4), dtype=int)
        self.inst = rng.integers(0, 3, (n, 4))''')
rep('''        self.noise = rng.normal(0, 0.2, (n, 3, LOOK))''', '''        self.noise = rng.normal(0, 0.2, (n, 4, LOOK))''')
rep('''    rng = np.random.default_rng([seed, 9, day, ["request", "new", "novel", "saying", "repair"].index(kind)])
    trials = []
    apart = sorted(sc.apart)
    for _ in range(n):
''',
    '''    rng = np.random.default_rng([seed, 9, day, ["request", "new", "novel", "saying", "repair", "alike"].index(kind)])
    trials = []
    apart = sorted(sc.apart)
    for _ in range(n):
        if kind == "alike":                                     # C0-B: the target among its two family members
            t0 = int(rng.integers(NC))
            cats = [c for c in range(NC) if FAMILY[c] == FAMILY[t0]]
            rest = [c for c in range(NC) if FAMILY[c] != FAMILY[t0]]
            cats.append(int(rng.choice(rest)))
            rng.shuffle(cats)
            inst = rng.integers(0, 3, 4)
            looks = sc.centre[cats] + sc.offset[cats, inst] + rng.normal(0, 0.2, (4, LOOK))
            trials.append((np.array(cats), looks, cats.index(t0), int(rng.integers(1 << 30)), int(rng.integers(1 << 30))))
            continue
''')
rep('''    for kind, n in (("request", 60), ("new", 60)):''', '''    for kind, n in (("request", 60), ("new", 60), ("alike", 60)):''')
rep('''    out_d = {"arm": arm, "seed": seed, "scene": sc.fingerprint(), "results": results,''',
    '''    out_d = {"arm": arm, "seed": seed, "level": LEVEL, "scene": sc.fingerprint(), "results": results,''')
rep('''    cmd = sys.argv[1]
    if cmd == "one":''',
    '''    import os
    cmd = sys.argv[1]
    LEVEL = os.environ.get("C0B_LEVEL", "L1")                  # C0-B: the level sets the moments a day and the spread
    if cmd == "one" and len(sys.argv) > 5:
        LEVEL = sys.argv[5]
    if cmd == "scenehash" and len(sys.argv) > 3:
        LEVEL = sys.argv[3]
    MOMENTS = LEVELS[LEVEL][0]
    if cmd == "one":''')
(HERE / "c0b.py").write_text(s, encoding="utf-8")
print("built", HERE / "c0b.py")
