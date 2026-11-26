import Lake
open Lake DSL

package «amm-verification» where
  version := v!"0.1.0"
  fixedToolchain := true

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.35.0"

@[default_target]
lean_lib AmmVerification where
  roots := #[`AmmVerification]
