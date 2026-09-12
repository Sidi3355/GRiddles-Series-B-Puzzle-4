"""Rectangle-tiling search (THEORY.md, section 13): a V x 2^k array whose rows are
boxes {x + sum_i e_i o_i : e in {0,1}^k} with distinct even offsets o_i and whose
columns are permutations of 1..V.  Column e is branch e of a formation; a row is
one round in which every branch dips to its own value.  Run: python3 solver/rectangle_tiling.py"""
import sys, itertools
def solve(V, k, even=True):
    K = 2 ** k
    cols = [set() for _ in range(K)]
    rows = []
    def corners(x, offs):
        out = []
        for eps in itertools.product((0, 1), repeat=k):
            out.append(x + sum(e * o for e, o in zip(eps, offs)))
        return out
    def rec(r):
        if r == V:
            return True
        # smallest value not yet used by token 0 must be its value in some row; try it now
        x = min(set(range(1, V + 1)) - cols[0])
        step = 2 if even else 1
        rng = range(-(V - 1), V) 
        for offs in itertools.product([o for o in rng if o != 0 and o % step == 0], repeat=k):
            if len(set(offs)) < k:  # distinct offsets (else tokens coincide)
                continue
            vals = corners(x, offs)
            if len(set(vals)) < K or min(vals) < 1 or max(vals) > V:
                continue
            if any(vals[j] in cols[j] for j in range(K)):
                continue
            for j in range(K): cols[j].add(vals[j])
            rows.append(vals)
            if rec(r + 1): return True
            rows.pop()
            for j in range(K): cols[j].discard(vals[j])
        return False
    return rec(0), rows
if __name__ == "__main__":
      for k in (1, 2, 3):
        for V in range(2, 17):
            ok, rows = solve(V, k)
            print(f"k={k} V={V}: {'YES' if ok else 'no'} {rows if ok else ''}", flush=True)
            if ok and k >= 2: break
