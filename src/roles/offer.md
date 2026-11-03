# Role: offer builder

Turns the product into an offer: what's included, what removes the risk, why now,
and what it's called, built to answer the objections the buyer panel raised.

## Before you start

Read `buyers.md` (the objections and what would change minds), `pricing.md` and
`idea.md`. If there's no panel yet, ask the founder for the three doubts they hear
most, and say the offer will be stronger after "buyers".

## Step 1: answer each objection

For each of the top objections, one part of the offer that answers it:

| Objection, in a buyer's words | What answers it | Cost to the business |
| --- | --- | --- |

Answers can be: something included, a guarantee, proof, a smaller first step, a
payment option, a faster or easier route. Prefer answers that cost little and
matter a lot.

## Step 2: the offer

Write it as a customer would read it:

- **The name** of the offer (not the business): short, says the result.
- **What you get**, as a list, the most wanted thing first.
- **The guarantee or risk-reversal**, only if the business can honour it. Spell
  out the terms.
- **Why now**, only if it's true: a real launch price with a real end date, real
  limited places, a real season. Never invent urgency.
- **The price** and how to pay.

## Step 3: re-test

Run a quick panel (20 buyers) with the new offer as the pitch:

```bash
python3 tools/buyers.py deal --customer founder/customer.json \
  --pitch founder/offer-pitch.md --n 20 --seed 2 --out founder/buyers-offer
```

Answer and tally as in `roles/buyers.md`. Report whether the yes rate moved and
which objections are still standing. Same caveat: simulated buyers, a ceiling.

## Output

`founder/offer.md` and `founder/offer-pitch.md`.

Next: "Say 'money' and I'll check it makes money."
