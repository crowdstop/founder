"""Tests for the crowdstop Founder Team tools. Run: python3 -m unittest discover -s tests -v"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "src", "tools")
EXAMPLES = os.path.join(ROOT, "src", "examples")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


money = load("money")
buyers = load("buyers")
price_range = load("price_range")
verdict = load("verdict")


def answer(bid, decision, prices, tag="x"):
    return {"id": bid, "decision": decision, "reason": "Because.", "reason_tag": tag,
            "what_would_change_my_mind": "", "too_cheap": prices[0], "good_value": prices[1],
            "getting_expensive": prices[2], "too_expensive": prices[3]}


class MoneyTests(unittest.TestCase):
    def setUp(self):
        self.data = money.load(os.path.join(EXAMPLES, "numbers.json"))

    def test_example_figures(self):
        r = money.calculate(self.data)
        self.assertEqual(r["unit_cost"], 7.4)
        self.assertEqual(r["per_sale"], 37.6)
        self.assertEqual(r["fixed_per_month"], 2234)
        self.assertEqual(r["breakeven_units_per_month"], 60)   # ceil(2234 / 37.6)
        self.assertEqual(r["profit_full_per_month"], 3782.0)   # 160 * 37.6 - 2234
        self.assertEqual(r["months"][0]["running_total"], -6518.2)
        self.assertEqual(r["cash_needed"], 6518.2)
        self.assertEqual(r["payback_month"], 5)

    def test_losing_money_per_sale(self):
        d = dict(self.data, price_per_unit=5)
        r = money.calculate(d)
        self.assertLess(r["per_sale"], 0)
        self.assertIsNone(r["breakeven_units_per_month"])
        self.assertFalse(r["breakeven_within_capacity"])

    def test_missing_input_is_an_error(self):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"currency": "GBP"}, tmp)
        tmp.close()
        with self.assertRaises(money.InputError):
            money.load(tmp.name)
        os.unlink(tmp.name)

    def test_what_ifs_are_worse(self):
        base = money.calculate(self.data)
        for case in money.what_ifs(self.data).values():
            self.assertLess(case["year_one_profit"], base["year_one_profit"])


class BuyerTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.customer = buyers.read_customer(os.path.join(EXAMPLES, "customer.json"))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_same_seed_same_panel(self):
        self.assertEqual(buyers.deal(self.customer, 50, 7), buyers.deal(self.customer, 50, 7))
        self.assertNotEqual(buyers.deal(self.customer, 50, 7), buyers.deal(self.customer, 50, 8))

    def test_every_option_is_dealt(self):
        cards = buyers.deal(self.customer, 40, 1)
        for trait, options in self.customer["varies_by"].items():
            self.assertEqual(set(c[trait] for c in cards), set(options))

    def test_tally_counts_and_flags(self):
        cards = buyers.deal(self.customer, 4, 1)
        buyers.write_panel(self.customer, "A pitch.", cards, self.dir)
        ans = os.path.join(self.dir, "answers")
        good = [(cards[0]["id"], "yes"), (cards[1]["id"], "no"), (cards[2]["id"], "maybe")]
        for bid, d in good:
            with open(os.path.join(ans, bid + ".json"), "w") as f:
                json.dump(answer(bid, d, [10, 20, 30, 40]), f)
        # cards[3]: prices that don't rise, so it must be rejected
        with open(os.path.join(ans, cards[3]["id"] + ".json"), "w") as f:
            json.dump(answer(cards[3]["id"], "yes", [40, 30, 20, 10]), f)
        r = buyers.tally(self.dir)
        self.assertEqual(r["counted"], 3)
        self.assertEqual(r["decisions"], {"yes": 1, "maybe": 1, "no": 1})
        self.assertIn(cards[3]["id"], r["invalid"])
        self.assertAlmostEqual(r["yes_rate"], 0.3333, places=3)


class PriceRangeTests(unittest.TestCase):
    def test_points_are_in_order_and_sensible(self):
        rows = [[10 + i % 5, 20 + i % 5, 30 + i % 5, 40 + i % 5] for i in range(50)]
        p = price_range.analyse(rows)
        self.assertTrue(p["lowest_acceptable"] <= p["balance_point"] <= p["highest_acceptable"])
        self.assertTrue(p["lowest_acceptable"] <= p["fewest_object"] <= p["highest_acceptable"])
        self.assertTrue(14 <= p["lowest_acceptable"] <= 20)   # between the too-cheap and bargain answers
        self.assertTrue(34 <= p["highest_acceptable"] <= 40)  # between getting-expensive and too-expensive

    def test_too_few_people(self):
        tmp = tempfile.mkdtemp()
        with open(os.path.join(tmp, "a.json"), "w") as f:
            json.dump(answer("a", "yes", [1, 2, 3, 4]), f)
        with self.assertRaises(price_range.InputError):
            price_range.read_answers(tmp)
        shutil.rmtree(tmp)


class VerdictTests(unittest.TestCase):
    def money_json(self, **over):
        m = {"per_sale": 30, "year_one_profit": 1000, "breakeven_within_capacity": True,
             "breakeven_units_per_month": 50, "capacity": 200}
        m.update(over)
        return m

    def test_profitable(self):
        v, _ = verdict.decide(self.money_json(), {"counted": 100, "yes_rate": 0.3})
        self.assertEqual(v, "Profitable")

    def test_not_yet(self):
        v, tests = verdict.decide(self.money_json(year_one_profit=-5), {"counted": 100, "yes_rate": 0.3})
        self.assertEqual(v, "Not yet")
        self.assertFalse(tests[1][1])

    def test_incomplete(self):
        self.assertEqual(verdict.decide(None, None)[0], "Incomplete")
        self.assertEqual(verdict.decide(self.money_json(), {"counted": 0})[0], "Incomplete")


if __name__ == "__main__":
    unittest.main()
