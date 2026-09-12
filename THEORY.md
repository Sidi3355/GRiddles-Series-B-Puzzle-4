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
