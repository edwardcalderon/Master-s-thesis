import json
import os
import unittest
from unittest.mock import Mock, patch

import app


class ScenarioEndpointTests(unittest.TestCase):
    def setUp(self):
        app.app.config.update(TESTING=True)
        app._last_dispatch_at = 0.0
        self.client = app.app.test_client()
        self.environment = patch.dict(
            os.environ,
            {"GITHUB_DISPATCH_TOKEN": "test-token", "GITHUB_REPO": "owner/repo"},
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @patch("app.requests.post")
    def test_rejects_invalid_scenarios_without_dispatch(self, post):
        invalid = [
            '{"shock_scale":NaN}',
            '{"shock_scale":Infinity}',
            '{"shock_scale":-Infinity}',
            '{"shock_scale":' + str(10**400) + '}',
            '{"capacity_fraction":true}',
            '{"capacity_fraction":1.01}',
            '{"unknown":0.1}',
            '[]',
        ]
        for payload in invalid:
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/api/scenario", data=payload, content_type="application/json"
                )
                self.assertEqual(response.status_code, 400)
        post.assert_not_called()

    @patch("app.requests.post")
    def test_dispatches_valid_bounded_scenario(self, post):
        post.return_value = Mock(status_code=204, text="")
        response = self.client.post(
            "/api/scenario",
            json={"no_arbitrage_band_log": 0.5, "capacity_fraction": 0.0},
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(
            response.get_json()["accepted"],
            {"no_arbitrage_band_log": 0.5, "capacity_fraction": 0.0},
        )
        dispatched = post.call_args.kwargs["json"]["inputs"]["scenario_json"]
        self.assertEqual(json.loads(dispatched), response.get_json()["accepted"])


if __name__ == "__main__":
    unittest.main()
