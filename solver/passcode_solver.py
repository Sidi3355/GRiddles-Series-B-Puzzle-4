#!/usr/bin/env python3
"""Finite-analogue solver for GRiddles Series B, Puzzle 4 (Ana/Bob passcode game).

Original game (G-Research, https://www.gresearch.com/griddles/series-b-puzzle-4/):

    Let l be a non-negative integer.  Ana and Bob play a game.  To start, Bob
    publicly chooses a sequence (a_n)_{n>=1} containing every positive integer
    exactly once, and sets his starting passcode to 0.

    On each turn n = 1, 2, 3, ..., Bob updates his passcode by adding a_n to it
    or subtracting a_n from it.  The new passcode must be a positive integer not
    used as a passcode before.  If no valid move is possible, Ana wins.

    If n > T = 2026^2026^2026, Ana gets up to l guesses for Bob's passcode this
    turn.  She cannot repeat a guess across the entire game.  If a guess is
    correct, she wins.

    If the game goes on forever, Bob wins if every positive integer eventually
    appears as his passcode.  Otherwise, Ana wins.

    Find the smallest l for which Ana has a winning strategy.

Finite analogue F(N, t0, K, M) solved here
------------------------------------------
* Bob publicly picks a permutation a = (a_1, ..., a_N) of {1, ..., N}.
* p_0 = 0.  On turn n Bob sets p_n = p_{n-1} + a_n or p_{n-1} - a_n; p_n must be
  a positive integer (at most M if a cap M is given) not used before.
  Stuck => Ana wins.
* On every turn n >= t0 Ana gets up to l guesses (none on turns < t0).  A value
  may be guessed at most once in the whole game.  Correct guess => Ana wins.
* Bob wins iff he survives all N turns and every value in {1, ..., K} has
  appeared (K = 0: pure survival).  K plays the role of "every positive integer
  eventually appears"; t0 plays the role of the threshold T.

Degenerate corners (see tests): t0 = 1 makes l* = 1 for every N because
p_1 = a_1 is public; K = M = N forces the unique zig-zag walk 0, N, 1, N-1, ...
(a = N, N-1, ..., 1) so Bob has no freedom at all.

Why Ana's strategy is open-loop (a fixed guess schedule)
--------------------------------------------------------
Ana never learns anything except "all my guesses so far were wrong" (a correct
guess ends the game).  Given a, that information state is the same on every
branch of the game that is still running, so an Ana strategy is exactly a
schedule G = (G_{t0}, ..., G_N) of pairwise-disjoint guess sets with |G_n| <= l.
Bob wins against G iff some valid walk p satisfies p_n not in G_n for all n
(he may as well pick that walk from the start).  Hence

    l*(a) = min { l : there is a schedule G hitting every valid walk for a }
    l*(N) = max over a of l*(a)            (Bob chooses a first, publicly)

and Ana has a winning strategy in F(N, t0, K, M) with l guesses iff l >= l*(N).
Hitting every walk is a hitting-set problem with two side constraints: at most
l pairs (n, v) per turn n and at most one pair per value v.

Usage
-----
    python3 solver/passcode_solver.py --max-n 7                 # l*(N), N = 1..7, t0 = 2
    python3 solver/passcode_solver.py --n 6 --t0 2,3,4 --cover 0,2,4
    python3 solver/passcode_solver.py --n 6 --full              # distribution of l*(a)
    python3 solver/passcode_solver.py --n 6 --max-value 6 --cover 6   # degenerate

Standard library only.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple

Walk = Tuple[int, ...]          # (p_1, ..., p_N)
Schedule = Dict[int, Set[int]]  # turn n -> set of guessed values


# ----------------------------------------------------------------------------
# Walk enumeration
# ----------------------------------------------------------------------------

def _covered(walk: Sequence[int], cover: int) -> bool:
    return cover == 0 or set(range(1, cover + 1)) <= set(walk)


def valid_walks(a: Sequence[int], max_value: Optional[int] = None, cover: int = 0
                ) -> List[Walk]:
    """All sign choices for which Bob survives every turn of ``a`` and has
    visited every value in 1..cover by the end.

    A walk is the tuple (p_1, ..., p_N); p_0 = 0 is implicit.  Each p_n must be
    a positive integer, at most ``max_value`` if given, distinct from all
    earlier passcodes.
    """
    n_steps = len(a)
    out: List[Walk] = []
    path: List[int] = []
    used: Set[int] = {0}
    uncovered = cover  # number of values in 1..cover not yet visited

    def rec(pos: int, i: int, uncovered: int) -> None:
        if uncovered > n_steps - i:
            return
        if i == n_steps:
            out.append(tuple(path))
            return
        step = a[i]
        for nxt in (pos + step, pos - step):
            if nxt < 1 or nxt in used or (max_value is not None and nxt > max_value):
                continue
            used.add(nxt)
            path.append(nxt)
            rec(nxt, i + 1, uncovered - (1 if nxt <= cover else 0))
            path.pop()
            used.remove(nxt)

    rec(0, 0, uncovered)
    return out


def sequences_with_walks(n_steps: int, max_value: Optional[int] = None, cover: int = 0
                         ) -> Iterator[Tuple[Tuple[int, ...], List[Walk]]]:
    """Yield (a, valid_walks(a, max_value, cover)) for every permutation a of
    1..n_steps that admits at least one valid walk.

    The permutation is built one entry at a time while the set of live walk
    prefixes is tracked, so a prefix that already strands every walk is never
    extended.
    """
    prefix: List[int] = []
    unused_steps = set(range(1, n_steps + 1))

    def extend(w: Tuple[int, ...], step: int, remaining_after: int) -> Iterator[Tuple[int, ...]]:
        pos = w[-1] if w else 0
        for nxt in (pos + step, pos - step):
            if nxt < 1 or nxt in w or (max_value is not None and nxt > max_value):
                continue
            if cover:
                still_uncovered = cover - sum(1 for v in w if v <= cover) - (1 if nxt <= cover else 0)
                if still_uncovered > remaining_after:
                    continue
            yield w + (nxt,)

    def rec(live: List[Tuple[int, ...]]) -> Iterator[Tuple[Tuple[int, ...], List[Walk]]]:
        if len(prefix) == n_steps:
            yield tuple(prefix), list(live)
            return
        remaining_after = n_steps - len(prefix) - 1
        for step in sorted(unused_steps):
            new_live = [w2 for w in live for w2 in extend(w, step, remaining_after)]
            if not new_live:
                continue
            prefix.append(step)
            unused_steps.remove(step)
            yield from rec(new_live)
            unused_steps.add(step)
            prefix.pop()

    yield from rec([()])


# ----------------------------------------------------------------------------
# Ana's hitting-set problem
# ----------------------------------------------------------------------------

def hits_all(schedule: Schedule, walks: Sequence[Walk]) -> bool:
    """True iff every walk has some turn n with p_n in schedule[n]."""
    return all(any(w[n - 1] in vals for n, vals in schedule.items()) for w in walks)


def find_schedule(walks: Sequence[Walk], guesses_per_turn: int, first_turn: int = 2
                  ) -> Optional[Schedule]:
    """A guess schedule with <= ``guesses_per_turn`` guesses on each turn
    n >= ``first_turn`` (none earlier), no value guessed twice, that hits every
    walk in ``walks``; or None if no such schedule exists.

    Backtracking hitting set: repeatedly pick an un-hit walk with the fewest
    admissible (turn, value) pairs and branch on those pairs.
    """
    if not walks:
        return {}
    if guesses_per_turn <= 0:
        return None
    n_steps = len(walks[0])
    schedule: Schedule = {}
    used_values: Set[int] = set()

    def options(w: Walk) -> List[Tuple[int, int]]:
        opts = []
        for n in range(first_turn, n_steps + 1):
            v = w[n - 1]
            if v in used_values:
                continue
            if len(schedule.get(n, ())) >= guesses_per_turn:
                continue
            opts.append((n, v))
        return opts

    def rec(remaining: List[Walk]) -> bool:
        if not remaining:
            return True
        best_w: Optional[Walk] = None
        best_opts: List[Tuple[int, int]] = []
        for w in remaining:
            opts = options(w)
            if not opts:
                return False
            if best_w is None or len(opts) < len(best_opts):
                best_w, best_opts = w, opts
                if len(opts) == 1:
                    break
        for n, v in best_opts:
            schedule.setdefault(n, set()).add(v)
            used_values.add(v)
            still = [w for w in remaining if w[n - 1] != v]
            if rec(still):
                return True
            schedule[n].remove(v)
            if not schedule[n]:
                del schedule[n]
            used_values.remove(v)
        return False

    return schedule if rec(list(walks)) else None


def min_guesses(walks: Sequence[Walk], first_turn: int = 2, lower: int = 0
                ) -> Tuple[Optional[int], Optional[Schedule]]:
    """Smallest l >= ``lower`` for which a hitting schedule exists, with one
    such schedule.  Returns (None, None) when no l works, i.e. when there are
    walks but no turn >= first_turn on which Ana may guess.

    Otherwise l = number of walks always works: on turn N each walk can be hit
    by its own final value (walks sharing a final value share the guess)."""
    if not walks:
        return 0, {}
    n_steps = len(walks[0])
    if first_turn > n_steps:
        return None, None
    l = max(lower, 0)
    while l <= len(walks):
        sched = find_schedule(walks, l, first_turn)
        if sched is not None:
            return l, sched
        l += 1
    raise AssertionError("hitting-set search failed to terminate within the trivial bound")


# ----------------------------------------------------------------------------
# Whole-game solve
# ----------------------------------------------------------------------------

class Result:
    def __init__(self, n_steps: int, first_turn: int, cover: int, max_value: Optional[int]) -> None:
        self.n_steps = n_steps
        self.first_turn = first_turn
        self.cover = cover
        self.max_value = max_value
        self.ell: Optional[int] = 0       # l*(N); None = Bob wins for every l
        self.worst: List[Tuple[Tuple[int, ...], int]] = []  # (a, #walks) attaining l*(N)
        self.schedule: Optional[Schedule] = None   # optimal schedule vs worst[0]
        self.histogram: Counter = Counter()        # l*(a) -> count (only if full)
        self.sequences_with_walks = 0
        self.max_walks = 0
        self.elapsed = 0.0

    def params(self) -> str:
        m = "inf" if self.max_value is None else str(self.max_value)
        return f"N={self.n_steps} t0={self.first_turn} K={self.cover} M={m}"

    def summary(self) -> str:
        lines = [
            f"{self.params()}: l*(N) = {'unbounded' if self.ell is None else self.ell}   "
            f"[{self.sequences_with_walks} sequences admit a walk; "
            f"max #walks = {self.max_walks}; {self.elapsed:.1f}s]",
        ]
        if self.worst:
            a, nw = self.worst[0]
            lines.append(f"  worst a for Ana: {list(a)}  (#walks={nw}; "
                         f"{len(self.worst)} sequence(s) attain l*)")
            if self.schedule is not None:
                sched = ", ".join(f"t{n}:{sorted(v)}" for n, v in sorted(self.schedule.items()))
                lines.append(f"  optimal schedule vs it: {sched if sched else '(none needed)'}")
        if self.histogram:
            hist = ", ".join(f"l*={k}: {v}" for k, v in sorted(self.histogram.items(), key=str))
            lines.append(f"  distribution of l*(a) over all N! sequences: {hist}")
        return "\n".join(lines)


def solve(n_steps: int, first_turn: int = 2, cover: int = 0, max_value: Optional[int] = None,
          full: bool = False, keep_worst: int = 5) -> Result:
    """Compute l*(N) for the finite analogue F(N, t0, K, M).

    With ``full`` the exact l*(a) is computed for every a (for the histogram);
    otherwise a is skipped as soon as it is known not to beat the current best.
    """
    t_start = time.perf_counter()
    res = Result(n_steps, first_turn, cover, max_value)
    for a, walks in sequences_with_walks(n_steps, max_value, cover):
        res.sequences_with_walks += 1
        res.max_walks = max(res.max_walks, len(walks))
        if res.ell is None and not full:
            continue  # already unbounded; nothing can beat that
        if not full and find_schedule(walks, res.ell, first_turn) is not None:
            continue  # l*(a) <= current best; cannot raise it
        ell_a, sched = min_guesses(walks, first_turn, lower=0 if full else res.ell + 1)
        if full:
            res.histogram["unbounded" if ell_a is None else ell_a] += 1
        if res.ell is not None and (ell_a is None or ell_a > res.ell):
            res.ell = ell_a
            res.worst = [(a, len(walks))]
            res.schedule = sched
        elif ell_a == res.ell and len(res.worst) < keep_worst:
            res.worst.append((a, len(walks)))
    if full:
        total_perms = 1
        for k in range(2, n_steps + 1):
            total_perms *= k
        res.histogram[0] += total_perms - res.sequences_with_walks  # no walk => l*(a) = 0
    res.elapsed = time.perf_counter() - t_start
    return res


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _int_list(text: str) -> List[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Finite-analogue solver for the Ana/Bob passcode game (GRiddles B4).")
    ap.add_argument("--n", type=int, help="number of turns N (a is a permutation of 1..N)")
    ap.add_argument("--max-n", type=int, help="solve every N from 1 to this value")
    ap.add_argument("--t0", type=_int_list, default=[2],
                    help="first turn(s) on which Ana may guess, comma-separated (default 2)")
    ap.add_argument("--cover", type=_int_list, default=[0],
                    help="Bob must have visited 1..K by the end, comma-separated K (default 0)")
    ap.add_argument("--max-value", type=int, default=None,
                    help="largest allowed passcode M (default: unbounded)")
    ap.add_argument("--full", action="store_true",
                    help="compute l*(a) for every a and print its distribution")
    args = ap.parse_args(argv)
    if (args.n is None) == (args.max_n is None):
        ap.error("give exactly one of --n / --max-n")
    ns = [args.n] if args.n is not None else list(range(1, args.max_n + 1))
    for n in ns:
        for t0 in args.t0:
            for k in args.cover:
                res = solve(n, t0, k, args.max_value, args.full)
                print(res.summary())
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
