"""Tests for the finite-analogue solver (run: python3 -m unittest discover solver)."""

import itertools
import unittest

from passcode_solver import (
    find_schedule,
    hits_all,
    min_guesses,
    sequences_with_walks,
    solve,
    valid_walks,
)


def brute_force_walks(a, max_value=None, cover=0):
    """Reference implementation: try all 2^N sign vectors."""
    out = []
    for signs in itertools.product((1, -1), repeat=len(a)):
        pos, seen, path, ok = 0, {0}, [], True
        for s, step in zip(signs, a):
            pos += s * step
            if pos < 1 or pos in seen or (max_value is not None and pos > max_value):
                ok = False
                break
            seen.add(pos)
            path.append(pos)
        if ok and set(range(1, cover + 1)) <= seen:
            out.append(tuple(path))
    return sorted(out)


def brute_force_min_guesses(walks, first_turn):
    """Reference implementation: enumerate every schedule up to the trivial bound."""
    if not walks:
        return 0
    n = len(walks[0])
    turns = list(range(first_turn, n + 1))
    if not turns:
        return None
    for ell in range(0, len(walks) + 1):
        per_turn = []
        for t in turns:
            cands = sorted({w[t - 1] for w in walks})
            per_turn.append([frozenset(c) for k in range(ell + 1)
                             for c in itertools.combinations(cands, k)])
        for choice in itertools.product(*per_turn):
            vals = [v for c in choice for v in c]
            if len(vals) != len(set(vals)):
                continue
            sched = {t: set(c) for t, c in zip(turns, choice) if c}
            if hits_all(sched, walks):
                return ell
    raise AssertionError("bound violated")


class WalkTests(unittest.TestCase):
    def test_hand_examples(self):
        self.assertEqual(valid_walks((3, 2, 1), max_value=3), [(3, 1, 2)])
        self.assertEqual(valid_walks((1, 2, 3), max_value=3), [])
        self.assertEqual(sorted(valid_walks((2, 1))), [(2, 1), (2, 3)])
        self.assertEqual(sorted(valid_walks((3, 1, 2))), [(3, 2, 4), (3, 4, 2), (3, 4, 6)])
        self.assertEqual(valid_walks((3, 1, 2), cover=1), [])      # 1 is never visited
        self.assertEqual(sorted(valid_walks((2, 1, 3))), [(2, 1, 4), (2, 3, 6)])
        self.assertEqual(valid_walks((2, 1, 3), cover=2), [(2, 1, 4)])
        self.assertEqual(valid_walks((2, 1, 3), cover=3), [])

    def test_matches_brute_force(self):
        for n in range(1, 6):
            for a in itertools.permutations(range(1, n + 1)):
                for max_value in (None, n, n + 2):
                    for cover in (0, 1, n - 1, n):
                        self.assertEqual(
                            sorted(valid_walks(a, max_value, cover)),
                            brute_force_walks(a, max_value, cover),
                            msg=f"a={a} M={max_value} K={cover}")

    def test_sequences_with_walks_matches_permutation_filter(self):
        for n in range(1, 6):
            for max_value in (None, n):
                for cover in (0, 2, n):
                    got = {a: sorted(w) for a, w in sequences_with_walks(n, max_value, cover)}
                    want = {}
                    for a in itertools.permutations(range(1, n + 1)):
                        w = brute_force_walks(a, max_value, cover)
                        if w:
                            want[a] = w
                    self.assertEqual(got, want, msg=f"N={n} M={max_value} K={cover}")

    def test_zigzag_is_the_only_full_cover_walk(self):
        # K = M = N: only a = (N, ..., 1) survives, with the unique walk 0,N,1,N-1,2,...
        for n in range(1, 8):
            seqs = list(sequences_with_walks(n, max_value=n, cover=n))
            self.assertEqual(len(seqs), 1)
            a, walks = seqs[0]
            self.assertEqual(a, tuple(range(n, 0, -1)))
            zig = [n - i // 2 if i % 2 == 0 else (i + 1) // 2 for i in range(n)]
            self.assertEqual(walks, [tuple(zig)])


class ScheduleTests(unittest.TestCase):
    def test_hand_examples(self):
        walks = [(3, 2, 4), (3, 4, 2), (3, 4, 6)]  # a = (3, 1, 2)
        self.assertIsNone(find_schedule(walks, 1, first_turn=2))
        sched = find_schedule(walks, 2, first_turn=2)
        self.assertIsNotNone(sched)
        self.assertTrue(hits_all(sched, walks))
        self.assertEqual(min_guesses(walks, first_turn=2), (2, {2: {2, 4}}))
        # guessing from turn 1 is trivial: p_1 = a_1 is public
        self.assertEqual(min_guesses(walks, first_turn=1)[0], 1)
        # no turn to guess on
        self.assertEqual(min_guesses(walks, first_turn=4), (None, None))
        self.assertEqual(min_guesses([], first_turn=9), (0, {}))

    def test_schedule_respects_constraints(self):
        for n in range(2, 6):
            for a, walks in sequences_with_walks(n):
                for t0 in (1, 2, 3):
                    ell, sched = min_guesses(walks, t0)
                    if ell is None:
                        self.assertGreater(t0, n)
                        continue
                    self.assertTrue(hits_all(sched, walks))
                    self.assertTrue(all(t >= t0 for t in sched))
                    self.assertTrue(all(len(v) <= ell for v in sched.values()))
                    vals = [v for s in sched.values() for v in s]
                    self.assertEqual(len(vals), len(set(vals)), "a value was guessed twice")

    def test_matches_brute_force(self):
        for n in range(1, 5):
            for cover in (0, n - 1):
                for a, walks in sequences_with_walks(n, cover=cover):
                    for t0 in (1, 2, 3):
                        self.assertEqual(min_guesses(walks, t0)[0],
                                         brute_force_min_guesses(walks, t0),
                                         msg=f"a={a} t0={t0} K={cover}")


class SolveTests(unittest.TestCase):
    def test_guessing_from_turn_one_is_trivial(self):
        for n in range(1, 6):
            self.assertEqual(solve(n, first_turn=1).ell, 1)

    def test_small_values(self):
        self.assertIsNone(solve(1).ell)                       # Ana never gets to guess
        self.assertEqual(solve(2).ell, 2)                     # a = (2, 1): p_2 in {1, 3}
        r = solve(3)
        self.assertEqual(r.ell, 2)
        self.assertEqual(r.worst[0][0], (3, 1, 2))            # swap gadget 3,2,4 / 3,4,2
        self.assertEqual(solve(n_steps=3, max_value=3, cover=3).ell, 1)  # forced zig-zag

    def test_full_histogram_counts_all_permutations(self):
        r = solve(4, full=True)
        self.assertEqual(sum(r.histogram.values()), 24)
        self.assertEqual(max(k for k in r.histogram if isinstance(k, int)), r.ell)
        r2 = solve(4)
        self.assertEqual(r2.ell, r.ell)


if __name__ == "__main__":
    unittest.main()
