"""Boundary checks for engineering metrics and intervention definitions."""
import json
import unittest
from pathlib import Path
from engineering import tracking_metrics, variant_config, wilson


class EngineeringTests(unittest.TestCase):
    def path(self, values):
        return [dict(tick=t, log_error=v) for t,v in enumerate([0]+values)]

    def test_deadline_requires_completed_pair_and_detects_departure(self):
        m=tracking_metrics(self.path([0.1]*4+[0,0,0.1,0]),0.003,[5,6,8])
        self.assertEqual(m['confirmation_tick'],6)
        self.assertEqual(m['recovered_by_5'],0)
        self.assertEqual(m['recovered_by_6'],1)
        self.assertEqual(m['later_departure'],1)
        self.assertEqual(m['terminal_in_band'],1)

    def test_initial_tick_and_single_final_tick_do_not_establish_recovery(self):
        m=tracking_metrics(self.path([0,0.1,0]),0.003,[2,3])
        self.assertEqual(m['recovered'],0)
        self.assertEqual(m['confirmation_tick'],'')
        self.assertEqual(m['later_departure'],0)

    def test_pair_at_horizon_is_observed(self):
        m=tracking_metrics(self.path([0.1]*18+[0,0]),0.003,[5,10,20])
        self.assertEqual(m['confirmation_tick'],20)
        self.assertEqual(m['recovered_by_20'],1)

    def test_scale_control_and_panic_ablation_preserve_other_rules(self):
        model=json.loads((Path(__file__).parent/'abm_config.json').read_text())
        fixed=variant_config(model,0.5,'fixed_orders')
        prop=variant_config(model,0.5,'proportional_orders')
        no_panic=variant_config(model,0.5,'no_panic')
        self.assertEqual(fixed['initial_reserve_x'],5000)
        self.assertEqual(fixed['noise_trader']['order_fraction_of_initial_reserve'],0.008)
        self.assertEqual(prop['noise_trader']['order_fraction_of_initial_reserve'],0.004)
        self.assertEqual(no_panic['trend_panic_trader']['panic_max_orders_per_run'],0)
        self.assertEqual(no_panic['trend_panic_trader']['trend_order_fraction_of_initial_reserve'],0.012)
        self.assertEqual(model['trend_panic_trader']['panic_max_orders_per_run'],1)

    def test_all_successes_does_not_imply_certain_population_recovery(self):
        low,high=wilson(300,300)
        self.assertLess(low,1)
        self.assertGreater(low,0.98)
        self.assertAlmostEqual(high,1)


if __name__=='__main__':
    unittest.main()
