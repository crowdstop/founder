#!/usr/bin/env python3
"""crowdstop Founder Team: the money lead's calculator.

Reads one numbers.json and works out what each sale leaves, break-even, profit
at full speed, the first 12 months, the most cash needed, the payback month and
three what-ifs. Standard library only. Every figure comes from an input; a
missing input is an error, never a guess.

    python3 money.py numbers.json [--out money.md] [--json money.json]
"""
import argparse
import json
import math
import sys

REQUIRED = [
    "currency", "unit", "price_per_unit", "costs_per_unit",
    "fixed_costs_per_month", "startup_costs",
    "units_per_month_at_full_speed", "capacity_units_per_month",
]
DEFAULT_RAMP = [0.3, 0.5, 0.7, 0.85]
SYMBOLS = {"GBP": "£", "EUR": "€", "USD": "$", "CAD": "$", "AUD": "$"}


class InputError(ValueError):
    pass


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise InputError("missing from numbers.json: " + ", ".join(missing))
    for key in ("costs_per_unit", "fixed_costs_per_month", "startup_costs"):
        if not isinstance(data[key], dict):
            raise InputError(key + " must be a list of named amounts, e.g. {\"rent\": 900}")
        for name, value in data[key].items():
            if not isinstance(value, (int, float)) or value < 0:
                raise InputError("%s > %s must be a number of 0 or more" % (key, name))
    for key in ("price_per_unit", "units_per_month_at_full_speed", "capacity_units_per_month"):
        if not isinstance(data[key], (int, float)) or data[key] <= 0:
            raise InputError(key + " must be a number above 0")
    ramp = data.get("ramp", DEFAULT_RAMP)
    if not all(isinstance(r, (int, float)) and 0 <= r <= 1 for r in ramp):
        raise InputError("ramp must be a list of shares between 0 and 1, e.g. [0.3, 0.5]")
    data["ramp"] = list(ramp)
    return data


def months_ramp(ramp, n=12):
    """Share of full speed for each of n months; after the ramp, full speed."""
    return [ramp[i] if i < len(ramp) else 1.0 for i in range(n)]


def calculate(data, price=None, units=None, cost_factor=1.0):
    """The core sums. Optional overrides drive the what-ifs."""
    price = data["price_per_unit"] if price is None else price
    full_units = data["units_per_month_at_full_speed"] if units is None else units
    unit_cost = sum(data["costs_per_unit"].values()) * cost_factor
    fixed = sum(data["fixed_costs_per_month"].values())
    startup = sum(data["startup_costs"].values())
    per_sale = price - unit_cost

    breakeven_units = math.ceil(fixed / per_sale) if per_sale > 0 else None
    profit_full = full_units * per_sale - fixed
    revenue_full = full_units * price
    margin_full = profit_full / revenue_full if revenue_full else 0.0

    months = []
    running = -startup
    lowest = running
    payback_month = None
    for i, share in enumerate(months_ramp(data["ramp"]), start=1):
        u = full_units * share
        revenue = u * price
        contribution = u * per_sale
        profit = contribution - fixed
        running += profit
        lowest = min(lowest, running)
        if payback_month is None and running >= 0:
            payback_month = i
        months.append({
            "month": i, "units": round(u, 1), "revenue": round(revenue, 2),
            "contribution": round(contribution, 2), "fixed": round(fixed, 2),
            "profit": round(profit, 2), "running_total": round(running, 2),
        })

    return {
        "price": price,
        "unit_cost": round(unit_cost, 2),
        "per_sale": round(per_sale, 2),
        "per_sale_share": round(per_sale / price, 4) if price else 0.0,
        "fixed_per_month": round(fixed, 2),
        "startup": round(startup, 2),
        "breakeven_units_per_month": breakeven_units,
        "breakeven_units_per_week": (round(breakeven_units * 12 / 52, 1)
                                     if breakeven_units is not None else None),
        "units_full": full_units,
        "capacity": data["capacity_units_per_month"],
        "breakeven_within_capacity": (breakeven_units is not None
                                      and breakeven_units <= data["capacity_units_per_month"]),
        "profit_full_per_month": round(profit_full, 2),
        "margin_full": round(margin_full, 4),
        "year_one_profit": round(sum(m["profit"] for m in months), 2),
        "cash_needed": round(max(0.0, -lowest), 2),
        "payback_month": payback_month,
        "months": months,
    }


def what_ifs(data):
    return {
        "price 10% lower": calculate(data, price=data["price_per_unit"] * 0.9),
        "20% fewer sales": calculate(data, units=data["units_per_month_at_full_speed"] * 0.8),
        "costs per sale 20% higher": calculate(data, cost_factor=1.2),
    }


def money(v, sym):
    sign = "-" if v < 0 else ""
    return "%s%s%s" % (sign, sym, format(abs(v), ",.2f"))


def report(data, base, cases):
    sym = SYMBOLS.get(data["currency"], data["currency"] + " ")
    unit = data["unit"]
    name = data.get("business", "The business")
    lines = ["# Money: " + name, ""]
    if base["per_sale"] <= 0:
        lines += ["**Each %s loses money.** It sells for %s and costs %s to deliver. "
                  "Fix the price or the costs before anything else." % (
                      unit, money(base["price"], sym), money(base["unit_cost"], sym)), ""]
    lines += [
        "| | |", "| --- | --- |",
        "| Price per %s | %s |" % (unit, money(base["price"], sym)),
        "| Costs per %s | %s |" % (unit, money(base["unit_cost"], sym)),
        "| Left per %s | %s (%d%% of the price) |" % (unit, money(base["per_sale"], sym),
                                                     round(base["per_sale_share"] * 100)),
        "| Fixed costs per month | %s |" % money(base["fixed_per_month"], sym),
        "| Start-up costs | %s |" % money(base["startup"], sym),
        "| Break-even | %s %ss a month (about %s a week) |" % (
            base["breakeven_units_per_month"] if base["breakeven_units_per_month"] is not None else "never",
            unit, base["breakeven_units_per_week"] if base["breakeven_units_per_week"] is not None else "n/a"),
        "| Planned at full speed | %s a month; capacity %s |" % (
            format(base["units_full"], "g"), format(base["capacity"], "g")),
        "| Profit at full speed | %s a month (%d%% margin) |" % (
            money(base["profit_full_per_month"], sym), round(base["margin_full"] * 100)),
        "| First 12 months | %s |" % money(base["year_one_profit"], sym),
        "| Most cash needed | %s |" % money(base["cash_needed"], sym),
        "| Pays back | %s |" % ("month %d" % base["payback_month"] if base["payback_month"]
                                else "not within 12 months"),
        "",
    ]
    if not base["breakeven_within_capacity"]:
        lines += ["**Break-even is more than the business can handle.** Even at capacity it "
                  "won't cover its fixed costs.", ""]
    lines += ["## The first 12 months", "",
              "| Month | %ss | Revenue | Left after costs per sale | Fixed costs | Profit | Running total |" % unit.capitalize(),
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for m in base["months"]:
        lines.append("| %d | %s | %s | %s | %s | %s | %s |" % (
            m["month"], format(m["units"], "g"), money(m["revenue"], sym),
            money(m["contribution"], sym), money(m["fixed"], sym),
            money(m["profit"], sym), money(m["running_total"], sym)))
    lines += ["", "The running total starts at minus the start-up costs.", "",
              "## What if", "",
              "| | Left per %s | Break-even a month | First 12 months | Most cash needed | Pays back |" % unit,
              "| --- | --- | --- | --- | --- | --- |"]
    for label, c in [("As planned", base)] + list(cases.items()):
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            label, money(c["per_sale"], sym),
            c["breakeven_units_per_month"] if c["breakeven_units_per_month"] is not None else "never",
            money(c["year_one_profit"], sym), money(c["cash_needed"], sym),
            "month %d" % c["payback_month"] if c["payback_month"] else "not in 12 months"))
    basis = data.get("basis", {})
    estimates = sorted(k for k, v in basis.items() if str(v).lower() == "estimate")
    lines += [""]
    if estimates:
        lines += ["**Estimates to replace with real figures:** " + ", ".join(estimates) + ".", ""]
    lines += ["Not financial or tax advice. Check VAT, tax and structure with an accountant.", "",
              "Made with the crowdstop Founder Team · crowdstop.com", ""]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Margins, break-even and year one from numbers.json")
    p.add_argument("numbers")
    p.add_argument("--out", help="write the report here (markdown)")
    p.add_argument("--json", help="write the figures here, for the business plan")
    a = p.parse_args(argv)
    try:
        data = load(a.numbers)
    except (InputError, json.JSONDecodeError, OSError) as e:
        print("Can't run the numbers: %s" % e, file=sys.stderr)
        return 2
    base = calculate(data)
    cases = what_ifs(data)
    text = report(data, base, cases)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    if a.json:
        out = dict(base)
        out["currency_symbol"] = SYMBOLS.get(data["currency"], data["currency"] + " ")
        out["what_ifs"] = {k: {kk: vv for kk, vv in v.items() if kk != "months"} for k, v in cases.items()}
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
