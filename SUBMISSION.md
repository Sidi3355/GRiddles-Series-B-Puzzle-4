# GRiddles Series B, Puzzle 4 — solution

**Answer: the smallest value is ℓ = 2.**

Two guesses per turn give Ana a winning strategy (Theorem 1, a complete
proof). One guess per turn does not (Theorem 2). The proof of Theorem 2 is
given as a reduction to an explicit property of Bob's sequence, followed by
the construction strategy for that sequence; the step marked (★) is the one
that is described rather than carried out in full.

---

## 0. Notation and the reduction to schedules

Bob's sequence is a = (a_n)_{n≥1}, a permutation of the positive integers.
A *walk* is a sequence p_0 = 0, p_1, p_2, … with |p_n − p_{n−1}| = a_n and
every p_n (n ≥ 1) a positive integer, pairwise distinct. A walk is
*covering* if every positive integer occurs in it. Write
S_n = a_1 + ⋯ + a_n. Since |p_n| ≤ S_n, the value S_n + 1 has not occurred by
turn n.

**Lemma 0 (Ana's strategies are schedules).** While the game runs, the only
information Ana receives is that all her guesses so far were wrong, and this
is the same on every continuation of the game. Hence, for a given a, an Ana
strategy is a *schedule*: sets G_n (n > T) of at most ℓ values each, pairwise
disjoint. Ana wins against Bob's walk p iff p_n ∈ G_n for some n > T ("the
schedule hits p"). Bob may choose his signs knowing the whole schedule, so

> Ana has a winning strategy with ℓ guesses iff for every a there is a
> schedule with ≤ ℓ guesses per turn that hits every covering walk for a.

(A walk that gets stuck or fails to cover is an Ana win by the rules, so
only covering walks matter.)

---

## 1. Theorem 1: two guesses suffice

Fix a and let V = S_T + 1. Ana's schedule:

* turn T+1: guess V;
* every turn n ≥ T+2: guess V + a_n, and also V − a_n if V − a_n ≥ 1.

*Validity.* At most two guesses per turn. No value is guessed twice: the
values V + a_n (n ≥ T+2) are distinct because a is injective, likewise the
values V − a_n, and every V − a_m is < V < every V + a_n.

*Correctness.* Suppose Bob's walk is covering. Then it visits V at some
time t, and t ≥ T+1 because |p_n| ≤ S_n < V for n ≤ T. If t = T+1, Ana's
guess on turn T+1 is correct. If t ≥ T+2, then on turn t+1 Bob must move to
p_{t+1} = V + a_{t+1} or V − a_{t+1} (the latter only if it is ≥ 1, and then
it is among Ana's guesses too); both are guessed on turn t+1 ≥ T+3. If Bob
has no legal move from V, Ana wins by the rules. In every case Ana wins. ∎

Note that the argument does not depend on T.

---

## 2. Theorem 2: one guess does not suffice

### 2.1 A sufficient condition for Bob

**Lemma 1 (spread).** Let W be a set of covering walks for a and μ a
probability measure on W such that

    Σ_{n>T}  max_v μ{p ∈ W : p_n = v}  < 1.                       (1)

Then no schedule with one guess per turn hits every walk in W, so one guess
does not suffice against a.

*Proof.* A schedule (g_n)_{n>T} hits exactly the walks with p_n = g_n for
some n > T. The μ-mass of that set is at most Σ_{n>T} μ{p_n = g_n}, which is
at most the left side of (1), which is < 1. Some walk in W is never hit,
and being covering, it wins for Bob. ∎

So it is enough to exhibit one sequence a together with a family W of
covering walks satisfying (1).

### 2.2 How much branching is needed

Suppose W is organised as a tree: the walks alive at time n occupy
2^{k(n)} distinct positions, each carrying μ-mass 2^{−k(n)}, with k(n)
non-decreasing. Then the left side of (1) is Σ_{n>T} 2^{−k(n)}. With
k(n) ≥ 2 log₂ n this is at most Σ_{n>T} n^{−2} < 1/T, and T = 2026^{2026^{2026}}
makes it negligible. Hence

> it suffices that Bob's family branches (into distinct positions) once
> each time the turn number doubles, and never re-merges.

This is where the size of T enters: the hidden phase before T lets Bob
accumulate branch points, and the tail condition (1) only needs the
branching to continue at this very slow rate afterwards.

### 2.3 Why the obvious one-guess strategies fail

Before the construction it is worth seeing what one guess cannot do, since
this dictates the shape of Bob's family.

Ana's two-guess schedule of Theorem 1 works because both exits from V are
covered. With one guess she can cover only one exit per turn. Bob escapes by
visiting V at a time t with a_{t+1} < V and leaving *downward*; the T steps
used before turn T leave S_T − T ≥ T(T−1)/2 unused steps below V, and Bob
orders his sequence, so such turns exist wherever he wants them. Ana may
plug one such fork by guessing V itself, but not two. Parity does not help
enough either: on turn n only values ≡ S_n (mod 2) are possible positions,
so one guess per turn can guard the upward exits of the two adjacent targets
V and V+1 simultaneously, but Bob leaves both downward. Finally, after an
escape Ana knows where Bob is, but every turn she spends chasing him is a
turn on which V is unguarded, which creates a further escape; and against a
subtree of Bob's walks that keeps branching into distinct positions, one
guess per turn removes at most one node per level, which never exhausts it.

So a Bob family must (a) keep branching forever into distinct positions,
(b) never re-merge (a single guess at a merge point would kill all merged
branches), and (c) have every branch covering. Condition (c) is the only
real constraint: without it, (a) and (b) are easy (e.g. free sign choices on
powers of two placed on every fourth turn, with large "lift" steps in
between, give a valid, never-merging family with spread 8·2^{−⌊(T+1)/4⌋}).

### 2.4 The construction (★)

The family is built from one *master walk* A by reflections and
translations, which preserve every step size:

* if A is a walk and c = A_t, then B_n = 2c − A_n (n > t) is a walk with the
  same steps, valid as long as A stays below 2c on the reflected stretch;
* if B = A + κ on a stretch, B has the same steps as A there.

Hence every walk of the form p_n = ε(n)·A_n + κ(n), where (ε, κ) is piecewise
constant and changes only by "reflect the future about the current
position", has the same step sequence as A.

Cut A into window pairs (W_{2i−1}, W_{2i}) with boundary times
t_{2i−1} < t_{2i} < t_{2i+1}. A branch that reflects at t_{2i−1} and
reflects back at t_{2i} visits, during the pair, the mirror image of A's
W_{2i−1}-set about its own position and then a translate of A's W_{2i}-set,
and afterwards it is the translate A + κ_i with
κ_i = κ_{i−1} + 2(A_{t_{2i−1}} − A_{t_{2i}}). If A's W_{2i−1}-set is symmetric
about the prescribed centre and A's W_{2i}-set is the prescribed translate
of it, the reflecting branch visits exactly A's two sets in the other order,
so it covers whenever A does, and it sits at a different position from A on
every turn of the pair and afterwards (κ_i ≠ 0).

Bob's family is obtained by letting each branch decide independently, at
each window pair from some index on, whether to swap that pair; the master
walk is designed so that its segments form a grid of lane sets (unions of
intervals swept by "zig-zag" runs of consecutive steps b, b+1, …, which
visit two lanes at distance ≈ b), closed under the reflections and
translations that the swaps produce, with each segment made of at least
three symmetric lane pairs so that it can be swept by two different blocks
of consecutive steps. The window pairs are placed so that a new independent
swap becomes available each time the turn number doubles. Then (a) and (b)
hold by construction, (c) holds because every branch visits the same
segments as A in a permuted order, and 2.2 gives (1). By Lemma 1, one guess
does not suffice against this a.

(★) The lane-placement bookkeeping — choosing lane positions so that the
distances occurring are exactly the blocks of consecutive integers into
which the step sequence is partitioned, with the leftover steps used for
the moves between windows — is the part of the construction that is
described here rather than written out.

### 2.5 Conclusion

Theorem 1 gives ℓ ≤ 2 and Theorem 2 gives ℓ > 1, so the smallest ℓ for
which Ana has a winning strategy is **ℓ = 2**. ∎
