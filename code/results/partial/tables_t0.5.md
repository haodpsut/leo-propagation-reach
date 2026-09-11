# scale study: 480 runs, 0 INVALID (kept in CSV, excluded from means)


## task=delay · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n valid / n inv / beats-const) | heat mean±std (n valid / n inv / beats-const) | qw mean±std (n valid / n inv / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1607±0.0095 (10/0/10) | 0.1419±0.0267 (10/0/10) | 0.1493±0.0213 (10/0/10) | heat 6 · qw 4 (of 10) · gain 18.3% | tie |
| s1584 | 0.1709±0.0035 (10/0/9) | 0.1678±0.0074 (10/0/9) | 0.1693±0.0039 (10/0/9) | heat 8 · qw 2 (of 10) · gain 2.3% | FLOOR (gain 2.3% < 5%) |
| s3168 | 0.1701±0.0026 (10/0/2) | 0.1690±0.0028 (10/0/5) | 0.1689±0.0033 (10/0/6) | heat 8 · qw 2 (of 10) · gain 0.5% | FLOOR (gain 0.5% < 5%) |
| s4400 | 0.1693±0.0023 (10/0/2) | 0.1687±0.0030 (10/0/4) | 0.1690±0.0021 (10/0/2) | heat 8 · qw 2 (of 10) · gain 0.2% | FLOOR (gain 0.2% < 5%) |

## task=delay · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n valid / n inv / beats-const) | heat mean±std (n valid / n inv / beats-const) | qw mean±std (n valid / n inv / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1607±0.0095 (10/0/10) | 0.1518±0.0175 (10/0/10) | 0.1397±0.0260 (10/0/10) | heat 3 · qw 7 (of 10) · gain 19.5% | qw |
| s1584 | 0.1709±0.0035 (10/0/9) | 0.1718±0.0018 (10/0/7) | 0.1691±0.0056 (10/0/8) | heat 5 · qw 5 (of 10) · gain 1.5% | FLOOR (gain 1.5% < 5%) |
| s3168 | 0.1701±0.0026 (10/0/2) | 0.1694±0.0027 (10/0/4) | 0.1690±0.0030 (10/0/5) | heat 4 · qw 6 (of 10) · gain 0.4% | FLOOR (gain 0.4% < 5%) |
| s4400 | 0.1693±0.0023 (10/0/2) | 0.1693±0.0023 (10/0/1) | 0.1688±0.0018 (10/0/3) | heat 5 · qw 5 (of 10) · gain 0.1% | FLOOR (gain 0.1% < 5%) |

## task=hops · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n valid / n inv / beats-const) | heat mean±std (n valid / n inv / beats-const) | qw mean±std (n valid / n inv / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1747±0.0087 (10/0/10) | 0.1437±0.0400 (10/0/10) | 0.1451±0.0440 (10/0/10) | heat 6 · qw 4 (of 10) · gain 23.9% | tie |
| s1584 | 0.2004±0.0013 (10/0/10) | 0.1969±0.0068 (10/0/10) | 0.1959±0.0079 (10/0/10) | heat 6 · qw 4 (of 10) · gain 2.9% | FLOOR (gain 2.9% < 5%) |
| s3168 | 0.1771±0.0004 (10/0/9) | 0.1763±0.0022 (10/0/10) | 0.1765±0.0013 (10/0/10) | heat 7 · qw 3 (of 10) · gain 0.7% | FLOOR (gain 0.7% < 5%) |
| s4400 | 0.1871±0.0004 (10/0/10) | 0.1864±0.0014 (10/0/10) | 0.1865±0.0014 (10/0/10) | heat 9 · qw 1 (of 10) · gain 0.5% | FLOOR (gain 0.5% < 5%) |

## task=hops · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n valid / n inv / beats-const) | heat mean±std (n valid / n inv / beats-const) | qw mean±std (n valid / n inv / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1747±0.0087 (10/0/10) | 0.1615±0.0318 (10/0/10) | 0.1347±0.0502 (10/0/10) | heat 2 · qw 8 (of 10) · gain 28.7% | qw |
| s1584 | 0.2004±0.0013 (10/0/10) | 0.1996±0.0039 (10/0/10) | 0.1981±0.0042 (10/0/10) | heat 5 · qw 5 (of 10) · gain 1.8% | FLOOR (gain 1.8% < 5%) |
| s3168 | 0.1771±0.0004 (10/0/9) | 0.1770±0.0008 (10/0/10) | 0.1766±0.0010 (10/0/10) | heat 4 · qw 6 (of 10) · gain 0.5% | FLOOR (gain 0.5% < 5%) |
| s4400 | 0.1871±0.0004 (10/0/10) | 0.1868±0.0010 (10/0/10) | 0.1869±0.0007 (10/0/10) | heat 6 · qw 4 (of 10) · gain 0.3% | FLOOR (gain 0.3% < 5%) |

## Robustness across arms (the claim's own test)

A ranking at (task, shell) counts only if it is the SAME in every arm.

| task | shell | relu/t0=0.5 | softplus/t0=0.5 | robust? |
|---|---|---|---|---|
| delay | s264 | tie | qw | no |
| delay | s1584 | FLOOR (gain 2.3% < 5%) | FLOOR (gain 1.5% < 5%) | FLOOR |
| delay | s3168 | FLOOR (gain 0.5% < 5%) | FLOOR (gain 0.4% < 5%) | FLOOR |
| delay | s4400 | FLOOR (gain 0.2% < 5%) | FLOOR (gain 0.1% < 5%) | FLOOR |
| hops | s264 | tie | qw | no |
| hops | s1584 | FLOOR (gain 2.9% < 5%) | FLOOR (gain 1.8% < 5%) | FLOOR |
| hops | s3168 | FLOOR (gain 0.7% < 5%) | FLOOR (gain 0.5% < 5%) | FLOOR |
| hops | s4400 | FLOOR (gain 0.5% < 5%) | FLOOR (gain 0.3% < 5%) | FLOOR |

## Learned propagation time t (mean over valid runs, per layer)

| task | shell | arm | heat t | qw t |
|---|---|---|---|---|
| delay | s264 | relu/t0=0.5 | [1.49, -0.00, -0.16] | [0.78, 0.27, 0.03] |
| delay | s264 | softplus/t0=0.5 | [0.90, 0.18, 0.13] | [0.98, 0.60, 0.43] |
| delay | s1584 | relu/t0=0.5 | [1.07, 0.20, -0.13] | [0.82, 0.40, 0.13] |
| delay | s1584 | softplus/t0=0.5 | [0.76, 0.34, 0.17] | [0.85, 0.45, 0.33] |
| delay | s3168 | relu/t0=0.5 | [0.81, 0.45, 0.08] | [0.66, 0.49, 0.46] |
| delay | s3168 | softplus/t0=0.5 | [0.79, 0.39, 0.22] | [0.72, 0.68, 0.46] |
| delay | s4400 | relu/t0=0.5 | [0.90, 0.24, -0.08] | [0.70, 0.48, 0.33] |
| delay | s4400 | softplus/t0=0.5 | [0.77, 0.22, 0.12] | [0.71, 0.66, 0.58] |
| hops | s264 | relu/t0=0.5 | [1.45, 0.14, -0.16] | [1.02, 0.51, 0.20] |
| hops | s264 | softplus/t0=0.5 | [1.02, 0.28, 0.19] | [1.09, 0.70, 0.49] |
| hops | s1584 | relu/t0=0.5 | [1.20, 0.46, 0.02] | [1.01, 0.79, 0.30] |
| hops | s1584 | softplus/t0=0.5 | [0.85, 0.40, 0.22] | [0.93, 0.80, 0.52] |
| hops | s3168 | relu/t0=0.5 | [1.02, 0.24, -0.06] | [0.73, 0.48, 0.50] |
| hops | s3168 | softplus/t0=0.5 | [0.82, 0.26, 0.14] | [0.76, 0.71, 0.46] |
| hops | s4400 | relu/t0=0.5 | [1.10, 0.51, 0.11] | [0.66, 0.76, 0.63] |
| hops | s4400 | softplus/t0=0.5 | [0.83, 0.41, 0.25] | [0.73, 0.76, 0.56] |
