#!/usr/bin/env python3
"""Formation-window experiment (THEORY.md, section 13).

Run: python3 solver/formation_window.py 0,1,2 8,10,12,14,16
Environment: EARLY=1 (default) forces bit i to be introduced on step i+1;
MINCOMMON=c requires at least c common moves.

k bits, 2^k tokens (branches).  Steps 1..N in order.  Each step is either
common (all tokens move by +-n) or bit i (token eps moves by eps_i * s * n).
All tokens start at 0.  A token's positions must be pairwise distinct.
Goal: every token visits every value of [-m, m].  Report the largest m
feasible for given N, k (E(N,k)); with k = 0 this is N // 2 (the zig-zag).
"""
import sys, itertools, time, os
EARLY = os.environ.get("EARLY", "1") == "1"
MINCOMMON = int(os.environ.get("MINCOMMON", "0"))

def search(N, k, m, limit_nodes=None):
    tokens = list(itertools.product((1, -1), repeat=k))
    K = len(tokens)
    req = set(range(-m, m + 1)) - {0}
    pos = [0] * K
    visited = [{0} for _ in range(K)]
    missing = [len(req)] * K
    labels = []
    nodes = [0]

    moves = [("c", 1), ("c", -1)] + [("b", (i, s)) for i in range(k) for s in (1, -1)]

    def rec(n):
        nodes[0] += 1
        if limit_nodes and nodes[0] > limit_nodes:
            raise TimeoutError
        rem = N - n + 1
        for j in range(K):
            if missing[j] > rem:
                return False
        if n > N:
            used = {l[1][0] for l in labels if l[0] == "b"}
            ncommon = sum(1 for l in labels if l[0] == "c")
            return (all(x == 0 for x in missing) and len(used) == k and len(set(pos)) == K
                    and ncommon >= MINCOMMON)
        # every bit must still be introducible: bits not yet used need a step
        unused_bits = k - len({l[1][0] for l in labels if l[0] == "b"})
        if unused_bits > rem:
            return False
        for kind, par in moves:
            if EARLY and n <= k and (kind != "b" or par != (n - 1, 1)):
                continue  # bits introduced immediately: step i is bit i-1
            if kind == "c":
                deltas = [par * n] * K
            else:
                i, s = par
                deltas = [tokens[j][i] * s * n for j in range(K)]
            # symmetry breaking: the first move of bit i must be with s = +1,
            # and bits must be introduced in order
            if kind == "b":
                i, s = par
                if s == -1 and not any(l[0] == "b" and l[1][0] == i for l in labels):
                    continue
                if i > 0 and not any(l[0] == "b" and l[1][0] == i - 1 for l in labels):
                    continue
            new = [pos[j] + deltas[j] for j in range(K)]
            if any(new[j] in visited[j] for j in range(K)):
                continue
            for j in range(K):
                visited[j].add(new[j]); pos[j] = new[j]
                if new[j] in req: missing[j] -= 1
            labels.append((kind, par))
            if rec(n + 1):
                return True
            labels.pop()
            for j in range(K):
                visited[j].remove(new[j]); pos[j] -= deltas[j]
                if new[j] in req: missing[j] += 1
        return False

    ok = rec(1)
    return (ok, list(labels), nodes[0])

def E(N, k, limit_nodes=2_000_000):
    for m in range(N // 2, 0, -1):
        try:
            ok, labels, nodes = search(N, k, m, limit_nodes)
        except TimeoutError:
            return m, None, "timeout"
        if ok:
            return m, labels, nodes
    return 0, None, 0

if __name__ == "__main__":
    ks = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [0, 1, 2]
    Ns = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [8, 10, 12, 14, 16]
    for k in ks:
        for N in Ns:
            t = time.time()
            m, labels, nodes = E(N, k)
            lab = "".join(("+" if p == 1 else "-") if kd == "c" else (str(p[0]) if p[1] == 1 else chr(ord('a') + p[0]))
                          for kd, p in labels) if labels else "-"
            print(f"k={k} N={N}: E={m} (slack {N - 2*m}) nodes={nodes} {time.time()-t:.1f}s labels={lab}")
            sys.stdout.flush()
