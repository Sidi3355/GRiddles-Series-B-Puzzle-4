"""Tests for the finite-analogue solver (run: python3 -m unittest discover solver)."""

import itertools
import unittest

from passcode_solver import (
    bob_beats,
    find_schedule,
    forced_up_walks,
    is_free_turn,
    must_set,
    no_cover_bound,
    no_cover_sequence,
    search_bob,
    spread,
    spread_exact,
    hits_all,
    min_guesses,
    sequences_with_walks,
    solve,
    valid_walks,
)
from sweep_window import concentration_profile, is_zigzag, window_walks
from formation_window import E as formation_E
from multi_walk_greedy import run as greedy_run
from rectangle_tiling import solve as rectangle_solve


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


class LateCoverTests(unittest.TestCase):
    def test_must_set(self):
        self.assertEqual(must_set((3, 1, 2, 5), first_turn=3, cover=2, late_cover=2),
                         {1, 2, 5, 6})                         # reach before turn 3 is 3+1 = 4
        self.assertEqual(must_set((3, 1, 2, 5), first_turn=1, cover=0, late_cover=1), {1})

    def test_valid_walks_with_must(self):
        # a = (3,1,2,5): reach before turn 3 is 4, late target 5 must be visited
        self.assertEqual(sorted(valid_walks((3, 1, 2, 5))),
                         [(3, 2, 4, 9), (3, 4, 2, 7), (3, 4, 6, 1), (3, 4, 6, 11)])
        self.assertEqual(valid_walks((3, 1, 2, 5), must={5}), [])
        self.assertEqual(valid_walks((3, 1, 2, 5), must={1}), [(3, 4, 6, 1)])
        self.assertEqual(sorted(valid_walks((3, 1, 2, 5), must={2, 4})), [(3, 2, 4, 9), (3, 4, 2, 7)])

    def test_search_with_late_cover_respects_targets(self):
        res = search_bob(8, first_turn=3, cover=0, guesses_per_turn=1,
                         iterations=100, restarts=1, seed=3, steps_max=16, late_cover=1)
        a = res["a"]
        self.assertIsNotNone(a)
        must = must_set(a, 3, 0, 1)
        self.assertTrue(all(must <= set(w) for w in valid_walks(a, must=must)))


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


class SpreadTests(unittest.TestCase):
    def test_spread_values(self):
        walks = [(3, 2, 4), (3, 4, 2), (3, 4, 6)]  # a = (3, 1, 2)
        self.assertAlmostEqual(spread(walks, 1, 1), 1 + 2 / 3 + 1 / 3)   # turn 1 is certain
        self.assertAlmostEqual(spread(walks, 2, 1), 1.0)
        self.assertAlmostEqual(spread(walks, 2, 2), 1 + 2 / 3)
        self.assertEqual(spread([], 2, 1), float("inf"))
        self.assertEqual(spread(walks, 4, 1), 0.0)

    def test_spread_exactly_one_is_not_a_certificate(self):
        # a = (3,4,2,1,5), t0 = 3: spread is exactly 1/2 + 1/3 + 1/6 = 1 and Ana still wins
        walks = valid_walks((3, 4, 2, 1, 5))
        self.assertEqual(spread_exact(walks, 3, 1), 1)
        self.assertEqual(spread(walks, 3, 1), 1.0)
        self.assertLess(0.5 + 1 / 3 + 1 / 6, 1.0)          # naive float summation would round down
        self.assertIsNotNone(find_schedule(walks, 1, 3))
        self.assertFalse(bob_beats((3, 4, 2, 1, 5), 1, 3)[0])

    def test_certificate_is_sound(self):
        # spread < 1 must imply that the exact search finds no schedule
        for n in range(3, 8):
            for a, walks in sequences_with_walks(n):
                for t0 in (2, 3, 4):
                    if spread_exact(walks, t0, 1) < 1:
                        self.assertIsNone(find_schedule(walks, 1, t0), msg=f"a={a} t0={t0}")
                    beats, sp, nw = bob_beats(a, 1, t0)
                    self.assertEqual(beats, min_guesses(walks, t0)[0] != 1 and nw > 0,
                                     msg=f"a={a} t0={t0}")

    def test_search_finds_verified_sequence(self):
        res = search_bob(6, first_turn=3, cover=0, guesses_per_turn=1,
                         iterations=400, restarts=3, seed=1)
        self.assertTrue(res["beats"])                     # l*(6, t0=3) = 2 exhaustively
        self.assertTrue(bob_beats(res["a"], 1, 3)[0])
        res2 = search_bob(6, first_turn=3, cover=0, guesses_per_turn=1,
                          iterations=40, restarts=1, seed=2, steps_max=12)
        self.assertEqual(len(set(res2["a"])), 6)
        self.assertTrue(all(1 <= v <= 12 for v in res2["a"]))


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


class ConstructionTests(unittest.TestCase):
    """THEORY.md, Theorem 3: the no-coverage sequence beats any fixed l."""

    def test_sequence_shape(self):
        a = no_cover_sequence(40)
        self.assertEqual(len(set(a)), 40)
        free = [a[n - 1] for n in range(1, 41) if is_free_turn(n)]
        self.assertEqual(free, [2 ** k for k in range(10)])
        lifts = [a[n - 1] for n in range(1, 41) if n % 4 in (1, 2)]
        self.assertEqual(lifts, [3 * 4 ** n for n in range(1, 41) if n % 4 in (1, 2)])
        fillers = [a[n - 1] for n in range(1, 41) if n % 4 == 3]
        self.assertEqual(fillers, [3, 5, 6, 7, 9, 10, 11, 13, 14, 15])

    def test_family_is_valid_and_spread_out(self):
        for n in (12, 16, 20):
            a = no_cover_sequence(n)
            family = forced_up_walks(a)
            f = sum(1 for t in range(1, n + 1) if is_free_turn(t))
            self.assertEqual(len(family), 2 ** f)          # every sign choice is legal
            for w in family:                                # positive and pairwise distinct
                self.assertGreaterEqual(min(w), 1)
                self.assertEqual(len(set(w)), n)
            for t in range(1, n + 1):                       # 2^F(t) distinct positions at turn t
                f_t = sum(1 for m in range(1, t + 1) if is_free_turn(m))
                self.assertEqual(len({w[t - 1] for w in family}), 2 ** f_t)
            for t0 in (n // 2, n - 3):
                for l in (1, 2, 3):
                    self.assertLessEqual(spread_exact(family, t0, l), no_cover_bound(t0, n, l))

    def test_family_is_a_subfamily_of_valid_walks(self):
        a = no_cover_sequence(12)
        self.assertTrue(set(forced_up_walks(a)) <= set(valid_walks(a)))

    def test_bob_beats_one_guess_at_n_12(self):
        a = no_cover_sequence(12)
        walks = valid_walks(a)
        family = forced_up_walks(a)
        self.assertLess(spread_exact(family, 9, 1), 1)      # certificate for l = 1, t0 = 9
        self.assertIsNone(find_schedule(walks, 1, first_turn=9))
        self.assertGreater(min_guesses(walks, 9)[0], 1)     # (it is 4 over all 64 valid walks)


class SweepWindowTests(unittest.TestCase):
    def test_tight_window_forces_the_zigzag(self):
        for n in range(4, 15, 2):
            walks = window_walks(n, n // 2)
            self.assertEqual(len(walks), 2)
            self.assertTrue(all(is_zigzag(w) for w in walks))
            self.assertEqual(concentration_profile(walks), [0.5] * n)

    def test_counts_depend_on_the_slack_only(self):
        for slack, count in ((1, 6), (2, 16)):
            for n in (12, 14, 16):
                self.assertEqual(len(window_walks(n, n // 2 - slack)), count)

    def test_walks_are_valid(self):
        for w in window_walks(10, 3):
            self.assertEqual(len(set(w) | {0}), 11)
            self.assertEqual([abs(b - a) for a, b in zip((0,) + w[:-1], w)], list(range(1, 11)))
            self.assertTrue(set(range(-3, 4)) <= set(w) | {0})


class FormationTests(unittest.TestCase):
    def test_one_bit_formation_covers_a_window_only_as_a_mirror_pair(self):
        m, labels, _ = formation_E(12, 1)
        self.assertEqual(m, 6)                                   # perfect efficiency ...
        self.assertTrue(all(kind == "b" for kind, _ in labels))  # ... but only with bit moves (g = -f)

    def test_two_bit_formation_window_is_stuck(self):
        for n in (10, 12, 14):
            m, _, _ = formation_E(n, 2)
            self.assertEqual(m, 3)

    def test_rectangle_tilings(self):
        self.assertFalse(rectangle_solve(7, 2)[0])
        ok, rows = rectangle_solve(8, 2)
        self.assertTrue(ok)
        for col in range(4):
            self.assertEqual(sorted(r[col] for r in rows), list(range(1, 9)))

    def test_multi_walk_greedy_keeps_walks_distinct_and_covering(self):
        r = greedy_run(2, 150, 0)
        self.assertFalse(r["stuck"])
        self.assertGreater(min(r["front"]), 20)


if __name__ == "__main__":
    unittest.main()
