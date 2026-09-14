# GRiddles Series B, Puzzle 4 — the passcode game

Work towards a solution of [G-Research's GRiddles Series B, Puzzle 4](https://www.gresearch.com/griddles/series-b-puzzle-4/).

## The puzzle

Bob publicly chooses a sequence containing every positive integer exactly once
and starts with passcode 0. On turn *n* he adds or subtracts the *n*-th term;
the new passcode must be a positive integer he has not used before, and if no
move is possible Ana wins. After turn T = 2026^(2026^2026), Ana may make up to
ℓ guesses of the passcode each turn, never repeating a guess in the whole
game; a correct guess wins. If the game runs forever, Bob wins if and only if
every positive integer has appeared as a passcode. **What is the smallest ℓ
for which Ana has a winning strategy?**

## Answer and status

**ℓ = 2.**

| Claim | Status | Where |
|---|---|---|
| Two guesses per turn suffice for Ana | Proved (also checked in Lean 4) | `THEORY.md` §2, `lean/Passcode/TwoGuesses.lean` |
| One guess per turn does not suffice | Argued, one construction step left open | `THEORY.md` §12, `SUBMISSION.md` §2 |

The two-guess strategy: with V = 1 + a₁ + ⋯ + a_T, guess V on turn T+1, then
V + aₙ and V − aₙ on every later turn n. Bob cannot have reached V before
turn T, must visit it to win, and both exits from V are guessed.

The one-guess side reduces to exhibiting a sequence with a never-merging,
ever-branching family of covering walks; the required branching rate is only
one bit per doubling of the turn number, which the enormous T makes
sufficient. `THEORY.md` §12 gives the structural facts (why finite deadlines
mislead, mirror and non-mirror "debt-free" pairs of walks, the
reflection–translation family) and marks the lane-placement step that is not
yet written out.

## Repository layout

| Path | Contents |
|---|---|
| `SUBMISSION.md`, `SUBMISSION.pdf` | The solution in submission form (answer + proofs; the open step is marked ★) |
| `THEORY.md` | Full theory notes: reduction to schedules, Theorems 2 and 3, spread certificate, guard calculus, sweeps, phase-4 results |
| `NOTES.md` | Append-only log, five lines per phase |
| `solver/passcode_solver.py` | Finite-analogue solver: exhaustive hitting-set search, spread certificate, annealing over Bob sequences, Theorem 3 construction |
| `solver/sweep_window.py` | Rigidity of local sweeps with consecutive steps |
| `solver/pair_search.py` | Pairs of walks with a common step sequence: debt-free pairs (mirror / non-mirror) and the (empty) search for re-merging gadgets |
| `solver/make_submission_pdf.py` | Builds `SUBMISSION.pdf` (needs `reportlab` and the DejaVu fonts) |
| `lean/` | Lean 4 project; `Passcode/TwoGuesses.lean` formalises the two-guess theorem in core Lean, no Mathlib needed |

## Running things

```bash
cd solver && python3 -m unittest            # all solver tests (stdlib only)
python3 solver/passcode_solver.py --max-n 7  # l*(N) for the finite analogue
python3 solver/pair_search.py pairs --n 7 --b 9
python3 solver/pair_search.py merge --l 5 --b 12
cd lean && lake build                        # builds TwoGuesses.lean in seconds
```

The Lean toolchain is pinned in `lean/lean-toolchain`; `lakefile.toml` lists
Mathlib for `Basic.lean`, but `TwoGuesses.lean` imports nothing and builds
without it.
