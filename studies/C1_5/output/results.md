# C1.5: word order (results)

Frozen as `C1_5-frozen` (with correction 1, before data). c15.py, analyse_c15.py (written before data).

## Validity

- Code checks (checks.log, All: PASS): **yes**
- All 120 children present: **yes**
- The same home per seed in every arm: **yes**

**Valid.**

## Reading (frozen)

- **not learned.**
- Guard: B's plain accuracy at day 720 0.7069 [0.6736, 0.7403] against chance 0.20: informative **yes**.
- **Primary**, first-act order accuracy on held-out pairs (test frames): Q - B -0.1521 [-0.1842, -0.1173]; Q - Q- -0.0781 [-0.1066, -0.0465]; hears order **no**.
- Position: P - B -0.0048 [-0.0110, +0.0012], P - Q +0.1473 [+0.1125, +0.1786] (within +-0.05: no); K - B +0.0199 [-0.0014, +0.0390], K - Q +0.1719 [+0.1413, +0.2000] (within +-0.05: no).
- Negation (secondary): Q - B -0.1455 [-0.1673, -0.1218]; Q - Q- -0.0718 [-0.0915, -0.0494]; learned **no**.

Rules (frozen): 'it hears order' if the lower bounds of Q - B and Q - Q- (first act, held-out pairs) are above 0; 'position is enough' if P or K beats B (lower bound above 0) and its difference from Q lies within +-0.05; 'not learned' otherwise; no reading if B's plain accuracy is not above chance. Chance: first act 1/5; among the two named things 1/2.

Caution (GPT, council 5): passing shows order-sensitive behaviour, not compositional understanding.

## Day 720, every arm (mean [95%], 24 children)

| measure | B | P | K | Q | Q- |
|---|---|---|---|---|---|
| held_test_first | 0.431 [0.423, 0.438] | 0.426 [0.417, 0.435] | 0.451 [0.431, 0.469] | 0.279 [0.250, 0.311] | 0.357 [0.346, 0.367] |
| held_test_second | 0.569 [0.555, 0.583] | 0.535 [0.518, 0.553] | 0.698 [0.685, 0.711] | 0.321 [0.305, 0.336] | 0.443 [0.416, 0.467] |
| held_test_both | 0.218 [0.210, 0.226] | 0.204 [0.195, 0.213] | 0.268 [0.250, 0.285] | 0.083 [0.070, 0.097] | 0.132 [0.121, 0.143] |
| held_test_neg | 0.417 [0.408, 0.425] | 0.413 [0.403, 0.422] | 0.744 [0.735, 0.753] | 0.271 [0.251, 0.294] | 0.343 [0.332, 0.354] |
| held_test_neg_x | 0.417 [0.408, 0.425] | 0.413 [0.403, 0.422] | 0.194 [0.186, 0.203] | 0.266 [0.256, 0.275] | 0.351 [0.339, 0.362] |
| plain | 0.707 [0.674, 0.740] | 0.694 [0.662, 0.728] | 0.797 [0.772, 0.821] | 0.278 [0.244, 0.314] | 0.468 [0.424, 0.512] |
| held_test_after_first | 0.422 [0.414, 0.430] | 0.419 [0.413, 0.427] | 0.059 [0.051, 0.066] | 0.272 [0.257, 0.288] | 0.347 [0.328, 0.366] |
| held_life_first | 0.430 [0.423, 0.436] | 0.425 [0.419, 0.431] | 0.554 [0.541, 0.568] | 0.280 [0.247, 0.315] | 0.354 [0.341, 0.367] |
| held_life_neg | 0.418 [0.409, 0.428] | 0.416 [0.407, 0.426] | 0.770 [0.759, 0.782] | 0.272 [0.252, 0.294] | 0.349 [0.338, 0.360] |
| life_test_first | 0.436 [0.430, 0.443] | 0.433 [0.426, 0.441] | 0.455 [0.441, 0.468] | 0.299 [0.272, 0.329] | 0.365 [0.355, 0.376] |
| life_test_neg | 0.428 [0.420, 0.436] | 0.424 [0.417, 0.431] | 0.759 [0.749, 0.769] | 0.279 [0.259, 0.300] | 0.345 [0.335, 0.356] |

## First-act order accuracy over life (held-out pairs, test frames; mean over children)

| arm | 30 | 90 | 180 | 360 | 720 |
|---|---|---|---|---|---|
| B | 0.249 | 0.260 | 0.276 | 0.369 | 0.431 |
| P | 0.246 | 0.256 | 0.276 | 0.348 | 0.426 |
| K | 0.256 | 0.332 | 0.434 | 0.475 | 0.451 |
| Q | 0.243 | 0.240 | 0.243 | 0.217 | 0.279 |
| Q- | 0.244 | 0.249 | 0.255 | 0.261 | 0.357 |

## Plain accuracy over life (mean over children)

| arm | 30 | 90 | 180 | 360 | 720 |
|---|---|---|---|---|---|
| B | 0.249 | 0.260 | 0.289 | 0.497 | 0.707 |
| P | 0.239 | 0.272 | 0.290 | 0.464 | 0.694 |
| K | 0.253 | 0.374 | 0.536 | 0.699 | 0.797 |
| Q | 0.232 | 0.240 | 0.254 | 0.236 | 0.278 |
| Q- | 0.226 | 0.232 | 0.256 | 0.285 | 0.468 |
