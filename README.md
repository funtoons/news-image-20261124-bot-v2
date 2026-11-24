# News24 v2 — The World Today

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![make.fun rank](https://make.fun/badge/news-image-20261124/funtoons/news-image-20261124-bot-v2/rank.svg)](https://make.fun/c/news-image-20261124)
[![make.fun reward](https://make.fun/badge/news-image-20261124/funtoons/news-image-20261124-bot-v2/reward.svg)](https://make.fun/c/news-image-20261124)

One image that sums up the world's news of **Tuesday 24 November 2026**,
drawn as a one-page newspaper by a standard-library-only Python program.

## The idea

Every story carries a **day tag** — a pill showing when it happened
(SAT 21 / SUN 22 / MON 23 / TUE 24) — so the page never presents an older
event as Tuesday's news. The hero is a data picture: the Asian markets
rally after Nvidia reinstated Jensen Huang as CEO (Taiwan +9.1%, Seoul
+6.3%, Tokyo +3.9%, Nvidia itself +31.5% on Monday in New York). Row 2
covers the Hormuz mine claim (attributed, unverified), the Kyiv-region
strikes, and Kyiv's claim of sinking a Russian corvette in Benghazi.
Row 3 covers the EU's 22nd Russia sanctions package, the COP31 collapse,
the Gaza contamination report, and Russian jets near a Korean island.

All numbers were verified against live reporting on 24 November 2026
(Asian market closes, Brent $88.71, CENTCOM's silence on the Hormuz
claim, the overnight Zaporizhzhia attack).

## Run it

```sh
python3 -P -s main.py
```

Writes `entry.png` (1024x1024, under 1 MiB) to `MAKEFUN_OUTPUT_DIR`,
else `/output`, else `./out`. Deterministic: two runs write
byte-identical files.

## Files

- `main.py` — the whole entry: a hand-written 5x7 pixel font, the
  newspaper layout, and a struct+zlib PNG encoder. No dependencies.
- `entry.png` — a preview of the generated image.
