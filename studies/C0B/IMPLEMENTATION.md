# C0-B: implementation readings (written before the study's data)

- **The code:** `c0b.py` is built from C0-A's `c0a.py` by `make_c0b.py`. Every replacement must match exactly once,
  and every difference is marked "C0-B". C0-A's readings (`studies/C0A/IMPLEMENTATION.md`) all hold. The child, its
  learning rules and its rates are unchanged.
- **The home:**
  - 30 names in the plan's 10 families. A family's centre is N(0, 1) per number; a member's centre is the family
    centre + N(0, sd²), with sd set by the level. The instance offsets (sd 0.5) and the sighting noise (sd 0.2) are
    C0-A's.
  - 3 or 4 things in view; 30 never-together pairs.
  - The moments a day are set by the level.
- **The sentences:** C0-A's committed corpus. Frames holding any of the 30 names or their plurals outside the slot are
  dropped (6 background frames; the minimums still hold). The vocabulary is the corpus's tokens plus the 30 names.
- **Tests:** at the end of days 3, 7, 14, 30, 60, 90, 180, 360, 720 and 1,080.
  - **The look-alike test (60 trials):** the target, its two family members, and one thing from another family.
    Daily instances; a kept-back asking frame; no cue. Its trials come from their own random stream (kind index 5).
- **Growth (arm C):** at the start of day index 360 and 720. These come just after the tests of days 360 and 720, never
  on a test day.
- **There is no GL arm.**
- **The difficulty check:** `calibrate_c0b.py` runs arms A, P and E on seeds 101–104, up to day 90 only (nothing later
  is computed), at each level. The result (`calibration.md`) chose **L1**.
  - **Recorded honestly:** before the check, a code test of `c0b.py` ran arm A on seed 101 at L1 to day 1,080 and
    printed its day-1,080 results (request 1.0). The check reads only days 30 and 90 of A, P and E, so this cannot
    have steered the choice.
- **The analysis was tested** on throwaway seeds 201–216 (renamed 1–16 in a scratch folder, never committed). This was
  a code test only; its numbers are not looked at.
- **The study:** level L1, arms A, B, C, H, D, P, G, E, F and K, seeds 1–16, on the cloud (`c0b-run.yml`).
