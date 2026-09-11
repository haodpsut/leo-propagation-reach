# scale study: 960 runs · 5 PATHOLOGY (NaN/non-monotone, excluded) · 48 plateau (flat loss at the constant floor, kept)


## task=delay · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1572±0.0119 (10/0/0/10) | 0.1230±0.0117 (10/0/0/10) | 0.1436±0.0154 (10/0/1/10) | heat 8 · qw 2 (of 10) · gain 29.2% | heat |
| s1584 | 0.1711±0.0027 (10/0/0/7) | 0.1678±0.0059 (10/0/0/5) | 0.1685±0.0051 (10/0/1/7) | heat 4 · qw 6 (of 10) · gain 2.3% | FLOOR (gain 2.3% < 5%) |
| s3168 | 0.1697±0.0028 (10/0/0/2) | 0.1690±0.0029 (10/0/0/4) | 0.1691±0.0030 (10/0/0/6) | heat 4 · qw 6 (of 10) · gain 0.4% | FLOOR (gain 0.4% < 5%) |
| s4400 | 0.1691±0.0023 (10/0/0/3) | 0.1694±0.0024 (10/0/0/2) | 0.1691±0.0021 (10/0/0/3) | heat 4 · qw 6 (of 10) · gain -0.1% | FLOOR (gain -0.1% < 5%) |

## task=delay · arm=relu/t0=2 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1572±0.0119 (10/0/0/10) | 0.1360±0.0209 (10/0/1/9) | 0.1575±0.0138 (10/0/0/9) | heat 10 · qw 0 (of 10) · gain 21.6% | heat |
| s1584 | 0.1711±0.0027 (10/0/0/7) | 0.1697±0.0036 (10/0/0/8) | 0.1715±0.0072 (10/0/0/6) | heat 6 · qw 4 (of 10) · gain 1.2% | FLOOR (gain 1.2% < 5%) |
| s3168 | 0.1697±0.0028 (10/0/0/2) | 0.1698±0.0030 (10/0/0/3) | 0.1698±0.0025 (10/0/0/3) | heat 5 · qw 5 (of 10) · gain -0.0% | FLOOR (gain -0.0% < 5%) |
| s4400 | 0.1691±0.0023 (10/0/0/3) | 0.1693±0.0021 (10/0/0/2) | 0.1693±0.0021 (10/0/0/2) | heat 3 · qw 7 (of 10) · gain -0.1% | FLOOR (gain -0.1% < 5%) |

## task=delay · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1572±0.0119 (10/0/0/10) | 0.1414±0.0187 (10/0/0/10) | 0.1233±0.0194 (10/0/0/10) | heat 3 · qw 7 (of 10) · gain 29.0% | qw |
| s1584 | 0.1711±0.0027 (10/0/0/7) | 0.1706±0.0018 (9/1/0/3) | 0.1683±0.0046 (10/0/0/7) | heat 2 · qw 7 (of 9) · gain 1.9% | FLOOR (gain 1.9% < 5%) |
| s3168 | 0.1697±0.0028 (10/0/0/2) | 0.1696±0.0028 (10/0/0/3) | 0.1708±0.0034 (10/0/0/2) | heat 5 · qw 5 (of 10) · gain 0.0% | FLOOR (gain 0.0% < 5%) |
| s4400 | 0.1691±0.0023 (10/0/0/3) | 0.1694±0.0021 (10/0/0/2) | 0.1693±0.0022 (10/0/1/3) | heat 6 · qw 4 (of 10) · gain -0.1% | FLOOR (gain -0.1% < 5%) |

## task=delay · arm=softplus/t0=2 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1572±0.0119 (10/0/0/10) | 0.1572±0.0219 (10/0/1/9) | 0.1547±0.0202 (10/0/0/9) | heat 5 · qw 5 (of 10) · gain 10.9% | tie |
| s1584 | 0.1711±0.0027 (10/0/0/7) | 0.1713±0.0030 (10/0/0/5) | 0.1697±0.0048 (10/0/0/8) | heat 3 · qw 7 (of 10) · gain 1.1% | FLOOR (gain 1.1% < 5%) |
| s3168 | 0.1697±0.0028 (10/0/0/2) | 0.1699±0.0027 (10/0/0/1) | 0.1695±0.0031 (10/0/0/5) | heat 3 · qw 7 (of 10) · gain 0.1% | FLOOR (gain 0.1% < 5%) |
| s4400 | 0.1691±0.0023 (10/0/0/3) | 0.1693±0.0022 (10/0/0/1) | 0.1694±0.0021 (10/0/0/1) | heat 3 · qw 7 (of 10) · gain -0.1% | FLOOR (gain -0.1% < 5%) |

## task=hops · arm=relu/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1663±0.0124 (10/0/0/10) | 0.1235±0.0352 (10/0/0/10) | 0.1388±0.0420 (10/0/0/10) | heat 6 · qw 4 (of 10) · gain 34.6% | tie |
| s1584 | 0.2007±0.0012 (10/0/1/10) | 0.1983±0.0050 (10/0/1/9) | 0.1961±0.0111 (10/0/2/10) | heat 3 · qw 7 (of 10) · gain 2.8% | FLOOR (gain 2.8% < 5%) |
| s3168 | 0.1773±0.0005 (10/0/1/9) | 0.1774±0.0008 (10/0/1/9) | 0.1765±0.0013 (9/1/1/9) | heat 3 · qw 6 (of 9) · gain 0.6% | FLOOR (gain 0.6% < 5%) |
| s4400 | 0.1870±0.0005 (10/0/1/10) | 0.1871±0.0003 (10/0/1/10) | 0.1855±0.0041 (10/0/1/10) | heat 4 · qw 6 (of 10) · gain 1.0% | FLOOR (gain 1.0% < 5%) |

## task=hops · arm=relu/t0=2 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1663±0.0124 (10/0/0/10) | 0.1272±0.0445 (9/1/0/9) | 0.1517±0.0326 (10/0/1/10) | heat 8 · qw 1 (of 9) · gain 32.7% | heat |
| s1584 | 0.2007±0.0012 (10/0/1/10) | 0.1986±0.0057 (10/0/1/10) | 0.2004±0.0016 (10/0/1/10) | heat 3 · qw 7 (of 10) · gain 1.6% | FLOOR (gain 1.6% < 5%) |
| s3168 | 0.1773±0.0005 (10/0/1/9) | 0.1772±0.0003 (10/0/1/10) | 0.1771±0.0004 (10/0/1/10) | heat 2 · qw 8 (of 10) · gain 0.2% | FLOOR (gain 0.2% < 5%) |
| s4400 | 0.1870±0.0005 (10/0/1/10) | 0.1872±0.0003 (10/0/1/10) | 0.1872±0.0002 (10/0/1/10) | heat 5 · qw 5 (of 10) · gain 0.2% | FLOOR (gain 0.2% < 5%) |

## task=hops · arm=softplus/t0=0.5 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1663±0.0124 (10/0/0/10) | 0.1367±0.0310 (10/0/0/10) | 0.1129±0.0453 (10/0/0/10) | heat 4 · qw 6 (of 10) · gain 40.3% | tie |
| s1584 | 0.2007±0.0012 (10/0/1/10) | 0.2009±0.0023 (10/0/1/9) | 0.2001±0.0059 (9/1/2/8) | heat 2 · qw 7 (of 9) · gain 0.9% | FLOOR (gain 0.9% < 5%) |
| s3168 | 0.1773±0.0005 (10/0/1/9) | 0.1770±0.0008 (10/0/1/10) | 0.1769±0.0008 (9/1/2/9) | heat 4 · qw 5 (of 9) · gain 0.3% | FLOOR (gain 0.3% < 5%) |
| s4400 | 0.1870±0.0005 (10/0/1/10) | 0.1872±0.0002 (10/0/1/10) | 0.1861±0.0018 (10/0/1/10) | heat 3 · qw 7 (of 10) · gain 0.7% | FLOOR (gain 0.7% < 5%) |

## task=hops · arm=softplus/t0=2 · metric=mae

| shell | gcn mean±std (n used / n pathology / n plateau / beats-const) | heat mean±std (n used / n pathology / n plateau / beats-const) | qw mean±std (n used / n pathology / n plateau / beats-const) | heat vs qw: seeds won | verdict |
|---|---|---|---|---|---|
| s264 | 0.1663±0.0124 (10/0/0/10) | 0.1419±0.0420 (10/0/1/10) | 0.1583±0.0330 (10/0/1/10) | heat 7 · qw 3 (of 10) · gain 24.9% | heat |
| s1584 | 0.2007±0.0012 (10/0/1/10) | 0.1998±0.0044 (10/0/2/8) | 0.1997±0.0040 (10/0/1/10) | heat 3 · qw 7 (of 10) · gain 1.1% | FLOOR (gain 1.1% < 5%) |
| s3168 | 0.1773±0.0005 (10/0/1/9) | 0.1770±0.0008 (10/0/1/10) | 0.1771±0.0007 (10/0/1/10) | heat 3 · qw 7 (of 10) · gain 0.3% | FLOOR (gain 0.3% < 5%) |
| s4400 | 0.1870±0.0005 (10/0/1/10) | 0.1871±0.0005 (10/0/1/10) | 0.1872±0.0001 (10/0/1/10) | heat 5 · qw 5 (of 10) · gain 0.2% | FLOOR (gain 0.2% < 5%) |

## Robustness across arms (the claim's own test)

A ranking at (task, shell) counts only if it is the SAME in every arm.

| task | shell | relu/t0=0.5 | relu/t0=2 | softplus/t0=0.5 | softplus/t0=2 | robust? |
|---|---|---|---|---|---|---|
| delay | s264 | heat | heat | qw | tie | no |
| delay | s1584 | FLOOR (gain 2.3% < 5%) | FLOOR (gain 1.2% < 5%) | FLOOR (gain 1.9% < 5%) | FLOOR (gain 1.1% < 5%) | FLOOR |
| delay | s3168 | FLOOR (gain 0.4% < 5%) | FLOOR (gain -0.0% < 5%) | FLOOR (gain 0.0% < 5%) | FLOOR (gain 0.1% < 5%) | FLOOR |
| delay | s4400 | FLOOR (gain -0.1% < 5%) | FLOOR (gain -0.1% < 5%) | FLOOR (gain -0.1% < 5%) | FLOOR (gain -0.1% < 5%) | FLOOR |
| hops | s264 | tie | heat | tie | heat | no |
| hops | s1584 | FLOOR (gain 2.8% < 5%) | FLOOR (gain 1.6% < 5%) | FLOOR (gain 0.9% < 5%) | FLOOR (gain 1.1% < 5%) | FLOOR |
| hops | s3168 | FLOOR (gain 0.6% < 5%) | FLOOR (gain 0.2% < 5%) | FLOOR (gain 0.3% < 5%) | FLOOR (gain 0.3% < 5%) | FLOOR |
| hops | s4400 | FLOOR (gain 1.0% < 5%) | FLOOR (gain 0.2% < 5%) | FLOOR (gain 0.7% < 5%) | FLOOR (gain 0.2% < 5%) | FLOOR |

## Learned propagation time t (mean over valid runs, per layer)

| task | shell | arm | heat t | qw t |
|---|---|---|---|---|
| delay | s264 | relu/t0=0.5 | [1.88, 0.05, -0.17, -0.17] | [0.77, 0.24, 0.08, 0.13] |
| delay | s264 | relu/t0=2 | [1.38, 0.42, 0.28, -0.10] | [0.80, 0.29, 0.29, 0.19] |
| delay | s264 | softplus/t0=0.5 | [1.03, 0.30, 0.20, 0.18] | [1.12, 0.65, 0.62, 0.64] |
| delay | s264 | softplus/t0=2 | [0.87, 0.47, 0.41, 0.40] | [0.82, 0.52, 0.50, 0.46] |
| delay | s1584 | relu/t0=0.5 | [1.21, 0.34, 0.07, -0.01] | [0.61, 0.40, 0.09, 0.15] |
| delay | s1584 | relu/t0=2 | [1.28, 0.12, -0.02, -0.20] | [0.81, 0.33, 0.37, 0.36] |
| delay | s1584 | softplus/t0=0.5 | [0.89, 0.24, 0.08, 0.14] | [0.68, 0.51, 0.26, 0.35] |
| delay | s1584 | softplus/t0=2 | [0.91, 0.47, 0.36, 0.35] | [1.00, 0.56, 0.53, 0.47] |
| delay | s3168 | relu/t0=0.5 | [1.41, -0.13, -0.14, -0.14] | [0.47, 0.58, 0.31, 0.12] |
| delay | s3168 | relu/t0=2 | [1.10, -0.07, -0.16, -0.16] | [0.91, 0.38, 0.27, 0.38] |
| delay | s3168 | softplus/t0=0.5 | [1.01, 0.24, 0.08, 0.09] | [0.71, 0.64, 0.20, 0.33] |
| delay | s3168 | softplus/t0=2 | [1.00, 0.43, 0.40, 0.40] | [0.98, 0.58, 0.56, 0.51] |
| delay | s4400 | relu/t0=0.5 | [1.08, 0.15, -0.16, -0.14] | [0.61, 0.52, 0.04, 0.02] |
| delay | s4400 | relu/t0=2 | [1.23, -0.04, -0.13, -0.14] | [0.93, 0.30, 0.25, 0.31] |
| delay | s4400 | softplus/t0=0.5 | [0.94, 0.30, 0.08, 0.08] | [0.77, 0.70, 0.23, 0.31] |
| delay | s4400 | softplus/t0=2 | [1.16, 0.49, 0.47, 0.42] | [0.92, 0.53, 0.51, 0.52] |
| hops | s264 | relu/t0=0.5 | [1.84, -0.15, 0.07, 0.06] | [0.82, 0.36, 0.13, 0.22] |
| hops | s264 | relu/t0=2 | [1.71, 0.71, 0.12, -0.12] | [1.05, 0.63, 0.49, 0.38] |
| hops | s264 | softplus/t0=0.5 | [1.32, 0.41, 0.25, 0.19] | [1.34, 0.87, 0.67, 0.69] |
| hops | s264 | softplus/t0=2 | [1.20, 0.70, 0.53, 0.44] | [1.02, 0.75, 0.67, 0.60] |
| hops | s1584 | relu/t0=0.5 | [1.26, 0.13, 0.08, 0.07] | [0.37, 0.43, 0.12, 0.34] |
| hops | s1584 | relu/t0=2 | [1.44, 0.29, 0.06, -0.17] | [1.00, 0.59, 0.58, 0.36] |
| hops | s1584 | softplus/t0=0.5 | [1.06, 0.20, 0.09, 0.09] | [0.72, 0.64, 0.47, 0.62] |
| hops | s1584 | softplus/t0=2 | [1.24, 0.53, 0.55, 0.42] | [1.03, 0.54, 0.51, 0.51] |
| hops | s3168 | relu/t0=0.5 | [1.29, -0.13, -0.15, -0.15] | [0.58, 0.75, 0.12, 0.09] |
| hops | s3168 | relu/t0=2 | [1.32, -0.05, -0.15, -0.17] | [0.94, 0.29, 0.32, 0.38] |
| hops | s3168 | softplus/t0=0.5 | [1.07, 0.24, 0.09, 0.08] | [0.76, 0.71, 0.31, 0.30] |
| hops | s3168 | softplus/t0=2 | [1.19, 0.46, 0.44, 0.39] | [1.00, 0.56, 0.54, 0.51] |
| hops | s4400 | relu/t0=0.5 | [1.26, -0.11, -0.15, -0.15] | [0.42, 0.78, 0.17, 0.44] |
| hops | s4400 | relu/t0=2 | [1.39, 0.01, -0.12, -0.12] | [0.93, 0.45, 0.26, 0.28] |
| hops | s4400 | softplus/t0=0.5 | [1.09, 0.24, 0.09, 0.09] | [0.73, 0.74, 0.48, 0.56] |
| hops | s4400 | softplus/t0=2 | [1.22, 0.49, 0.48, 0.43] | [0.92, 0.54, 0.52, 0.52] |
