# C2-S: copy who succeeds (results)

Frozen as `C2S-frozen`. c2s.py, analyse_c2s.py (written before data).

## Validity

- Code checks (All: PASS): **yes**
- All 528 runs present: **yes**
- The same boxes, pairs and Ben's habits per seed in every arm: **yes**

- Not at ceiling (T's early learning 0.085 below 0.90): **yes**

**Valid.**

## Readings (frozen; early learning = mean success at days 1, 2, 3, 5, 7; n = 48 children per arm)

1. **A consistently wrong model harms blind copying** (Ca - Cb): +0.0403 [+0.0264, +0.0542], effect size 0.80 -> **yes**
2. **Copying only what was seen to work helps** (Co - Cb): -0.0160 [-0.0361, +0.0042], effect size -0.22 -> **no**
3. **Trust from seen results helps, beyond the amount of copying** (Ct - Cy): +0.0014 [-0.0146, +0.0174], effect size 0.02 -> **no** (Ct - Co, reported: +0.0146 [-0.0056, +0.0354])
4. **Trust from own experience helps** (Cp - Cb -0.0021 [-0.0111, +0.0069], effect size -0.06; Cp - Cpx -0.0083 [-0.0209, +0.0042], effect size -0.18) -> **no**
5. **...even with every result hidden** (Cp100 - Cb100): -0.0069 [-0.0208, +0.0069], effect size -0.14 -> **no**
- Checks: copying blind helps over watching (Cb - I) +0.0431 [+0.0174, +0.0701]; watching over nothing (I - T) +0.0111 [-0.0014, +0.0236]; Ct - Cb -0.0014 [-0.0132, +0.0104]

## Success rate by day (mean over 48 children)

| arm | 1 | 2 | 3 | 5 | 7 | 10 | 15 | 30 | 45 | 60 | early |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T | 0.066 | 0.073 | 0.076 | 0.090 | 0.118 | 0.115 | 0.139 | 0.181 | 0.181 | 0.229 | 0.085 |
| I | 0.069 | 0.076 | 0.097 | 0.111 | 0.125 | 0.122 | 0.156 | 0.184 | 0.205 | 0.208 | 0.096 |
| Cb | 0.094 | 0.115 | 0.149 | 0.160 | 0.177 | 0.215 | 0.250 | 0.372 | 0.427 | 0.500 | 0.139 |
| Co | 0.080 | 0.111 | 0.115 | 0.139 | 0.170 | 0.181 | 0.250 | 0.274 | 0.340 | 0.365 | 0.123 |
| Ct | 0.097 | 0.122 | 0.153 | 0.146 | 0.170 | 0.205 | 0.260 | 0.378 | 0.424 | 0.465 | 0.137 |
| Cy | 0.101 | 0.118 | 0.128 | 0.163 | 0.170 | 0.198 | 0.208 | 0.306 | 0.319 | 0.385 | 0.136 |
| Cp | 0.094 | 0.118 | 0.135 | 0.167 | 0.170 | 0.198 | 0.278 | 0.375 | 0.424 | 0.538 | 0.137 |
| Cpx | 0.108 | 0.125 | 0.142 | 0.170 | 0.181 | 0.198 | 0.229 | 0.333 | 0.372 | 0.444 | 0.145 |
| Ca | 0.104 | 0.146 | 0.174 | 0.219 | 0.253 | 0.285 | 0.347 | 0.549 | 0.670 | 0.747 | 0.179 |
| Cb100 | 0.101 | 0.149 | 0.149 | 0.170 | 0.174 | 0.208 | 0.236 | 0.378 | 0.399 | 0.507 | 0.149 |
| Cp100 | 0.087 | 0.122 | 0.142 | 0.174 | 0.184 | 0.205 | 0.243 | 0.410 | 0.434 | 0.517 | 0.142 |

## Retention and novel boxes

| arm | day 30 | day 60 | novel day 30 | novel day 60 |
|---|---|---|---|---|
| T | 0.181 | 0.229 | 0.049 | 0.069 |
| I | 0.184 | 0.208 | 0.056 | 0.083 |
| Cb | 0.372 | 0.500 | 0.083 | 0.104 |
| Co | 0.274 | 0.365 | 0.062 | 0.118 |
| Ct | 0.378 | 0.465 | 0.083 | 0.132 |
| Cy | 0.306 | 0.385 | 0.083 | 0.083 |
| Cp | 0.375 | 0.538 | 0.090 | 0.097 |
| Cpx | 0.333 | 0.444 | 0.104 | 0.125 |
| Ca | 0.549 | 0.747 | 0.083 | 0.132 |
| Cb100 | 0.378 | 0.507 | 0.090 | 0.104 |
| Cp100 | 0.410 | 0.517 | 0.104 | 0.118 |

## Descriptive (days 1-30)

| arm | uses Ben's habit | copies Ann's pair | copies Ben's pair | success after seen | after hidden | weight on Ann | weight on Ben |
|---|---|---|---|---|---|---|---|
| T | 0.062 | nan | nan | nan | nan | nan | nan |
| I | 0.067 | 0.084 | 0.071 | 0.080 | 0.078 | 0.000 | 0.000 |
| Cb | 0.091 | 0.170 | 0.112 | 0.162 | 0.149 | 1.000 | 1.000 |
| Co | 0.060 | 0.121 | 0.076 | 0.123 | 0.119 | 0.497 | 0.093 |
| Ct | 0.064 | 0.172 | 0.082 | 0.160 | 0.161 | 1.000 | 0.230 |
| Cy | 0.079 | 0.143 | 0.097 | 0.136 | 0.132 | 0.603 | 0.625 |
| Cp | 0.069 | 0.160 | 0.096 | 0.161 | 0.142 | 0.998 | 0.461 |
| Cpx | 0.087 | 0.153 | 0.107 | 0.141 | 0.142 | 0.856 | 0.870 |
| Ca | 0.055 | 0.235 | nan | 0.236 | 0.235 | 1.000 | nan |
| Cb100 | 0.083 | 0.172 | 0.117 | nan | 0.160 | 1.000 | 1.000 |
| Cp100 | 0.073 | 0.164 | 0.094 | nan | 0.152 | 0.997 | 0.473 |

- Adopting Ben's habit, against T (its spontaneous rate): Cb - T +0.0286 [+0.0207, +0.0363]; Co - T -0.0015 [-0.0091, +0.0062]; Ct - T +0.0019 [-0.0062, +0.0103]; Cp - T +0.0073 [-0.0003, +0.0152]
- Ben's right demonstrations: 16.8 of his 88.7 per child (mean).

## Trust (mean over children; Ann / Ben)

| day | Ct (seen results) | Cp (own experience) | Cpx (coin credit) | Cp100 |
|---|---|---|---|---|
| 1 | 0.70 / 0.41 | 0.52 / 0.48 | 0.51 / 0.51 | 0.53 / 0.49 |
| 2 | 0.81 / 0.31 | 0.54 / 0.45 | 0.51 / 0.51 | 0.55 / 0.47 |
| 3 | 0.88 / 0.28 | 0.58 / 0.43 | 0.53 / 0.53 | 0.58 / 0.45 |
| 5 | 0.96 / 0.29 | 0.66 / 0.40 | 0.53 / 0.51 | 0.63 / 0.42 |
| 7 | 0.98 / 0.22 | 0.71 / 0.38 | 0.53 / 0.54 | 0.69 / 0.38 |
| 15 | 1.00 / 0.15 | 0.89 / 0.30 | 0.63 / 0.58 | 0.88 / 0.32 |
| 30 | 1.00 / 0.15 | 0.99 / 0.37 | 0.70 / 0.71 | 0.99 / 0.36 |

Rules (frozen): readings as above; paired by seed; 10,000 draws, seed 20261113; no reading if T's early learning is 0.90 or more; reading 1 negative reads 'not shown'.

