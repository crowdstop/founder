# Role: business plan

Brings the team's work into one business plan, with a verdict worked out from the
numbers, not written to please.

## Step 1: compile

```bash
python3 tools/verdict.py --dir founder --out founder/business-plan.md
```

It reads the team's files, checks what's missing, works out the verdict and
assembles the plan. Without code, do the same by hand, using the rules below.

## The verdict

Worked out, never chosen:

- **Profitable:** each sale earns money, the first 12 months end in profit, break-even
  is reachable with the capacity the business has, and a quarter or more of the
  buyer panel said yes.
- **Not yet:** the numbers exist but at least one of those fails. The plan names
  which, by how much, and the change that would fix it.
- **Incomplete:** the money numbers or the buyer panel are missing. The plan says
  which role to run.

A "Profitable" from simulated buyers still needs the real test in `launch.md`. Say so
under the verdict.

## Step 2: the plan

`founder/business-plan.md`, in this order, each section a short summary of the
team's file with the key numbers:

1. **The verdict** and the one-line reason.
2. **The business** (from `idea.md`) and the board's view.
3. **The market:** competitors and the gap.
4. **The customer:** the panel's best audience and objections.
5. **The offer and the price.**
6. **The money:** what each sale leaves, break-even, year one, cash needed.
7. **Marketing:** positioning, channels, the first-month campaign.
8. **The brand:** name, promise, voice, and whether the look is done.
9. **Operations:** suppliers, the team, routines, permits and the main risks.
10. **The launch:** the real test and the countdown.
11. **Next steps:** the five things to do this fortnight.
12. **What this plan rests on:** the main assumptions and which ones are estimates.

Not financial, legal or tax advice.
