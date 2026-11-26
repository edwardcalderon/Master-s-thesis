import json
import math
import tempfile
import unittest
from pathlib import Path

import tick


class ScenarioValidationTests(unittest.TestCase):
    def test_valid_boundary_values_are_applied(self):
        state = dict(tick.DEFAULT_STATE)
        actual = tick.apply_scenario(
            state,
            json.dumps({
                "no_arbitrage_band_log": 0.5,
                "capacity_fraction": 0.0,
                "shock_scale": 0.2,
            }),
        )
        self.assertEqual(actual["no_arbitrage_band_log"], 0.5)
        self.assertEqual(actual["capacity_fraction"], 0.0)
        self.assertEqual(actual["shock_scale"], 0.2)

    def test_rejects_nonfinite_boolean_out_of_range_and_unknown_values(self):
        invalid = [
            '{"shock_scale": NaN}',
            '{"shock_scale": Infinity}',
            '{"shock_scale": -Infinity}',
            '{"shock_scale": ' + str(10**400) + '}',
            '{"capacity_fraction": true}',
            '{"capacity_fraction": 1.01}',
            '{"no_arbitrage_band_log": -0.01}',
            '{"shock_scale": 0.21}',
            '{"unknown": 0.1}',
            '[0.1]',
            '{not-json}',
        ]
        for scenario_json in invalid:
            with self.subTest(scenario_json=scenario_json):
                with self.assertRaises(ValueError):
                    tick.apply_scenario(dict(tick.DEFAULT_STATE), scenario_json)

    def test_load_state_fails_closed_on_nonfinite_saved_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_path = Path(temporary) / "state.json"
            state = dict(tick.DEFAULT_STATE)
            state["shock_scale"] = math.nan
            state_path.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, "shock_scale"):
                tick.load_state(Path(temporary))


if __name__ == "__main__":
    unittest.main()
