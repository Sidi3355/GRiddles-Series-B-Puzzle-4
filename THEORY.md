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
