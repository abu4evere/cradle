# C2: learning how (results)

Frozen as `C2-frozen`. c2.py, analyse_c2.py (written before data).

## Validity

- Code checks (All: PASS): **yes**
- All 120 runs present: **yes**
- The same boxes and pairs per seed in every arm: **yes**

- Not at ceiling (T's early learning 0.099 below 0.90): **yes**

**Valid.**

## Readings (frozen)

- **Watching the method helps** (I - E, early learning = mean success at days 1, 2, 3, 5, 7): -0.0125 [-0.0361, +0.0111] -> **no**
- **Copying helps** (Ic - I): +0.0903 [+0.0569, +0.1236] -> **yes**
- Check, seeing the result alone (E - T): +0.0153 [-0.0083, +0.0389]

## Success rate by day (mean over 24 children)

| arm | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 30 | 45 | 60 | early |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T | 0.104 | 0.083 | 0.104 | 0.097 | 0.104 | 0.139 | 0.153 | 0.146 | 0.194 | 0.285 | 0.099 |
| E | 0.090 | 0.104 | 0.111 | 0.139 | 0.125 | 0.125 | 0.174 | 0.181 | 0.208 | 0.257 | 0.114 |
| I | 0.076 | 0.076 | 0.104 | 0.132 | 0.118 | 0.097 | 0.146 | 0.194 | 0.201 | 0.257 | 0.101 |
| Ic | 0.125 | 0.139 | 0.174 | 0.236 | 0.285 | 0.292 | 0.354 | 0.569 | 0.701 | 0.799 | 0.192 |
| Iw | 0.104 | 0.146 | 0.160 | 0.160 | 0.201 | 0.236 | 0.264 | 0.410 | 0.507 | 0.597 | 0.154 |

## Retention and novel boxes

| arm | day 30 (last with demonstrations) | day 60 (30 days without) | novel boxes day 30 | novel boxes day 60 |
|---|---|---|---|---|
| T | 0.146 | 0.285 | 0.083 | 0.153 |
| E | 0.181 | 0.257 | 0.069 | 0.069 |
| I | 0.194 | 0.257 | 0.097 | 0.097 |
| Ic | 0.569 | 0.799 | 0.139 | 0.208 |
| Iw | 0.410 | 0.597 | 0.125 | 0.194 |

## Selective copying (Iw, descriptive)

- After a failed demonstration, Iw repeats the failed pair in 0.069 of its next tries; T, on the same tries with no demonstration, picks that pair 0.062 of the time (Iw - T +0.0066 [-0.0143, +0.0274]).

Rules (frozen): 'watching the method helps' if I - E has a lower bound above 0; 'copying helps' if Ic - I has a lower bound above 0 (paired by seed, 10,000 draws, seed 20261120); no reading if T's early learning is 0.90 or more.

