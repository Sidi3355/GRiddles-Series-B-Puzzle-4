#!/usr/bin/env python3
"""Sweep-window experiment (THEORY.md, section 10).

Walks with steps 1, 2, ..., N taken in order from position 0, with pairwise
distinct positions, that visit every value of [-m, m] by time N.  Positions
may be negative: the start stands for a huge hidden position, so positivity
never binds and the only constraints are distinctness and local coverage.

This is the local picture of a covering walk whose steps grow: to fill an
interval the walk has to zig-zag through it (0, +1, -1, +2, -2, ... or its
mirror image), and the only freedom is the slack s = N - 2m, the number of
positions that may lie outside the interval.  The experiment measures how much
freedom the slack buys: the number of walks, the entropy per step, the
concentration max_v mu(p_n = v) at every time n under the uniform measure and
its tail sums (the spread of THEORY.md section 4).

Usage:
    python3 solver/sweep_window.py --n 12,16,20 --slack 0,1,2,3,4

Standard library only.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from typing import List, Optional, Sequence, Tuple

Walk = Tuple[int, ...]


def window_walks(n_steps: int, half_width: int, limit: Optional[int] = None) -> List[Walk]:
    """All walks p_1..p_N (p_0 = 0) with |p_n - p_{n-1}| = n, pairwise distinct
    positions (0 included), visiting every value of [-half_width, half_width]."""
    required = set(range(-half_width, half_width + 1)) - {0}
    out: List[Walk] = []
    path: List[int] = []
    visited = {0}

    def rec(pos: int, i: int, missing: int) -> None:
        if missing > n_steps - i:
            return
        if i == n_steps:
            out.append(tuple(path))
            return
        step = i + 1
        for nxt in (pos + step, pos - step):
            if nxt in visited:
                continue
            visited.add(nxt)
            path.append(nxt)
            rec(nxt, i + 1, missing - (1 if nxt in required else 0))
            path.pop()
            visited.remove(nxt)
            if limit is not None and len(out) >= limit:
                return

    rec(0, 0, len(required))
    return out


def concentration_profile(walks: Sequence[Walk]) -> List[float]:
    """max_v mu(p_n = v) for n = 1..N under the uniform measure on ``walks``."""
    n_steps = len(walks[0])
    prof = []
    for n in range(1, n_steps + 1):
        counts = Counter(w[n - 1] for w in walks)
        prof.append(max(counts.values()) / len(walks))
    return prof


def is_zigzag(walk: Walk) -> bool:
    """True iff the walk is 0, +1, -1, +2, -2, ... or its mirror image."""
    zig = tuple((k + 1) // 2 * (1 if k % 2 == 1 else -1) for k in range(1, len(walk) + 1))
    return walk == zig or walk == tuple(-x for x in zig)


def report(n_steps: int, slack: int) -> str:
    half = n_steps // 2 - slack
    if half < 1:
        return f"N={n_steps} slack={slack}: window too small"
    walks = window_walks(n_steps, half)
    if not walks:
        return f"N={n_steps} m={half} slack={slack}: no walks"
    prof = concentration_profile(walks)
    entropy = math.log2(len(walks)) / n_steps
    tails = {t0: sum(prof[t0 - 1:]) for t0 in (2, n_steps // 2, 3 * n_steps // 4)}
    tail_txt = ", ".join(f"t0={k}: {v:.2f}" for k, v in tails.items())
    return (f"N={n_steps} m={half} slack={slack}: #walks={len(walks)} "
            f"entropy/step={entropy:.3f} spread tails {{{tail_txt}}}\n"
            f"  max atom by turn: {' '.join(f'{x:.2f}' for x in prof)}")


def _int_list(text: str) -> List[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Sweep-window experiment for the passcode game.")
    ap.add_argument("--n", type=_int_list, default=[12, 16, 20], help="numbers of steps N")
    ap.add_argument("--slack", type=_int_list, default=[0, 1, 2, 3, 4],
                    help="slack s = N - 2m (positions allowed outside the window)")
    args = ap.parse_args(argv)
    for n in args.n:
        for s in args.slack:
            print(report(n, s))
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
