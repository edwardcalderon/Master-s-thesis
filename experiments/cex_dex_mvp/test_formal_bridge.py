from fractions import Fraction
import unittest

import run
from formal_bridge import ExactPool, buy_x, price, sell_x, withdraw_proportionally


class ExactBridgeTests(unittest.TestCase):
    def test_exact_swap_invariants_and_float_implementation_agree(self) -> None:
        reserves = (Fraction(3), Fraction(10), Fraction(10000))
        inputs = (Fraction(0), Fraction(1, 10), Fraction(2), Fraction(40))
        for x in reserves:
            for y in reserves:
                pool = ExactPool(x, y)
                for amount in inputs:
                    with self.subTest(x=x, y=y, amount=amount, side="sell-x"):
                        exact = sell_x(pool, amount)
                        float_result = run.sell_x(float(x), float(y), float(amount))
                        self.assertEqual(exact.x * exact.y, x * y)
                        self.assertGreater(exact.x, 0)
                        self.assertGreater(exact.y, 0)
                        self.assertAlmostEqual(float(exact.x), float_result[0], places=10)
                        self.assertAlmostEqual(float(exact.y), float_result[1], places=10)

                    with self.subTest(x=x, y=y, amount=amount, side="buy-x"):
                        exact = buy_x(pool, amount)
                        float_result = run.buy_x(float(x), float(y), float(amount))
                        self.assertEqual(exact.x * exact.y, x * y)
                        self.assertGreater(exact.x, 0)
                        self.assertGreater(exact.y, 0)
                        self.assertAlmostEqual(float(exact.x), float_result[0], places=10)
                        self.assertAlmostEqual(float(exact.y), float_result[1], places=10)

    def test_proportional_withdrawal_preserves_price_and_scales_product(self) -> None:
        for x in (Fraction(3), Fraction(10000)):
            for y in (Fraction(10), Fraction(10000)):
                pool = ExactPool(x, y)
                for remaining in (Fraction(1, 10), Fraction(1, 2), Fraction(1)):
                    withdrawn = withdraw_proportionally(pool, remaining)
                    self.assertEqual(price(withdrawn), price(pool))
                    self.assertEqual(
                        withdrawn.x * withdrawn.y,
                        remaining**2 * pool.x * pool.y,
                    )

    def test_exact_reference_rejects_out_of_domain_inputs(self) -> None:
        pool = ExactPool(Fraction(10), Fraction(10))
        with self.assertRaises(ValueError):
            sell_x(pool, Fraction(-1))
        with self.assertRaises(ValueError):
            buy_x(pool, Fraction(-1))
        with self.assertRaises(ValueError):
            withdraw_proportionally(pool, Fraction(0))


if __name__ == "__main__":
    unittest.main()
