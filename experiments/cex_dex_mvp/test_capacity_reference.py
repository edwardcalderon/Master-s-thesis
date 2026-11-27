import unittest

from abm import capacity_fraction_for_input_limit


class CapacityReferenceTests(unittest.TestCase):
    def test_initial_reserve_mode_holds_sell_x_input_limit_constant(self):
        fraction = capacity_fraction_for_input_limit(
            0.03, "initial_reserves", "sell-x", 5000.0, 5000.0, 2750.0, 2750.0
        )
        self.assertAlmostEqual(fraction * 2750.0, 0.03 * 5000.0)

    def test_initial_reserve_mode_holds_buy_x_input_limit_constant(self):
        fraction = capacity_fraction_for_input_limit(
            0.03, "initial_reserves", "buy-x", 5000.0, 5000.0, 2750.0, 2750.0
        )
        self.assertAlmostEqual(fraction * 2750.0, 0.03 * 5000.0)

    def test_current_reserve_mode_preserves_existing_fraction(self):
        fraction = capacity_fraction_for_input_limit(
            0.03, "current_reserves", "sell-x", 5000.0, 5000.0, 2750.0, 2750.0
        )
        self.assertEqual(fraction, 0.03)

    def test_fixed_initial_limit_cannot_exceed_active_reserve(self):
        fraction = capacity_fraction_for_input_limit(
            0.03, "initial_reserves", "sell-x", 5000.0, 5000.0, 100.0, 100.0
        )
        self.assertEqual(fraction, 1.0)


if __name__ == "__main__":
    unittest.main()
