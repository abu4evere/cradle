# C1-B: a sibling (results)

Frozen as `C1B-frozen`. c1b.py, analyse_c1b.py (written before data).

## Validity

- Code checks (All: PASS): **yes**
- All 120 runs present: **yes**
- The same home per seed in every arm: **yes**

**Valid.**

## Readings (frozen)

- **Imitation helps** (Yi - Y, early learning = mean clean turn accuracy at days 7-90): -0.0032 [-0.0070, +0.0005] -> **no**
- **Hearing the sibling's feedback helps** (Y - Yo): +0.0001 [-0.0003, +0.0005] -> **no**
- Sequence continuity (Yo - Y-): +0.1676 [+0.1509, +0.1851]
- All of watching (Y - Y-): +0.1677 [+0.1509, +0.1852]
- Imitation against no sibling (Yi - A): -0.0055 [-0.0095, -0.0017]

## The younger's clean turn accuracy by day (mean over 24 children)

| arm | 7 | 14 | 30 | 60 | 90 | 180 | 360 | 720 | early mean |
|---|---|---|---|---|---|---|---|---|---|
| A | 0.509 | 0.629 | 0.707 | 0.767 | 0.810 | 0.838 | 0.868 | 0.898 | 0.684 |
| Y- | 0.371 | 0.455 | 0.526 | 0.597 | 0.623 | 0.686 | 0.730 | 0.780 | 0.515 |
| Yo | 0.506 | 0.625 | 0.707 | 0.766 | 0.806 | 0.832 | 0.865 | 0.887 | 0.682 |
| Y | 0.506 | 0.625 | 0.706 | 0.767 | 0.806 | 0.832 | 0.865 | 0.886 | 0.682 |
| Yi | 0.511 | 0.623 | 0.706 | 0.760 | 0.795 | 0.825 | 0.856 | 0.881 | 0.679 |

## Day 720 against A (paired)

- Y- - A, clean turn: -0.1184 [-0.1333, -0.1062]; noisy turn: -0.0730 [-0.0962, -0.0489]; clean anticipation: -0.0818 [-0.0947, -0.0703]
- Yo - A, clean turn: -0.0116 [-0.0161, -0.0071]; noisy turn: -0.0175 [-0.0315, -0.0046]; clean anticipation: -0.0118 [-0.0163, -0.0075]
- Y - A, clean turn: -0.0123 [-0.0161, -0.0083]; noisy turn: -0.0175 [-0.0318, -0.0043]; clean anticipation: -0.0122 [-0.0162, -0.0082]
- Yi - A, clean turn: -0.0178 [-0.0244, -0.0115]; noisy turn: -0.0224 [-0.0377, -0.0072]; clean anticipation: -0.0214 [-0.0265, -0.0168]

## Turn-matched (descriptive): the arm at day t against A at day t/2 (about the same own turns)

| t | Y- | Yo | Y | Yi | A at t/2 |
|---|---|---|---|---|---|
| 14 | 0.455 | 0.625 | 0.625 | 0.623 | 0.509 |
| 60 | 0.597 | 0.766 | 0.767 | 0.760 | 0.707 |
| 180 | 0.686 | 0.832 | 0.832 | 0.825 | 0.810 |
| 720 | 0.780 | 0.887 | 0.886 | 0.881 | 0.868 |

## The older sibling's clean turn accuracy (at the younger's days; day 0 = just before the birth)

| arm | 0 | 7 | 14 | 30 | 90 | 360 | 720 |
|---|---|---|---|---|---|---|---|
| Y- | 0.871 | 0.880 | 0.884 | 0.876 | 0.879 | 0.892 | 0.891 |
| Yo | 0.871 | 0.880 | 0.884 | 0.876 | 0.879 | 0.891 | 0.891 |
| Y | 0.871 | 0.880 | 0.884 | 0.876 | 0.879 | 0.891 | 0.891 |
| Yi | 0.871 | 0.880 | 0.884 | 0.876 | 0.879 | 0.891 | 0.891 |

## Turns per younger child (mean)

| arm | own | sibling's | seen | imitated |
|---|---|---|---|---|
| A | 5438 | 0 | 0 | 0 |
| Y- | 2723 | 2716 | 0 | 0 |
| Yo | 2723 | 2716 | 2716 | 0 |
| Y | 2723 | 2716 | 2716 | 0 |
| Yi | 2723 | 2716 | 2716 | 2260 |

Rules (frozen): 'imitation helps' if Yi - Y has a lower bound above 0; 'hearing the sibling's feedback helps' if Y - Yo has a lower bound above 0 (early learning, paired by seed, 10,000 draws, seed 20261117).

