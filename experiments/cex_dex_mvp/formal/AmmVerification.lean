module
public import Mathlib

public section

/-!
Exact rational specification of the zero-fee constant-product mechanics used by
`run.py`. These theorems state properties of this specification. The Python bridge
tests compare representative floating-point executions with this exact model; they do
not amount to a proof that arbitrary Python execution is refinement-correct.
-/

namespace CexDex

structure Pool where
  x : ℚ
  y : ℚ
deriving DecidableEq, Repr

def sellX (pool : Pool) (amountX : ℚ) : Pool :=
  ⟨pool.x + amountX, pool.y * pool.x / (pool.x + amountX)⟩

def buyX (pool : Pool) (amountY : ℚ) : Pool :=
  ⟨pool.x * pool.y / (pool.y + amountY), pool.y + amountY⟩

def withdrawProportionally (pool : Pool) (remaining : ℚ) : Pool :=
  ⟨remaining * pool.x, remaining * pool.y⟩

def price (pool : Pool) : ℚ := pool.y / pool.x

theorem sellX_preserves_product
    (pool : Pool) (amountX : ℚ)
    (hx : 0 < pool.x) (hy : 0 < pool.y) (ha : 0 ≤ amountX) :
    (sellX pool amountX).x * (sellX pool amountX).y = pool.x * pool.y := by
  have hden : pool.x + amountX ≠ 0 := ne_of_gt (by linarith)
  simp only [sellX]
  field_simp

theorem sellX_keeps_reserves_positive
    (pool : Pool) (amountX : ℚ)
    (hx : 0 < pool.x) (hy : 0 < pool.y) (ha : 0 ≤ amountX) :
    0 < (sellX pool amountX).x ∧ 0 < (sellX pool amountX).y := by
  have hden : 0 < pool.x + amountX := by linarith
  constructor
  · simp [sellX]
    linarith
  · simp [sellX]
    positivity

theorem buyX_preserves_product
    (pool : Pool) (amountY : ℚ)
    (hx : 0 < pool.x) (hy : 0 < pool.y) (ha : 0 ≤ amountY) :
    (buyX pool amountY).x * (buyX pool amountY).y = pool.x * pool.y := by
  have hden : pool.y + amountY ≠ 0 := ne_of_gt (by linarith)
  simp only [buyX]
  field_simp

theorem buyX_keeps_reserves_positive
    (pool : Pool) (amountY : ℚ)
    (hx : 0 < pool.x) (hy : 0 < pool.y) (ha : 0 ≤ amountY) :
    0 < (buyX pool amountY).x ∧ 0 < (buyX pool amountY).y := by
  have hden : 0 < pool.y + amountY := by linarith
  constructor
  · simp [buyX]
    positivity
  · simp [buyX]
    linarith

theorem proportional_withdrawal_preserves_price
    (pool : Pool) (remaining : ℚ)
    (hx : 0 < pool.x) (hy : 0 < pool.y) (hr : 0 < remaining) :
    price (withdrawProportionally pool remaining) = price pool := by
  have hx0 : pool.x ≠ 0 := ne_of_gt hx
  have hrx0 : remaining * pool.x ≠ 0 := ne_of_gt (mul_pos hr hx)
  simp only [price, withdrawProportionally]
  field_simp [hx0, hrx0]

theorem proportional_withdrawal_scales_product
    (pool : Pool) (remaining : ℚ) :
    (withdrawProportionally pool remaining).x *
      (withdrawProportionally pool remaining).y =
        remaining ^ 2 * (pool.x * pool.y) := by
  simp [withdrawProportionally]
  ring

/-! The next identities validate the polynomial expressions used for the
2×2 Jury/Schur diagnostic. They do not prove that those inequalities are equivalent
to spectral-radius stability; the current manuscript's theorem remains a cited,
mathematical result applied to the fitted linear map only.
-/

def schurLower (a beta c rho : ℝ) : ℝ :=
  1 - (a + rho) + (a * rho - beta * c)

def schurUpper (a beta c rho : ℝ) : ℝ :=
  1 + (a + rho) + (a * rho - beta * c)

def schurDeterminant (a beta c rho : ℝ) : ℝ :=
  1 - (a * rho - beta * c)

theorem schurLower_factorization (a beta c rho : ℝ) :
    schurLower a beta c rho = (1 - a) * (1 - rho) - beta * c := by
  simp [schurLower]
  ring

theorem schurUpper_factorization (a beta c rho : ℝ) :
    schurUpper a beta c rho = (1 + a) * (1 + rho) - beta * c := by
  simp [schurUpper]
  ring

theorem schurDeterminant_formula (a beta c rho : ℝ) :
    schurDeterminant a beta c rho = 1 - a * rho + beta * c := by
  simp [schurDeterminant]
  ring

end CexDex
