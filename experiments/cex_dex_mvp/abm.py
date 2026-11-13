#!/usr/bin/env python3
"""Run paired stochastic selection scenarios for the CEX/DEX thesis MVP."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run import DEFAULT_OUTPUT, arbitrage_order, execute_arbitrage_order, excess_error, git_context, log_error, price, sha256_bytes, sell_x, buy_x


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "abm_config.json"
DEFAULT_ABM_OUTPUT = DEFAULT_OUTPUT / "abm"
SUMMARY_FIELDS = [
    "shock_log_return",
    "scenario",
    "lp_policy",
    "arbitrage_capacity_fraction",
    "seed_count",
    "mean_peak_absolute_log_error",
    "median_peak_absolute_log_error",
    "p025_peak_absolute_log_error",
    "p975_peak_absolute_log_error",
    "mean_absolute_log_error",
    "mean_max_excess_error",
    "cumulative_excess_error",
    "return_to_band_rate",
    "median_return_tick_when_observed",
    "mean_minimum_geometric_depth",
    "lp_withdrawal_rate",
    "mean_noise_orders",
    "mean_trend_orders",
    "mean_panic_orders",
    "mean_arbitrage_orders",
    "mean_capital_limited_orders",
]
TIME_SERIES_FIELDS = [
    "shock_log_return",
    "scenario",
    "seed",
    "tick",
    "event",
    "cex_price",
    "cex_log_return",
    "dex_price",
    "reserve_x",
    "reserve_y",
    "log_error",
    "excess_error",
    "normalized_net_buy_pressure_z",
    "noise_order_side",
    "noise_order_requested",
    "noise_order_input",
    "trend_order_side",
    "trend_order_requested",
    "trend_order_input",
    "panic_order_fired",
    "lp_withdrawal_applied",
    "arbitrage_event",
    "wallet_x_total",
    "wallet_y_total",
    "system_x_total",
    "system_y_total",
    "system_x_conservation_error",
    "system_y_conservation_error",
]
PAIRED_FIELDS = [
    "shock_log_return",
    "seed",
    "contrast",
    "first_scenario",
    "second_scenario",
    "peak_error_difference_first_minus_second",
    "mean_absolute_error_difference_first_minus_second",
    "cumulative_excess_error_difference_first_minus_second",
    "max_excess_error_difference_first_minus_second",
    "minimum_depth_difference_first_minus_second",
    "return_tick_difference_first_minus_second",
]
PAIRED_SUMMARY_FIELDS = [
    "shock_log_return",
    "contrast",
    "seed_count",
    "mean_peak_error_difference",
    "standard_error_peak_error_difference",
    "approx_95pct_ci_low_peak_error_difference",
    "approx_95pct_ci_high_peak_error_difference",
    "approx_95pct_ci_half_width_peak_error_difference",
    "mean_absolute_error_difference",
    "approx_95pct_ci_low_mean_absolute_error_difference",
    "approx_95pct_ci_high_mean_absolute_error_difference",
    "cumulative_excess_error_difference",
    "approx_95pct_ci_low_cumulative_excess_error_difference",
    "approx_95pct_ci_high_cumulative_excess_error_difference",
    "precision_target",
    "precision_target_met",
    "mean_max_excess_error_difference",
    "mean_minimum_depth_difference",
    "median_return_tick_difference_when_observed",
]


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def validate(config: dict[str, Any]) -> None:
    for name in (
        "initial_reserve_x",
        "initial_reserve_y",
        "initial_cex_price",
        "horizon_ticks",
        "sustained_band_ticks",
        "wallet_inventory_multiple_of_initial_reserves",
        "arbitrage_inventory_multiple_of_initial_reserves",
    ):
        value = float(config[name])
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and positive")
    initial_price = float(config["initial_reserve_y"]) / float(config["initial_reserve_x"])
    if not math.isclose(initial_price, float(config["initial_cex_price"]), rel_tol=1e-12):
        raise ValueError("initial pool and CEX prices must match")
    horizon = int(config["horizon_ticks"])
    shock_tick = int(config["shock_tick"])
    if horizon <= 0 or not 1 <= shock_tick <= horizon:
        raise ValueError("shock_tick must fall within a positive horizon")
    if float(config["no_arbitrage_band_log"]) < 0.0:
        raise ValueError("no_arbitrage_band_log must be nonnegative")
    shocks = [float(value) for value in config["shock_log_returns"]]
    if not shocks or any(not math.isfinite(value) for value in shocks):
        raise ValueError("shock_log_returns must contain finite values")
    capacities = [float(value) for value in config["arbitrage_capacity_fractions"].values()]
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in capacities):
        raise ValueError("arbitrage capacity fractions must be in [0, 1]")
    noise = config["noise_trader"]
    if not 0.0 <= float(noise["activity_probability"]) <= 1.0:
        raise ValueError("noise activity probability must be in [0, 1]")
    if float(noise["order_fraction_of_initial_reserve"]) <= 0.0:
        raise ValueError("noise order fraction must be positive")
    trend = config["trend_panic_trader"]
    if float(trend["trend_log_return_threshold"]) < 0.0:
        raise ValueError("trend threshold must be nonnegative")
    if float(trend["trend_order_fraction_of_initial_reserve"]) <= 0.0:
        raise ValueError("trend order fraction must be positive")
    if float(trend["panic_dex_log_return_threshold"]) >= 0.0:
        raise ValueError("panic DEX return threshold must be negative")
    if float(trend["panic_sell_fraction_of_initial_reserve"]) <= 0.0:
        raise ValueError("panic sale fraction must be positive")
    if int(trend["panic_max_orders_per_run"]) < 0:
        raise ValueError("panic_max_orders_per_run must be nonnegative")
    lp = config["liquidity_provider"]
    if float(lp["adaptive_lp_trigger_log_error"]) < 0.0:
        raise ValueError("adaptive LP trigger must be nonnegative")
    remaining = float(lp["remaining_reserve_fraction"])
    if not 0.0 < remaining <= 1.0:
        raise ValueError("LP remaining reserve fraction must be in (0, 1]")
    replication = config["replication"]
    if int(replication["minimum_seed_count"]) <= 1:
        raise ValueError("minimum_seed_count must exceed one")
    if int(replication["seed_batch_size"]) <= 0:
        raise ValueError("seed_batch_size must be positive")
    if int(replication["maximum_seed_count"]) < int(replication["minimum_seed_count"]):
        raise ValueError("maximum_seed_count must be at least minimum_seed_count")
    if float(replication["target_95pct_half_width_peak_error"]) <= 0.0:
        raise ValueError("precision target must be positive")


def make_noise_schedule(config: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    probability = float(config["noise_trader"]["activity_probability"])
    schedule: list[dict[str, Any]] = []
    for tick in range(1, int(config["horizon_ticks"]) + 1):
        active_draw = rng.random()
        side_draw = rng.random()
        schedule.append(
            {
                "tick": tick,
                "active": active_draw < probability,
                "side": "buy-x" if side_draw < 0.5 else "sell-x",
                "active_draw": active_draw,
                "side_draw": side_draw,
            }
        )
    return schedule


def apply_wallet_order(
    reserve_x: float,
    reserve_y: float,
    wallet: dict[str, float],
    side: str,
    requested: float,
) -> tuple[float, float, float, bool]:
    """Execute a wallet-funded CPMM swap; return reserves, input used, and clipping."""
    key = "y" if side == "buy-x" else "x"
    available = wallet[key]
    amount = min(max(requested, 0.0), available)
    clipped = amount + 1e-12 < requested
    if amount <= 0.0:
        return reserve_x, reserve_y, 0.0, clipped
    if side == "sell-x":
        next_x, next_y = sell_x(reserve_x, reserve_y, amount)
        wallet["x"] = max(wallet["x"] - amount, 0.0)
        wallet["y"] += reserve_y - next_y
    elif side == "buy-x":
        next_x, next_y = buy_x(reserve_x, reserve_y, amount)
        wallet["y"] = max(wallet["y"] - amount, 0.0)
        wallet["x"] += reserve_x - next_x
    else:
        raise ValueError(f"unknown order side: {side}")
    return next_x, next_y, amount, clipped


def system_totals(
    reserve_x: float, reserve_y: float, wallets: dict[str, dict[str, float]]
) -> tuple[float, float, float, float]:
    wallet_x = sum(wallet["x"] for wallet in wallets.values())
    wallet_y = sum(wallet["y"] for wallet in wallets.values())
    return wallet_x, wallet_y, reserve_x + wallet_x, reserve_y + wallet_y


def run_condition(
    config: dict[str, Any],
    shock: float,
    seed: int,
    scenario: str,
    capacity: float,
    adaptive_lp: bool,
    noise_schedule: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reserve_x = float(config["initial_reserve_x"])
    reserve_y = float(config["initial_reserve_y"])
    initial_x = reserve_x
    initial_y = reserve_y
    reference = float(config["initial_cex_price"])
    band = float(config["no_arbitrage_band_log"])
    trader_multiple = float(config["wallet_inventory_multiple_of_initial_reserves"])
    arb_multiple = float(config["arbitrage_inventory_multiple_of_initial_reserves"])
    wallets = {
        "noise": {"x": initial_x * trader_multiple, "y": initial_y * trader_multiple},
        "trend_panic": {"x": initial_x * trader_multiple, "y": initial_y * trader_multiple},
        "arbitrageur": {"x": initial_x * arb_multiple, "y": initial_y * arb_multiple},
        "lp": {"x": 0.0, "y": 0.0},
    }
    initial_system_x = initial_x + sum(wallet["x"] for wallet in wallets.values())
    initial_system_y = initial_y + sum(wallet["y"] for wallet in wallets.values())
    system_tolerance = 1e-8 * max(initial_system_x, initial_system_y)
    rows: list[dict[str, Any]] = []
    errors: list[float] = []
    excess_values: list[float] = []
    in_band_streak = 0
    return_tick: int | None = None
    lp_withdrawal_tick: int | None = None
    panic_orders = 0
    counts = {"noise": 0, "trend": 0, "panic": 0, "arbitrage": 0, "capital_limited": 0}

    def record(
        tick: int,
        event: str,
        noise_side: str | None = None,
        noise_requested: float | None = None,
        noise_input: float | None = None,
        trend_side: str | None = None,
        trend_requested: float | None = None,
        trend_input: float | None = None,
        panic_fired: bool = False,
        lp_withdrawn: bool = False,
        arbitrage_event: str = "arbitrage-none",
        cex_log_return: float = 0.0,
        normalized_net_buy_pressure: float = 0.0,
    ) -> None:
        px = price(reserve_x, reserve_y)
        error = log_error(reserve_x, reserve_y, reference)
        wallet_x, wallet_y, total_x, total_y = system_totals(reserve_x, reserve_y, wallets)
        if min(reserve_x, reserve_y) <= 0.0 or not all(
            math.isfinite(value)
            for value in (reserve_x, reserve_y, total_x, total_y)
        ):
            raise ValueError(f"nonpositive or nonfinite state in {scenario}, seed {seed}, tick {tick}")
        if (
            abs(total_x - initial_system_x) > system_tolerance
            or abs(total_y - initial_system_y) > system_tolerance
        ):
            raise ValueError(
                f"asset conservation failed in {scenario}, seed {seed}, tick {tick}: "
                f"x={total_x - initial_system_x}, y={total_y - initial_system_y}"
            )
        errors.append(abs(error))
        excess_values.append(max(abs(error) - band, 0.0))
        rows.append(
            {
                "shock_log_return": shock,
                "scenario": scenario,
                "seed": seed,
                "tick": tick,
                "event": event,
                "cex_price": reference,
                "cex_log_return": cex_log_return,
                "dex_price": px,
                "reserve_x": reserve_x,
                "reserve_y": reserve_y,
                "log_error": error,
                "excess_error": excess_error(error, band),
                "normalized_net_buy_pressure_z": normalized_net_buy_pressure,
                "noise_order_side": noise_side,
                "noise_order_requested": noise_requested,
                "noise_order_input": noise_input,
                "trend_order_side": trend_side,
                "trend_order_requested": trend_requested,
                "trend_order_input": trend_input,
                "panic_order_fired": panic_fired,
                "lp_withdrawal_applied": lp_withdrawn,
                "arbitrage_event": arbitrage_event,
                "wallet_x_total": wallet_x,
                "wallet_y_total": wallet_y,
                "system_x_total": total_x,
                "system_y_total": total_y,
                "system_x_conservation_error": total_x - initial_system_x,
                "system_y_conservation_error": total_y - initial_system_y,
            }
        )

    record(0, "initial")
    previous_dex_price = price(reserve_x, reserve_y)
    shock_tick = int(config["shock_tick"])
    horizon = int(config["horizon_ticks"])
    noise_cfg = config["noise_trader"]
    trend_cfg = config["trend_panic_trader"]
    lp_cfg = config["liquidity_provider"]
    lp_withdrawn = False

    for tick in range(1, horizon + 1):
        events: list[str] = []
        cex_log_return = 0.0
        signed_buy_pressure_y = 0.0
        if tick == shock_tick:
            reference *= math.exp(shock)
            cex_log_return = shock
            events.append("cex-shock")

        scheduled_noise = noise_schedule[tick - 1]
        noise_side: str | None = None
        noise_requested: float | None = None
        noise_input: float | None = None
        if scheduled_noise["active"]:
            noise_side = str(scheduled_noise["side"])
            base = initial_y if noise_side == "buy-x" else initial_x
            noise_requested = base * float(noise_cfg["order_fraction_of_initial_reserve"])
            noise_reference_price = price(reserve_x, reserve_y)
            reserve_x, reserve_y, noise_input, clipped = apply_wallet_order(
                reserve_x, reserve_y, wallets["noise"], noise_side, noise_requested
            )
            if noise_side == "buy-x":
                signed_buy_pressure_y += noise_input
            else:
                signed_buy_pressure_y -= noise_input * noise_reference_price
            counts["noise"] += int(noise_input > 0.0)
            counts["capital_limited"] += int(clipped)
            events.append("noise-" + (noise_side if noise_input > 0.0 else "order-unfunded"))

        trend_side: str | None = None
        trend_requested: float | None = None
        trend_input: float | None = None
        panic_fired = False
        dex_return = math.log(price(reserve_x, reserve_y) / previous_dex_price)
        if (
            panic_orders < int(trend_cfg["panic_max_orders_per_run"])
            and dex_return <= float(trend_cfg["panic_dex_log_return_threshold"])
        ):
            trend_side = "sell-x"
            trend_requested = initial_x * float(
                trend_cfg["panic_sell_fraction_of_initial_reserve"]
            )
            panic_fired = True
            panic_orders += 1
            counts["panic"] += 1
            events.append("trend-panic-sell-x")
        elif abs(dex_return) >= float(trend_cfg["trend_log_return_threshold"]):
            trend_side = "buy-x" if dex_return > 0.0 else "sell-x"
            base = initial_y if trend_side == "buy-x" else initial_x
            trend_requested = base * float(
                trend_cfg["trend_order_fraction_of_initial_reserve"]
            )
            counts["trend"] += 1
            events.append("trend-follow-" + trend_side)
        if trend_side is not None and trend_requested is not None:
            trend_reference_price = price(reserve_x, reserve_y)
            reserve_x, reserve_y, trend_input, clipped = apply_wallet_order(
                reserve_x, reserve_y, wallets["trend_panic"], trend_side, trend_requested
            )
            if trend_side == "buy-x":
                signed_buy_pressure_y += trend_input
            else:
                signed_buy_pressure_y -= trend_input * trend_reference_price
            counts["capital_limited"] += int(clipped)
            if trend_input <= 0.0:
                events.append("trend-order-unfunded")

        if adaptive_lp and not lp_withdrawn:
            observed_error = abs(log_error(reserve_x, reserve_y, reference))
            if observed_error > float(lp_cfg["adaptive_lp_trigger_log_error"]):
                remaining = float(lp_cfg["remaining_reserve_fraction"])
                withdrawn_x = reserve_x * (1.0 - remaining)
                withdrawn_y = reserve_y * (1.0 - remaining)
                reserve_x *= remaining
                reserve_y *= remaining
                wallets["lp"]["x"] += withdrawn_x
                wallets["lp"]["y"] += withdrawn_y
                lp_withdrawn = True
                lp_withdrawal_tick = tick
                events.append("adaptive-lp-proportional-withdrawal")

        order = arbitrage_order(reserve_x, reserve_y, reference, band, capacity)
        arbitrage_event = "arbitrage-none"
        if order is not None:
            side, requested, event_name = order
            reserve_x, reserve_y, used, clipped = apply_wallet_order(
                reserve_x, reserve_y, wallets["arbitrageur"], side, requested
            )
            if used > 0.0:
                arbitrage_event = event_name
                counts["arbitrage"] += 1
                events.append(event_name)
            else:
                events.append("arbitrage-order-unfunded")
            counts["capital_limited"] += int(clipped)

        if not events:
            events.append("no-trade")
        record(
            tick,
            "+".join(events),
            noise_side,
            noise_requested,
            noise_input,
            trend_side,
            trend_requested,
            trend_input,
            panic_fired,
            lp_withdrawal_tick == tick,
            arbitrage_event,
            cex_log_return,
            signed_buy_pressure_y / initial_y,
        )
        if abs(float(rows[-1]["log_error"])) <= band + 1e-12:
            in_band_streak += 1
            sustained_ticks = int(config["sustained_band_ticks"])
            if return_tick is None and in_band_streak >= sustained_ticks:
                return_tick = tick - sustained_ticks + 1
        else:
            in_band_streak = 0
        previous_dex_price = price(reserve_x, reserve_y)

    wallet_x, wallet_y, total_x, total_y = system_totals(reserve_x, reserve_y, wallets)
    conservation_x = total_x - initial_system_x
    conservation_y = total_y - initial_system_y
    if min(reserve_x, reserve_y) <= 0.0 or not all(
        math.isfinite(value)
        for value in (reserve_x, reserve_y, total_x, total_y, conservation_x, conservation_y)
    ):
        raise ValueError(f"nonpositive or nonfinite state in {scenario}, seed {seed}")
    if abs(conservation_x) > system_tolerance or abs(conservation_y) > system_tolerance:
        raise ValueError(
            f"asset conservation failed in {scenario}, seed {seed}: "
            f"x={conservation_x}, y={conservation_y}"
        )

    summary = {
        "shock_log_return": shock,
        "scenario": scenario,
        "lp_policy": "one-shot-threshold-withdrawal" if adaptive_lp else "static",
        "arbitrage_capacity_fraction": capacity,
        "seed": seed,
        "maximum_absolute_log_error": max(errors),
        "mean_absolute_log_error": statistics.mean(errors[1:]),
        "maximum_excess_error": max(excess_values),
        "cumulative_excess_error": sum(excess_values[1:]),
        "sustained_return_tick": return_tick,
        "minimum_geometric_depth": min(
            math.sqrt(float(row["reserve_x"]) * float(row["reserve_y"])) for row in rows
        ),
        "ending_geometric_depth": math.sqrt(reserve_x * reserve_y),
        "lp_withdrawal_applied": lp_withdrawn,
        "lp_withdrawal_tick": lp_withdrawal_tick,
        "noise_orders": counts["noise"],
        "trend_orders": counts["trend"],
        "panic_orders": counts["panic"],
        "arbitrage_orders": counts["arbitrage"],
        "capital_limited_orders": counts["capital_limited"],
        "system_x_conservation_error": conservation_x,
        "system_y_conservation_error": conservation_y,
    }
    return rows, summary


def mean_and_half_width(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, 0.0, 0.0
    standard_error = statistics.stdev(values) / math.sqrt(len(values))
    return mean, standard_error, 1.96 * standard_error


def aggregate_summaries(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[float, str], list[dict[str, Any]]] = defaultdict(list)
    for summary in summaries:
        grouped[(float(summary["shock_log_return"]), str(summary["scenario"]))].append(summary)
    rows: list[dict[str, Any]] = []
    for (shock, scenario), group in sorted(grouped.items()):
        peaks = [float(item["maximum_absolute_log_error"]) for item in group]
        excesses = [float(item["maximum_excess_error"]) for item in group]
        depths = [float(item["minimum_geometric_depth"]) for item in group]
        return_ticks = [float(item["sustained_return_tick"]) for item in group if item["sustained_return_tick"] is not None]
        capacity = float(group[0]["arbitrage_capacity_fraction"])
        rows.append(
            {
                "shock_log_return": shock,
                "scenario": scenario,
                "lp_policy": group[0]["lp_policy"],
                "arbitrage_capacity_fraction": capacity,
                "seed_count": len(group),
                "mean_peak_absolute_log_error": statistics.mean(peaks),
                "median_peak_absolute_log_error": statistics.median(peaks),
                "p025_peak_absolute_log_error": quantile(peaks, 0.025),
                "p975_peak_absolute_log_error": quantile(peaks, 0.975),
                "mean_absolute_log_error": statistics.mean(
                    float(item["mean_absolute_log_error"]) for item in group
                ),
                "mean_max_excess_error": statistics.mean(excesses),
                "cumulative_excess_error": statistics.mean(
                    float(item["cumulative_excess_error"]) for item in group
                ),
                "return_to_band_rate": len(return_ticks) / len(group),
                "median_return_tick_when_observed": statistics.median(return_ticks) if return_ticks else None,
                "mean_minimum_geometric_depth": statistics.mean(depths),
                "lp_withdrawal_rate": statistics.mean(float(item["lp_withdrawal_applied"]) for item in group),
                "mean_noise_orders": statistics.mean(float(item["noise_orders"]) for item in group),
                "mean_trend_orders": statistics.mean(float(item["trend_orders"]) for item in group),
                "mean_panic_orders": statistics.mean(float(item["panic_orders"]) for item in group),
                "mean_arbitrage_orders": statistics.mean(float(item["arbitrage_orders"]) for item in group),
                "mean_capital_limited_orders": statistics.mean(float(item["capital_limited_orders"]) for item in group),
            }
        )
    return rows


def paired_rows_by_seed(
    summaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_key = {
        (float(item["shock_log_return"]), int(item["seed"]), str(item["scenario"])): item
        for item in summaries
    }
    output: list[dict[str, Any]] = []
    scenario_pairs = (
        ("E1-high-minus-off", "E1-arb-high-static", "E0-arb-off-static"),
        ("E1-high-minus-low", "E1-arb-high-static", "E1-arb-low-static"),
        ("E3-adaptive-minus-static", "E3-adaptive-lp-high-arb", "E1-arb-high-static"),
    )
    shocks = sorted({key[0] for key in by_key})
    seeds = sorted({key[1] for key in by_key})
    for shock in shocks:
        for seed in seeds:
            for contrast, first_name, second_name in scenario_pairs:
                first = by_key[(shock, seed, first_name)]
                second = by_key[(shock, seed, second_name)]
                first_tick = first["sustained_return_tick"]
                second_tick = second["sustained_return_tick"]
                output.append(
                    {
                        "shock_log_return": shock,
                        "seed": seed,
                        "contrast": contrast,
                        "first_scenario": first_name,
                        "second_scenario": second_name,
                        "peak_error_difference_first_minus_second": float(
                            first["maximum_absolute_log_error"]
                        ) - float(second["maximum_absolute_log_error"]),
                        "mean_absolute_error_difference_first_minus_second": float(
                            first["mean_absolute_log_error"]
                        ) - float(second["mean_absolute_log_error"]),
                        "cumulative_excess_error_difference_first_minus_second": float(
                            first["cumulative_excess_error"]
                        ) - float(second["cumulative_excess_error"]),
                        "max_excess_error_difference_first_minus_second": float(
                            first["maximum_excess_error"]
                        ) - float(second["maximum_excess_error"]),
                        "minimum_depth_difference_first_minus_second": float(
                            first["minimum_geometric_depth"]
                        ) - float(second["minimum_geometric_depth"]),
                        "return_tick_difference_first_minus_second": (
                            int(first_tick) - int(second_tick)
                            if first_tick is not None and second_tick is not None
                            else None
                        ),
                    }
                )
    return output


def aggregate_paired_effects(
    paired: list[dict[str, Any]], target_half_width: float
) -> list[dict[str, Any]]:
    grouped: dict[tuple[float, str], list[dict[str, Any]]] = defaultdict(list)
    for item in paired:
        grouped[(float(item["shock_log_return"]), str(item["contrast"]))].append(item)
    output: list[dict[str, Any]] = []
    for (shock, contrast), group in sorted(grouped.items()):
        peak = [float(item["peak_error_difference_first_minus_second"]) for item in group]
        mean_absolute = [
            float(item["mean_absolute_error_difference_first_minus_second"])
            for item in group
        ]
        cumulative_excess = [
            float(item["cumulative_excess_error_difference_first_minus_second"])
            for item in group
        ]
        excesses = [float(item["max_excess_error_difference_first_minus_second"]) for item in group]
        depths = [float(item["minimum_depth_difference_first_minus_second"]) for item in group]
        return_diffs = [
            float(item["return_tick_difference_first_minus_second"])
            for item in group
            if item["return_tick_difference_first_minus_second"] is not None
        ]
        mean, standard_error, half_width = mean_and_half_width(peak)
        mean_absolute, mean_absolute_se, mean_absolute_half_width = mean_and_half_width(
            mean_absolute
        )
        cumulative, cumulative_se, cumulative_half_width = mean_and_half_width(
            cumulative_excess
        )
        output.append(
            {
                "shock_log_return": shock,
                "contrast": contrast,
                "seed_count": len(group),
                "mean_peak_error_difference": mean,
                "standard_error_peak_error_difference": standard_error,
                "approx_95pct_ci_low_peak_error_difference": mean - half_width,
                "approx_95pct_ci_high_peak_error_difference": mean + half_width,
                "approx_95pct_ci_half_width_peak_error_difference": half_width,
                "mean_absolute_error_difference": mean_absolute,
                "approx_95pct_ci_low_mean_absolute_error_difference": (
                    mean_absolute - mean_absolute_half_width
                ),
                "approx_95pct_ci_high_mean_absolute_error_difference": (
                    mean_absolute + mean_absolute_half_width
                ),
                "cumulative_excess_error_difference": cumulative,
                "approx_95pct_ci_low_cumulative_excess_error_difference": (
                    cumulative - cumulative_half_width
                ),
                "approx_95pct_ci_high_cumulative_excess_error_difference": (
                    cumulative + cumulative_half_width
                ),
                "precision_target": target_half_width,
                "precision_target_met": half_width <= target_half_width,
                "mean_max_excess_error_difference": statistics.mean(excesses),
                "mean_minimum_depth_difference": statistics.mean(depths),
                "median_return_tick_difference_when_observed": statistics.median(return_diffs) if return_diffs else None,
            }
        )
    return output


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(config_path: Path, output_root: Path) -> Path:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    validate(config)
    source = Path(__file__).read_bytes()
    mechanics_source = (HERE / "run.py").read_bytes()
    run_hash = sha256_bytes(config_bytes + source + mechanics_source)[:12]
    run_id = f"cex-dex-abm-{run_hash}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rep = config["replication"]
    min_seeds = int(rep["minimum_seed_count"])
    batch_size = int(rep["seed_batch_size"])
    max_seeds = int(rep["maximum_seed_count"])
    target = float(rep["target_95pct_half_width_peak_error"])
    capacities = config["arbitrage_capacity_fractions"]
    conditions = (
        ("E0-arb-off-static", float(capacities["off"]), False),
        ("E1-arb-low-static", float(capacities["low"]), False),
        ("E1-arb-high-static", float(capacities["high"]), False),
        ("E3-adaptive-lp-high-arb", float(capacities["high"]), True),
    )
    shocks = [float(value) for value in config["shock_log_returns"]]
    all_summaries: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    seed_count = 0
    precision_rows: list[dict[str, Any]] = []

    while seed_count < max_seeds:
        batch_end = min(seed_count + batch_size, max_seeds)
        for seed in range(seed_count, batch_end):
            noise_schedule = make_noise_schedule(config, seed)
            for shock in shocks:
                for scenario, capacity, adaptive_lp in conditions:
                    rows, summary = run_condition(
                        config,
                        shock,
                        seed,
                        scenario,
                        capacity,
                        adaptive_lp,
                        noise_schedule,
                    )
                    all_rows.extend(rows)
                    all_summaries.append(summary)
        seed_count = batch_end
        paired = paired_rows_by_seed(all_summaries)
        precision_rows = aggregate_paired_effects(paired, target)
        if seed_count >= min_seeds and all(
            bool(item["precision_target_met"]) for item in precision_rows
        ):
            break

    summary_rows = aggregate_summaries(all_summaries)
    paired = paired_rows_by_seed(all_summaries)
    precision_rows = aggregate_paired_effects(paired, target)
    seeds = [{"seed": seed} for seed in range(seed_count)]

    (run_dir / "config.json").write_bytes(config_bytes)
    write_csv(run_dir / "timeseries.csv", TIME_SERIES_FIELDS, all_rows)
    write_csv(run_dir / "summary.csv", SUMMARY_FIELDS, summary_rows)
    write_csv(run_dir / "paired_effects.csv", PAIRED_FIELDS, paired)
    write_csv(run_dir / "paired_effects_summary.csv", PAIRED_SUMMARY_FIELDS, precision_rows)
    write_csv(run_dir / "replication_seeds.csv", ["seed"], seeds)

    artifacts = (
        "config.json",
        "timeseries.csv",
        "summary.csv",
        "paired_effects.csv",
        "paired_effects_summary.csv",
        "replication_seeds.csv",
    )
    metadata = {
        "run_id": run_id,
        "model_version": config["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "config_sha256": sha256_bytes(config_bytes),
        "abm_runner_sha256": sha256_bytes(source),
        "mechanics_runner_sha256": sha256_bytes(mechanics_source),
        "randomness": "one pre-generated Bernoulli/direction stream per seed, shared by paired conditions",
        "seed_count": seed_count,
        "shock_conditions": shocks,
        "scenario_count": len(summary_rows),
        "precision_target_peak_error_ci_half_width": target,
        "precision_target_met_for_all_paired_contrasts": all(
            bool(item["precision_target_met"]) for item in precision_rows
        ),
        "precision_interval": "normal approximation: paired mean +/- 1.96 standard errors; exploratory selection output",
        "selection_only": True,
        "confirmation_configurations_included": False,
        **git_context(),
        "artifact_sha256": {
            name: sha256_bytes((run_dir / name).read_bytes()) for name in artifacts
        },
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_ABM_OUTPUT)
    args = parser.parse_args()
    run_dir = run(args.config.resolve(), args.output.resolve())
    metadata = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
    print(
        f"Wrote stochastic CEX/DEX selection run to {run_dir} "
        f"({metadata['seed_count']} seeds; precision target met: "
        f"{metadata['precision_target_met_for_all_paired_contrasts']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
