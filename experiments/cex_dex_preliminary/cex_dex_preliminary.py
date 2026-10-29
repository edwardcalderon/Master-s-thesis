#!/usr/bin/env python3
"""Preliminary CEX/DEX ABM evidence for the thesis v2.0.

This is deliberately small and auditable. It does not forecast a real market.
It tests whether the proposed mechanisms have the direction and comparative
statics claimed in the manuscript under transparent synthetic scenarios.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Config:
    steps: int = 120
    x0: float = 10_000.0
    y0: float = 10_000.0
    cex0: float = 1.0
    gamma: float = 0.003
    arb_capacity_fraction: float = 0.03
    noise_sigma_fraction: float = 0.0015
    trend_strength: float = 0.10
    panic_strength: float = 0.22
    lp_adaptive: bool = False
    lp_trigger_return: float = 0.035
    lp_withdraw_fraction: float = 0.55
    shock_tick: int = 30
    shock_log_return: float = 0.0
    fixed_sell_tick: int | None = None
    fixed_sell_quantity: float = 0.0
    forced_sell_start: int | None = None
    forced_sell_end: int | None = None
    forced_sell_quantity: float = 0.0
    use_noise: bool = True
    use_trend: bool = True
    use_panic: bool = True


def amm_price(x: float, y: float) -> float:
    return y / x


def sell_x(x: float, y: float, quantity: float) -> tuple[float, float, float]:
    """Sell X into a constant-product AMM and return new reserves and log price impact."""
    q = max(0.0, quantity)
    before = np.log(amm_price(x, y))
    k = x * y
    x_new = x + q
    y_new = k / x_new
    impact = np.log(amm_price(x_new, y_new)) - before
    return x_new, y_new, impact


def buy_x(x: float, y: float, quantity: float) -> tuple[float, float, float]:
    """Buy X from a constant-product AMM and return new reserves and log price impact."""
    q = min(max(0.0, quantity), x * 0.80)
    before = np.log(amm_price(x, y))
    k = x * y
    x_new = x - q
    y_new = k / x_new
    impact = np.log(amm_price(x_new, y_new)) - before
    return x_new, y_new, impact


def signed_flow(x: float, y: float, sell_fraction: float) -> tuple[float, float, float]:
    """Positive flow sells X (DEX price down); negative flow buys X (DEX price up)."""
    if sell_fraction >= 0:
        return sell_x(x, y, sell_fraction * x)
    return buy_x(x, y, min(-sell_fraction * x, x * 0.50))


def apply_arbitrage(x: float, y: float, p_cex: float, gamma: float, cap: float) -> tuple[float, float, float, float]:
    """Move DEX price toward the no-arbitrage band using a bounded arbitrageur."""
    before_error = np.log(amm_price(x, y) / p_cex)
    if cap <= 0 or abs(before_error) <= gamma:
        return x, y, 0.0, before_error

    if before_error > gamma:
        # To reduce p_D, sell X. Target p_D = p_C * exp(gamma).
        needed_fraction = np.exp((before_error - gamma) / 2.0) - 1.0
        fraction = min(max(needed_fraction, 0.0), cap)
        x, y, _ = sell_x(x, y, x * fraction)
        signed_quantity = x * fraction
    else:
        # To increase p_D, buy X. Target p_D = p_C * exp(-gamma).
        needed_fraction = 1.0 - np.exp((before_error + gamma) / 2.0)
        fraction = min(max(needed_fraction, 0.0), cap)
        quantity = x * fraction
        x, y, _ = buy_x(x, y, quantity)
        signed_quantity = -quantity
    after_error = np.log(amm_price(x, y) / p_cex)
    return x, y, signed_quantity, after_error


def first_sustained_band_tick(error: np.ndarray, gamma: float, shock_tick: int, horizon: int = 8) -> float:
    for t in range(shock_tick, max(shock_tick, len(error) - horizon)):
        if np.all(np.abs(error[t : t + horizon]) <= gamma):
            return float(t - shock_tick)
    return np.nan


def run_once(config: Config, seed: int, experiment: str, variant: str) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    x, y = config.x0, config.y0
    p_cex = config.cex0
    previous_p_dex = amm_price(x, y)
    previous_p_cex = p_cex
    lp_withdrawn = False
    rows: list[dict] = []

    for tick in range(config.steps):
        cex_log_return = config.shock_log_return if tick == config.shock_tick else 0.0
        p_cex *= float(np.exp(cex_log_return))

        p_dex_before = amm_price(x, y)
        dex_return = float(np.log(p_dex_before / previous_p_dex))

        # Positive sell flow lowers the DEX price. Trend/panic rules are deliberately simple.
        noise_flow = float(rng.normal(0.0, config.noise_sigma_fraction)) if config.use_noise else 0.0
        trend_flow = config.trend_strength * max(0.0, -cex_log_return) if config.use_trend else 0.0
        panic_flow = config.panic_strength * max(0.0, -dex_return) if config.use_panic else 0.0
        forced_flow = 0.0
        if config.forced_sell_start is not None and config.forced_sell_end is not None:
            if config.forced_sell_start <= tick <= config.forced_sell_end:
                forced_flow = config.forced_sell_quantity / x

        raw_flow = noise_flow + trend_flow + panic_flow + forced_flow
        # Limit any individual combined flow to avoid reserve exhaustion.
        raw_flow = float(np.clip(raw_flow, -0.30, 0.30))
        x, y, ordinary_impact = signed_flow(x, y, raw_flow)

        fixed_trade_impact = 0.0
        if config.fixed_sell_tick == tick and config.fixed_sell_quantity > 0:
            x, y, fixed_trade_impact = sell_x(x, y, config.fixed_sell_quantity)

        # An adaptive LP withdraws only after observing the exogenous shock magnitude.
        if (
            config.lp_adaptive
            and not lp_withdrawn
            and abs(cex_log_return) >= config.lp_trigger_return
        ):
            x *= 1.0 - config.lp_withdraw_fraction
            y *= 1.0 - config.lp_withdraw_fraction
            lp_withdrawn = True

        error_before_arb = float(np.log(amm_price(x, y) / p_cex))
        x, y, arb_quantity, error_after_arb = apply_arbitrage(
            x, y, p_cex, config.gamma, config.arb_capacity_fraction
        )
        p_dex = amm_price(x, y)
        liquidity = float(np.sqrt(x * y))
        rows.append(
            {
                "experiment": experiment,
                "variant": variant,
                "seed": seed,
                "tick": tick,
                "p_cex": p_cex,
                "p_dex": p_dex,
                "error": error_after_arb,
                "error_before_arb": error_before_arb,
                "x": x,
                "y": y,
                "liquidity": liquidity,
                "net_sell_fraction": raw_flow,
                "buy_pressure_z": -raw_flow,
                "cex_log_return": cex_log_return,
                "ordinary_log_impact": ordinary_impact,
                "fixed_trade_log_impact": fixed_trade_impact,
                "arb_signed_quantity": arb_quantity,
                "lp_withdrawn": lp_withdrawn,
            }
        )
        previous_p_dex, previous_p_cex = p_dex, p_cex

    path = pd.DataFrame(rows)
    after = path[path.tick >= config.shock_tick]
    metrics = {
        "experiment": experiment,
        "variant": variant,
        "seed": seed,
        "max_abs_error_after_shock": float(after.error.abs().max()),
        "mean_abs_error_after_shock": float(after.error.abs().mean()),
        "time_to_sustained_band": first_sustained_band_tick(path.error.to_numpy(), config.gamma, config.shock_tick),
        "minimum_liquidity": float(path.liquidity.min()),
        "max_fixed_trade_abs_impact": float(path.fixed_trade_log_impact.abs().max()),
        "cascade_ticks_abs_return_gt_1pct": int((path.p_dex.pct_change().abs() > 0.01).sum()),
        "final_abs_error": float(abs(path.error.iloc[-1])),
    }
    return path, metrics


def median_path(paths: pd.DataFrame, experiment: str, variant: str) -> pd.DataFrame:
    data = paths[(paths.experiment == experiment) & (paths.variant == variant)]
    return data.groupby("tick", as_index=False).median(numeric_only=True)


def local_mechanism_diagnostics() -> pd.DataFrame:
    """Finite differences for the simulator's one-tick error map near a stated operating point."""
    rows = []
    for error0 in (-0.08, -0.04, 0.04, 0.08):
        for sell_fraction in (-0.006, 0.0, 0.006):
            x = 10_000.0 / np.sqrt(np.exp(error0))
            y = 10_000.0 * np.sqrt(np.exp(error0))
            x, y, _ = signed_flow(x, y, sell_fraction)
            e_before = float(np.log(amm_price(x, y)))
            x, y, _, e_after = apply_arbitrage(x, y, 1.0, gamma=0.003, cap=0.03)
            rows.append(
                {
                    "error_initial": error0,
                    "sell_fraction": sell_fraction,
                    "error_after_flow": e_before,
                    "error_after_arbitrage": e_after,
                    "contraction_ratio": abs(e_after) / max(abs(e_before), 1e-12),
                    "signed_excess_before": np.sign(e_before) * max(abs(e_before) - 0.003, 0.0),
                    "signed_excess_after": np.sign(e_after) * max(abs(e_after) - 0.003, 0.0),
                }
            )
    return pd.DataFrame(rows)


def build_experiments() -> list[tuple[str, str, Config]]:
    quiet = dict(noise_sigma_fraction=0.0, use_noise=False, use_trend=False, use_panic=False)
    base = Config(**quiet)
    return [
        ("E0", "arbitrage_active", replace(base, shock_log_return=-0.10, arb_capacity_fraction=0.03)),
        ("E0", "arbitrage_off", replace(base, shock_log_return=-0.10, arb_capacity_fraction=0.0)),
        ("E1", "high_capacity", replace(base, shock_log_return=-0.12, arb_capacity_fraction=0.08)),
        ("E1", "low_capacity", replace(base, shock_log_return=-0.12, arb_capacity_fraction=0.006)),
        (
            "E2",
            "lp_static",
            replace(base, shock_log_return=-0.08, arb_capacity_fraction=0.04, fixed_sell_tick=48, fixed_sell_quantity=500.0),
        ),
        (
            "E2",
            "lp_adaptive",
            replace(
                base,
                shock_log_return=-0.08,
                arb_capacity_fraction=0.04,
                lp_adaptive=True,
                fixed_sell_tick=48,
                fixed_sell_quantity=500.0,
            ),
        ),
        (
            "E3",
            "liquidity_static",
            replace(
                Config(),
                shock_log_return=-0.12,
                arb_capacity_fraction=0.015,
                forced_sell_start=38,
                forced_sell_end=55,
                forced_sell_quantity=135.0,
            ),
        ),
        (
            "E3",
            "liquidity_adaptive",
            replace(
                Config(),
                shock_log_return=-0.12,
                arb_capacity_fraction=0.015,
                lp_adaptive=True,
                forced_sell_start=38,
                forced_sell_end=55,
                forced_sell_quantity=135.0,
            ),
        ),
    ]


def plot_evidence(paths: pd.DataFrame, metrics: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    panels = [
        ("E0", ["arbitrage_active", "arbitrage_off"], "|log(pDEX/pCEX)|", "error"),
        ("E1", ["high_capacity", "low_capacity"], "|log(pDEX/pCEX)|", "error"),
        ("E2", ["lp_static", "lp_adaptive"], "Liquidity sqrt(xy)", "liquidity"),
        ("E3", ["liquidity_static", "liquidity_adaptive"], "DEX price", "p_dex"),
    ]
    colors = ["#1f77b4", "#d62728"]
    for ax, (experiment, variants, ylabel, column) in zip(axes.flat, panels):
        for variant, color in zip(variants, colors):
            subset = paths[(paths.experiment == experiment) & (paths.variant == variant)]
            grouped = subset.groupby("tick")[column]
            med = grouped.median()
            if column == "error":
                med = med.abs()
            q25 = grouped.quantile(0.25)
            q75 = grouped.quantile(0.75)
            if column == "error":
                q25 = q25.abs()
                q75 = q75.abs()
            ax.plot(med.index, med.values, label=variant.replace("_", " "), color=color, lw=2)
            ax.fill_between(med.index, q25.values, q75.values, color=color, alpha=0.16)
        shock_tick = int(subset.shock_tick.iloc[0]) if "shock_tick" in subset else 30
        ax.axvline(30, color="0.35", lw=1, ls="--", label="CEX shock")
        if experiment == "E2":
            ax.axvline(48, color="0.35", lw=1, ls=":", label="fixed sell")
        ax.set_title(experiment)
        ax.set_xlabel("tick")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.22)
        ax.legend(fontsize=8)
    fig.suptitle("Preliminary synthetic evidence: bounded mechanisms, not empirical validation", fontsize=12)
    fig.savefig(output, dpi=190)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("output/preliminary_simulations"))
    parser.add_argument("--seeds", type=int, default=100)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    all_paths: list[pd.DataFrame] = []
    all_metrics: list[dict] = []
    for experiment, variant, config in build_experiments():
        for seed in range(args.seeds):
            path, metrics = run_once(config, seed, experiment, variant)
            path["shock_tick"] = config.shock_tick
            all_paths.append(path)
            all_metrics.append(metrics)

    paths = pd.concat(all_paths, ignore_index=True)
    metrics = pd.DataFrame(all_metrics)
    diagnostics = local_mechanism_diagnostics()
    d_before = diagnostics.signed_excess_before.to_numpy()
    d_after = diagnostics.signed_excess_after.to_numpy()
    local_slope = float(np.dot(d_before, d_after) / np.dot(d_before, d_before))
    alpha_effective = float(1.0 - local_slope)
    paths.to_csv(args.output / "preliminary_trajectories.csv", index=False)
    metrics.to_csv(args.output / "preliminary_metrics.csv", index=False)
    diagnostics.to_csv(args.output / "local_map_diagnostics.csv", index=False)
    plot_evidence(paths, metrics, args.output / "preliminary_evidence.png")

    summary = (
        metrics.groupby(["experiment", "variant"])
        .agg(
            runs=("seed", "count"),
            max_abs_error_median=("max_abs_error_after_shock", "median"),
            mean_abs_error_median=("mean_abs_error_after_shock", "median"),
            time_to_band_median=("time_to_sustained_band", "median"),
            min_liquidity_median=("minimum_liquidity", "median"),
            fixed_trade_impact_median=("max_fixed_trade_abs_impact", "median"),
            cascade_ticks_median=("cascade_ticks_abs_return_gt_1pct", "median"),
        )
        .reset_index()
    )
    summary.to_csv(args.output / "preliminary_summary.csv", index=False)
    report = {
        "model_status": "synthetic mechanism check; not real-market validation",
        "seeds_per_variant": args.seeds,
        "summary": summary.to_dict(orient="records"),
        "local_map_excess_slope_k": local_slope,
        "local_effective_arbitrage_contraction_alpha": alpha_effective,
        "local_contraction_median": float(diagnostics.contraction_ratio.median()),
        "local_contraction_max": float(diagnostics.contraction_ratio.max()),
        "config_note": "The discrete map is anchored to AMM swaps and bounded arbitrage. It is a candidate abstraction, not a calibrated market law.",
    }
    (args.output / "preliminary_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.5f}"))
    print("\nLocal map diagnostics:")
    print(diagnostics.to_string(index=False, float_format=lambda x: f"{x:.5f}"))
    print(f"\nLocal excess-map slope k={local_slope:.6f}; effective alpha={alpha_effective:.6f}")


if __name__ == "__main__":
    main()
