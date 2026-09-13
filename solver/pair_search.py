#!/usr/bin/env python3
"""Pairs of walks sharing one step sequence (THEORY.md, section 12).

Any Bob win against one guess needs at least two covering walks for the same
step sequence a.  Two such walks A, B satisfy |A_n - A_{n-1}| = |B_n - B_{n-1}|
= a_n for every n, so they differ only through sign choices.  This script
enumerates the finite building blocks such a pair must be made of:

* ``pairs``  debt-free pairs: N distinct steps <= B, two valid walks from 0
  that are at different positions on every turn >= t0 and have visited the
  SAME set of values after turn N (so neither owes the other anything).  Each
  pair is classified as a *mirror* pair (B_n = 2c - A_n from the split on,
  c = the common position just before the split: reflecting the future about
  the current position keeps every step size) or a non-mirror pair.

* ``merge``  re-merging gadgets: two walks with the same steps, opposite
  first sign, the same visited set AND the same final position (this would
  let a branch point be undone).  None exist for L <= 6 steps drawn from
  1..12; merging is fatal for Bob anyway (THEORY.md 12.3).

Usage:
    python3 solver/pair_search.py pairs --n 7 --b 9            # exhaustive
    python3 solver/pair_search.py pairs --n 9 --b 14 --cover 3 --limit 3 --random
    python3 solver/pair_search.py merge --l 5 --b 12

Standard library only.
"""

from __future__ import annotations

import argparse
import itertools
import random
from typing import Iterator, List, Optional, Sequence, Set, Tuple

Pair = Tuple[List[int], List[int], List[int]]  # (steps, walk A, walk B)


def is_mirror(pa: Sequence[int], pb: Sequence[int]) -> bool:
    """True iff B is the reflection of A about the position where they split."""
    k = next((j for j in range(len(pa)) if pa[j] != pb[j]), None)
    if k is None:
        return False
    c = pa[k - 1] if k > 0 else 0
    return all(pa[j] + pb[j] == 2 * c for j in range(k, len(pa)))


def debt_free_pairs(n_steps: int, max_step: int, first_turn: int = 2, cover: int = 0,
                    debt: int = 0, randomize: bool = False, node_limit: Optional[int] = None,
                    seed: int = 0) -> Iterator[Pair]:
    """Yield (a, A, B): distinct steps a_1..a_N in 1..max_step, two valid walks
    with p_0 = 0, positions distinct on every turn >= first_turn, both visiting
    1..cover, and |values visited by A only| <= debt at the end (debt = 0:
    identical visited sets).  Exhaustive unless node_limit is given."""
    rng = random.Random(seed)
    nodes = 0

    def rec(i: int, x: int, y: int, ux: Set[int], uy: Set[int], used: Set[int],
            steps: List[int], pa: List[int], pb: List[int]) -> Iterator[Pair]:
        nonlocal nodes
        nodes += 1
        if node_limit is not None and nodes > node_limit:
            return
        rem = n_steps - i
        if sum(1 for v in range(1, cover + 1) if v not in ux) > rem:
            return
        if sum(1 for v in range(1, cover + 1) if v not in uy) > rem:
            return
        if len(ux ^ uy) > 2 * rem + 2 * debt:
            return
        if i == n_steps:
            if len(ux ^ uy) <= 2 * debt:
                yield list(steps), list(pa), list(pb)
            return
        cand = [s for s in range(1, max_step + 1) if s not in used]
        if randomize:
            rng.shuffle(cand)
        for s in cand:
            for ex in (1, -1):
                nx = x + ex * s
                if nx < 1 or nx in ux:
                    continue
                for ey in (1, -1):
                    ny = y + ey * s
                    if ny < 1 or ny in uy:
                        continue
                    if i + 1 >= first_turn and nx == ny:
                        continue
                    used.add(s); ux.add(nx); uy.add(ny)
                    steps.append(s); pa.append(nx); pb.append(ny)
                    yield from rec(i + 1, nx, ny, ux, uy, used, steps, pa, pb)
                    steps.pop(); pa.pop(); pb.pop()
                    used.discard(s); ux.discard(nx); uy.discard(ny)

    yield from rec(0, 0, 0, {0}, {0}, set(), [], [], [])


def merge_gadgets(length: int, max_step: int) -> Iterator[Pair]:
    """Yield (steps, A, B): L distinct steps <= max_step, two walks from 0 with
    opposite first sign, no repeated position within a walk, the same visited
    set and the same final position.  Positivity is not required (translate)."""
    for steps in itertools.permutations(range(1, max_step + 1), length):
        for sa in itertools.product((1, -1), repeat=length - 1):
            a = [0]
            for s, e in zip(steps, (1,) + sa):
                a.append(a[-1] + e * s)
            if len(set(a)) < length + 1:
                continue
            for sb in itertools.product((1, -1), repeat=length - 1):
                b = [0]
                for s, e in zip(steps, (-1,) + sb):
                    b.append(b[-1] + e * s)
                if len(set(b)) < length + 1 or a[-1] != b[-1] or set(a) != set(b):
                    continue
                yield list(steps), a[1:], b[1:]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs")
    p.add_argument("--n", type=int, default=7)
    p.add_argument("--b", type=int, default=9)
    p.add_argument("--t0", type=int, default=2)
    p.add_argument("--cover", type=int, default=0)
    p.add_argument("--debt", type=int, default=0)
    p.add_argument("--limit", type=int, default=0, help="stop after this many pairs (0 = all)")
    p.add_argument("--random", action="store_true", help="randomised branch order")
    p.add_argument("--nodes", type=int, default=0, help="node limit (0 = exhaustive)")
    p.add_argument("--seed", type=int, default=0)
    m = sub.add_parser("merge")
    m.add_argument("--l", type=int, default=4)
    m.add_argument("--b", type=int, default=12)
    args = ap.parse_args()
    if args.cmd == "pairs":
        mirror = other = 0
        shown = 0
        for steps, pa, pb in debt_free_pairs(args.n, args.b, args.t0, args.cover, args.debt,
                                             args.random, args.nodes or None, args.seed):
            kind = "mirror" if is_mirror(pa, pb) else "non-mirror"
            if kind == "mirror":
                mirror += 1
            else:
                other += 1
            if shown < 10:
                shown += 1
                print(f"{kind}: a={steps} A={pa} B={pb} A-only={sorted(set(pa) - set(pb))}")
            if args.limit and mirror + other >= args.limit:
                break
        print(f"N={args.n} steps<={args.b} t0={args.t0} cover={args.cover} debt={args.debt}: "
              f"{mirror} mirror pairs, {other} non-mirror pairs")
    else:
        count = 0
        for steps, a, b in merge_gadgets(args.l, args.b):
            count += 1
            if count <= 10:
                print(f"steps={steps} A={a} B={b}")
        print(f"L={args.l} steps<={args.b}: {count} re-merging gadgets")


if __name__ == "__main__":
    main()
