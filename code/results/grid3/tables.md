# scale study: 360 runs · 40 PATHOLOGY (NaN/non-monotone, excluded) · 46 plateau (flat loss at the constant floor, kept)


## task=delay · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1334±0.0076 (8/2/1/8) | 0.1105±0.0041 (10/0/1/10) | 0.1222±0.0092 (7/3/0/7) | heat 7 · qw 0 (of 7) · gain 36.3% | heat |
| s1584 | 0.1632±0.0028 (9/1/1/9) | 0.1346±0.0058 (10/0/0/10) | 0.1506±0.0165 (10/0/2/10) | heat 8 · qw 2 (of 10) · gain 21.6% | heat |
| s3168 | 0.1654±0.0029 (8/2/4/8) | 0.1375±0.0125 (10/0/0/10) | 0.1362±0.0321 (10/0/3/9) | heat 6 · qw 4 (of 10) · gain 19.7% | tie |

## task=delay · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1334±0.0076 (8/2/1/8) | 0.1109±0.0033 (9/1/0/9) | 0.1125±0.0044 (10/0/1/10) | heat 7 · qw 2 (of 9) · gain 36.1% | heat |
| s1584 | 0.1632±0.0028 (9/1/1/9) | 0.1321±0.0041 (10/0/0/10) | 0.1393±0.0128 (10/0/0/10) | heat 8 · qw 2 (of 10) · gain 23.1% | heat |
| s3168 | 0.1654±0.0029 (8/2/4/8) | 0.1402±0.0329 (9/1/0/7) | 0.1288±0.0237 (7/3/1/6) | heat 1 · qw 5 (of 6) · gain 24.1% | n<7 |

## task=hops · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1368±0.0019 (8/2/0/8) | 0.0646±0.0348 (9/1/0/9) | 0.1232±0.0383 (10/0/0/10) | heat 8 · qw 1 (of 9) · gain 65.8% | heat |
| s1584 | 0.1928±0.0039 (9/1/3/9) | 0.1185±0.0369 (6/4/0/6) | 0.1681±0.0390 (10/0/4/10) | heat 4 · qw 2 (of 6) · gain 41.3% | n<7 |
| s3168 | 0.1729±0.0015 (9/1/5/9) | 0.1517±0.0286 (9/1/0/7) | 0.1534±0.0329 (9/1/4/7) | heat 5 · qw 3 (of 8) · gain 14.5% | tie |

## task=hops · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1368±0.0019 (8/2/0/8) | 0.0581±0.0048 (10/0/0/10) | 0.0641±0.0042 (10/0/1/10) | heat 7 · qw 3 (of 10) · gain 69.2% | heat |
| s1584 | 0.1928±0.0039 (9/1/3/9) | 0.1010±0.0370 (10/0/0/9) | 0.0987±0.0568 (8/2/0/7) | heat 2 · qw 6 (of 8) · gain 51.1% | tie |
| s3168 | 0.1729±0.0015 (9/1/5/9) | 0.1348±0.0316 (7/3/0/7) | 0.1201±0.0474 (8/2/1/6) | heat 2 · qw 3 (of 5) · gain 32.3% | n<7 |

## Robustness across arms (the claim's own test)

A ranking at (task, shell) counts only if it is the SAME in every arm.

| task | shell | relu/t0=0.5 | softplus/t0=0.5 | robust? |
|---|---|---|---|---|
| delay | s264 | heat | heat | YES: heat |
| delay | s1584 | heat | heat | YES: heat |
| delay | s3168 | tie | n<7 | no |
| delay | s4400 | — | — | no |
| hops | s264 | heat | heat | YES: heat |
| hops | s1584 | n<7 | tie | no |
| hops | s3168 | tie | n<7 | no |
| hops | s4400 | — | — | no |

## Learned propagation time t (mean over valid runs, per layer)

| task | shell | arm | heat t | qw t |
|---|---|---|---|---|
| delay | s264 | relu/t0=0.5 | [3.27, 0.23, -0.17, -0.17] | [0.82, 0.47, 0.13, 0.23] |
| delay | s264 | softplus/t0=0.5 | [2.03, 0.68, 0.54, 0.48] | [1.04, 0.82, 0.82, 1.07] |
| delay | s1584 | relu/t0=0.5 | [8.06, 1.14, 0.37, 0.40] | [1.34, 0.88, 0.22, 0.22] |
| delay | s1584 | softplus/t0=0.5 | [4.71, 2.36, 1.57, 4.36] | [1.51, 1.91, 1.50, 1.77] |
| delay | s3168 | relu/t0=0.5 | [12.70, -0.13, -0.14, -0.14] | [1.84, 2.10, 0.95, 1.15] |
| delay | s3168 | softplus/t0=0.5 | [10.12, 5.94, 4.90, 5.33] | [1.18, 1.79, 0.27, 4.00] |
| hops | s264 | relu/t0=0.5 | [4.87, -0.16, 0.10, 0.06] | [0.91, 0.40, 0.13, 0.20] |
| hops | s264 | softplus/t0=0.5 | [3.11, 1.70, 0.98, 0.71] | [1.29, 1.11, 1.25, 1.25] |
| hops | s1584 | relu/t0=0.5 | [8.27, 1.51, 1.36, 1.38] | [0.58, 0.58, 0.45, 1.65] |
| hops | s1584 | softplus/t0=0.5 | [8.21, 5.29, 4.79, 6.27] | [1.85, 2.33, 2.56, 4.64] |
| hops | s3168 | relu/t0=0.5 | [12.46, -0.13, -0.15, -0.15] | [1.75, 2.15, 0.95, 0.38] |
| hops | s3168 | softplus/t0=0.5 | [10.65, 5.90, 3.85, 5.27] | [2.26, 4.28, 1.58, 3.33] |
