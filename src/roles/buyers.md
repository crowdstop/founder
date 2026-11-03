# Role: the buyer panel

A panel of simulated buyers (100 by default, 20 for a quick read), each with their
own circumstances, habits and doubts. Each one hears the pitch and decides. Back
comes who buys, who doesn't, why, and what would change their mind.

This is research, not demand. It's fast and cheap for finding objections and the
best first audience. It isn't a sales forecast. AI buyers tend to be kinder than
real ones, so take the buy rate as the best case, and test with real people (the
launch lead starts with exactly that).

## Step 1: the customer and the pitch

From `idea.md` and `competitors.md`, write two files with the founder:

`founder/customer.json`: who the buyers are and how they differ. Use the
shape in `examples/customer.json`: a segment description, a location, an age
range, and lists of the ways buyers vary (income band, how often they have the
problem, what they use now, how they decide, a likely doubt). Ask the founder to
correct it; the panel is only as good as this file.

`founder/pitch.md`: the words a buyer would meet: the offer in a few
lines, the price, how to buy. No hype; the same words a real ad or page would
use.

## Step 2: deal the panel

```bash
python3 tools/buyers.py deal --customer founder/customer.json \
  --pitch founder/pitch.md --n 100 --seed 1 --out founder/buyers
```

This writes one card per buyer (`cards.json`) and one brief per buyer
(`briefs/buyer-001.md` ...). The same seed always deals the same panel.

Without code, deal the cards by hand: for each buyer pick one value from each
list, spread evenly, and write the brief yourself.

## Step 3: each buyer decides

Each buyer reads only their own brief and answers as that person, honestly,
including saying no. Where you can start sub-agents, give each buyer (or each
batch of ten) its own agent. Otherwise answer one buyer at a time and keep each
separate.

Each answer is saved as `founder/buyers/answers/buyer-001.json`:

```json
{
  "id": "buyer-001",
  "decision": "yes | maybe | no",
  "reason": "In their own words, one or two sentences.",
  "reason_tag": "short label, e.g. too expensive",
  "what_would_change_my_mind": "One sentence, or empty.",
  "too_cheap": 10,
  "good_value": 25,
  "getting_expensive": 45,
  "too_expensive": 70
}
```

The four prices answer: at what price would this be so cheap you'd doubt it; a
bargain; starting to feel expensive; too expensive to consider. They feed the
pricing lead.

## Step 4: the tally

```bash
python3 tools/buyers.py tally --dir founder/buyers
```

This checks every answer, then writes `founder/buyers.md` and
`founder/buyers/results.json`: the buy rate (yes, maybe, no), the buy rate by
each way buyers differ (which shows the best first audience), the top reasons for
yes and for no with counts, and what would change minds. The tool never answers
for a buyer; if answers are missing it says how many.

## Step 5: what it means

Add to `buyers.md`, in plain words:

1. The best first audience: the group most likely to buy, and how big the
   difference is.
2. The three objections to answer, with a buyer's words for each.
3. What would turn maybes into yeses.
4. A reminder that this is simulated, and what real test would confirm it.

Next: "Say 'pricing' and I'll work out the price people accept."
