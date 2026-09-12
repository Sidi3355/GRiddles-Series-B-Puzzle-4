/-
# Two guesses suffice for Ana (THEORY.md, Theorem 2)

Core-Lean formalisation (no Mathlib import, so it builds without the Mathlib
cache) of the upper bound `l ≤ 2` for the GRiddles Series B Puzzle 4 game.

Model.  Turns are `1, 2, 3, …`; `a n` is Bob's step on turn `n` (`a 0` is
unused).  A walk is a position function `p : Nat → Int` with `p 0 = 0`,
`p (n+1) = p n ± a (n+1)` and `p (n+1) ≥ 1`.  (Distinctness of the passcodes
is not needed for the upper bound, so it is not assumed.)  A walk is covering
if every positive integer is some `p t`.

Ana's schedule is a list of guesses per turn.  It is valid if no turn has a
repeated guess, no value is guessed on two different turns, and nothing is
guessed on turns `≤ T`.  A schedule hits a walk if some guess is correct.

Theorem `two_guesses_suffice`: for every injective step sequence with positive
steps and every threshold `T`, there is a valid schedule with at most two
guesses per turn that hits every covering walk.  The schedule is the one of
THEORY.md section 2: with `V = 1 + a 1 + ⋯ + a T`, guess `V` on turn `T+1` and
`V + a n`, `V - a n` (the latter only if positive) on every turn `n ≥ T+2`.
-/

namespace Passcode

/-- `partialSum a n = a 1 + ⋯ + a n`. -/
def partialSum (a : Nat → Nat) : Nat → Nat
  | 0 => 0
  | n + 1 => partialSum a n + a (n + 1)

/-- Bob's walk for the step sequence `a`. -/
structure IsWalk (a : Nat → Nat) (p : Nat → Int) : Prop where
  zero : p 0 = 0
  step : ∀ n, p (n + 1) = p n + (a (n + 1) : Int) ∨ p (n + 1) = p n - (a (n + 1) : Int)
  pos : ∀ n, 1 ≤ p (n + 1)

/-- Every positive integer appears as a passcode. -/
def Covering (p : Nat → Int) : Prop :=
  ∀ v : Int, 1 ≤ v → ∃ t, p t = v

/-- A schedule assigns a list of guesses to every turn. -/
def Schedule := Nat → List Int

/-- Valid schedule for threshold `T`: nothing before turn `T+1`, no repeated
guess within a turn, no value guessed on two different turns. -/
structure ValidSchedule (T : Nat) (G : Schedule) : Prop where
  early : ∀ n, n ≤ T → G n = []
  nodup : ∀ n, (G n).Nodup
  disjoint : ∀ m n x, x ∈ G m → x ∈ G n → m = n

/-- The schedule hits the walk `p`: some guess is correct. -/
def Hits (G : Schedule) (p : Nat → Int) : Prop :=
  ∃ n, p n ∈ G n

/-! ### Positions are bounded by the partial sums -/

theorem abs_le_partialSum {a : Nat → Nat} {p : Nat → Int} (h : IsWalk a p) (n : Nat) :
    -(partialSum a n : Int) ≤ p n ∧ p n ≤ partialSum a n := by
  induction n with
  | zero => simp [partialSum, h.zero]
  | succ n ih =>
    rcases h.step n with hs | hs <;> simp only [partialSum] <;> omega

/-! ### Ana's two-guess schedule -/

/-- The target value `V = 1 + a 1 + ⋯ + a T`: unvisited at time `T`. -/
def target (a : Nat → Nat) (T : Nat) : Int := 1 + (partialSum a T : Int)

/-- Ana's schedule: `V` on turn `T+1`; `V + a n` and (if positive) `V - a n` on
turns `n ≥ T+2`. -/
def twoGuessSchedule (a : Nat → Nat) (T : Nat) : Schedule := fun n =>
  if n ≤ T then []
  else if n = T + 1 then [target a T]
  else if 1 ≤ target a T - (a n : Int) then [target a T + a n, target a T - a n]
  else [target a T + a n]

theorem twoGuessSchedule_length (a : Nat → Nat) (T n : Nat) :
    (twoGuessSchedule a T n).length ≤ 2 := by
  unfold twoGuessSchedule
  split <;> (try split) <;> (try split) <;> simp

/-- Membership in the schedule, unfolded. -/
theorem mem_twoGuessSchedule {a : Nat → Nat} {T n : Nat} {x : Int} :
    x ∈ twoGuessSchedule a T n ↔
      (n = T + 1 ∧ x = target a T) ∨
      (T + 2 ≤ n ∧ x = target a T + a n) ∨
      (T + 2 ≤ n ∧ x = target a T - a n ∧ 1 ≤ target a T - (a n : Int)) := by
  unfold twoGuessSchedule
  split
  · simp; omega
  · split
    · simp; omega
    · split
      · simp; omega
      · simp; omega

theorem twoGuessSchedule_valid (a : Nat → Nat) (T : Nat)
    (hpos : ∀ n, 1 ≤ n → 1 ≤ a n)
    (hinj : ∀ m n, 1 ≤ m → 1 ≤ n → a m = a n → m = n) :
    ValidSchedule T (twoGuessSchedule a T) where
  early := by
    intro n hn
    simp [twoGuessSchedule, hn]
  nodup := by
    intro n
    unfold twoGuessSchedule
    split
    · simp
    · split
      · simp
      · split
        · have := hpos n (by omega)
          simp; omega
        · simp
  disjoint := by
    intro m n x hm hn
    rw [mem_twoGuessSchedule] at hm hn
    have hm1 : 1 ≤ m := by rcases hm with h | h | h <;> omega
    have hn1 : 1 ≤ n := by rcases hn with h | h | h <;> omega
    have am := hpos m hm1
    have an := hpos n hn1
    rcases hm with ⟨hm, rfl⟩ | ⟨hm, rfl⟩ | ⟨hm, rfl, hm'⟩ <;>
      rcases hn with ⟨hn, hx⟩ | ⟨hn, hx⟩ | ⟨hn, hx, hn'⟩
    all_goals first
      | omega
      | exact hinj m n hm1 hn1 (by omega)
      | (exfalso; omega)

/-! ### The main theorem -/

theorem twoGuessSchedule_hits {a : Nat → Nat} {T : Nat} {p : Nat → Int}
    (hw : IsWalk a p) (hc : Covering p) :
    Hits (twoGuessSchedule a T) p := by
  -- Bob visits `V` at some time `t`; `V` exceeds every position up to time `T`.
  obtain ⟨t, ht⟩ := hc (target a T) (by unfold target; omega)
  have htT : T + 1 ≤ t := by
    rcases Nat.lt_or_ge t (T + 1) with hlt | hge
    · exfalso
      have hb := abs_le_partialSum hw t
      have hmono : partialSum a t ≤ partialSum a T := by
        have key : ∀ k, partialSum a t ≤ partialSum a (t + k) := by
          intro k
          induction k with
          | zero => exact Nat.le_refl _
          | succ k ih =>
            exact Nat.le_trans ih (Nat.le_add_right (partialSum a (t + k)) (a (t + k + 1)))
        have h := key (T - t)
        have e : t + (T - t) = T := by omega
        rw [e] at h
        exact h
      unfold target at ht
      omega
    · exact hge
  rcases Nat.eq_or_lt_of_le htT with h | h
  · -- visited exactly on turn `T+1`: guessed there
    exact ⟨t, by rw [mem_twoGuessSchedule]; left; exact ⟨h.symm, ht⟩⟩
  · -- visited on turn `t ≥ T+2`: the next passcode `V ± a (t+1)` is guessed on turn `t+1`
    refine ⟨t + 1, ?_⟩
    rw [mem_twoGuessSchedule]
    have hp := hw.pos t
    rcases hw.step t with hs | hs
    · right; left; exact ⟨by omega, by rw [hs, ht]⟩
    · right; right; refine ⟨by omega, by rw [hs, ht], ?_⟩
      rw [← ht]; omega

/-- **Theorem 2.**  Against any injective sequence of positive steps and any
threshold `T`, Ana has a valid schedule with at most two guesses per turn
that hits every covering walk; so `l = 2` suffices. -/
theorem two_guesses_suffice (a : Nat → Nat) (T : Nat)
    (hpos : ∀ n, 1 ≤ n → 1 ≤ a n)
    (hinj : ∀ m n, 1 ≤ m → 1 ≤ n → a m = a n → m = n) :
    ∃ G : Schedule, ValidSchedule T G ∧ (∀ n, (G n).length ≤ 2) ∧
      ∀ p, IsWalk a p → Covering p → Hits G p :=
  ⟨twoGuessSchedule a T, twoGuessSchedule_valid a T hpos hinj,
    twoGuessSchedule_length a T, fun _ hw hc => twoGuessSchedule_hits hw hc⟩

/-- The two-guess schedule does not use the size of `T` (remark after Theorem 2),
and the hitting turn is at most one after Bob's visit to the target. -/
theorem twoGuessSchedule_hits_soon {a : Nat → Nat} {T : Nat} {p : Nat → Int}
    (hw : IsWalk a p) {t : Nat} (ht : p t = target a T) (htT : T + 1 ≤ t) :
    p t ∈ twoGuessSchedule a T t ∨ p (t + 1) ∈ twoGuessSchedule a T (t + 1) := by
  rcases Nat.eq_or_lt_of_le htT with h | h
  · left; rw [mem_twoGuessSchedule]; left; exact ⟨h.symm, ht⟩
  · right; rw [mem_twoGuessSchedule]
    have hp := hw.pos t
    rcases hw.step t with hs | hs
    · right; left; exact ⟨by omega, by rw [hs, ht]⟩
    · right; right; refine ⟨by omega, by rw [hs, ht], ?_⟩
      rw [← ht]; omega

end Passcode
