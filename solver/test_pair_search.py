import unittest

from pair_search import debt_free_pairs, is_mirror, merge_gadgets


def valid_walk(steps, walk):
    pos, seen = 0, {0}
    for s, p in zip(steps, walk):
        if abs(p - pos) != s or p < 1 or p in seen:
            return False
        seen.add(p)
        pos = p
    return True


class PairSearchTests(unittest.TestCase):
    def test_mirror_example(self):
        a = [8, 7, 4, 10, 1, 3, 9]
        A = [8, 15, 11, 1, 2, 5, 14]
        B = [16 - p for p in A]
        self.assertTrue(valid_walk(a, A) and valid_walk(a, B))
        self.assertEqual(set(A), set(B))
        self.assertTrue(is_mirror(A, B))

    def test_non_mirror_example(self):
        a = [3, 1, 4, 2, 5, 8, 7]
        A = [3, 4, 8, 6, 1, 9, 2]
        B = [3, 2, 6, 4, 9, 1, 8]
        self.assertTrue(valid_walk(a, A) and valid_walk(a, B))
        self.assertEqual(set(A), set(B))
        self.assertTrue(all(x != y for x, y in zip(A[1:], B[1:])))
        self.assertFalse(is_mirror(A, B))

    def test_small_exhaustive_counts(self):
        pairs = list(debt_free_pairs(5, 7))
        for steps, pa, pb in pairs:
            self.assertTrue(valid_walk(steps, pa) and valid_walk(steps, pb))
            self.assertEqual(set(pa), set(pb))
            self.assertTrue(is_mirror(pa, pb))
        self.assertGreater(len(pairs), 0)

    def test_no_small_merge_gadget(self):
        self.assertEqual(sum(1 for _ in merge_gadgets(3, 8)), 0)
        self.assertEqual(sum(1 for _ in merge_gadgets(4, 8)), 0)


if __name__ == "__main__":
    unittest.main()
