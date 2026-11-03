#!/usr/bin/env python3
"""crowdstop Founder Team: the pricing lead's price range.

Reads four price answers per person (the buyer panel's answers folder, or a
spreadsheet saved as CSV with columns named too_cheap, good_value,
getting_expensive and too_expensive) and
finds where the answer curves cross (the Van Westendorp method):

  lowest acceptable   where "too cheap" meets "not a bargain"
  highest acceptable  where "too expensive" meets "not getting expensive"
  fewest object       where "too cheap" meets "too expensive"
  balance point       where "a bargain" meets "getting expensive"

Standard library only.

    python3 price_range.py buyers/answers [--price 45] [--out pricing.md]
    python3 price_range.py survey.csv --price 45
"""
import argparse
import csv
import glob
import json
import os
import sys

KEYS = ("too_cheap", "good_value", "getting_expensive", "too_expensive")
MIN_PEOPLE = 10


class InputError(ValueError):
    pass


def read_answers(path):
    rows = []
    if os.path.isdir(path):
        for fp in sorted(glob.glob(os.path.join(path, "*.json"))):
            with open(fp, encoding="utf-8") as f:
                a = json.load(f)
            rows.append([a.get(k) for k in KEYS])
    else:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append([r.get(k) for k in KEYS])
    clean = []
    for r in rows:
        try:
            vals = [float(v) for v in r]
        except (TypeError, ValueError):
            continue
        if all(vals[i] < vals[i + 1] for i in range(3)) and vals[0] >= 0:
            clean.append(vals)
    if len(clean) < MIN_PEOPLE:
        raise InputError("need at least %d complete, rising sets of four prices; found %d"
                         % (MIN_PEOPLE, len(clean)))
    return clean


def curves(rows, price):
    """Share of people for each statement at a given price."""
    n = len(rows)
    too_cheap = sum(1 for r in rows if r[0] >= price) / n        # falls as price rises
    bargain = sum(1 for r in rows if r[1] >= price) / n          # falls
    expensive = sum(1 for r in rows if r[2] <= price) / n        # rises
    too_expensive = sum(1 for r in rows if r[3] <= price) / n    # rises
    return too_cheap, bargain, expensive, too_expensive


def crossing(rows, grid, falling, rising):
    """The price at which the upward curve catches the downward one, read
    between grid points where needed."""
    prev = None
    for i, p in enumerate(grid):
        c = curves(rows, p)
        diff = rising(c) - falling(c)
        if diff > 0:
            if prev is None:
                return p
            p0, d0 = prev
            return p0 + (p - p0) * (0 - d0) / (diff - d0)
        if diff == 0:
            # the curves touch over a stretch (often both at zero between two
            # groups of answers): take the middle of that stretch
            end = p
            for q in grid[i + 1:]:
                cq = curves(rows, q)
                if rising(cq) - falling(cq) != 0:
                    break
                end = q
            return (p + end) / 2
        prev = (p, diff)
    return None


def analyse(rows, steps=400):
    lo = min(r[0] for r in rows)
    hi = max(r[3] for r in rows)
    grid = [lo + (hi - lo) * i / steps for i in range(steps + 1)]
    points = {
        "lowest_acceptable": crossing(rows, grid, lambda c: c[0], lambda c: 1 - c[1]),
        "highest_acceptable": crossing(rows, grid, lambda c: 1 - c[2], lambda c: c[3]),
        "fewest_object": crossing(rows, grid, lambda c: c[0], lambda c: c[3]),
        "balance_point": crossing(rows, grid, lambda c: c[1], lambda c: c[2]),
    }
    return {k: (round(v, 2) if v is not None else None) for k, v in points.items()}


def report(rows, pts, price=None, currency="£"):
    def m(v):
        return "%s%.2f" % (currency, v) if v is not None else "not found"
    lines = ["# Pricing: the acceptable range", "",
             "From %d people's four price answers." % len(rows), "",
             "| Point | Price | What it means |", "| --- | --- | --- |",
             "| Lowest acceptable | %s | Below this, too many doubt the quality |" % m(pts["lowest_acceptable"]),
             "| Fewest object | %s | The fewest people call it too cheap or too expensive |" % m(pts["fewest_object"]),
             "| Balance point | %s | Equal numbers see a bargain and see it as pricey |" % m(pts["balance_point"]),
             "| Highest acceptable | %s | Above this, too many say it's too expensive |" % m(pts["highest_acceptable"]),
             ""]
    lo, hi = pts["lowest_acceptable"], pts["highest_acceptable"]
    if price is not None:
        tc, bg, ex, te = curves(rows, price)
        if lo is not None and hi is not None:
            where = ("inside the range" if lo <= price <= hi
                     else "below the range" if price < lo else "above the range")
        else:
            where = "not placed (the range couldn't be found)"
        lines += ["**The planned price, %s, is %s.** At that price %d%% would call it too cheap, "
                  "%d%% a bargain, %d%% getting expensive and %d%% too expensive."
                  % (m(price), where, round(tc * 100), round(bg * 100), round(ex * 100), round(te * 100)), ""]
    lines += ["If these answers came from simulated buyers, treat the range as a first guess and "
              "test it with real people.", "",
              "Made with the crowdstop Founder Team · crowdstop.com", ""]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="The acceptable price range from four price answers per person")
    p.add_argument("source", help="an answers folder of JSON files, or a CSV")
    p.add_argument("--price", type=float, help="the planned price, to place it in the range")
    p.add_argument("--currency", default="£")
    p.add_argument("--out")
    a = p.parse_args(argv)
    try:
        rows = read_answers(a.source)
    except (InputError, OSError, json.JSONDecodeError) as e:
        print("Can't work out the range: %s" % e, file=sys.stderr)
        return 2
    pts = analyse(rows)
    text = report(rows, pts, a.price, a.currency)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
