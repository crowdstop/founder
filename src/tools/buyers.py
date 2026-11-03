#!/usr/bin/env python3
"""crowdstop Founder Team: the buyer panel's admin.

deal   Deals buyer cards from customer.json (the same seed always gives the
       same panel) and writes one brief per buyer.
tally  Checks every answer and counts them: the buy rate overall and by each
       way buyers differ, the top reasons, and what would change minds.

It never answers for a buyer. Standard library only.

    python3 buyers.py deal --customer customer.json --pitch pitch.md --n 100 --seed 1 --out buyers
    python3 buyers.py tally --dir buyers
"""
import argparse
import collections
import json
import os
import random
import sys

DECISIONS = ("yes", "maybe", "no")
PRICE_KEYS = ("too_cheap", "good_value", "getting_expensive", "too_expensive")
ANSWER_KEYS = ("id", "decision", "reason", "reason_tag", "what_would_change_my_mind") + PRICE_KEYS


class InputError(ValueError):
    pass


def read_customer(path):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    for key in ("segment", "age_range", "varies_by"):
        if key not in c:
            raise InputError("customer.json needs '%s'" % key)
    lo, hi = c["age_range"]
    if not (isinstance(lo, int) and isinstance(hi, int) and 16 <= lo <= hi <= 100):
        raise InputError("age_range must be two whole numbers, e.g. [24, 55]")
    if not c["varies_by"] or not all(isinstance(v, list) and v for v in c["varies_by"].values()):
        raise InputError("varies_by must list at least one way buyers differ, each with options")
    return c


def deal(customer, n, seed):
    """Spread each trait's options evenly across the panel, then shuffle each
    trait independently, so every option is represented and the mix varies."""
    rng = random.Random(seed)
    traits = {}
    for trait, options in customer["varies_by"].items():
        column = [options[i % len(options)] for i in range(n)]
        rng.shuffle(column)
        traits[trait] = column
    lo, hi = customer["age_range"]
    cards = []
    for i in range(n):
        card = {"id": "buyer-%03d" % (i + 1), "age": rng.randint(lo, hi)}
        for trait in customer["varies_by"]:
            card[trait] = traits[trait][i]
        cards.append(card)
    return cards


BRIEF = """# You are {id}

You're one real person, not a marketer and not an assistant. Read who you are,
then the pitch, and decide honestly whether you'd buy it. Most pitches get a no.
Saying no is a good answer if it's true for you.

## Who you are

- Part of this group: {segment}
- Where: {location}
- Age: {age}
{traits}

## The pitch

{pitch}

## Your answer

Save it as `answers/{id}.json`, exactly this shape:

```json
{{
  "id": "{id}",
  "decision": "yes | maybe | no",
  "reason": "In your own words, one or two sentences.",
  "reason_tag": "a short label for the main reason, e.g. too expensive",
  "what_would_change_my_mind": "One sentence, or an empty string.",
  "too_cheap": 0,
  "good_value": 0,
  "getting_expensive": 0,
  "too_expensive": 0
}}
```

The four prices are in the pitch's currency: so cheap you'd doubt it; a bargain;
starting to feel expensive; too expensive to consider. Each one higher than the
one before.
"""


def write_panel(customer, pitch, cards, out):
    os.makedirs(os.path.join(out, "briefs"), exist_ok=True)
    os.makedirs(os.path.join(out, "answers"), exist_ok=True)
    with open(os.path.join(out, "cards.json"), "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2)
    for card in cards:
        traits = "\n".join("- %s: %s" % (k.replace("_", " ").capitalize(), v)
                           for k, v in card.items() if k not in ("id", "age"))
        text = BRIEF.format(id=card["id"], segment=customer["segment"],
                            location=customer.get("location", "not stated"),
                            age=card["age"], traits=traits, pitch=pitch.strip())
        with open(os.path.join(out, "briefs", card["id"] + ".md"), "w", encoding="utf-8") as f:
            f.write(text)


def check_answer(a, expected_id):
    problems = []
    for k in ANSWER_KEYS:
        if k not in a:
            problems.append("missing '%s'" % k)
    if problems:
        return problems
    if a["id"] != expected_id:
        problems.append("id is '%s', file is for '%s'" % (a["id"], expected_id))
    if a["decision"] not in DECISIONS:
        problems.append("decision must be yes, maybe or no")
    prices = [a[k] for k in PRICE_KEYS]
    if not all(isinstance(p, (int, float)) and p >= 0 for p in prices):
        problems.append("the four prices must be numbers")
    elif not all(prices[i] < prices[i + 1] for i in range(3)):
        problems.append("the four prices must rise: too cheap < good value < getting expensive < too expensive")
    if not str(a["reason"]).strip():
        problems.append("reason is empty")
    return problems


def tally(folder):
    with open(os.path.join(folder, "cards.json"), encoding="utf-8") as f:
        cards = json.load(f)
    answers, missing, invalid = {}, [], {}
    for card in cards:
        path = os.path.join(folder, "answers", card["id"] + ".json")
        if not os.path.exists(path):
            missing.append(card["id"])
            continue
        try:
            with open(path, encoding="utf-8") as f:
                a = json.load(f)
        except json.JSONDecodeError as e:
            invalid[card["id"]] = ["not valid JSON: %s" % e]
            continue
        problems = check_answer(a, card["id"])
        if problems:
            invalid[card["id"]] = problems
        else:
            answers[card["id"]] = a

    counted = len(answers)
    overall = collections.Counter(a["decision"] for a in answers.values())
    by_trait = {}
    traits = [k for k in (cards[0] if cards else {}) if k not in ("id", "age")]
    for trait in traits:
        groups = collections.defaultdict(collections.Counter)
        for card in cards:
            if card["id"] in answers:
                groups[card[trait]][answers[card["id"]]["decision"]] += 1
        by_trait[trait] = {opt: dict(c) for opt, c in groups.items()}
    reasons = {d: collections.Counter(a["reason_tag"].strip().lower()
                                      for a in answers.values() if a["decision"] == d)
               for d in DECISIONS}
    flips = [a["what_would_change_my_mind"].strip() for a in answers.values()
             if a["decision"] != "yes" and a["what_would_change_my_mind"].strip()]
    return {
        "panel_size": len(cards), "counted": counted,
        "missing": missing, "invalid": invalid,
        "decisions": {d: overall.get(d, 0) for d in DECISIONS},
        "yes_rate": round(overall.get("yes", 0) / counted, 4) if counted else 0.0,
        "by_trait": by_trait,
        "top_reasons": {d: reasons[d].most_common(5) for d in DECISIONS},
        "would_change_minds": flips[:15],
        "quotes": {d: [answers[k]["reason"] for k in sorted(answers) if answers[k]["decision"] == d][:3]
                   for d in DECISIONS},
    }


def pct(part, whole):
    return "%d%%" % round(100 * part / whole) if whole else "n/a"


def report(r):
    n = r["counted"]
    lines = ["# The buyer panel", "",
             "Simulated buyers, not customers. Read the yes rate as a ceiling and confirm it with real people.", ""]
    if r["missing"] or r["invalid"]:
        lines += ["**Not complete:** %d of %d answers counted. Missing: %d. Invalid: %d."
                  % (n, r["panel_size"], len(r["missing"]), len(r["invalid"])), ""]
        for bid, probs in sorted(r["invalid"].items()):
            lines.append("- %s: %s" % (bid, "; ".join(probs)))
        lines.append("")
    d = r["decisions"]
    lines += ["| Decision | Buyers | Share |", "| --- | --- | --- |"]
    for k in DECISIONS:
        lines.append("| %s | %d | %s |" % (k.capitalize(), d[k], pct(d[k], n)))
    lines += ["", "## Who says yes", ""]
    for trait, groups in r["by_trait"].items():
        lines += ["**%s**" % trait.replace("_", " ").capitalize(), "",
                  "| | Yes | Maybe | No | Yes rate |", "| --- | --- | --- | --- | --- |"]
        rows = sorted(groups.items(), key=lambda kv: -(kv[1].get("yes", 0) / max(1, sum(kv[1].values()))))
        for opt, c in rows:
            total = sum(c.values())
            lines.append("| %s | %d | %d | %d | %s |" % (opt, c.get("yes", 0), c.get("maybe", 0),
                                                        c.get("no", 0), pct(c.get("yes", 0), total)))
        lines.append("")
    lines += ["## Why", ""]
    for k in DECISIONS:
        if r["top_reasons"][k]:
            lines.append("**%s:** " % k.capitalize() + ", ".join("%s (%d)" % (t, c) for t, c in r["top_reasons"][k]))
            for q in r["quotes"][k]:
                lines.append("> %s" % q)
            lines.append("")
    if r["would_change_minds"]:
        lines += ["## What would change their minds", ""] + ["- " + s for s in r["would_change_minds"]] + [""]
    lines += ["Made with the crowdstop Founder Team · crowdstop.com", ""]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Deal and tally a simulated buyer panel")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("deal")
    d.add_argument("--customer", required=True)
    d.add_argument("--pitch", required=True)
    d.add_argument("--n", type=int, default=100)
    d.add_argument("--seed", type=int, default=1)
    d.add_argument("--out", required=True)
    t = sub.add_parser("tally")
    t.add_argument("--dir", required=True)
    t.add_argument("--out", help="defaults to buyers.md beside the panel folder")
    a = p.parse_args(argv)
    try:
        if a.cmd == "deal":
            if not 1 <= a.n <= 500:
                raise InputError("--n must be between 1 and 500")
            customer = read_customer(a.customer)
            with open(a.pitch, encoding="utf-8") as f:
                pitch = f.read()
            if not pitch.strip():
                raise InputError("the pitch is empty")
            cards = deal(customer, a.n, a.seed)
            write_panel(customer, pitch, cards, a.out)
            print("Dealt %d buyers into %s. Each answers its brief into answers/." % (a.n, a.out))
        else:
            r = tally(a.dir)
            with open(os.path.join(a.dir, "results.json"), "w", encoding="utf-8") as f:
                json.dump(r, f, indent=2)
            out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.dir)), "buyers.md")
            with open(out, "w", encoding="utf-8") as f:
                f.write(report(r))
            print("Counted %d of %d. Yes rate %s. Written to %s"
                  % (r["counted"], r["panel_size"], pct(r["decisions"]["yes"], r["counted"]), out))
    except (InputError, OSError, json.JSONDecodeError, ValueError) as e:
        print("Can't run the panel: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
