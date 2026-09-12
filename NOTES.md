# NOTES (append-only, max 5 lines per phase)

## Phase 0
- Layout: solver/ (Python stdlib), lean/Passcode/ (Lean 4 + Mathlib v4.33.1, toolchain v4.33.1), NOTES.md.
- Mathlib cache hosts (cache.mathlib.org, lakecache.blob.core.windows.net) are blocked by egress policy; Mathlib is compiled from source (lean/.lake is gitignored).
- Modeling decision for phases 1-3: the threshold T = 2026^2026^2026 is a tail condition; the finite solver treats Ana as guessing from turn 1. This is the largest gap between the finite analogue and the real problem.

## Phase 1
- Solver: solver/passcode_solver.py (stdlib only); tests: `cd solver && python3 -m unittest`. Finite analogue F(N,t0,K,M): Bob's a is a permutation of 1..N, passcodes are positive integers (≤ M if capped), Ana guesses on turns ≥ t0, Bob must have visited 1..K by turn N.
- Reduction used: Ana learns nothing while the game runs, so her strategy is a fixed schedule of pairwise-disjoint guess sets; ℓ*(a) = min ℓ such that a schedule with ≤ ℓ guesses per turn hits every valid walk (hitting set), ℓ*(N) = max over a. Exhaustive over all N! sequences: N = 8 in seconds, N = 9 in about a minute per setting.
- Corrects the phase-0 note: guessing from turn 1 is degenerate (p_1 = a_1 is public, so ℓ* = 1 always) and K = M = N forces the unique zig-zag walk 0,N,1,N-1,...; a non-trivial analogue needs t0 ≥ 2 and K < N.
- Data (K=0, M=∞): ℓ*(N, t0=2) = ∞,2,2,1,1,1,1,1,1 for N=1..9 (worst a for N=3 is the swap gadget 3,1,2 with walks 3,2,4 / 3,4,2 / 3,4,6); ℓ* grows as t0 approaches N (N=7, t0=3..6 → 2,3,7,10) and falls with K (N=7, t0=6, K=0,2,4,6 → 10,4,2,1).
- Open for phase 2: is ℓ* bounded when N, t0 and K all grow together (the regime of the real game)? Needs search beyond N = 8 (symmetry / pruning / restricted Bob sequences).
