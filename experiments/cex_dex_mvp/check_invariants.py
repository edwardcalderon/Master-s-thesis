#!/usr/bin/env python3
"""Check CPMM accounting invariants separately from the thesis scenarios."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from abm import (
    DEFAULT_CONFIG as DEFAULT_ABM_CONFIG,
    make_noise_schedule,
    run_condition,
    validate as validate_abm,
)
from run import (
    DEFAULT_CONFIG,
    NUMERIC_TOLERANCE,
    adaptive_liquidity_case,
    buy_x,
    fixed_sale_case,
    price,
    sell_x,
    tracking_case,
    validate,
)

DEFAULT_GRID = Path(__file__).resolve().with_name("sweep.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check(
    config_path: Path, grid_path: Path, abm_config_path: Path
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    grid = json.loads(grid_path.read_text(encoding="utf-8"))
    abm_config = json.loads(abm_config_path.read_text(encoding="utf-8"))
    validate(config)
    validate_abm(abm_config)
    checks: list[dict[str, Any]] = []

    def record(name: str, observed: Any) -> None:
        checks.append({"name": name, "status": "PASS", "observed": observed})

    reserve_x = float(config["initial_reserve_x"])
    reserve_y = float(config["initial_reserve_y"])
    invariant_before = reserve_x * reserve_y
    amount_x = float(config["fixed_sale_x"])
    amount_y = amount_x * float(config["initial_cex_price"])

    sell_reserve_x, sell_reserve_y = sell_x(reserve_x, reserve_y, amount_x)
    require(
        sell_reserve_x > 0.0 and sell_reserve_y > 0.0,
        "sell_x produced a nonpositive reserve",
    )
    sell_product = sell_reserve_x * sell_reserve_y
    require(
        math.isclose(sell_product, invariant_before, rel_tol=NUMERIC_TOLERANCE),
        f"sell_x changed k from {invariant_before} to {sell_product}",
    )
    record("sell_x preserves k and positive reserves", {"k_before": invariant_before, "k_after": sell_product})

    buy_reserve_x, buy_reserve_y = buy_x(reserve_x, reserve_y, amount_y)
    require(
        buy_reserve_x > 0.0 and buy_reserve_y > 0.0,
        "buy_x produced a nonpositive reserve",
    )
    buy_product = buy_reserve_x * buy_reserve_y
    require(
        math.isclose(buy_product, invariant_before, rel_tol=NUMERIC_TOLERANCE),
        f"buy_x changed k from {invariant_before} to {buy_product}",
    )
    record("buy_x preserves k and positive reserves", {"k_before": invariant_before, "k_after": buy_product})

    fraction = float(config["lp_remaining_reserve_fraction"])
    withdrawn_x = reserve_x * fraction
    withdrawn_y = reserve_y * fraction
    require(
        withdrawn_x > 0.0 and withdrawn_y > 0.0,
        "proportional withdrawal produced a nonpositive reserve",
    )
    original_price = price(reserve_x, reserve_y)
    withdrawn_price = price(withdrawn_x, withdrawn_y)
    require(
        math.isclose(original_price, withdrawn_price, rel_tol=NUMERIC_TOLERANCE),
        f"proportional withdrawal changed price from {original_price} to {withdrawn_price}",
    )
    record(
        "proportional withdrawal preserves marginal price",
        {"price_before": original_price, "price_after": withdrawn_price, "remaining_fraction": fraction},
    )

    states: list[dict[str, Any]] = []
    for shock in grid["shock_log_returns"]:
        for band in grid["no_arbitrage_band_logs"]:
            case_config = {
                **config,
                "shock_log_return": float(shock),
                "no_arbitrage_band_log": float(band),
            }
            validate(case_config)
            for delay in grid["execution_delay_ticks"]:
                for capacity in grid["arbitrage_capacity_fractions"]:
                    scenario = f"invariant-shock-{shock}-band-{band}-delay-{delay}-capacity-{capacity}"
                    rows, _ = tracking_case(
                        case_config,
                        scenario,
                        float(capacity),
                        int(delay),
                    )
                    states.extend(rows)
    for remaining in grid["liquidity_remaining_fractions"]:
        scenario = f"invariant-e2-remaining-{remaining}"
        rows, _ = fixed_sale_case(config, scenario, float(remaining))
        states.extend(rows)
    e3_selection = grid["e3_policy_selection"]
    for trigger in e3_selection["trigger_log_errors"]:
        for remaining in e3_selection["remaining_reserve_fractions"]:
            e3_config = {
                **config,
                "e3": {
                    **config["e3"],
                    "adaptive_lp_trigger_log_error": float(trigger),
                    "lp_remaining_reserve_fraction": float(remaining),
                },
            }
            validate(e3_config)
            for adaptive in (False, True):
                scenario = (
                    f"invariant-e3-trigger-{trigger}-remaining-{remaining}-"
                    f"adaptive-{adaptive}"
                )
                rows, _ = adaptive_liquidity_case(e3_config, scenario, adaptive)
                states.extend(rows)
    static_e3_rows, static_e3 = adaptive_liquidity_case(config, "invariant-e3-static", False)
    adaptive_e3_rows, adaptive_e3 = adaptive_liquidity_case(config, "invariant-e3-adaptive", True)
    states.extend(static_e3_rows)
    states.extend(adaptive_e3_rows)
    require(
        all(
            math.isfinite(float(row["reserve_x"]))
            and math.isfinite(float(row["reserve_y"]))
            and float(row["reserve_x"]) > 0.0
            and float(row["reserve_y"]) > 0.0
            for row in states
        ),
        "one or more configured E0/E1/E2/E3 states has a nonpositive or nonfinite reserve",
    )
    record("all configured E0/E1/E2/E3 states have positive finite reserves", {"states_checked": len(states)})

    capacity_levels = sorted(
        {float(value) for value in config["capacity_fractions"].values()}
    )
    arbitrage_results: list[dict[str, Any]] = []
    shock_size = abs(float(config["shock_log_return"]))
    for shock in (-shock_size, shock_size):
        case_config = {**config, "shock_log_return": shock}
        capacity_summaries: list[float] = []
        for capacity in capacity_levels:
            rows, summary = tracking_case(
                case_config,
                f"invariant-arbitrage-shock-{shock}-capacity-{capacity}",
                capacity,
                0,
            )
            first_post_shock_error = float(rows[1]["log_error"])
            if capacity > 0.0:
                require(
                    abs(first_post_shock_error) < shock_size,
                    f"arbitrage failed to reduce first-tick error for shock {shock} at capacity {capacity}",
                )
                require(
                    first_post_shock_error * shock < 0.0,
                    f"arbitrage moved price past the reference for shock {shock} at capacity {capacity}",
                )
                require(
                    abs(first_post_shock_error)
                    >= float(config["no_arbitrage_band_log"]) - NUMERIC_TOLERANCE,
                    "arbitrage crossed the configured band instead of stopping at its edge",
                )
            capacity_summaries.append(float(summary["max_absolute_log_error"]))
        require(
            all(
                capacity_summaries[index + 1]
                <= capacity_summaries[index] + NUMERIC_TOLERANCE
                for index in range(len(capacity_summaries) - 1)
            ),
            f"larger arbitrage capacity worsened peak error for shock {shock}: {capacity_summaries}",
        )
        arbitrage_results.append(
            {
                "shock_log_return": shock,
                "capacity_fractions": capacity_levels,
                "max_absolute_log_errors": capacity_summaries,
            }
        )
    record(
        "arbitrage reduces error from either shock direction and capacity is non-worsening",
        arbitrage_results,
    )

    require(
        not static_e3["adaptive_lp_withdrawal_applied"]
        and adaptive_e3["adaptive_lp_withdrawal_applied"],
        "E3 must leave the static control untouched and trigger the adaptive withdrawal",
    )
    require(
        float(adaptive_e3["minimum_geometric_depth"])
        < float(static_e3["minimum_geometric_depth"]),
        "E3 adaptive withdrawal did not reduce geometric pool depth",
    )
    require(
        float(adaptive_e3["max_absolute_log_error"])
        > float(static_e3["max_absolute_log_error"]),
        "configured E3 adaptive rule did not increase peak tracking error",
    )
    record(
        "configured E3 threshold policy triggers and amplifies peak error",
        {
            "static_peak_error": static_e3["max_absolute_log_error"],
            "adaptive_peak_error": adaptive_e3["max_absolute_log_error"],
            "static_return_tick": static_e3["sustained_return_tick"],
            "adaptive_return_tick": adaptive_e3["sustained_return_tick"],
        },
    )

    require(
        [row["cex_price"] for row in static_e3_rows]
        == [row["cex_price"] for row in adaptive_e3_rows],
        "paired E3 policy runs must share the same exogenous CEX path",
    )
    require(
        [row["tick"] for row in static_e3_rows]
        == [row["tick"] for row in adaptive_e3_rows],
        "paired E3 policy runs must share the same tick schedule",
    )
    record(
        "E3 static/adaptive comparison shares exogenous shock path and ticks",
        {"paired_ticks": len(static_e3_rows)},
    )

    impact_levels: list[dict[str, float]] = []
    for remaining in grid["liquidity_remaining_fractions"]:
        scenario = f"invariant-impact-remaining-{remaining}"
        _, summary = fixed_sale_case(config, scenario, float(remaining))
        impact_levels.append(
            {
                "remaining_fraction": float(remaining),
                "absolute_log_impact": float(summary["absolute_log_price_impact"]),
            }
        )
    ordered_impacts = sorted(impact_levels, key=lambda item: item["remaining_fraction"], reverse=True)
    require(
        all(
            ordered_impacts[index + 1]["absolute_log_impact"]
            > ordered_impacts[index]["absolute_log_impact"]
            for index in range(len(ordered_impacts) - 1)
        ),
        f"fixed-sale impact did not increase with each reduction in depth: {ordered_impacts}",
    )
    record("fixed-sale impact increases at every lower liquidity level", ordered_impacts)

    stochastic_states = 0
    abm_capacities = abm_config["arbitrage_capacity_fractions"]
    abm_conditions = (
        ("E0-arb-off-static", float(abm_capacities["off"]), False),
        ("E1-arb-low-static", float(abm_capacities["low"]), False),
        ("E1-arb-high-static", float(abm_capacities["high"]), False),
        ("E3-adaptive-lp-high-arb", float(abm_capacities["high"]), True),
    )
    for seed in (0, 17, 99):
        noise_schedule = make_noise_schedule(abm_config, seed)
        for shock in abm_config["shock_log_returns"]:
            shared_noise_signature: list[tuple[Any, Any]] | None = None
            for scenario, capacity, adaptive in abm_conditions:
                rows, _ = run_condition(
                    abm_config,
                    float(shock),
                    seed,
                    scenario,
                    capacity,
                    adaptive,
                    noise_schedule,
                )
                stochastic_states += len(rows)
                signature = [
                    (row["noise_order_side"], row["noise_order_requested"])
                    for row in rows
                ]
                if shared_noise_signature is None:
                    shared_noise_signature = signature
                else:
                    require(
                        signature == shared_noise_signature,
                        "paired stochastic conditions do not share the same noise orders",
                    )
    record(
        "stochastic paired conditions share noise orders and conserve assets",
        {"trajectories": 24, "states_checked": stochastic_states},
    )

    return {
        "model_version": config["model_version"],
        "stochastic_model_version": abm_config["model_version"],
        "config": str(config_path),
        "stochastic_config": str(abm_config_path),
        "sweep_grid": str(grid_path),
        "numeric_relative_tolerance": NUMERIC_TOLERANCE,
        "checks_passed": len(checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--grid", type=Path, default=DEFAULT_GRID)
    parser.add_argument("--abm-config", type=Path, default=DEFAULT_ABM_CONFIG)
    args = parser.parse_args()
    try:
        result = check(
            args.config.resolve(), args.grid.resolve(), args.abm_config.resolve()
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
