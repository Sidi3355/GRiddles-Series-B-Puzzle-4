# NOTES (append-only, max 5 lines per phase)

## Phase 0
- Layout: solver/ (Python stdlib), lean/Passcode/ (Lean 4 + Mathlib v4.33.1, toolchain v4.33.1), NOTES.md.
- Mathlib cache hosts (cache.mathlib.org, lakecache.blob.core.windows.net) are blocked by egress policy; Mathlib is compiled from source (lean/.lake is gitignored).
- Modeling decision for phases 1-3: the threshold T = 2026^2026^2026 is a tail condition; the finite solver treats Ana as guessing from turn 1. This is the largest gap between the finite analogue and the real problem.
