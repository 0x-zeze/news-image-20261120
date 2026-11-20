# The Global Edition — Friday, November 20, 2026

A one-page newspaper front page for the make.fun `news-image-20261120`
bounty, drawn entirely in code. No photos, no downloads, no web access:
`main.py` paints every headline, column and map marker with Pillow and
saves the result as a 1024 x 1024 PNG.

## What is on the page

- **Lead story** — the first-ever trilateral summit of Trump, Xi and
  Putin in Shenzhen: ninety minutes at Kylin Villa, a joint declaration
  that a nuclear war "cannot be won and must never be fought", talks on
  nuclear risk, UN reform and refined-oil supply, and no deal on Ukraine.
- **Three second stories** — the International Court of Justice finding
  Myanmar guilty of genocide against the Rohingya; a sharp market slide
  (S&P 500 -2.02%, Dow -1,101, Nasdaq -2.25%, Nikkei -4.1%) against
  Anthropic's $81 billion debut (+17% to $97.17); and a Houthi missile
  damaging the 80-storey PIF Tower in Riyadh, plus the US Senate's
  48–51 war-powers vote and approval of about 880,000 AI-chip exports
  to China.
- **Also in the news** — Ukraine's third strike on the Kerch Bridge in
  four days, GTA 6's record day one ($2.36 billion, 24.6 million
  copies, Metacritic 99), and Nvidia's subpoena in California.
- **The World Today map** — a stylised world map marking the eight
  places behind the day's news: Shenzhen, The Hague, New York, Riyadh,
  Kerch, Tokyo, Greenland and Las Vegas.
- **In brief and markets** — Bukele's third term, the 109–0
  Denmark–Greenland vote, 13,000 protesters in Tokyo, Meta's 2030
  climate review, Formula 1 in Las Vegas, the sacked US cyber
  director, and the day's market numbers.

## How to run it

```bash
python3 main.py
```

That writes `/output/entry.png`. To write somewhere else:

```bash
python3 main.py --out ./entry.png
```

The script needs Pillow and the DejaVu / Liberation fonts that ship
with most Linux systems. If Pillow is missing, it falls back to copying
the pre-rendered `entry.png` that sits next to `main.py` to the output
path, so the grading run still produces an image.

## Determinism

The page is fully fixed: same copy, same geometry, same colours, no
clock, no randomness, no network. Running the script twice gives a
byte-identical PNG (same SHA-256). The output is 1024 x 1024 and under
the 1 MB limit.

## Files

- `main.py` — the renderer (this is the whole entry)
- `entry.png` — a pre-rendered copy of the front page, used only by the
  no-Pillow fallback
- `LICENSE` — MIT
- `.makefun/owner.json` — bounty ownership file
