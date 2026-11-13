# H1c reduced-map selection and confirmation protocol

**Status:** executable protocol draft. The analysis is separate from the thesis's
preliminary table and does not change manuscript claims.

## Selection data

Fit one local two-state map for each of the four model conditions using the versioned
stochastic selection run (`abm.py`, model 0.4.0). Selection uses CEX log shocks of
`-0.1` and `+0.1`, seeds from that run, and the configured capacities and LP condition.
The condition-specific fit avoids pooling parameters across distinct arbitrage and LP
rules.

Operationalize the state and input from recorded, observable model events:

- `d_t`: signed excess tracking error, `sign(e_t) max(|e_t| - gamma, 0)`.
- `z_t`: quote-valued net trader buying pressure during tick `t`, divided by initial
  `y` reserves. A buy-x order contributes its actual `y` input; a sell-x order subtracts
  its actual `x` input valued at the pool price immediately before that order. Noise,
  trend, and panic trader orders contribute; arbitrage does not.
- `u_t`: the CEX log-price return applied during tick `t`.

Estimate each operating condition by ordinary least squares without an intercept:

```text
d_(t+1) - u_(t+1) = a * d_t + beta * z_t + error_d
z_(t+1)             = c * d_t + rho * z_t + error_z

A = [[a, beta], [c, rho]]
alpha = 1 - a
chi   = -c
```

Report both equations' fit diagnostics and retain coefficients even when they fail the
Schur conditions. The map's local classification is **contractive** only when its
estimated spectral radius is below one (equivalently, all three 2x2 Schur inequalities
hold). This criterion is a diagnostic, not a stability guarantee for the ABM.

## Held-out confirmation data

Do not reuse selection seeds. The confirmation config fixes seeds 1000–1299 and CEX log
shocks `-0.05` and `+0.05`, which are absent from the selection set. It holds the
selected model's other parameters constant and applies each condition-specific matrix
without refitting.

For each held-out seed and condition, label observed error **contractive** when mean
absolute signed excess error over ticks 16–20 is below its mean over ticks 1–5;
otherwise label it **persistent**. Compare that condition's majority label with the
precomputed Schur label. Report the Wilson interval for the observed contraction share,
classification agreement, and one-step RMSE for `d` and `z`.

This first confirmation checks generalization to shock magnitude and new random streams
within the same representative-agent rules. It does not test new agent policies, fee
regimes, capacity levels, or live-market behavior. Mixed/noisy outcomes and disagreements
remain findings; do not revise the thresholds after inspecting the confirmation output.
