# Theory notes for GRiddles Series B, Puzzle 4

Statement (G-Research, https://www.gresearch.com/griddles/series-b-puzzle-4/).
Let l >= 0. Bob publicly chooses a sequence (a_n)_{n>=1} containing every
positive integer exactly once and sets his passcode to p_0 = 0. On turn n Bob
sets p_n = p_{n-1} + a_n or p_{n-1} - a_n; p_n must be a positive integer that
has not been a passcode before, and Ana wins if no valid move exists. On every
turn n > T = 2026^(2026^2026) Ana may make up to l guesses of p_n; she may never
repeat a guess in the whole game; a correct guess wins for Ana. If the game
goes on forever, Bob wins iff every positive integer appears as a passcode.
Find the smallest l for which Ana has a winning strategy.

Throughout, a *walk* for a is a sequence p_0 = 0, p_1, p_2, ... with
|p_n - p_{n-1}| = a_n, all p_n (n >= 1) positive and pairwise distinct.
It is *covering* if {p_n : n >= 1} is the whole set of positive integers.
W(a) denotes the set of covering walks for a.

## 1. Ana's strategies are schedules (open-loop reduction)

While the game is running Ana has learned exactly one thing: every guess so far
was wrong (a correct guess ends the game). Given a, this information state is
identical on every branch that is still running, so an Ana strategy is nothing
more than a *schedule*: sets G_n (n > T) with |G_n| <= l and G_n pairwise
disjoint. Bob, who may fix his whole sign sequence in advance, beats the
schedule iff some walk p in W(a) has p_n not in G_n for every n > T (a walk that
gets stuck or fails to cover is an Ana win anyway).

Hence Ana has a winning strategy with l guesses iff for every a there is a
schedule with <= l guesses per turn *hitting* every covering walk, where G hits
p iff p_n in G_n for some n > T. This is the hitting-set problem solved by
`solver/passcode_solver.py` in its finite analogue.

## 2. Theorem: l = 2 suffices for Ana

Fix a. Let V = 1 + a_1 + ... + a_T. Ana's schedule:

* turn T+1: guess V;
* turn n >= T+2: guess V + a_n, and V - a_n if V - a_n >= 1.

Validity. All guesses are distinct: the values V + a_n are distinct because a
is injective, so are the values V - a_n, and V - a_m < V < V + a_n. At most
two guesses are made per turn.

Correctness. |p_n| <= a_1 + ... + a_n < V for n <= T, so V is unvisited at time
T. If Bob wins the game he visits V at some time t >= T+1. If t = T+1 the turn-
(T+1) guess is correct. Otherwise t >= T+2, and at turn t+1 >= T+3 Bob must
move to p_{t+1} = V + a_{t+1} or V - a_{t+1}; both are guessed on that turn (if
V - a_{t+1} < 1 that move is illegal anyway). So every covering walk is hit and
Ana wins. Therefore the answer is 1 or 2.

Remark: this argument does not use the size of T at all.

## 3. Bob needs uncountably many covering walks to beat l = 1

Lemma. If W(a) is countable then a schedule with one guess per turn hits all
of it. Proof: enumerate W(a) = {w_1, w_2, ...}. Pick turns T < n_1 < n_2 < ...
and guess w_i(n_i) at turn n_i, choosing n_i so large that w_i(n_i) differs
from the finitely many values already scheduled (possible because w_i is
injective, so only finitely many turns are excluded).

Consequently, if Bob beats l = 1, the tree of covering sign choices for his a
contains a perfect subtree: infinitely many branch points along every branch.
In particular, at every turn n > T at least two distinct positions p_n occur
among covering walks (otherwise Ana guesses the unique one). This is the
"never fully re-merge" constraint: any gadget whose branches re-merge at a
common position at a common time is useless for Bob.

## 4. A sufficient criterion for Bob: spread measures

Lemma. Suppose there is a probability measure mu on W(a) with

    sum_{n > T}  (sum of the l largest values of mu(p_n = v) over v)  < 1.

Then no schedule with l guesses per turn hits all of W(a), so l guesses do not
suffice for Ana against this a.
Proof: a schedule hits a walk only through some (n, v) with v in G_n, and the
mu-mass of walks passing through the chosen pairs is at most the sum above,
which is < 1; the remaining walks survive.

Counting version (used by the solver): with mu uniform on a finite family,
mu(p_n = v) = (#walks with p_n = v) / #walks. `spread(walks, t0, l)` computes
the sum and `spread < 1` certifies l*(a) > l without any hitting-set search.

Role of T. If Bob's tree branches roughly once every m steps and different
branches sit at different positions, then mu(p_n = v) is about 2^{-n/m} and the
sum over n > T is about m * 2^{-T/m}, which is < 1 as soon as T >> m log m.
So an astronomically large T lets Bob use very long gadgets; with T = 0 there
is no room at all (p_1 = a_1 is public and Ana wins with one guess).

## 5. Obstacles for Bob's construction

* Parity is public: p_n = a_1 + ... + a_n (mod 2), so at each turn the possible
  positions all have the same parity.
* A "block" gadget where all branches visit the same set S of values in the same
  window of times, with positions of different branches distinct at every
  time, requires the map "position at time n-1 -> position at time n" to be a
  permutation of S moving every element by exactly a_n. Such a permutation is a
  perfect matching of the difference-a_n graph on S, so the block needs |S|-1
  perfect matchings of S with distinct differences, each column of which is a
  Hamiltonian path. For |S| = 4 this is impossible (the three pairings of
  {x0<x1<x2<x3} would need x1-x0 = x3-x2, x2-x0 = x3-x1 and x3-x0 = x2-x1, and
  the last is absurd). Bob's tree therefore cannot be built from exact blocks
  of size 3 or 4; branches must differ in *when* they visit values, not only in
  the order within a common window.
* Branches that split at time n (positions P+a_n and P-a_n) each have to visit
  the other's value later; the later visit needs a step of exactly the right
  size at exactly the right time, which the fixed sequence a must supply for
  both branches simultaneously.

## 6. Why the two-guess strategy does not shrink to one guess

Call a schedule *single-target* if every guess is one of V, V + a_n, V - a_n,
V + a_{n+1}, V - a_{n+1} at turn n for one fixed unvisited value V (these are
the only values that catch "Bob is at V now", "Bob just left V" or "Bob is
about to arrive at V"). Suppose Bob visits V at time t with a_t < V and
a_{t+1} < V (a *bad* time for V). Both arrival directions V +- a_t and both
departure directions V +- a_{t+1} are positive, so a single guess at turn t-1
or t+1 covers only one of them and Bob takes the other; only the guess V at
turn t itself catches him, and V can be guessed once. Hence a single-target
schedule can cope with at most one bad time, and Bob only needs the freedom to
visit V at either of two bad times.

Bob can make bad times plentiful for every V at once: after turn T, list the
unused step sizes in increasing order. For any V the steps smaller than V then
occupy an initial segment of turns T+1..m, and every t in T+1..m-1 is bad; the
segment has at least a_1 + ... + a_T - T unused values below V_min, so with
T >= 3 every admissible target has at least two bad times. This does not by
itself give Bob a walk (he still has to cover everything while keeping two
options for V), but it rules out the obvious one-guess analogue of section 2
and tells a construction which shape to take.

## 7. Conjecture and what the finite experiments say

Theorem 2 leaves exactly one question: does one guess per turn suffice?

Finite analogue F(N, t0, K, M) (solver): steps 1..N (or, with --steps-max B,
any N distinct integers <= B, which is what Bob's first N steps are in the real
game), guessing from turn t0, must visit 1..K by turn N, values <= M.  The
option --late-cover K additionally makes Bob visit the K smallest values beyond
his reach before turn t0 (R+1..R+K with R = a_1+..+a_{t0-1}), the finite
version of the targets in Theorem 2.  The analogue cannot express "every value
must eventually be visited" beyond turn N, so l*(N) > 2 is an artefact of the
horizon; the informative question is whether Bob can beat one guess.

Findings (exhaustive for N <= 9 with steps 1..N; simulated annealing over walks
otherwise, so "not found" is evidence, not proof):

* t0 = 1 is trivial (l* = 1) and t0 = 2 gives l* = 1 for N = 4..9: two possible
  positions at the first guessed turn are not enough for Bob.
* No coverage (K = 0): Bob beats one guess for every t0 >= 3 and every N tried
  (7 <= N <= 12), often certified by spread < 1.  This is the measure argument
  of section 4 at work.
* Coverage that can be completed before turn t0 (K = 1, or K = 2 with steps
  2, 1 first; late-cover 1) changes nothing: Bob still beats one guess
  (N = 12, 14).
* Coverage that cannot be completed before t0 (K >= t0 - 1 with steps 1..N;
  late-cover 2 with free steps up to 2N; N = 8..16): every sequence examined
  loses to a one-guess schedule, exhaustively for N <= 9 and in every
  annealing run for N = 10..16.

Reading: in the finite game the second unreachable target is what kills Bob.
Whether this survives the passage to infinitely many turns and infinitely many
unreachable targets is the open question; the deadline N works for Ana, the
astronomically large T and the unbounded step sizes work for Bob.

Conjecture (weakly held): the answer is 2.  For: Theorem 2, the size of T
(which only matters if Bob needs a long hidden phase), and the freedom of
subset-sum-like position sets with increasing steps after T (section 6).
Against: every finite instance with two unreachable targets so far.  Deciding
it needs either an explicit a with an uncountable family of covering walks
that dodges every one-guess schedule (sections 3 to 6 constrain its shape) or
an Ana argument that turns "two unreachable targets" into a schedule.

## 8. What one guess forbids

A guess x on turn n hits exactly the walks with p_n = x. Seen from a value V
that Bob visits at time t (so p_{t-1} = V -+ a_t and p_{t+1} = V +- a_{t+1}),
the visit is caught by any of

    (t, V)                        the *direct* guard, usable once per V,
    (t-1, V + a_t)                the *arrival guard* (arrival from above),
    (t-1, V - a_t)                arrival from below, only possible if a_t < V,
    (t+1, V + a_{t+1})            the *departure guard* (upward departure),
    (t+1, V - a_{t+1})            downward departure, only possible if a_{t+1} < V.

Theorem 2 is the schedule that plays both departure guards at every turn. With
one guess per turn Ana has to choose. Two facts about a single target V > S_T
(S_T = a_1 + ... + a_T), writing D = {n > T : a_n < V} for the finitely many
turns on which a downward move from V is possible:

* *Modes.* Write E_n = V + a_n. Besides V itself (usable once), the guard
  E_n protects the visit at time n-1 when guessed on turn n (departure) and
  the visit at time n when guessed on turn n-1 (arrival). Guessing E_n on
  turn n and E_{n+1} on turn n would take two guesses on one turn, so a
  schedule built from the guards of V is in *arrival mode* (g_n = E_{n+1})
  up to some pivot turn s and in *departure mode* (g_n = E_n) after it, and
  whenever the arrival mode is non-empty the visit at time T+1 can only be
  guarded by V on turn T+1 (there is no turn T). Bob escapes such a schedule
  by a visit at a time t <= s in D arriving from below (p_{t-1} = V - a_t),
  or by a visit at a time n-1 > s with n in D leaving downward
  (p_n = V - a_n), and in pure departure mode V can plug only one such
  downward fork. Hence if Bob can leave V downward at two turns n_1 < n_2 of
  D and can arrive at V from below at some turn t <= n_2 - 1 of D, all inside
  covering walks, then no schedule built from the guards of V hits every
  walk. This is the precise form of section 6 and the reason the second
  guess of Theorem 2 cannot simply be dropped.
* *Parity.* p_n = a_1 + ... + a_n (mod 2), so on turn n only values of one
  parity can be positions. Departure guards of two targets of opposite parity
  (V and V+1, say) therefore never compete for the same turn: one guess per
  turn already runs departure mode for both. The obstruction is not the
  number of targets but the downward departures, which need a_n < V and are
  plentiful because Bob may use the S_T - T integers below V that the hidden
  phase did not use.

Ana's schedules are of course not restricted to guards of one or two targets,
so this only shows which natural strategies fail, not that all do.

## 9. Theorem 3: without the covering condition there is no finite l

The covering condition is what makes Theorem 2 work: it supplies one value
Bob is forced to visit. The next theorem shows it is essential.

**Theorem 3.** Consider the *survival variant*, in which Bob wins iff the
game goes on forever (no covering condition). For every l >= 1 and every
T with 2^(floor((T+1)/4)) > 8 l (in particular for l = 1 and T >= 15, and for
every l < 2^(floor((T+1)/4) - 3)), Bob has a sequence a against which no
schedule with l guesses per turn hits every valid walk.

*Construction.* Number the turns n = 1, 2, 3, ... and let

    turn n = 0 (mod 4)      free turn:    a_n = 2^(n/4 - 1)      (1, 2, 4, 8, ...),
    turn n = 1, 2 (mod 4)   lift turn:    a_n = 3 * 4^n,
    turn n = 3 (mod 4)      filler turn:  a_n = the smallest positive integer not
                            used before that is neither a power of two nor of the
                            form 3 * 4^m with m = 1, 2 (mod 4).

Every positive integer occurs exactly once (powers of two on the free turns,
the reserved values 3 * 4^m on the lift turns, every other integer on some
filler turn because only finitely many integers precede it). Bob's family W
of walks: sign + on every lift and filler turn, either sign on every free
turn; mu is the uniform (product) measure on the free signs.

*Validity.* Write p_n = C_n + X_n with C_n the sum of the lift and filler steps
up to turn n and X_n the signed sum of the free steps. X_n is a signed sum of
distinct powers of two, so |X_n| <= 2^F(n) - 1 with F(n) = floor(n/4), and X_n
determines its signs. Positivity: C_n >= 12 > |X_n| for n <= 4 and C_n >=
3 * 4^(n-2) > 2^(n/4) > |X_n| for n >= 2. Distinctness along a walk: for m < n
the window (m, n] contains a lift turn c >= n-2 unless it is a single turn
(sum +-a ≠ 0) or the pair {4k-1, 4k} (sum b +- 2^(k-1) ≠ 0 because the filler b
is not a power of two); in the first case p_n - p_m >= 3 * 4^c - 2 * 2^F(n) > 0.
So every one of the 2^F(n) sign choices gives a valid walk, and at every turn n
the walks of W occupy 2^F(n) distinct positions, each of mu-mass 2^(-F(n)).

*Spread.* For a schedule G with |G_n| <= l,

    mu(some guess is correct) <= sum_{n > T} sum_{x in G_n} mu(p_n = x)
                              <= l * sum_{n > T} 2^(-floor(n/4))
                              <= 8 l * 2^(-floor((T+1)/4)) < 1,

so some walk of W is never guessed and never gets stuck: Bob wins. QED.

Remarks. (i) The answer of the survival variant depends on T: with T = 0 Ana
wins with one guess (p_1 = a_1), with T >= 15 no fixed l works. (ii) The
construction is the pure form of section 4: hidden fine offsets (the powers
of two before turn T) give the 2^(-F(T)) factor and the continuing free turns
give the geometric decay; no coverage is possible for this family, because a
branch's offset modulo 2^k is frozen after its k-th free turn, so a far dip
(one large step taking all branches into a block of small values) always puts
the same branch on the same residue of every block, while covering would
require every branch to visit every value of the block. (iii) `python3
solver/passcode_solver.py --construction N --t0 t0` prints the first N steps,
the exact spread of the family (it equals the bound, the positions being
distinct) and, for N <= 14, the exact l*(a) over *all* valid walks; e.g. at
N = 12, t0 = 9 the family has spread 0.875 and l*(a) = 4 (the extra downward
moves on filler turns help Bob further in the finite game).

Theorem 2 and Theorem 3 together locate the whole difficulty of the puzzle in
the interaction between spread (section 4) and coverage.

## 10. Coverage versus spread

Theorem 3 also clarifies how much branching Bob needs. If mu is a measure on
covering walks with max_v mu(p_n = v) <= c n^(-1-eps) for n > T, then the sum
of section 4 is at most c' T^(-eps) < 1 once T is large; with the hidden phase
supplying a factor 2^(-K), a *logarithmic* number of binary choices by time n
already suffices. So the question is not the rate of branching but whether a
family of covering walks can branch forever at all without its branches
re-merging in (time, position).

*Local rigidity.* Where the branching cannot come from: `solver/sweep_window.py`
enumerates the walks with steps 1, 2, ..., N (in order) from a huge start that
visit every value within distance m of the start by time N (the local picture
of a covering walk with growing steps, positivity being irrelevant). The count
depends only on the slack s = N - 2m, not on N:

    slack s      0   1    2    3      4        5        6
    #walks       2   6   16   ~50   ~120     ~330    ~1000      (N = 10..24)

With s = 0 the only walks are the zig-zags 0, +1, -1, +2, -2, ... and their
mirror image, and the family's concentration is 1/2 at every turn. Sweeping
an interval is deterministic; the freedom (about 3 per unit of slack) lies in
the excursions outside it, and every excursion is a value that some later
sweep, with larger steps, must work around.

*Formation walks.* The natural way to reconcile the two is to keep Bob's
branches in *formation*: branch epsilon in {+-1}^k sits at P(n) + sum_i
epsilon_i u_i(n), all branches sweep translated copies of the same interval
with the same steps (rigidity is harmless: the sweep is common), and between
sweeps the formation is reshaped by signed transitions, a step u used with the
sign epsilon_i by branch epsilon changing the offset u_i by +-u for every
branch at once (the two-branch case is the swap gadget 3, 1, 2 of phase 1:
P + u -> P' + u -> P' - u and P - u -> P' - u -> P' + u with the steps
|P' - P| and 2u). In formation the positions at any time are distinct across
branches, so the spread condition holds automatically with F(n) = k(n) free
transitions. What is *not* automatic is coverage: a sweep around the low lane
L covers L, L-1, ..., L-m+1 and the high lane L + s, ..., L + s + m - 1, and
leaves the gap between them; branch epsilon's lanes are those of the common
skeleton shifted by sum epsilon_i u_i(n), so every branch must eventually
sweep every interval of every other branch. This is a scheduling problem on
intervals (which interval does each branch sweep in each round, with the
constraint that all branches use the same steps), and it is the concrete open
problem left by this phase:

    Formation problem. Find offsets u_i(n), a skeleton P(n) and a sequence
    of intervals such that (a) all branches' sweeps and transitions are
    legal with one common step sequence a that is a permutation of the
    positive integers, and (b) for every epsilon the union of branch
    epsilon's low and high lanes is the whole of the positive integers.

A solution gives the answer 2; a proof that no formation (or no family at
all) can satisfy (b) would be the heart of an Ana argument for the answer 1.

## 11. Status after phase 3

* Answer is 1 or 2 (Theorem 2; formalised in `lean/Passcode/TwoGuesses.lean`).
* Without coverage the answer would be "no finite l" for T >= 15 (Theorem 3),
  so any Ana argument for 1 must use coverage beyond the single forced visit
  of Theorem 2, and any Bob construction for 2 must solve the formation
  problem (or something equivalent) rather than just spread out.
* Conjecture unchanged (2, weakly): the formation mechanism supplies spread
  for free, and the requirement it leaves, a schedule of sweeps in which
  every branch eventually sweeps every interval, looks like a design problem
  rather than an impossibility; but it has resisted a quick solution and the
  finite experiments with two unreachable targets still all favour Ana.

## 12. Phase 4: what a one-guess Ana needs, what a one-guess Bob needs

The question left open is whether l = 1 suffices. This section records the
structural facts established in phase 4 and the resulting verdict. Script:
`solver/pair_search.py` (tests in `solver/test_pair_search.py`).

### 12.1 Reformulations

* Bob needs no family. Since Ana's strategy is a schedule G (section 1), Bob
  beats l guesses iff for *every* valid schedule with l guesses per turn there
  is a covering walk avoiding it. The measure certificate of section 4 is a
  sufficient condition, not the definition; a Bob strategy may pick the walk
  after seeing the whole schedule.
* A covering walk visits every value exactly once, so p is a permutation of
  the positive integers (with p_0 = 0), a = |Delta p| is a permutation as
  well, and p_n -> infinity along every valid walk (the walk stays in [1, K]
  for at most K turns). Restricted to turns n > T, a walk is a perfect
  matching between turns and the values unvisited at time T, and a one-guess
  schedule is a partial matching; Ana wins iff her matching meets every Bob
  matching.

### 12.2 One guess removes one node per turn

Let Bob's walks form a tree in which the branches alive at time n occupy
2^k(n) distinct positions, with the uniform measure on branches. One guess
per turn removes mass at most 2^(-k(n)) at turn n, so the schedule removes
total mass at most sum_{n > T} 2^(-k(n)): with k(n) >= (1 + eps) log_2 n
the removed mass is O(T^(-eps)) < 1. Branching once per doubling of n is
therefore already enough spread, given the size of T; the whole difficulty
is that every branch must cover (as section 10 concluded). Ana's actual
optimum is a matching problem and can be better than this bound, but the
bound is what any Bob construction has to satisfy.

### 12.3 Synchronised windows are useless for Bob

If, during a window of L turns, all branches visit the same set S of L
values (in different orders), the positions at each turn of the window lie
in S, so the most popular position has mass >= 1/L and the window
contributes >= 1 to the spread sum. Bob's branches must therefore be
*desynchronised*: at any time after T different branches must have visited
different sets, and each branch's "debt" (values visited by other branches
but not by it) must be settled later without ever re-synchronising the whole
family. Full re-merging (same set and same final position) is also fatal (a
single guess at the merge point kills everything) and does not occur in
small cases anyway: no such gadget exists for windows of L <= 6 steps drawn
from 1..12 (`pair_search.py merge`).

### 12.4 Debt-free pairs exist, mirror and non-mirror

Two walks with the same steps, distinct positions on every turn >= 2 and
identical visited sets at the end ("debt-free pairs") do exist:

* Mirror pairs. Reflecting the future of a walk about its current position
  keeps every step size: if A is a walk and c = A_t, then B_n = 2c - A_n for
  n > t is a walk with the same steps, valid as long as A_n <= 2c - 1. If the
  set A visits after t is symmetric about c, the pair is debt-free with B at
  the mirror position. Example: a = 8, 7, 4, 10, 1, 3, 9 with A = 8, 15,
  11, 1, 2, 5, 14 and B = 16 - A = 8, 1, 5, 15, 14, 11, 2 (common set
  {1, 2, 5, 8, 11, 14, 15}, final positions 14 and 2).
* Non-mirror pairs. a = 3, 1, 4, 2, 5, 8, 7 with A = 3, 4, 8, 6, 1, 9, 2 and
  B = 3, 2, 6, 4, 9, 1, 8: B is the translate A - 2 for three turns (visiting
  {2, 6, 4} against A's {4, 8, 6}), then the branches cross (A: 1, 9, 2;
  B: 9, 1, 8) and the sets agree again.

Exhaustive counts (N steps from 1..9, t0 = 2): N = 5: 108 mirror, 0 other;
N = 6: none; N = 7: 1058 mirror, 86 non-mirror. So the two-branch
synchronisation that section 5 could not get from blocks of 3 or 4 values
is available from turn 5 on, provided the branches end at different
positions. By 12.3 such gadgets cannot be used to re-synchronise the whole
family, but they show how debts are settled locally: by translation
followed by a crossing, or by reflection about a pivot.

### 12.5 The reflection-translation family

Every walk of the form p_n = eps(n) A_n + kappa(n), with eps = +-1 and kappa
piecewise constant and (eps, kappa) changing only by "reflect the future
about the current position" (eps -> -eps, kappa -> kappa + 2 eps A_t), has
the steps of the master walk A. This gives a clean two-branch design:

* Cut A into window pairs (W_{2i-1}, W_{2i}) with t_{2i-1} < t_{2i} < t_{2i+1}.
* Branch B is the translate A + kappa_{i-1} at time t_{2i-1}, reflects there,
  and reflects back at t_{2i}; afterwards it is the translate A + kappa_i
  with kappa_i = kappa_{i-1} + 2 (A_{t_{2i-1}} - A_{t_{2i}}).
* B visits, in W_{2i-1}, the mirror image of A's W_{2i-1}-set about
  A_{t_{2i-1}} + kappa_{i-1}, and in W_{2i} the translate by kappa_i of A's
  W_{2i}-set. B is covering iff these are A's two sets in the other order,
  i.e. iff A's W_{2i-1}-set is symmetric about a prescribed centre and A's
  W_{2i}-set is the prescribed translate of it.
* Positivity of B during a reflected window bounds A's excursion by
  2 A_{t_{2i-1}} + kappa_{i-1} - 1, and kappa must never return to 0.

A constraint on the segments: a two-lane zigzag set (section 10) can only be
swept by a zigzag with its own lane distance, so a set that must be swept
twice with different step blocks needs at least three symmetric lane pairs;
with six lanes at positions l_1 < l_2 < l_3 < h_3 < h_2 < h_1 (h_j = 2c -
l_j) the pairings (l_j, h_j) and (l_1, h_1'), (l_2, h_3), (l_3, h_2) give six
distinct distances whenever the l_j avoid arithmetic progressions. For more
than one bit, only a branch whose current offset equals kappa_{i-1} can
reflect at pair i and still visit A's sets, so a k-bit version needs A's
segments to form a grid closed under the offsets and reflections in play.
This is the concrete form of the formation problem of section 10 for this
class of families; it is a design problem with many free parameters (window
lengths, lane counts, lane positions, which pairs each branch swaps) and no
obstruction found, but it has not been completed.

### 12.6 Ana's side: guards, ghosts and parity

* Parity split. On turn n only values congruent to S_n mod 2 can be
  positions, so one guess per turn can run the upward departure guard
  (V + a_n or V + 1 + a_n, whichever has the right parity) for the two
  adjacent targets V = S_T + 1 and V + 1 simultaneously.
* Escapes. Against such a schedule Bob escapes only by visiting a target at
  a time t with a_{t+1} < V and leaving downward. The steps below V unused
  at time T number S_T - T, and Bob places them where he likes, so escapes
  are available to him at every target; Ana can plug one downward fork per
  target by guessing the target itself.
* Ghosts. After an escape Ana knows the escaped walk's position (a "ghost")
  but has no spare guess: every turn she does not guard creates one or two
  new ghosts, and a ghost subtree that is full binary with distinct
  positions loses at most 2^m - 1 of its 2^m depth-m leaves to any schedule
  (one node per level). So target-guard strategies cannot be repaired by
  chasing; a one-guess Ana argument would have to use coverage in a
  genuinely different way, and none has been found.

### 12.7 Verdict

The answer is 1 or 2 (Theorem 2, formalised). Phase 4's assessment is that
the answer is **2**:

* The only thing that stops Bob is coverage, and coverage is compatible with
  the two mechanisms he needs (debt settlement by reflection or by
  translate-and-cross, 12.4) in every small case examined; the finite
  experiments favouring Ana (section 7) all impose a deadline, which is
  exactly the synchronisation that 12.3 shows Bob must avoid, so they do
  not bear on the infinite game.
* The natural one-guess Ana strategies fail for a structural reason (12.6)
  that does not depend on N or T, and the countable-family lemma (section 3)
  is the only general Ana tool available; nothing in the analysis suggests a
  hidden Ana argument.
* The threshold T = 2026^2026^2026 only ever helps Bob (12.2: it turns any
  branching rate of one bit per doubling into a winning spread), which is
  the role a large T plays if and only if the intended answer is 2; for an
  answer of 1 its size would be irrelevant.

What is proved: l <= 2, and every structural requirement on a Bob
construction listed above. What is not proved: an explicit sequence a with a
family of covering walks meeting 12.2. The reflection-translation family of
12.5 is the recommended route to it.
