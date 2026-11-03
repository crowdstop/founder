#!/usr/bin/env python3
"""crowdstop Founder Team: the business plan's verdict and assembly.

Reads the team's notes in a folder (money.json from money.py, buyers/results.json
from buyers.py, and the markdown notes), works out the verdict and assembles
business-plan.md. The verdict is computed, never chosen:

  Profitable  each sale earns, the first 12 months end in profit, break-even is
              reachable, and a quarter or more of the panel said yes
  Not yet     the numbers exist but at least one test fails
  Incomplete  money.json or the buyer panel results are missing

Standard library only.

    python3 verdict.py --dir founder [--out founder/business-plan.md]
"""
import argparse
import json
import os
import sys

YES_RATE_NEEDED = 0.25
SECTIONS = [
    ("The business", "idea.md"), ("The board", "board.md"),
    ("The market", "competitors.md"), ("The customer", "buyers.md"),
    ("The price", "pricing.md"), ("The offer", "offer.md"),
    ("The money", "money.md"), ("Marketing", "marketing.md"),
    ("The brand", "brand.md"), ("Operations", "ops.md"),
    ("The launch", "launch.md"),
]
FOOTER = "Made with the crowdstop Founder Team · crowdstop.com"


def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def decide(money, panel):
    """Returns (verdict, list of (test, passed, detail))."""
    missing = []
    if money is None:
        missing.append("money.json (run the money lead)")
    if panel is None or not panel.get("counted"):
        missing.append("buyer panel results (run the buyer panel)")
    if missing:
        return "Incomplete", [("Missing", False, m) for m in missing]
    sym = money.get("currency_symbol", "£")

    def m(v):
        return "%s%s%s" % ("-" if v < 0 else "", sym, format(abs(v), ",.2f"))
    tests = [
        ("Every sale makes money", money["per_sale"] > 0,
         "each sale leaves %s" % m(money["per_sale"])),
        ("Year one makes a profit", money["year_one_profit"] > 0,
         "first 12 months: %s" % m(money["year_one_profit"])),
        ("Break-even fits capacity", bool(money.get("breakeven_within_capacity")),
         "break-even %s a month, capacity %s" % (money.get("breakeven_units_per_month"), money.get("capacity"))),
        ("Enough of the panel buys", panel["yes_rate"] >= YES_RATE_NEEDED,
         "%d%% said yes, %d%% needed" % (round(panel["yes_rate"] * 100), round(YES_RATE_NEEDED * 100))),
    ]
    verdict = "Profitable" if all(t[1] for t in tests) else "Not yet"
    return verdict, tests


def strip_footer(text):
    return "\n".join(l for l in text.splitlines() if l.strip() != FOOTER).strip()


def demote(text):
    """Push headings down two levels so each note sits under its plan section."""
    out = []
    for line in text.splitlines():
        if line.startswith("#"):
            line = "##" + line
        out.append(line)
    return "\n".join(out)


def assemble(folder):
    money = read_json(os.path.join(folder, "money.json"))
    panel = read_json(os.path.join(folder, "buyers", "results.json"))
    verdict, tests = decide(money, panel)
    name = "Your business"
    idea = os.path.join(folder, "idea.md")
    if os.path.exists(idea):
        with open(idea, encoding="utf-8") as f:
            first = f.readline().strip().lstrip("# ").strip()
        if first:
            name = first
    lines = ["# Business plan: " + name, "", "## The verdict: " + verdict, ""]
    for test, passed, detail in tests:
        lines.append("- %s %s: %s" % ("✓" if passed else "✗", test, detail))
    lines.append("")
    if verdict == "Profitable":
        lines += ["Profitable on paper. The buyer panel is simulated, so run the real test in the launch "
                  "plan before the big spend.", ""]
    elif verdict == "Not yet":
        lines += ["Fix the ✗ items before spending more. The money lead's what-ifs show which "
                  "change moves the numbers most.", ""]
    else:
        lines += ["Run the missing roles, then compile again.", ""]
    missing_notes = []
    for title, fname in SECTIONS:
        path = os.path.join(folder, fname)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                body = strip_footer(f.read())
            lines += ["## " + title, "", demote(body), ""]
        else:
            missing_notes.append(title)
    if missing_notes:
        lines += ["## Not yet written", "", ", ".join(missing_notes) + ".", ""]
    lines += ["Not financial, legal or tax advice.", "", FOOTER, ""]
    return verdict, "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Compile the business plan and work out its verdict")
    p.add_argument("--dir", required=True)
    p.add_argument("--out")
    a = p.parse_args(argv)
    if not os.path.isdir(a.dir):
        print("No folder at %s" % a.dir, file=sys.stderr)
        return 2
    try:
        verdict, text = assemble(a.dir)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print("Can't compile the plan: %s" % e, file=sys.stderr)
        return 2
    out = a.out or os.path.join(a.dir, "business-plan.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print("Verdict: %s. Plan written to %s" % (verdict, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
