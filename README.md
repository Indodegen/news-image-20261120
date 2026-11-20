# The World Today — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Indodegen/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Indodegen/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A make.fun bounty entry for **news-image-20261120**: sum up 20 November's
world news in one image. Bounty page:
[Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120).

`main.py` is a Python standard-library-only program (no PIL, no network,
no API keys). It draws a 1024×1024 newspaper front-page infographic and
writes it as a PNG. Every glyph comes from a hand-written 5×7 bitmap font
(uppercase A–Z, digits 0–9 and punctuation), scaled by integer factors,
and every icon (the three summit flags, scales of justice, cyclone
spiral, suspension bridge, oil tanker, globe with a crossed-out oil
drop) is drawn from geometric shapes in code. The PNG encoder is pure
stdlib too (`zlib` + `struct`, RGB, no interlace).

Running the program twice produces byte-identical PNG output: there is no
randomness and no timestamp anywhere in the image or the file.

## How to run

```sh
python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output` when the variable is not set).

## The stories covered

1. **Trump, Xi and Putin meet in China** — The first-ever three-way
   summit puts nuclear arms, energy security and the wars in Ukraine
   and the Gulf on the table.
2. **Myanmar guilty of genocide** — The world court rules the 2017
   crackdown on the Rohingya was genocide. The verdict cannot be
   appealed.
3. **Cyclone Akvan makes landfall** — The storm crosses India's east
   coast as 80,000 flee Odisha and Andhra Pradesh.
4. **Ukraine hits the Crimean Bridge** — Third strike on the bridge
   this week. Russian blasts damage embassies in Kyiv.
5. **Iran widens Gulf attacks** — Tankers and Gulf states hit. The
   energy watchdog calls it a historic threat.
6. **COP31 draft drops fossil fuels** — Climate talks in Türkiye cut
   the reference to ending fossil fuels from the draft deal.

## Layout

- Navy masthead with the date set large: **FRIDAY, 20 NOVEMBER 2026**
- Lead story panel (the Beijing summit) with the three flags drawn
  in code: USA, China, Russia
- Four stories in a 2×2 grid, each with its own drawn icon
- Wide bottom row for the COP31 story
- Footer crediting reports published on 20 November 2026

## License

MIT — see `LICENSE`.
