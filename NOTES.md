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

## Phase 2
- THEORY.md: open-loop reduction, Theorem l <= 2 (Ana targets V = 1 + a_1 + ... + a_T: guess V at turn T+1, then V + a_n and V - a_n at every later turn n), so the answer is 1 or 2; Bob beats one guess only with an uncountable family of covering walks; spread(mu) < 1 is a sufficient certificate for Bob (exact rationals, the sum can be exactly 1).
- Solver: `--check a` (walks, spread, l*(a)), `--search L` simulated annealing over witness walks with `--steps-max B` (any N distinct steps <= B, as in the real game) and `--late-cover K` (must visit the K smallest values unreachable before t0, the targets of the theorem); `--t0`/`--cover` take lists. Tests cover the certificate, the exact-1 corner and the search.
- Exhaustive N <= 9: l*(N, t0=2) = 1 for N >= 4; without coverage l* = 2 at t0 = 3 (N = 6..9), 3 at t0 = 4 (N = 8, 9); with K >= t0 - 1 (N <= 9) l* = 1 everywhere.
- Annealing N = 10..16, free steps <= 2N: Bob beats one guess with K = 0 or a single late target; with two unreachable targets (late-cover 2, or K >= t0 - 1) no sequence beating one guess was found in any run.
- Open: whether the second unreachable target still wins for Ana with unbounded turns (answer 1) or T >> 1 lets Bob keep dodging (answer 2); conjecture 2, weakly. Phase 3 candidates: a Bob construction with increasing steps after T (THEORY.md section 6), or an Ana argument from two targets; Lean work should start from Theorem 2 (the upper bound is short and self-contained).

## Phase 3
- Branch starts from phase 2's commits (8ea52c8, bf4072f), which PR #2 had squash-merged without; the Lean toolchain comes from the GitHub release tarball (`elan` cannot download: release.lean-lang.org is blocked) and is linked with `elan toolchain link`.
- Lean: `lean/Passcode/TwoGuesses.lean` formalises Theorem 2 (`two_guesses_suffice`: a valid schedule with <= 2 guesses per turn hits every covering walk) in core Lean 4 with no Mathlib import, so `cd lean && lake build` finishes in seconds; the full Mathlib source build (hours on 4 cores) is not needed for it.
- Theorem 3 (THEORY.md section 9): without the covering condition no finite l works for T >= 15 (powers of two on turns 0 mod 4, lifts 3*4^n, fillers elsewhere; 2^floor(n/4) distinct positions per turn, spread <= 8 l 2^-floor((T+1)/4)); `solver/passcode_solver.py --construction N --t0 t0` checks it and, for N <= 14, the exact l*(a). So the whole difficulty is coverage versus spread.
- Section 8 (guard calculus): a one-guess schedule built from the guards of one target is arrival mode then departure mode; two downward forks plus one from-below arrival beat it; parity lets one guess per turn run departure guards for two targets at once, so the obstruction is downward departures, not the number of targets.
- Section 10: `solver/sweep_window.py` shows local sweeps are rigid (#walks ~ 3^slack, independent of N), so Bob's branching must come from the order of sweeps; proposed "formation walks" (branches at P(n) + sum eps_i u_i(n), common sweeps, swap-gadget transitions) give spread for free and reduce the answer-2 direction to the formation problem (every branch must eventually sweep every interval). Conjecture still 2, weakly; phase 4: attack the formation problem, or prove it impossible (Ana, answer 1).
