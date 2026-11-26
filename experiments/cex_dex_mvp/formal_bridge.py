"""Exact-rational reference operations for the Lean CPMM specification.

The functions deliberately mirror only the zero-fee reserve mechanics. They are a
test oracle for representative Python float results, not a proof that Python code
refines Lean for every possible input.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ExactPool:
    x: Fraction
    y: Fraction

    def __post_init__(self) -> None:
        if self.x <= 0 or self.y <= 0:
            raise ValueError("pool reserves must be positive")


def sell_x(pool: ExactPool, amount_x: Fraction) -> ExactPool:
    if amount_x < 0:
        raise ValueError("swap input must be nonnegative")
    return ExactPool(
        pool.x + amount_x,
        pool.y * pool.x / (pool.x + amount_x),
    )


def buy_x(pool: ExactPool, amount_y: Fraction) -> ExactPool:
    if amount_y < 0:
        raise ValueError("swap input must be nonnegative")
    return ExactPool(
        pool.x * pool.y / (pool.y + amount_y),
        pool.y + amount_y,
    )


def withdraw_proportionally(pool: ExactPool, remaining: Fraction) -> ExactPool:
    if not 0 < remaining <= 1:
        raise ValueError("remaining reserve fraction must be in (0, 1]")
    return ExactPool(remaining * pool.x, remaining * pool.y)


def price(pool: ExactPool) -> Fraction:
    return pool.y / pool.x
