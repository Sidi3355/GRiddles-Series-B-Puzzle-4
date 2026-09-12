#!/usr/bin/env python3
"""Long-horizon greedy (THEORY.md, section 13): can 2^k walks with a common
step sequence, pairwise distinct positions and every step size eventually used
all keep covering?  Run: python3 solver/multi_walk_greedy.py K STEPS [SEEDS]
(TRACE=n prints the first n moves).

Tokens eps in {+-1}^k (all start at 0, shared prefix until bits are introduced).
Each step: Bob picks an unused step size and a sign function on tokens
(common sign, or the sign of one bit, or the product of bits -- any character).
All tokens must land on fresh positive values.  Coverage progress is measured
by each token's frontier (smallest unvisited value).  We also force every step
size to be used eventually (smallest unused size must be used before it is
"overdue").  Reports frontier growth and position growth.
"""
import sys, random, itertools, os
TRACE = int(os.environ.get('TRACE', '0'))

def run(k, steps, seed, verbose=False, overdue=2.0):
    rng = random.Random(seed)
    tokens = list(itertools.product((1, -1), repeat=k))
    K = len(tokens)
    chars = [()] + [c for r in range(1, k + 1) for c in itertools.combinations(range(k), r)]
    pos = [0] * K
    vis = [set([0]) for _ in range(K)]
    front = [1] * K
    used = set()
    introduced = set()
    smallest_unused = 1
    hist = []
    for n in range(1, steps + 1):
        while smallest_unused in used:
            smallest_unused += 1
        # candidate sizes: overdue smallest size, distances to frontiers, random
        cands = []
        must_small = smallest_unused < n / overdue
        sizes = set()
        if must_small:
            sizes.add(smallest_unused)
        else:
            sizes.add(smallest_unused)
            for j in range(K):
                sizes.add(abs(pos[j] - front[j]))
            for _ in range(8):
                sizes.add(rng.randint(1, max(4, 2 * n)))
        for s in sizes:
            if s < 1 or s in used:
                continue
            for c in chars:
                for base in (1, -1):
                    signs = [base * (1 if sum(t[i] == -1 for i in c) % 2 == 0 else -1) for t in tokens]
                    new = [pos[j] + signs[j] * s for j in range(K)]
                    if any(v < 1 or v in vis[j] for j, v in enumerate(new)):
                        continue
                    pending = [i for i in range(k) if i not in introduced and n >= 6 * (i + 1)]
                    if pending and c != (pending[0],):
                        continue  # overdue bit must be introduced now
                    if len(introduced) == k and len(set(new)) < K:
                        continue  # tokens must stay at pairwise distinct positions
                    # score: frontier hits, then keep positions low, distinctness
                    hits = sum(1 for j, v in enumerate(new) if v == front[j])
                    holes = sum(1 for j, v in enumerate(new) if v < max(vis[j]))
                    distinct = len(set(new))
                    score = 100 * hits + 10 * holes + distinct - 0.001 * max(new)
                    if must_small and s != smallest_unused:
                        score -= 1000
                    cands.append((score, rng.random(), s, tuple(new), c))
        if not cands:
            for s in range(1, 4 * n + 4):
                if s in used:
                    continue
                for c in chars:
                    for base in (1, -1):
                        signs = [base * (1 if sum(t[i] == -1 for i in c) % 2 == 0 else -1) for t in tokens]
                        new = [pos[j] + signs[j] * s for j in range(K)]
                        if any(v < 1 or v in vis[j] for j, v in enumerate(new)):
                            continue
                        if len(introduced) == k and len(set(new)) < K:
                            continue
                        holes = sum(1 for j, v in enumerate(new) if v < max(vis[j]))
                        cands.append((10 * holes + len(set(new)) - 0.001 * max(new), rng.random(), s, tuple(new), c))
        if not cands:
            return dict(k=k, steps=n - 1, front=front, maxpos=max(max(v) for v in vis), stuck=True, hist=hist)
        cands.sort(reverse=True)
        _, _, s, new, _c = cands[0]
        used.add(s)
        introduced.update(cands[0][4])
        if TRACE and n <= TRACE:
            print(f'n={n:3d} size={s:4d} pos={new}')
        for j in range(K):
            pos[j] = new[j]
            vis[j].add(new[j])
            while front[j] in vis[j]:
                front[j] += 1
        if n % max(1, steps // 10) == 0:
            hist.append((n, min(front), max(front), smallest_unused, max(pos)))
            if verbose:
                print(f"  n={n} frontiers={front} smallest_unused_step={smallest_unused} maxpos={max(pos)}", flush=True)
    return dict(k=k, steps=steps, front=front, maxpos=max(pos), stuck=False, hist=hist)

if __name__ == "__main__":
    k = int(sys.argv[1]); steps = int(sys.argv[2]); seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    for seed in range(seeds):
        r = run(k, steps, seed)
        print(f"k={k} seed={seed}: steps={r['steps']} stuck={r['stuck']} min frontier={min(r['front'])} "
              f"frontiers={r['front'][:8]} maxpos={r['maxpos']}", flush=True)
        for h in r['hist']:
            print("   ", h)
