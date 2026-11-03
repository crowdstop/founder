# crowdstop Founder Team

The team you can't afford to hire yet, as eleven free Claude skills. Put your
business idea in front of them before you put your savings into it.

Free to use. You don't need an account with us, an API key or any connections.

They work like a small company. A board pressure-tests the idea. A scout maps who
you're up against. A hundred simulated buyers say whether they'd pay, and why
not. Specialists then work out the price, the offer and the money, plan the
marketing, the brand and the day-to-day running, and get you to launch day. Last
of all, everything is pulled into one business plan, and the numbers decide its
verdict.

## Getting it

**Claude (claude.ai or the app):** in `dist/` there's a zip for each skill, plus
`crowdstop-founder-team-all.zip` with all eleven inside. Upload each skill's zip
in Claude's Settings, under Skills, as it is (no unzipping).

**Claude Code, as a plugin** (all eleven in one go):

```
/plugin marketplace add crowdstop/founder
/plugin install crowdstop-founder-team@crowdstop
```

**Claude Code, as loose skills:**

```bash
git clone https://github.com/crowdstop/founder.git
cp -r founder/skills/crowdstop-* ~/.claude/skills/
```

**Anything else:** paste one `SKILL.md` into the start of a conversation with an
AI and it will act as that specialist. Without Claude Code there are no helper
agents and no Python, so the maths is done by hand, but each step still works.

The Python tools run on any Python from 3.8 up, with no extra packages.

## Who's on the team

| Skill | Role | Its job |
| --- | --- | --- |
| `crowdstop-board` | The board | Writes down your idea, then three board members look at it through three ideas from well-known business books (how strong the offer is, how hard it is to copy, how focused the product is). Each gives a score, the thing most likely to sink it, and a vote. |
| `crowdstop-competitors` | Competitor scout | Finds the businesses, alternatives and DIY workarounds your customers use now, with their prices, their own headlines and their customers' complaints, each one linked to its source. |
| `crowdstop-buyers` | Buyer panel | Creates 100 made-up buyers from your description of the customer, all different in money, habits and doubts, has each one decide, and counts the yeses, the noes and the reasons. |
| `crowdstop-pricing` | Pricing lead | Reads the panel's views on price to find what people will accept, then weighs your price against that, the competition and your costs. |
| `crowdstop-offer` | Offer builder | Shapes what you're selling around the panel's doubts (what's included, a guarantee, a reason to act now if there's a true one, a name) and checks it on a fresh, smaller panel. |
| `crowdstop-money` | Money lead | Shows what you keep from each sale, how many sales cover the bills, your first year month by month, how much cash you'll need, when you get it back, and what happens if things go worse. |
| `crowdstop-marketing` | Marketing lead | Your position in one sentence, the few places your buyers really pay attention, a day-by-day first month, ten opening lines, and the most you can spend to win each customer. |
| `crowdstop-brand` | Brand lead | Name ideas and the checks to run on them, a promise, a voice, and a brief for how it should look. When the brief is ready, crowdstop can turn it into the real thing. |
| `crowdstop-ops` | Operations lead | Who supplies what, who does the work, routines for a normal day, the software, the permissions to check and what could go wrong, with any new costs sent back to the money lead. |
| `crowdstop-launch` | Launch lead | A small test with real money first, then a week-by-week road to launch day, a timed plan for the day itself, and the month after. |
| `crowdstop-plan` | Business plan | Collects everything into one plan and works out the verdict from the numbers: Profitable, Not yet or Incomplete. |

## Running it

Start at the top. Each skill saves its notes in a `founder/` folder and the
later ones read them:

```
board > competitors > buyers > pricing > offer > money > marketing > brand > ops > launch > plan
```

Any skill also works alone. For a quick read on an idea, run the board and then a
20-buyer panel.

**Worked example: Kiln Room** (invented), beginner pottery classes in Leeds at
£45 a place. Its inputs are in `src/examples/`, so you can try the tools on it.
Here's what the money lead gives back from those inputs:

- £37.60 left from each £45 place once clay, firing and card fees are paid
- 60 places a month to cover the £2,234 of monthly bills
- a 53% margin at the planned 160 places a month
- £6,518 of cash needed at the low point, earned back in month 5

The board, scout and panel would come first in real use: does Leeds want this,
who else runs classes and for how much, and which kinds of people say yes. The
plan at the end only says Profitable if every one of its tests passes.

## The tools

Four small Python scripts, using only what comes with Python, and none of them
goes online.

| Script | Used by | What it does |
| --- | --- | --- |
| `money.py` | money lead | Takes `numbers.json` and produces the money report. Refuses to run if an input is missing rather than guessing it. |
| `buyers.py` | buyer panel, offer builder | `deal` creates the buyers (the same seed number always gives the same panel) and a brief for each; `tally` checks the answers and counts them. It never fills in an answer itself. |
| `price_range.py` | pricing lead | Finds the acceptable price range from four price questions per person (the Van Westendorp method), from the panel or from a real survey saved as CSV. |
| `verdict.py` | business plan | Puts the plan together and works out the verdict. |

```bash
python3 skills/crowdstop-money/tools/money.py founder/numbers.json --out founder/money.md --json founder/money.json
python3 skills/crowdstop-buyers/tools/buyers.py deal --customer founder/customer.json --pitch founder/pitch.md --n 100 --out founder/buyers
python3 skills/crowdstop-buyers/tools/buyers.py tally --dir founder/buyers
python3 skills/crowdstop-pricing/tools/price_range.py founder/buyers/answers --price 45
python3 skills/crowdstop-plan/tools/verdict.py --dir founder
python3 -m unittest discover -s tests -v
```

## Please read

**About the board.** Its three viewpoints are our own short summaries of ideas
from three books: *$100M Offers* (Alex Hormozi), *Zero to One* (Peter Thiel and
Blake Masters) and *Steve Jobs* (Walter Isaacson). The authors and subjects have
nothing to do with this project. The board doesn't pretend to be them or quote
them.

**About the buyers.** They're simulated, not real. They're good at surfacing
doubts and the right words quickly, and bad at predicting sales: AI buyers are
more generous than real ones. Treat their yes rate as the best case, check
anything important with real people (the launch lead's first step is exactly
that), and never present their answers as reviews.

**About the numbers.** They're only as good as what you put in. Estimates are
labelled. Get real quotes from suppliers, and talk to an accountant about tax,
VAT and how to set up.

**About research.** Facts come from public pages, with links. Nothing is
invented, and sites are read the way a person would read them.

**Not professional advice.** This isn't financial, legal or tax advice. The rules
on licences, trade marks and advertising depend on where you trade; the skills
point you to what to check, and a professional should confirm it.

## What's in the repo

```
skills/crowdstop-*/   the eleven skills as installed (generated from src/)
src/roles/            each specialist's instructions
src/shared.md         the rules all eleven follow
src/tools/            the four Python scripts
src/examples/         Kiln Room's example inputs

build.py              regenerates skills/ and dist/ from src/
dist/                 the zips for uploading to Claude
tests/                tests for the scripts
```

Change things in `src/`, then run `python3 build.py`.

## About crowdstop

crowdstop is a UK studio that turns a founder's brief into a finished brand in 48
hours: logo, brand guidelines, colours and type, a one-page website and a social
kit, at a one-off price, with every file yours to keep. When the brand lead's brief is
ready, choose a package at crowdstop.com and we take it from there.
[crowdstop.com](https://crowdstop.com) · [@crowdstop](https://instagram.com/crowdstop)

## Licence

MIT, © 2026 crowdstop. Use it, change it and share it.
