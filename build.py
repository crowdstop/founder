#!/usr/bin/env python3
"""Builds the 11 crowdstop Founder Team skills from src/.

Edit the files in src/, then run:  python3 build.py
It writes skills/crowdstop-<role>/ (what the plugin installs) and
dist/crowdstop-<role>.zip (one per skill, for uploading to Claude), plus
dist/crowdstop-founder-team-all.zip with all 11 zips inside.
"""
import os
import re
import shutil
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

# role file, skill name, title, description, extra files (src path -> path in skill)
SKILLS = [
    ("board", "crowdstop-board", "The board",
     "Three board members score a business idea through three lenses (offer, monopoly, product), "
     "name the biggest threat to it and vote: back it, back it if, or pass. Starts by writing down the idea. "
     "Use when the user says \"is my idea any good\", \"pressure-test my idea\", \"should I start this\", "
     "\"board\" or \"start my business\".", {}),
    ("competitors", "crowdstop-competitors", "Competitor scout",
     "Maps the competitors, the alternatives and the do-it-yourself options from public sources, "
     "every fact linked, with prices, their headlines and what their customers complain about, then "
     "finds the gap. Use when the user says \"competitors\", \"who am I up against\", \"is this market "
     "crowded\" or \"find the gap\".", {}),
    ("buyers", "crowdstop-buyers", "The buyer panel",
     "Runs a panel of simulated buyers (100 by default) with different circumstances and doubts, "
     "each deciding on the pitch, then tallies who buys, who doesn't and why. Research, not demand. "
     "Use when the user says \"buyers\", \"buyer panel\", \"would people buy this\" or \"test my "
     "pitch\".", {"tools/buyers.py": "tools/buyers.py", "examples/customer.json": "examples/customer.json",
                  "examples/pitch.md": "examples/pitch.md"}),
    ("pricing", "crowdstop-pricing", "Pricing lead",
     "Finds the range of prices buyers accept from four price answers per person, checks the planned "
     "price against it, competitors and the margin, and picks what to test. Use when the user says "
     "\"pricing\", \"what should I charge\" or \"is my price right\".",
     {"tools/price_range.py": "tools/price_range.py"}),
    ("offer", "crowdstop-offer", "Offer builder",
     "Builds the offer around the buyer panel's objections: what's included, risk reversal, true "
     "urgency only, the offer's name, then re-tests it on a quick panel. Use when the user says "
     "\"offer\", \"make my offer better\" or \"why aren't people buying\".",
     {"tools/buyers.py": "tools/buyers.py", "examples/customer.json": "examples/customer.json"}),
    ("money", "crowdstop-money", "Money lead",
     "Works out what each sale leaves, break-even, profit at full speed, the first 12 months, the most "
     "cash needed, the payback month and three what-ifs, every number from the founder's inputs. "
     "Use when the user says \"money\", \"margins\", \"break-even\", \"will it make money\" or "
     "\"how much do I need\".", {"tools/money.py": "tools/money.py",
                                 "examples/numbers.json": "examples/numbers.json"}),
    ("marketing", "crowdstop-marketing", "Marketing lead",
     "Positioning, the channels the first audience really uses, a dated campaign from 14 days before "
     "launch to 16 after, ten hooks, the budget and the most to spend to win a customer. Use when "
     "the user says \"marketing\", \"marketing plan\", \"how do I get customers\" or \"positioning\".", {}),
    ("brand", "crowdstop-brand", "Brand lead",
     "The brand's foundations: name candidates with the checks to run, the promise, voice and a brief "
     "for the look, ready to hand to a designer. Use when the user says \"brand\", \"name my business\", "
     "\"brand voice\", \"tagline\" or \"what should it look like\".",
     {}),
    ("ops", "crowdstop-ops", "Operations lead",
     "How the business will run: suppliers, prices and lead times, who does what, routines for a "
     "normal day, software, the permissions to look into and what could go wrong, with new costs "
     "passed to the money lead. Use when the user says \"operations\", \"suppliers\", \"what permits do "
     "I need\", \"how will I run it\" or \"risks\".", {}),
    ("launch", "crowdstop-launch", "Launch lead",
     "Proves people will pay with a small real-money test, then plans the weeks to launch day, a "
     "timed plan for the day and the month after. Use when the user says \"launch\", \"plan my launch\", \"launch checklist\", \"when can I "
     "launch\" or \"go live\".", {}),
    ("plan", "crowdstop-plan", "Business plan",
     "Pulls the team's notes into one business plan and lets the numbers decide its verdict "
     "(Profitable, Not yet or Incomplete). Use when the user says \"business plan\", \"put it all together\" "
     "or \"is this business ready\".", {"tools/verdict.py": "tools/verdict.py"}),
]

REWRITES = [
    (r"`roles/buyers\.md`", "the crowdstop-buyers skill"),
]


def frontmatter(name, desc):
    desc = desc.replace('"', '\\"')
    return '---\nname: %s\ndescription: "%s"\n---\n\n' % (name, desc)


def build():
    with open(os.path.join(SRC, "shared.md"), encoding="utf-8") as f:
        shared = f.read().strip()
    out_skills = os.path.join(ROOT, "skills")
    dist = os.path.join(ROOT, "dist")
    for d in (out_skills, dist):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
    zips = []
    for role, name, title, desc, extras in SKILLS:
        with open(os.path.join(SRC, "roles", role + ".md"), encoding="utf-8") as f:
            body = f.read()
        body = re.sub(r"^# Role: .*\n", "", body, count=1).strip()
        for pat, rep in REWRITES:
            body = re.sub(pat, rep, body)
        text = (frontmatter(name, desc) + "# crowdstop %s\n\n" % title + body + "\n\n" + shared + "\n")
        sdir = os.path.join(out_skills, name)
        os.makedirs(sdir)
        with open(os.path.join(sdir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(text)
        for src_rel, dst_rel in extras.items():
            dst = os.path.join(sdir, dst_rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(SRC, src_rel), dst)
        zpath = os.path.join(dist, name + ".zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for base, _, files in os.walk(sdir):
                for fn in sorted(files):
                    full = os.path.join(base, fn)
                    z.write(full, os.path.relpath(full, out_skills))
        zips.append(zpath)
    with zipfile.ZipFile(os.path.join(dist, "crowdstop-founder-team-all.zip"), "w") as z:
        for zp in zips:
            z.write(zp, os.path.basename(zp))
    print("Built %d skills into skills/ and dist/" % len(SKILLS))


if __name__ == "__main__":
    build()
